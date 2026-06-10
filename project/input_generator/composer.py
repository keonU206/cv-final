"""SC-FEGAN 9채널 입력 통합 — sketch + color + mask + noise + incomplete image.

SC-FEGAN 원논문(Jo & Park 2019) 입력 채널 (총 9):
    - incomplete_image: (3) 원본 image의 mask 영역을 0으로 가린 것
    - sketch:           (1) 사용자 가이드 라인 (binary)
    - color:            (3) 사용자 색칠 가이드 (RGB)
    - mask:             (1) 편집 영역 binary mask
    - noise:            (1) gaussian noise (random latent)

본 모듈은 procedure dict(또는 procedure_id 문자열)와 image + landmarks
입력만으로 위 9채널을 자동 생성한다.

⚠ sketch.py와 mask.py/color.py의 패턴 불일치 어댑팅:
    - sketch.py: procedure_id 문자열 기반 (nose_tip / double_eyelid / v_line)
    - mask/color.py: procedure dict 기반 (procedures.yaml 항목)
    - procedures.yaml의 'jaw_v_line' ↔ sketch.py의 'v_line' 매핑 필요
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import numpy as np

from .color import make_color
from .mask import make_mask
from .sketch import SKETCH_GENERATORS, generate_sketch

# procedures.yaml의 id → sketch.py의 SKETCH_GENERATORS key 매핑
PROCEDURE_ID_TO_SKETCH = {
    "nose_tip": "nose_tip",
    "double_eyelid": "double_eyelid",
    "jaw_v_line": "v_line",
}

DEFAULT_PROCEDURES_YAML = (
    Path(__file__).resolve().parents[1] / "recommender" / "procedures.yaml"
)


def load_procedures(yaml_path: str | Path = DEFAULT_PROCEDURES_YAML) -> dict[str, dict]:
    """procedures.yaml 로드 후 id → procedure dict 매핑 반환.

    Args:
        yaml_path: procedures.yaml 경로 (기본: project/recommender/procedures.yaml).

    Returns:
        {procedure_id: procedure_dict} — 예: {"nose_tip": {...}, ...}.
    """
    import yaml

    with open(yaml_path, "r", encoding="utf-8") as f:
        items = yaml.safe_load(f)
    return {item["id"]: item for item in items}


def _resolve_procedure(
    procedure: str | dict[str, Any],
    procedures_db: Optional[dict[str, dict]] = None,
) -> dict[str, Any]:
    """procedure 인자가 id 문자열이면 dict로 변환, dict면 그대로 반환."""
    if isinstance(procedure, dict):
        return procedure
    if procedures_db is None:
        procedures_db = load_procedures()
    if procedure not in procedures_db:
        raise ValueError(
            f"unknown procedure id={procedure!r}. "
            f"available: {list(procedures_db.keys())}"
        )
    return procedures_db[procedure]


def _sketch_key_for(procedure: dict[str, Any]) -> str:
    """procedure dict의 id를 sketch.py의 키로 변환."""
    pid = procedure.get("id", "")
    sketch_key = PROCEDURE_ID_TO_SKETCH.get(pid)
    if sketch_key is None or sketch_key not in SKETCH_GENERATORS:
        raise ValueError(
            f"procedure id={pid!r}에 대한 sketch generator 없음. "
            f"PROCEDURE_ID_TO_SKETCH 매핑 또는 SKETCH_GENERATORS 확인."
        )
    return sketch_key


def compose_scfegan_input(
    image: np.ndarray,
    landmarks: np.ndarray,
    procedure: str | dict[str, Any],
    size: int = 512,
    intensity: float = 0.5,
    noise_sigma: float = 1.0,
    seed: Optional[int] = None,
    procedures_db: Optional[dict[str, dict]] = None,
) -> dict[str, np.ndarray]:
    """SC-FEGAN 9채널 입력을 dict 형태로 생성.

    Args:
        image: (size, size, 3) uint8 RGB. 원본 얼굴 이미지.
        landmarks: (478, 2) int32. MediaPipe Face Mesh 좌표.
        procedure: procedure id 문자열 또는 procedure dict.
        size: 출력 H, W.
        intensity: sketch 변형 강도 (0.0~1.0).
        noise_sigma: gaussian noise 표준편차.
        seed: noise 재현성 seed.
        procedures_db: 미리 로드한 procedures dict (반복 호출 시 캐시).

    Returns:
        {
            'incomplete_image': (size, size, 3) uint8 — mask 영역 0,
            'sketch':           (size, size, 1) uint8 — 0/255,
            'color':            (size, size, 3) uint8,
            'mask':             (size, size, 1) uint8 — 0/255,
            'noise':            (size, size, 1) float32 — N(0, σ²),
            'procedure':        dict — 사용된 procedure 항목,
        }

    Raises:
        ValueError: image shape 불일치 또는 알 수 없는 procedure id.
    """
    if image.shape[:2] != (size, size):
        raise ValueError(
            f"image shape {image.shape[:2]} != ({size}, {size})"
        )

    proc = _resolve_procedure(procedure, procedures_db)

    # 1. mask
    mask = make_mask(landmarks, proc, size=size)  # (size, size, 1)

    # 2. color
    color = make_color(image, landmarks, proc, size=size)  # (size, size, 3)

    # 3. sketch (procedure_id 어댑팅)
    sketch_key = _sketch_key_for(proc)
    sketch_2d = generate_sketch(
        landmarks, procedure_id=sketch_key, intensity=intensity, size=size
    )
    sketch = sketch_2d[..., None]  # (size, size, 1)

    # 4. incomplete image (mask 영역 0)
    mask_bool = mask[..., 0] > 0
    incomplete = image.copy()
    incomplete[mask_bool] = 0

    # 5. noise
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, noise_sigma, size=(size, size, 1)).astype(np.float32)

    return {
        "incomplete_image": incomplete,
        "sketch": sketch,
        "color": color,
        "mask": mask,
        "noise": noise,
        "procedure": proc,
    }


def to_scfegan_tensor(
    composed: dict[str, np.ndarray],
    normalize: bool = True,
    channels_first: bool = False,
    batch_dim: bool = False,
) -> np.ndarray:
    """compose_scfegan_input의 dict를 (size, size, 9) 단일 numpy 배열로 변환.

    채널 순서 (SC-FEGAN 원논문 순서):
        [incomplete(3), sketch(1), color(3), mask(1), noise(1)] = 9

    Args:
        composed: compose_scfegan_input() 반환 dict.
        normalize: True면 image/color를 [-1, 1]로, mask/sketch를 [0, 1]로 정규화.
        channels_first: True면 (C, H, W) 순서로 변환 (PyTorch).
        batch_dim: True면 앞에 batch 차원 추가.

    Returns:
        (size, size, 9) 또는 (9, size, size) 또는 batch dim 포함.
        dtype: normalize=True면 float32, 아니면 원본 dtype (uint8 캐스팅).
    """
    incomplete = composed["incomplete_image"]
    sketch = composed["sketch"]
    color = composed["color"]
    mask = composed["mask"]
    noise = composed["noise"]

    if normalize:
        # image, color: [0, 255] → [-1, 1]
        incomplete_n = (incomplete.astype(np.float32) / 127.5) - 1.0
        color_n = (color.astype(np.float32) / 127.5) - 1.0
        # mask, sketch: [0, 255] → [0, 1]
        sketch_n = sketch.astype(np.float32) / 255.0
        mask_n = mask.astype(np.float32) / 255.0
        # noise: 이미 float32, 그대로
        noise_n = noise
        stacked = np.concatenate(
            [incomplete_n, sketch_n, color_n, mask_n, noise_n], axis=-1
        )
    else:
        stacked = np.concatenate(
            [incomplete, sketch, color, mask, noise.astype(np.uint8)], axis=-1
        )

    if channels_first:
        stacked = np.transpose(stacked, (2, 0, 1))  # (9, H, W)

    if batch_dim:
        stacked = stacked[None, ...]

    return stacked


def compose_and_pack(
    image: np.ndarray,
    landmarks: np.ndarray,
    procedure: str | dict[str, Any],
    size: int = 512,
    intensity: float = 0.5,
    **tensor_kwargs,
) -> np.ndarray:
    """compose_scfegan_input + to_scfegan_tensor 일괄 처리.

    Returns:
        SC-FEGAN에 바로 feed 가능한 numpy 배열.
    """
    composed = compose_scfegan_input(
        image, landmarks, procedure, size=size, intensity=intensity
    )
    return to_scfegan_tensor(composed, **tensor_kwargs)
