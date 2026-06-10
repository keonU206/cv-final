"""얼굴 비율 지표 계산.

삼정오안(三停五眼), E라인, 황금비 기반 8개 지표.
모든 지표는 얼굴 크기에 정규화되어 [0, 1] 또는 각도 단위.
"""
from __future__ import annotations

import numpy as np

# MediaPipe Face Mesh 478 인덱스
IDX = {
    "forehead_top": 10,
    "glabella": 168,
    "nose_top": 6,
    "nose_tip": 1,
    "philtrum_top": 164,
    "lip_top_center": 13,
    "lip_bottom_center": 14,
    "chin": 152,
    "left_eye_outer": 33,
    "left_eye_inner": 133,
    "right_eye_outer": 263,
    "right_eye_inner": 362,
    "left_eyelid_top": 159,
    "left_eyelid_bottom": 145,
    "right_eyelid_top": 386,
    "right_eyelid_bottom": 374,
    "left_brow_inner": 55,
    "right_brow_inner": 285,
    "left_cheek": 234,
    "right_cheek": 454,
    "left_jaw_corner": 172,
    "right_jaw_corner": 397,
    "left_nostril": 98,
    "right_nostril": 327,
}


def _dist(p1: np.ndarray, p2: np.ndarray) -> float:
    return float(np.linalg.norm(p1 - p2))


def _angle_deg(vertex: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    """vertex를 꼭짓점으로 a-vertex-b의 사잇각 (degree)."""
    v1 = a - vertex
    v2 = b - vertex
    cos = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))
    cos = max(-1.0, min(1.0, cos))
    return float(np.degrees(np.arccos(cos)))


def _signed_dist_to_line(point: np.ndarray, line_a: np.ndarray, line_b: np.ndarray) -> float:
    """point에서 직선 ab까지의 부호 있는 거리. line 오른쪽이면 양수."""
    ab = line_b - line_a
    ap = point - line_a
    cross = ab[0] * ap[1] - ab[1] * ap[0]
    length = np.linalg.norm(ab) + 1e-9
    return float(cross / length)


def compute_ratios(landmarks: np.ndarray) -> dict[str, float]:
    """얼굴 랜드마크 478점에서 비율 지표 dict 반환.

    Args:
        landmarks: (478, 2) int32, 정규화된 512 공간 좌표 권장.

    Returns:
        지표 dict (모든 값 float).
    """
    p = {k: landmarks[i].astype(np.float64) for k, i in IDX.items()}

    face_h = _dist(p["forehead_top"], p["chin"])
    face_w = _dist(p["left_cheek"], p["right_cheek"])

    forehead_h = _dist(p["forehead_top"], p["glabella"])
    midface_h = _dist(p["glabella"], p["philtrum_top"])
    lowerface_h = _dist(p["philtrum_top"], p["chin"])
    total_thirds = forehead_h + midface_h + lowerface_h + 1e-9

    left_eye_w = _dist(p["left_eye_outer"], p["left_eye_inner"])
    right_eye_w = _dist(p["right_eye_outer"], p["right_eye_inner"])
    avg_eye_w = (left_eye_w + right_eye_w) / 2
    intercanthal = _dist(p["left_eye_inner"], p["right_eye_inner"])

    left_eyelid_h = _dist(p["left_eyelid_top"], p["left_eyelid_bottom"])
    right_eyelid_h = _dist(p["right_eyelid_top"], p["right_eyelid_bottom"])
    avg_eyelid_h = (left_eyelid_h + right_eyelid_h) / 2

    nose_length = _dist(p["nose_top"], p["nose_tip"])

    nostril_y = (p["left_nostril"][1] + p["right_nostril"][1]) / 2
    nose_tip_y = p["nose_tip"][1]
    tip_droop = (nose_tip_y - nostril_y) / (face_h + 1e-9)

    jaw_angle_left = _angle_deg(p["left_jaw_corner"], p["left_cheek"], p["chin"])
    jaw_angle_right = _angle_deg(p["right_jaw_corner"], p["right_cheek"], p["chin"])
    jaw_angle = (jaw_angle_left + jaw_angle_right) / 2

    e_line_offset = _signed_dist_to_line(
        p["lip_top_center"], p["nose_tip"], p["chin"]
    ) / (face_h + 1e-9)

    return {
        "face_h_w_ratio": face_h / (face_w + 1e-9),
        "forehead_ratio": forehead_h / total_thirds,
        "midface_ratio": midface_h / total_thirds,
        "lowerface_ratio": lowerface_h / total_thirds,
        "eye_width_ratio": intercanthal / (avg_eye_w + 1e-9),
        "eyelid_height_ratio": avg_eyelid_h / (avg_eye_w + 1e-9),
        "nose_length_ratio": nose_length / (face_h + 1e-9),
        "nose_tip_droop": tip_droop,
        "jaw_angle_deg": jaw_angle,
        "e_line_offset": e_line_offset,
    }
