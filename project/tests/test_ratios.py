"""face_analyzer.ratios 단위 테스트.

합성 랜드마크로 비율 계산 동작 검증 (mediapipe 미설치 환경에서도 동작).
"""
import math

import numpy as np
import pytest

from project.face_analyzer.ratios import IDX, compute_ratios


def _build_synthetic_face() -> np.ndarray:
    """대략 정면 정상 얼굴의 랜드마크 478개 합성."""
    lm = np.zeros((478, 2), dtype=np.int32)

    # 세로 기준선 (forehead 50 → chin 450)
    lm[IDX["forehead_top"]] = (256, 50)
    lm[IDX["glabella"]] = (256, 150)
    lm[IDX["nose_top"]] = (256, 160)
    lm[IDX["nose_tip"]] = (256, 280)
    lm[IDX["philtrum_top"]] = (256, 300)
    lm[IDX["lip_top_center"]] = (256, 340)
    lm[IDX["lip_bottom_center"]] = (256, 365)
    lm[IDX["chin"]] = (256, 450)

    # 좌우 눈
    lm[IDX["left_eye_outer"]] = (170, 200)
    lm[IDX["left_eye_inner"]] = (220, 200)
    lm[IDX["right_eye_inner"]] = (292, 200)
    lm[IDX["right_eye_outer"]] = (342, 200)
    lm[IDX["left_eyelid_top"]] = (195, 192)
    lm[IDX["left_eyelid_bottom"]] = (195, 208)
    lm[IDX["right_eyelid_top"]] = (317, 192)
    lm[IDX["right_eyelid_bottom"]] = (317, 208)

    lm[IDX["left_brow_inner"]] = (215, 170)
    lm[IDX["right_brow_inner"]] = (297, 170)

    # 얼굴 너비
    lm[IDX["left_cheek"]] = (120, 250)
    lm[IDX["right_cheek"]] = (392, 250)

    # 턱각
    lm[IDX["left_jaw_corner"]] = (160, 380)
    lm[IDX["right_jaw_corner"]] = (352, 380)

    # 콧방울
    lm[IDX["left_nostril"]] = (240, 275)
    lm[IDX["right_nostril"]] = (272, 275)

    return lm


def test_compute_ratios_returns_all_expected_keys():
    lm = _build_synthetic_face()
    ratios = compute_ratios(lm)
    expected = {
        "face_h_w_ratio",
        "forehead_ratio",
        "midface_ratio",
        "lowerface_ratio",
        "eye_width_ratio",
        "eyelid_height_ratio",
        "nose_length_ratio",
        "nose_tip_droop",
        "jaw_angle_deg",
        "e_line_offset",
    }
    assert set(ratios.keys()) == expected


def test_thirds_sum_to_one():
    lm = _build_synthetic_face()
    ratios = compute_ratios(lm)
    total = ratios["forehead_ratio"] + ratios["midface_ratio"] + ratios["lowerface_ratio"]
    assert math.isclose(total, 1.0, abs_tol=1e-6)


def test_face_h_w_ratio_in_reasonable_range():
    lm = _build_synthetic_face()
    ratios = compute_ratios(lm)
    assert 1.0 < ratios["face_h_w_ratio"] < 2.0


def test_jaw_angle_in_degrees():
    lm = _build_synthetic_face()
    ratios = compute_ratios(lm)
    assert 0 < ratios["jaw_angle_deg"] < 180


def test_ratios_are_finite():
    lm = _build_synthetic_face()
    ratios = compute_ratios(lm)
    for k, v in ratios.items():
        assert np.isfinite(v), f"{k} not finite: {v}"
