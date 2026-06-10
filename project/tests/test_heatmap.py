"""heatmap.landmark_heatmap 단위 테스트.

heavy deps 없음 (numpy만 사용).
"""
import numpy as np
import pytest

from project.segmentation.heatmap import (
    FACE_PART_GROUPS,
    landmark_heatmap,
    landmark_heatmap_multichannel,
)


def _synthetic_landmarks(n: int = 478, size: int = 256) -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.integers(0, size, size=(n, 2), dtype=np.int32)


def test_returns_correct_shape():
    lm = _synthetic_landmarks()
    hm = landmark_heatmap(lm, size=256)
    assert hm.shape == (256, 256)
    assert hm.dtype == np.float32


def test_values_in_range():
    lm = _synthetic_landmarks()
    hm = landmark_heatmap(lm, size=256)
    assert hm.min() >= 0.0
    assert hm.max() <= 1.0


def test_max_at_landmark_position():
    """각 랜드마크 위치의 픽셀 값은 1.0 (Gaussian 정점)."""
    lm = np.array([[100, 100], [200, 50]], dtype=np.int32)
    hm = landmark_heatmap(lm, size=256, sigma=3.0)
    assert hm[100, 100] == pytest.approx(1.0, abs=1e-5)
    assert hm[50, 200] == pytest.approx(1.0, abs=1e-5)


def test_decay_away_from_landmark():
    """랜드마크에서 멀어질수록 값 감소."""
    lm = np.array([[128, 128]], dtype=np.int32)
    hm = landmark_heatmap(lm, size=256, sigma=3.0)
    # 중심값 > 5픽셀 떨어진 값 > 10픽셀 떨어진 값
    assert hm[128, 128] > hm[128, 133]
    assert hm[128, 133] > hm[128, 138]


def test_out_of_bounds_landmarks_ignored():
    """범위 밖 랜드마크는 무시 (에러 없이)."""
    lm = np.array([[100, 100], [1000, 1000], [-5, -5]], dtype=np.int32)
    hm = landmark_heatmap(lm, size=256)
    # 첫 랜드마크는 정상 처리
    assert hm[100, 100] == pytest.approx(1.0, abs=1e-5)


def test_indices_subset():
    """indices로 일부 랜드마크만 사용."""
    lm = np.array([[50, 50], [100, 100], [150, 150]], dtype=np.int32)
    hm_all = landmark_heatmap(lm, size=256, sigma=3.0)
    hm_subset = landmark_heatmap(lm, size=256, sigma=3.0, indices=[0, 2])
    # 인덱스 1 (100, 100) 위치는 subset에서 약함
    assert hm_subset[100, 100] < hm_all[100, 100] - 0.1


def test_multichannel():
    lm = _synthetic_landmarks()
    hm_mc = landmark_heatmap_multichannel(
        lm, groups=FACE_PART_GROUPS, size=256, sigma=3.0
    )
    assert hm_mc.shape == (len(FACE_PART_GROUPS), 256, 256)
    assert hm_mc.dtype == np.float32


def test_rejects_wrong_shape():
    with pytest.raises(ValueError):
        landmark_heatmap(np.zeros(10), size=256)
    with pytest.raises(ValueError):
        landmark_heatmap(np.zeros((10, 3)), size=256)


def test_rejects_invalid_size():
    lm = _synthetic_landmarks()
    with pytest.raises(ValueError):
        landmark_heatmap(lm, size=0)
    with pytest.raises(ValueError):
        landmark_heatmap(lm, size=-10)


def test_rejects_invalid_sigma():
    lm = _synthetic_landmarks()
    with pytest.raises(ValueError):
        landmark_heatmap(lm, sigma=0)
    with pytest.raises(ValueError):
        landmark_heatmap(lm, sigma=-1.0)


def test_smaller_sigma_tighter_peak():
    """작은 sigma → 더 좁은 peak."""
    lm = np.array([[128, 128]], dtype=np.int32)
    hm_tight = landmark_heatmap(lm, size=256, sigma=1.0)
    hm_wide = landmark_heatmap(lm, size=256, sigma=5.0)
    # 멀리 떨어진 픽셀: wide가 더 큰 값
    assert hm_wide[128, 140] > hm_tight[128, 140]
