"""CelebAMask-HQ 19 클래스 → 우리 5 학습 클래스 매핑.

학습 단계에서는 jaw/forehead 라벨이 없으므로 skin으로 묶어 학습.
추론 후 postprocess.py 에서 MediaPipe 랜드마크로 jaw/forehead 분리.
"""
from __future__ import annotations

import numpy as np

# CelebAMask-HQ 원본 19 라벨 (0 = background)
ORIGINAL_LABELS = {
    "background": 0,
    "skin": 1,
    "nose": 2,
    "eye_g": 3,
    "l_eye": 4,
    "r_eye": 5,
    "l_brow": 6,
    "r_brow": 7,
    "l_ear": 8,
    "r_ear": 9,
    "mouth": 10,
    "u_lip": 11,
    "l_lip": 12,
    "hair": 13,
    "hat": 14,
    "ear_r": 15,
    "neck_l": 16,
    "neck": 17,
    "cloth": 18,
}

# 우리 6 클래스 (5 + bg)
OURS = {
    "background": 0,
    "nose": 1,
    "eye": 2,
    "mouth": 3,
    "skin": 4,
    "unused": 5,
}

# 매핑 테이블 (19 → 6)
# 눈썹은 eye 클래스에 합침 (시술 부위 아님 + flip 시 좌/우 교환 회피)
MAPPING: dict[int, int] = {
    0: 0,   # bg            -> bg
    1: 4,   # skin          -> skin
    2: 1,   # nose          -> nose
    3: 0,   # eye_g (안경)   -> bg
    4: 2,   # l_eye         -> eye
    5: 2,   # r_eye         -> eye
    6: 2,   # l_brow        -> eye
    7: 2,   # r_brow        -> eye
    8: 0,   # l_ear         -> bg
    9: 0,   # r_ear         -> bg
    10: 3,  # mouth         -> mouth
    11: 3,  # u_lip         -> mouth
    12: 3,  # l_lip         -> mouth
    13: 0,  # hair          -> bg
    14: 0,  # hat           -> bg
    15: 0,  # ear_r (귀걸이) -> bg
    16: 0,  # neck_l (목걸이)-> bg
    17: 0,  # neck          -> bg
    18: 0,  # cloth         -> bg
}


def remap(label_19: np.ndarray) -> np.ndarray:
    """CelebAMask-HQ 19 클래스 라벨맵 → 우리 6 클래스 라벨맵.

    Args:
        label_19: (H, W) uint8 ndarray, 값 0~18.

    Returns:
        (H, W) uint8 ndarray, 값 0~5.
    """
    if not isinstance(label_19, np.ndarray):
        raise TypeError(f"numpy array가 필요합니다. got {type(label_19)}")
    if label_19.ndim != 2:
        raise ValueError(f"2D 마스크가 필요합니다. got shape={label_19.shape}")

    result = np.zeros_like(label_19, dtype=np.uint8)
    for src, dst in MAPPING.items():
        result[label_19 == src] = dst
    return result
