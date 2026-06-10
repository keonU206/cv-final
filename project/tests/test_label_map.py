"""label_map 19→6 매핑 단위 테스트."""
import numpy as np
import pytest

from project.segmentation.label_map import (
    MAPPING,
    OURS,
    ORIGINAL_LABELS,
    remap,
)


def test_mapping_covers_all_19_classes():
    """원본 19개 클래스 모두 매핑되어야 함."""
    assert set(MAPPING.keys()) == set(range(19))


def test_mapping_destinations_in_our_classes():
    """모든 매핑 대상이 우리 6 클래스 범위 안에 있어야 함."""
    for dst in MAPPING.values():
        assert 0 <= dst < len(OURS)


def test_remap_basic():
    """간단한 입력으로 매핑 결과 확인."""
    label_19 = np.array([
        [0, 1, 2, 4],     # bg, skin, nose, l_eye
        [10, 13, 14, 17],  # mouth, hair, hat, neck
    ], dtype=np.uint8)
    expected = np.array([
        [0, 4, 1, 2],     # bg, skin, nose, eye
        [3, 0, 0, 0],     # mouth, bg, bg, bg
    ], dtype=np.uint8)
    result = remap(label_19)
    np.testing.assert_array_equal(result, expected)


def test_remap_preserves_shape_and_dtype():
    label_19 = np.random.randint(0, 19, size=(64, 64), dtype=np.uint8)
    result = remap(label_19)
    assert result.shape == label_19.shape
    assert result.dtype == np.uint8
    assert result.max() <= 5
    assert result.min() >= 0


def test_remap_eyebrows_to_eye():
    """l_brow, r_brow는 eye 클래스로 매핑됨."""
    assert MAPPING[ORIGINAL_LABELS["l_brow"]] == OURS["eye"]
    assert MAPPING[ORIGINAL_LABELS["r_brow"]] == OURS["eye"]


def test_remap_lips_to_mouth():
    """u_lip, l_lip은 mouth 클래스로 매핑됨."""
    assert MAPPING[ORIGINAL_LABELS["u_lip"]] == OURS["mouth"]
    assert MAPPING[ORIGINAL_LABELS["l_lip"]] == OURS["mouth"]


def test_remap_rejects_3d_input():
    with pytest.raises(ValueError):
        remap(np.zeros((4, 4, 3), dtype=np.uint8))


def test_remap_rejects_non_numpy():
    with pytest.raises(TypeError):
        remap([[0, 1], [2, 3]])
