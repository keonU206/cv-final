"""input_generator.composer 단위 테스트.

9채널 SC-FEGAN 입력 통합 동작 검증.
"""
import numpy as np
import pytest

from project.input_generator.composer import (
    PROCEDURE_ID_TO_SKETCH,
    _resolve_procedure,
    _sketch_key_for,
    compose_and_pack,
    compose_scfegan_input,
    load_procedures,
    to_scfegan_tensor,
)


def _synthetic_landmarks(n: int = 478) -> np.ndarray:
    rng = np.random.default_rng(seed=13)
    pts = rng.integers(low=180, high=340, size=(n, 2), dtype=np.int32)
    return pts


def _fake_image(size: int = 512) -> np.ndarray:
    return np.full((size, size, 3), [220, 195, 175], dtype=np.uint8)


# ─── load_procedures ───

def test_load_procedures_has_all_three():
    procs = load_procedures()
    assert {"nose_tip", "double_eyelid", "jaw_v_line"}.issubset(procs.keys())


# ─── _resolve_procedure ───

def test_resolve_procedure_string():
    procs = load_procedures()
    resolved = _resolve_procedure("nose_tip", procs)
    assert resolved["id"] == "nose_tip"


def test_resolve_procedure_dict_passthrough():
    proc = {"id": "custom", "region": "nose", "mask_landmarks": [0, 1, 2]}
    resolved = _resolve_procedure(proc, None)
    assert resolved is proc


def test_resolve_procedure_unknown_raises():
    procs = load_procedures()
    with pytest.raises(ValueError):
        _resolve_procedure("ghost_proc_xyz", procs)


# ─── _sketch_key_for (jaw_v_line ↔ v_line 어댑팅) ───

def test_sketch_key_adapting_jaw_v_line():
    proc = {"id": "jaw_v_line"}
    assert _sketch_key_for(proc) == "v_line"


def test_sketch_key_passthrough():
    for pid in ("nose_tip", "double_eyelid"):
        assert _sketch_key_for({"id": pid}) == pid


def test_sketch_key_unknown_raises():
    with pytest.raises(ValueError):
        _sketch_key_for({"id": "ghost"})


# ─── compose_scfegan_input ───

def test_compose_returns_all_keys():
    lm = _synthetic_landmarks()
    img = _fake_image()
    out = compose_scfegan_input(img, lm, "nose_tip")
    assert set(out.keys()) == {
        "incomplete_image", "sketch", "color", "mask", "noise", "procedure",
    }


def test_compose_channel_shapes():
    lm = _synthetic_landmarks()
    img = _fake_image()
    out = compose_scfegan_input(img, lm, "nose_tip", size=512)
    assert out["incomplete_image"].shape == (512, 512, 3)
    assert out["sketch"].shape == (512, 512, 1)
    assert out["color"].shape == (512, 512, 3)
    assert out["mask"].shape == (512, 512, 1)
    assert out["noise"].shape == (512, 512, 1)
    assert out["noise"].dtype == np.float32


def test_compose_incomplete_image_masks_region():
    """incomplete_image는 mask 영역에서 0이어야 함."""
    lm = _synthetic_landmarks()
    img = _fake_image()
    out = compose_scfegan_input(img, lm, "nose_tip")
    mask_bool = out["mask"][..., 0] > 0
    assert out["incomplete_image"][mask_bool].sum() == 0


def test_compose_noise_seed_reproducible():
    lm = _synthetic_landmarks()
    img = _fake_image()
    a = compose_scfegan_input(img, lm, "nose_tip", seed=42)["noise"]
    b = compose_scfegan_input(img, lm, "nose_tip", seed=42)["noise"]
    np.testing.assert_array_equal(a, b)


def test_compose_image_size_mismatch_raises():
    lm = _synthetic_landmarks()
    bad_img = _fake_image(size=256)
    with pytest.raises(ValueError):
        compose_scfegan_input(bad_img, lm, "nose_tip", size=512)


def test_compose_jaw_v_line_uses_v_line_sketch():
    """jaw_v_line procedure가 sketch 어댑팅을 거쳐 정상 작동."""
    lm = _synthetic_landmarks()
    img = _fake_image()
    out = compose_scfegan_input(img, lm, "jaw_v_line")
    assert out["sketch"].shape == (512, 512, 1)


# ─── to_scfegan_tensor ───

def test_to_tensor_normalize_hwc():
    lm = _synthetic_landmarks()
    composed = compose_scfegan_input(_fake_image(), lm, "nose_tip")
    t = to_scfegan_tensor(composed, normalize=True, channels_first=False)
    assert t.shape == (512, 512, 9)
    assert t.dtype == np.float32


def test_to_tensor_pytorch_style():
    lm = _synthetic_landmarks()
    composed = compose_scfegan_input(_fake_image(), lm, "nose_tip")
    t = to_scfegan_tensor(composed, channels_first=True, batch_dim=True)
    assert t.shape == (1, 9, 512, 512)


def test_to_tensor_normalize_range_image_color():
    """incomplete + color 채널은 [-1, 1] 범위에 있어야 (image 0~255 입력)."""
    lm = _synthetic_landmarks()
    composed = compose_scfegan_input(_fake_image(), lm, "nose_tip", noise_sigma=0.0)
    t = to_scfegan_tensor(composed, normalize=True, channels_first=False)
    # incomplete (0~2), color (4~6)
    img_color = t[..., list(range(0, 3)) + list(range(4, 7))]
    assert img_color.min() >= -1.0001
    assert img_color.max() <= 1.0001


def test_to_tensor_mask_sketch_in_0_1():
    """mask, sketch 채널은 [0, 1] 범위."""
    lm = _synthetic_landmarks()
    composed = compose_scfegan_input(_fake_image(), lm, "nose_tip")
    t = to_scfegan_tensor(composed, normalize=True)
    # sketch (3), mask (7)
    assert t[..., 3].min() >= 0.0
    assert t[..., 3].max() <= 1.0
    assert t[..., 7].min() >= 0.0
    assert t[..., 7].max() <= 1.0


# ─── compose_and_pack ───

def test_compose_and_pack_one_shot():
    lm = _synthetic_landmarks()
    img = _fake_image()
    arr = compose_and_pack(
        img, lm, "double_eyelid", channels_first=True, batch_dim=True
    )
    assert arr.shape == (1, 9, 512, 512)


# ─── 상수 ───

def test_procedure_id_to_sketch_mapping():
    assert PROCEDURE_ID_TO_SKETCH == {
        "nose_tip": "nose_tip",
        "double_eyelid": "double_eyelid",
        "jaw_v_line": "v_line",
    }
