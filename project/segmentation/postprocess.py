"""U-Net 출력 후처리.

핵심: 학습 단계에서는 jaw/forehead 라벨이 없어 skin으로 묶었음.
추론 후 MediaPipe 478 랜드마크로 skin 영역을 jaw/forehead로 분리.

전략:
- jaw: skin ∩ (입술 아래 영역) — landmark 14 (lip_bottom) 기준
- forehead: skin ∩ (눈썹 위 영역) — landmark 55/285 (brow_inner) 기준
"""
from __future__ import annotations

import numpy as np

# MediaPipe Face Mesh 478 인덱스 (face_analyzer/ratios.py 와 일치)
IDX_FOREHEAD_TOP = 10
IDX_BROW_INNER_LEFT = 55
IDX_BROW_INNER_RIGHT = 285
IDX_LIP_BOTTOM = 14
IDX_CHIN = 152


def split_skin_by_landmarks(
    skin_mask: np.ndarray,
    landmarks: np.ndarray,
    margin: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """skin 영역을 jaw / forehead 로 분리.

    Args:
        skin_mask: (H, W) uint8 binary. U-Net 출력의 skin 클래스 픽셀 (255 또는 0).
        landmarks: (478, 2) int32. MediaPipe 478점 (정규화된 512 공간).
        margin: 경계 여유 픽셀.

    Returns:
        (jaw_mask, forehead_mask) — 각 (H, W) uint8 binary.
    """
    if skin_mask.ndim != 2:
        raise ValueError(f"skin_mask는 2D여야 합니다. got {skin_mask.shape}")
    if landmarks.shape != (478, 2):
        raise ValueError(f"landmarks shape (478, 2) 필요. got {landmarks.shape}")

    h, w = skin_mask.shape

    # 입술 아래 Y
    lip_bottom_y = int(landmarks[IDX_LIP_BOTTOM][1])
    # 눈썹 위 Y
    brow_y = int(min(landmarks[IDX_BROW_INNER_LEFT][1],
                     landmarks[IDX_BROW_INNER_RIGHT][1]))

    # jaw: skin 픽셀 중 Y >= lip_bottom_y + margin
    jaw_mask = skin_mask.copy()
    cutoff_jaw = min(h, lip_bottom_y + margin)
    jaw_mask[:cutoff_jaw, :] = 0

    # forehead: skin 픽셀 중 Y <= brow_y - margin
    forehead_mask = skin_mask.copy()
    cutoff_fore = max(0, brow_y - margin)
    forehead_mask[cutoff_fore:, :] = 0

    return jaw_mask, forehead_mask


def get_procedure_masks(
    pred_label: np.ndarray,
    landmarks: np.ndarray,
) -> dict[str, np.ndarray]:
    """추론 결과 (6 클래스 라벨맵)에서 시술별 마스크 dict 추출.

    Args:
        pred_label: (H, W) uint8/long. argmax 결과, 값 0~5.
        landmarks: (478, 2) int32. MediaPipe.

    Returns:
        {
          'background': (H, W) uint8,
          'nose':       (H, W) uint8,
          'eye':        (H, W) uint8,
          'mouth':      (H, W) uint8,
          'skin':       (H, W) uint8,
          'jaw':        (H, W) uint8,  # skin에서 분리
          'forehead':   (H, W) uint8,  # skin에서 분리
        }
        값은 255 (마스크) 또는 0 (배경).
    """
    masks: dict[str, np.ndarray] = {}
    for idx, name in enumerate(["background", "nose", "eye", "mouth", "skin"]):
        masks[name] = ((pred_label == idx).astype(np.uint8)) * 255

    jaw, forehead = split_skin_by_landmarks(masks["skin"], landmarks)
    masks["jaw"] = jaw
    masks["forehead"] = forehead
    return masks
