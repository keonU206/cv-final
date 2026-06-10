"""SC-FEGAN Fine-tuning 데이터 파이프라인.

CelebAMask-HQ에서 2,000장 sampling → MediaPipe로 랜드마크 추출 →
project.input_generator.compose_scfegan_input으로 9채널 입력 생성.

⚠ MediaPipe 0.10.21 권장 (이전 호환).
⚠ 랜드마크 추출 실패 이미지는 자동 skip.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

import numpy as np

try:
    import cv2
except ImportError as e:
    raise ImportError("opencv-python 필요") from e


@dataclass
class FineTuneSamplePack:
    """1개 학습 sample 묶음.

    Fields:
        image: (H, W, 3) uint8 RGB — 원본 (target).
        composed: dict — compose_scfegan_input 결과 (9채널).
        procedure_id: str — 사용된 시술 (랜덤 sampling).
        source_path: str — 원본 이미지 경로 (디버깅).
    """
    image: np.ndarray
    composed: dict
    procedure_id: str
    source_path: str


def sample_celebamask_subset(
    image_dir: str | Path,
    n: int = 2000,
    seed: int = 0,
    exts: tuple = (".jpg", ".jpeg", ".png"),
) -> list[Path]:
    """폴더에서 n개 이미지 경로를 deterministic하게 sampling.

    Args:
        image_dir: clean image 폴더.
        n: 추출 개수.
        seed: 재현성.
        exts: 허용 확장자.

    Returns:
        [Path, ...] — 길이 ≤ n (폴더에 부족하면 전체).
    """
    image_dir = Path(image_dir)
    paths = sorted(p for p in image_dir.rglob("*") if p.suffix.lower() in exts)
    if not paths:
        raise FileNotFoundError(f"no images in {image_dir}")
    if len(paths) <= n:
        return paths
    rng = random.Random(seed)
    return sorted(rng.sample(paths, n))


def _load_image_rgb(path: Path, size: int = 512) -> np.ndarray:
    img = cv2.imread(str(path))
    if img is None:
        raise IOError(f"failed to read {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if img.shape[:2] != (size, size):
        img = cv2.resize(img, (size, size))
    return img


def _extract_landmarks_mediapipe(image_rgb: np.ndarray, size: int) -> Optional[np.ndarray]:
    """MediaPipe Face Mesh로 478점 추출. 실패 시 None."""
    try:
        import mediapipe as mp
    except ImportError as e:
        raise ImportError("mediapipe==0.10.21 필요") from e

    mp_face = mp.solutions.face_mesh
    with mp_face.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True,
    ) as fm:
        res = fm.process(image_rgb)
    if not res.multi_face_landmarks:
        return None
    lms = res.multi_face_landmarks[0].landmark
    h, w = image_rgb.shape[:2]
    pts = np.array([[lm.x * w, lm.y * h] for lm in lms], dtype=np.float32)
    if w != size:
        pts = pts * (size / w)
    return pts.astype(np.int32)


def build_finetune_sample(
    image_path: Path,
    procedure_id: str,
    size: int = 512,
    intensity: float = 0.5,
    seed: Optional[int] = None,
) -> Optional[FineTuneSamplePack]:
    """1개 이미지에서 학습 sample 생성. 랜드마크 실패 시 None."""
    from project.input_generator import compose_scfegan_input

    image = _load_image_rgb(image_path, size=size)
    lm = _extract_landmarks_mediapipe(image, size=size)
    if lm is None:
        return None

    composed = compose_scfegan_input(
        image, lm, procedure_id, size=size, intensity=intensity, seed=seed,
    )
    return FineTuneSamplePack(
        image=image, composed=composed,
        procedure_id=procedure_id, source_path=str(image_path),
    )


def iter_finetune_samples(
    image_paths: list[Path],
    procedure_ids: tuple = ("nose_tip", "double_eyelid", "jaw_v_line"),
    size: int = 512,
    intensity_range: tuple[float, float] = (0.3, 0.8),
    skip_failed: bool = True,
    seed: int = 0,
) -> Iterator[FineTuneSamplePack]:
    """학습 sample iterator.

    각 이미지에 대해 시술 1개를 랜덤 sampling, intensity도 랜덤.

    Yields:
        FineTuneSamplePack — 랜드마크 실패 시 skip.
    """
    rng = random.Random(seed)
    for i, p in enumerate(image_paths):
        proc_id = rng.choice(procedure_ids)
        intensity = rng.uniform(*intensity_range)
        try:
            pack = build_finetune_sample(
                p, proc_id, size=size, intensity=intensity, seed=seed + i,
            )
        except Exception as e:
            if skip_failed:
                print(f"  skip {p.name}: {e}")
                continue
            raise
        if pack is None:
            if skip_failed:
                continue
            raise RuntimeError(f"landmark extraction failed: {p}")
        yield pack
