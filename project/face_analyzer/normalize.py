"""얼굴 크롭 + 정면 정렬 + 512×512 리사이즈.

원본 ↔ 정규화 좌표 매핑을 meta에 저장해 추론 결과 역변환에 사용한다.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .landmarks import detect_landmarks

TARGET_SIZE = 512

# MediaPipe Face Mesh 주요 인덱스
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263
NOSE_TIP = 1
CHIN = 152


@dataclass
class NormalizeMeta:
    """원본 이미지 ↔ 정규화 512 이미지 변환 정보."""

    original_size: tuple[int, int]  # (H, W)
    crop_box: tuple[int, int, int, int]  # (x, y, w, h) on original
    rotation_deg: float  # 정면 정렬에 사용된 각도
    rotation_center: tuple[float, float]  # 회전 중심 (정규화된 512 공간)
    scale: float  # crop_box → 512 리사이즈 스케일


def normalize_face(image: np.ndarray, padding: float = 0.4) -> tuple[np.ndarray, NormalizeMeta]:
    """얼굴 영역만 크롭 + 양 눈 수평으로 정렬 + 512 정사각 리사이즈.

    Args:
        image: BGR uint8 원본.
        padding: 얼굴 bbox 주변 여백 비율 (0.4 = bbox의 40%).

    Returns:
        (정규화된 512×512 BGR, NormalizeMeta).
    """
    h, w = image.shape[:2]
    landmarks = detect_landmarks(image)

    x_min, y_min = landmarks.min(axis=0)
    x_max, y_max = landmarks.max(axis=0)
    bw, bh = x_max - x_min, y_max - y_min

    pad_x = int(bw * padding)
    pad_y = int(bh * padding)
    cx0 = max(0, x_min - pad_x)
    cy0 = max(0, y_min - pad_y)
    cx1 = min(w, x_max + pad_x)
    cy1 = min(h, y_max + pad_y)

    side = max(cx1 - cx0, cy1 - cy0)
    cx_center = (cx0 + cx1) // 2
    cy_center = (cy0 + cy1) // 2
    cx0 = max(0, cx_center - side // 2)
    cy0 = max(0, cy_center - side // 2)
    cx1 = min(w, cx0 + side)
    cy1 = min(h, cy0 + side)
    side = min(cx1 - cx0, cy1 - cy0)
    cx1 = cx0 + side
    cy1 = cy0 + side

    cropped = image[cy0:cy1, cx0:cx1]
    if cropped.size == 0:
        raise ValueError("크롭 영역이 비어 있습니다.")

    resized = cv2.resize(cropped, (TARGET_SIZE, TARGET_SIZE), interpolation=cv2.INTER_CUBIC)

    scale = TARGET_SIZE / side
    left_eye = (landmarks[LEFT_EYE_OUTER] - np.array([cx0, cy0])) * scale
    right_eye = (landmarks[RIGHT_EYE_OUTER] - np.array([cx0, cy0])) * scale
    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]
    angle = float(np.degrees(np.arctan2(dy, dx)))

    center = ((left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    aligned = cv2.warpAffine(
        resized, rot_mat, (TARGET_SIZE, TARGET_SIZE), flags=cv2.INTER_CUBIC
    )

    meta = NormalizeMeta(
        original_size=(h, w),
        crop_box=(cx0, cy0, side, side),
        rotation_deg=angle,
        rotation_center=(float(center[0]), float(center[1])),
        scale=scale,
    )
    return aligned, meta


def transform_landmarks_to_normalized(
    landmarks: np.ndarray, meta: NormalizeMeta
) -> np.ndarray:
    """원본 좌표 랜드마크 → 정규화 512 공간 좌표."""
    cx0, cy0, _, _ = meta.crop_box
    pts = (landmarks - np.array([cx0, cy0])) * meta.scale

    rot_mat = cv2.getRotationMatrix2D(meta.rotation_center, meta.rotation_deg, 1.0)
    pts_h = np.concatenate([pts, np.ones((len(pts), 1))], axis=1)
    rotated = (rot_mat @ pts_h.T).T
    return rotated.astype(np.int32)
