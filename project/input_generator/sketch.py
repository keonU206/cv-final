"""시술별 자동 스케치 생성 — SC-FEGAN 입력의 가이드 라인.

원본 랜드마크를 "이상적 위치"로 이동시킨 후 그 점들을 잇는 라인을 그려
SC-FEGAN에 "이런 모양으로 변형해라" 가이드 제공.

intensity 슬라이더 (0.0~1.0)로 변형 강도 조절 가능.

주요 시술:
- nose_tip:    코끝을 위로 올림 + 콧방울 좁힘
- double_eyelid: 윗눈꺼풀 line 위로 올림 (쌍커풀 라인)
- v_line:       턱각을 안쪽으로 (V라인)
"""
from __future__ import annotations

from typing import Any

import cv2
import numpy as np


def _bezier_curve(p0, p1, p2, n_points: int = 30) -> np.ndarray:
    """2차 베지어 곡선 — 자연스러운 곡선 라인 생성.

    Args:
        p0, p1, p2: (x, y) 시작/제어/끝점.
        n_points: 곡선 분해 점 수.

    Returns:
        (n_points, 2) int32 배열.
    """
    t = np.linspace(0, 1, n_points)[:, None]
    p0, p1, p2 = np.asarray(p0), np.asarray(p1), np.asarray(p2)
    curve = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
    return curve.astype(np.int32)


def _draw_curve_polyline(
    sketch: np.ndarray, points: np.ndarray, thickness: int = 1
) -> None:
    """점 리스트를 polyline으로 sketch에 그림 (in-place)."""
    cv2.polylines(sketch, [points.reshape(-1, 1, 2)],
                  isClosed=False, color=255, thickness=thickness)


def generate_nose_tip_sketch(
    landmarks: np.ndarray, intensity: float = 0.5, size: int = 512
) -> np.ndarray:
    """코끝 성형 — 코끝을 위로 + 콧방울 좁힘.

    Args:
        landmarks: (478, 2) int32.
        intensity: 0.0 (변형 없음) ~ 1.0 (최대).
        size: 출력 H, W.

    Returns:
        (size, size) uint8 binary sketch.
    """
    sketch = np.zeros((size, size), dtype=np.uint8)

    # 핵심 랜드마크
    tip = landmarks[1].astype(np.float32)        # 코끝
    bridge = landmarks[6].astype(np.float32)     # 콧대 중앙
    left_nostril = landmarks[98].astype(np.float32)
    right_nostril = landmarks[327].astype(np.float32)
    nose_top = landmarks[168].astype(np.float32)  # 미간

    # 변형 (intensity 비례)
    lift = intensity * 8  # 코끝을 최대 8 픽셀 위로
    narrow = intensity * 4  # 콧방울을 최대 4 픽셀 안쪽으로

    tip_new = np.array([tip[0], tip[1] - lift])
    left_nostril_new = np.array([left_nostril[0] + narrow, left_nostril[1]])
    right_nostril_new = np.array([right_nostril[0] - narrow, right_nostril[1]])

    # 콧대 라인 (미간 → 코끝)
    curve_bridge = _bezier_curve(nose_top, bridge, tip_new, n_points=20)
    _draw_curve_polyline(sketch, curve_bridge, thickness=1)

    # 코끝 둥근 라인 (왼콧방울 → 코끝 → 오른콧방울)
    curve_tip_left = _bezier_curve(left_nostril_new, tip_new, tip_new, n_points=15)
    curve_tip_right = _bezier_curve(tip_new, tip_new, right_nostril_new, n_points=15)
    _draw_curve_polyline(sketch, curve_tip_left, thickness=1)
    _draw_curve_polyline(sketch, curve_tip_right, thickness=1)

    return sketch


def generate_double_eyelid_sketch(
    landmarks: np.ndarray, intensity: float = 0.5, size: int = 512
) -> np.ndarray:
    """쌍커풀 — 윗눈꺼풀 위로 라인 추가.

    Args:
        landmarks: (478, 2) int32.
        intensity: 0.0 ~ 1.0.

    Returns:
        (size, size) uint8 binary sketch.
    """
    sketch = np.zeros((size, size), dtype=np.uint8)

    # 좌우 눈 윗꺼풀 인덱스 (MediaPipe Face Mesh)
    # 왼쪽 윗꺼풀: 246, 161, 160, 159, 158, 157, 173 (외→내)
    # 오른쪽 윗꺼풀: 466, 388, 387, 386, 385, 384, 398 (내→외)
    left_lid = [246, 161, 160, 159, 158, 157, 173]
    right_lid = [398, 384, 385, 386, 387, 388, 466]

    lift = intensity * 3  # 쌍커풀 라인을 최대 3 픽셀 위로

    for indices in (left_lid, right_lid):
        # 원 랜드마크 위에서 약간 위로 이동시킨 점들
        pts = landmarks[indices].astype(np.float32).copy()
        pts[:, 1] -= lift
        pts_int = pts.astype(np.int32)

        # polyline으로 연결 (자연스러운 곡선이지만 베지어 대신 직접 polyline)
        _draw_curve_polyline(sketch, pts_int, thickness=1)

    return sketch


def generate_v_line_sketch(
    landmarks: np.ndarray, intensity: float = 0.5, size: int = 512
) -> np.ndarray:
    """V라인 — 턱각을 안쪽으로 모음.

    Args:
        landmarks: (478, 2) int32.
        intensity: 0.0 ~ 1.0.

    Returns:
        (size, size) uint8 binary sketch.
    """
    sketch = np.zeros((size, size), dtype=np.uint8)

    # 턱 라인 핵심 점 (왼 턱각 → 턱끝 → 오른 턱각)
    left_jaw = landmarks[172].astype(np.float32)
    chin = landmarks[152].astype(np.float32)
    right_jaw = landmarks[397].astype(np.float32)

    # 턱끝 좌표 기준으로 양 턱각을 안쪽으로 이동
    narrow = intensity * 10  # 최대 10 픽셀 안쪽으로

    direction_left = chin[0] - left_jaw[0]  # 양수: 턱끝이 왼턱보다 오른쪽
    direction_right = right_jaw[0] - chin[0]

    left_jaw_new = np.array([
        left_jaw[0] + narrow * np.sign(direction_left), left_jaw[1]
    ])
    right_jaw_new = np.array([
        right_jaw[0] - narrow * np.sign(direction_right), right_jaw[1]
    ])

    # 베지어 곡선 — 왼턱 → 턱끝 (제어점) → 오른턱
    curve = _bezier_curve(left_jaw_new, chin, right_jaw_new, n_points=40)
    _draw_curve_polyline(sketch, curve, thickness=1)

    return sketch


# 시술 이름 → 스케치 함수 매핑
SKETCH_GENERATORS = {
    "nose_tip": generate_nose_tip_sketch,
    "double_eyelid": generate_double_eyelid_sketch,
    "v_line": generate_v_line_sketch,
    # 추가 시술은 함수 정의 후 여기 등록
}


def generate_sketch(
    landmarks: np.ndarray,
    procedure_id: str,
    intensity: float = 0.5,
    size: int = 512,
) -> np.ndarray:
    """시술 ID로 자동 스케치 생성.

    Args:
        landmarks: (478, 2) int32.
        procedure_id: 'nose_tip' / 'double_eyelid' / 'v_line' 등.
        intensity: 0.0 ~ 1.0.
        size: 출력 H, W.

    Returns:
        (size, size) uint8 binary sketch.

    Raises:
        ValueError: 알 수 없는 procedure_id.
    """
    if procedure_id not in SKETCH_GENERATORS:
        raise ValueError(
            f"unknown procedure_id={procedure_id!r}. "
            f"supported: {list(SKETCH_GENERATORS.keys())}"
        )
    fn = SKETCH_GENERATORS[procedure_id]
    return fn(landmarks, intensity=intensity, size=size)
