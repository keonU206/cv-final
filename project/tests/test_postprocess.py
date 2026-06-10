"""postprocess.split_skin_by_landmarks 단위 테스트.

heavy dependency 없이 동작 (numpy만 사용).
"""
import numpy as np
import pytest

from project.segmentation.postprocess import (
    IDX_BROW_INNER_LEFT,
    IDX_BROW_INNER_RIGHT,
    IDX_LIP_BOTTOM,
    get_procedure_masks,
    split_skin_by_landmarks,
)


def _synthetic_landmarks(brow_y: int = 200, lip_y: int = 340) -> np.ndarray:
    """랜드마크 478점 합성. 핵심 인덱스만 의미있는 값."""
    lm = np.zeros((478, 2), dtype=np.int32)
    lm[IDX_BROW_INNER_LEFT] = (215, brow_y)
    lm[IDX_BROW_INNER_RIGHT] = (297, brow_y)
    lm[IDX_LIP_BOTTOM] = (256, lip_y)
    return lm


def test_split_returns_two_masks():
    skin = np.ones((512, 512), dtype=np.uint8) * 255
    lm = _synthetic_landmarks()
    jaw, fh = split_skin_by_landmarks(skin, lm)
    assert jaw.shape == (512, 512)
    assert fh.shape == (512, 512)


def test_jaw_below_lip():
    """jaw 마스크는 lip_bottom_y 이하에만 존재해야 함."""
    skin = np.ones((512, 512), dtype=np.uint8) * 255
    lm = _synthetic_landmarks(brow_y=200, lip_y=340)
    jaw, _ = split_skin_by_landmarks(skin, lm, margin=5)

    # lip_y + margin = 345 이상에만 픽셀 존재
    assert (jaw[:345, :] == 0).all()
    assert (jaw[345:, :] > 0).any()


def test_forehead_above_brow():
    """forehead 마스크는 brow_y 이상에만 존재해야 함."""
    skin = np.ones((512, 512), dtype=np.uint8) * 255
    lm = _synthetic_landmarks(brow_y=200, lip_y=340)
    _, fh = split_skin_by_landmarks(skin, lm, margin=5)

    # brow_y - margin = 195 이하에만 픽셀 존재
    assert (fh[:195, :] > 0).any()
    assert (fh[195:, :] == 0).all()


def test_jaw_and_forehead_disjoint():
    """jaw와 forehead 영역이 겹치지 않아야 함."""
    skin = np.ones((512, 512), dtype=np.uint8) * 255
    lm = _synthetic_landmarks(brow_y=200, lip_y=340)
    jaw, fh = split_skin_by_landmarks(skin, lm)

    overlap = (jaw > 0) & (fh > 0)
    assert overlap.sum() == 0


def test_split_rejects_wrong_landmarks_shape():
    skin = np.ones((512, 512), dtype=np.uint8) * 255
    with pytest.raises(ValueError):
        split_skin_by_landmarks(skin, np.zeros((68, 2), dtype=np.int32))


def test_split_rejects_3d_skin():
    lm = _synthetic_landmarks()
    with pytest.raises(ValueError):
        split_skin_by_landmarks(
            np.ones((512, 512, 3), dtype=np.uint8), lm
        )


def test_get_procedure_masks_keys():
    """get_procedure_masks가 7개 키 모두 반환해야 함."""
    pred = np.zeros((512, 512), dtype=np.uint8)
    # 임의 영역에 각 클래스 설정
    pred[0:50, 0:50] = 1     # nose
    pred[100:150, :] = 2     # eye
    pred[300:320, :] = 3     # mouth
    pred[400:450, :] = 4     # skin

    lm = _synthetic_landmarks()
    masks = get_procedure_masks(pred, lm)

    expected = {"background", "nose", "eye", "mouth", "skin", "jaw", "forehead"}
    assert set(masks.keys()) == expected
    for v in masks.values():
        assert v.shape == (512, 512)
        assert v.dtype == np.uint8
