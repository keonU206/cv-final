"""input_generator.color 단위 테스트.

합성 image + 랜드마크로 색상 가이드 생성 동작 검증.
"""
import numpy as np
import pytest

from project.input_generator.color import (
    DEFAULT_V_OFFSET,
    _adjust_hsv_v,
    _sample_skin_tone,
    make_color,
    make_color_simple,
)


def _synthetic_landmarks(n: int = 478) -> np.ndarray:
    rng = np.random.default_rng(seed=11)
    pts = rng.integers(low=180, high=340, size=(n, 2), dtype=np.int32)
    return pts


def _fake_image(size: int = 512, rgb=(220, 195, 175)) -> np.ndarray:
    return np.full((size, size, 3), rgb, dtype=np.uint8)


def _nose_proc() -> dict:
    return {
        "id": "nose_tip",
        "region": "nose",
        "mask_landmarks": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "dilate_px": 15,
    }


def test_make_color_shape_dtype():
    lm = _synthetic_landmarks()
    img = _fake_image()
    out = make_color(img, lm, _nose_proc(), size=512)
    assert out.shape == (512, 512, 3)
    assert out.dtype == np.uint8


def test_make_color_outside_mask_is_zero():
    """mask 영역 밖은 0이어야 함 (soft mask 적용 후)."""
    lm = _synthetic_landmarks()
    img = _fake_image()
    out = make_color(img, lm, _nose_proc(), size=512)
    # 코너는 mask 밖
    assert out[0, 0].sum() == 0
    assert out[-1, -1].sum() == 0


def test_make_color_simple_works_without_image():
    lm = _synthetic_landmarks()
    out = make_color_simple(lm, _nose_proc(), size=512)
    assert out.shape == (512, 512, 3)
    assert out.dtype == np.uint8


def test_make_color_image_size_mismatch_raises():
    lm = _synthetic_landmarks()
    bad_img = _fake_image(size=256)  # 512 기대인데 256
    with pytest.raises(ValueError):
        make_color(bad_img, lm, _nose_proc(), size=512)


def test_region_v_offset_changes_brightness():
    """region별 V offset이 다르면 출력 색상 평균 밝기도 달라야 함."""
    lm = _synthetic_landmarks()
    img = _fake_image()

    results = {}
    for region in ("nose", "eye", "jaw"):
        proc = {**_nose_proc(), "region": region}
        out = make_color(img, lm, proc, size=512)
        nonzero = out[out.sum(axis=2) > 0]
        if len(nonzero) > 0:
            results[region] = nonzero.mean()

    # nose(V+12) > jaw(V+0) > eye(V-18)
    assert results["nose"] > results["jaw"] > results["eye"]


def test_adjust_hsv_v_brighten():
    rgb = np.array([100, 100, 100], dtype=np.uint8)
    bright = _adjust_hsv_v(rgb, 50)
    assert bright.mean() > rgb.mean()


def test_adjust_hsv_v_zero_returns_same():
    rgb = np.array([123, 200, 99], dtype=np.uint8)
    same = _adjust_hsv_v(rgb, 0)
    np.testing.assert_array_equal(rgb, same)


def test_sample_skin_tone_fallback_on_empty_ring():
    """mask가 이미지 전체일 때 ring이 비어있어도 fallback 색 반환."""
    img = _fake_image()
    full_mask = np.full((512, 512), 255, dtype=np.uint8)
    tone = _sample_skin_tone(img, full_mask)
    assert tone.shape == (3,)
    assert tone.dtype == np.uint8


def test_default_v_offset_keys():
    assert {"nose", "eye", "jaw", "mouth"}.issubset(DEFAULT_V_OFFSET.keys())
