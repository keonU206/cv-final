"""시술별 자동 마스크 생성.

랜드마크 인덱스 집합 → convex hull → dilate → 512×512 binary mask.
"""
from __future__ import annotations

from typing import Any

import cv2
import numpy as np


def make_mask(
    landmarks: np.ndarray,
    procedure: dict[str, Any],
    size: int = 512,
) -> np.ndarray:
    """시술 정의에 따라 512×512 binary mask 생성.

    Args:
        landmarks: (478, 2) int32, 정규화 공간 좌표.
        procedure: procedures.yaml의 한 항목.
        size: 출력 크기 (기본 512).

    Returns:
        (size, size, 1) uint8. 255 = 편집 영역, 0 = 보존.
    """
    indices = procedure["mask_landmarks"]
    dilate_px = int(procedure.get("dilate_px", 15))

    pts = landmarks[indices].astype(np.int32)
    if len(pts) < 3:
        raise ValueError(f"mask_landmarks가 최소 3개 필요. got {len(pts)}")

    mask = np.zeros((size, size), dtype=np.uint8)

    # 눈처럼 좌/우로 분리된 영역은 단일 convex hull로 묶으면 영역이 너무 커진다.
    # K-means 비스무리하게 x좌표 중앙값 기준으로 좌/우 분리해서 각각 hull 처리.
    x_med = np.median(pts[:, 0])
    spread_x = pts[:, 0].max() - pts[:, 0].min()
    spread_y = pts[:, 1].max() - pts[:, 1].min()

    if spread_x > spread_y * 2 and procedure.get("region") == "eye":
        left = pts[pts[:, 0] < x_med]
        right = pts[pts[:, 0] >= x_med]
        for group in (left, right):
            if len(group) >= 3:
                hull = cv2.convexHull(group)
                cv2.fillPoly(mask, [hull], 255)
    else:
        hull = cv2.convexHull(pts)
        cv2.fillPoly(mask, [hull], 255)

    if dilate_px > 0:
        kernel = np.ones((dilate_px, dilate_px), np.uint8)
        mask = cv2.dilate(mask, kernel)

    return mask[..., None]
