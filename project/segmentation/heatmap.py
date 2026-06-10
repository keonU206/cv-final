"""MediaPipe 478 landmark → Gaussian heatmap.

각 랜드마크 위치에 Gaussian (σ=3) 점을 찍고 max로 합성.
U-Net의 4번째 입력 채널로 사용 — 모델에 도메인 지식(부위 위치) 주입.

핵심 함수:
    landmark_heatmap(landmarks, size, sigma) → (size, size) float32 [0, 1]
"""
from __future__ import annotations

from typing import Optional

import numpy as np


def landmark_heatmap(
    landmarks: np.ndarray,
    size: int = 256,
    sigma: float = 3.0,
    indices: Optional[list[int]] = None,
) -> np.ndarray:
    """랜드마크 좌표 → Gaussian heatmap.

    Args:
        landmarks: (N, 2) int32 또는 float, 픽셀 좌표 (x, y).
                   N=478 (MediaPipe Face Mesh)이 일반적.
        size: 출력 H, W (정사각형).
        sigma: Gaussian 반경 (픽셀 단위).
        indices: 사용할 랜드마크 인덱스 부분집합. None이면 전체 사용.

    Returns:
        (size, size) float32 in [0, 1]. 각 위치의 max Gaussian 값.
    """
    if landmarks.ndim != 2 or landmarks.shape[1] != 2:
        raise ValueError(f"landmarks must be (N, 2). got {landmarks.shape}")
    if size <= 0:
        raise ValueError(f"size must be positive. got {size}")
    if sigma <= 0:
        raise ValueError(f"sigma must be positive. got {sigma}")

    if indices is not None:
        landmarks = landmarks[indices]

    H = W = size
    # Grid for Gaussian computation
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    heatmap = np.zeros((H, W), dtype=np.float32)
    two_sigma_sq = 2.0 * sigma * sigma

    for x, y in landmarks:
        # Skip out-of-bounds
        if not (0 <= x < W and 0 <= y < H):
            continue
        # Bounding box of Gaussian (3σ radius) — efficient
        x_min = max(0, int(x - 3 * sigma))
        x_max = min(W, int(x + 3 * sigma) + 1)
        y_min = max(0, int(y - 3 * sigma))
        y_max = min(H, int(y + 3 * sigma) + 1)

        # Gaussian within bbox
        dx = xx[y_min:y_max, x_min:x_max] - x
        dy = yy[y_min:y_max, x_min:x_max] - y
        g = np.exp(-(dx * dx + dy * dy) / two_sigma_sq)

        # Merge with max
        np.maximum(
            heatmap[y_min:y_max, x_min:x_max],
            g,
            out=heatmap[y_min:y_max, x_min:x_max],
        )

    return heatmap


def landmark_heatmap_multichannel(
    landmarks: np.ndarray,
    groups: dict[str, list[int]],
    size: int = 256,
    sigma: float = 3.0,
) -> np.ndarray:
    """랜드마크를 부위별 그룹으로 묶어 다채널 heatmap 생성.

    Args:
        landmarks: (478, 2)
        groups: 부위별 인덱스 dict. 예: {'nose': [1, 2, 98], 'eye': [33, 263, ...]}
        size: H, W
        sigma: Gaussian 반경

    Returns:
        (len(groups), size, size) float32. 각 채널 = 한 부위 heatmap.
    """
    channels = []
    for name in sorted(groups.keys()):  # 안정적 순서
        ch = landmark_heatmap(landmarks, size=size, sigma=sigma, indices=groups[name])
        channels.append(ch)
    return np.stack(channels, axis=0)  # (C, H, W)


# 부위별 표준 그룹 (face_analyzer/ratios.py 와 동기화)
FACE_PART_GROUPS = {
    "nose": [1, 2, 4, 5, 19, 94, 98, 168, 197, 327],
    "eye": [33, 133, 263, 362, 159, 145, 386, 374],
    "brow": [55, 285, 70, 300, 105, 334],
    "mouth": [13, 14, 61, 291, 78, 308, 178, 402],
    "jaw": [152, 172, 397, 136, 365],
    "forehead": [10, 67, 297, 109, 338],
}
