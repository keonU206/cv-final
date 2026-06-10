"""input_generator.mask 단위 테스트.

합성 랜드마크로 마스크 생성 동작 검증.
"""
import numpy as np
import pytest

from project.input_generator.mask import make_mask


def _synthetic_landmarks(n: int = 478) -> np.ndarray:
    """더미 478점 랜드마크 — 모두 (256, 256) 중심으로 작은 영역."""
    rng = np.random.default_rng(seed=42)
    pts = rng.integers(low=200, high=320, size=(n, 2), dtype=np.int32)
    return pts


def test_make_mask_shape_and_dtype():
    lm = _synthetic_landmarks()
    proc = {
        "id": "test",
        "region": "nose",
        "mask_landmarks": [0, 1, 2, 3, 4],
        "dilate_px": 10,
    }
    mask = make_mask(lm, proc, size=512)
    assert mask.shape == (512, 512, 1)
    assert mask.dtype == np.uint8
    assert mask.max() == 255
    assert mask.min() == 0


def test_make_mask_dilate_increases_area():
    lm = _synthetic_landmarks()
    base = {"id": "t", "region": "nose", "mask_landmarks": [0, 1, 2, 3, 4]}
    small = make_mask(lm, {**base, "dilate_px": 0})
    big = make_mask(lm, {**base, "dilate_px": 20})
    assert (big > 0).sum() > (small > 0).sum()


def test_make_mask_eye_region_creates_two_blobs():
    """region=eye 인 경우 좌/우로 분리된 hull 2개를 생성해야 한다."""
    left = np.array([[100, 250], [110, 240], [120, 250], [110, 260]] * 3, dtype=np.int32)
    right = np.array([[400, 250], [410, 240], [420, 250], [410, 260]] * 3, dtype=np.int32)
    lm = np.zeros((478, 2), dtype=np.int32)
    lm[:12] = left
    lm[12:24] = right
    proc = {
        "id": "double_eyelid",
        "region": "eye",
        "mask_landmarks": list(range(24)),
        "dilate_px": 5,
    }
    mask = make_mask(lm, proc)

    # 좌/우 영역 모두 마스크 픽셀 존재
    left_half = mask[:, :256, 0]
    right_half = mask[:, 256:, 0]
    assert (left_half > 0).sum() > 0
    assert (right_half > 0).sum() > 0


def test_make_mask_raises_on_too_few_points():
    lm = _synthetic_landmarks()
    proc = {"id": "x", "region": "nose", "mask_landmarks": [0, 1]}
    with pytest.raises(ValueError):
        make_mask(lm, proc)
