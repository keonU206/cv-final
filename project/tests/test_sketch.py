"""input_generator.sketch 단위 테스트.

합성 랜드마크로 시술별 sketch 생성 동작 검증.
"""
import numpy as np
import pytest

from project.input_generator.sketch import (
    SKETCH_GENERATORS,
    generate_double_eyelid_sketch,
    generate_nose_tip_sketch,
    generate_sketch,
    generate_v_line_sketch,
)


def _synthetic_landmarks(n: int = 478) -> np.ndarray:
    rng = np.random.default_rng(seed=7)
    pts = rng.integers(low=150, high=362, size=(n, 2), dtype=np.int32)
    return pts


@pytest.mark.parametrize("fn", [
    generate_nose_tip_sketch,
    generate_double_eyelid_sketch,
    generate_v_line_sketch,
])
def test_sketch_shape_dtype(fn):
    lm = _synthetic_landmarks()
    out = fn(lm, intensity=0.5, size=512)
    assert out.shape == (512, 512)
    assert out.dtype == np.uint8
    assert out.max() == 255  # 라인이 그려졌어야 함
    assert out.min() == 0


def test_generate_sketch_dispatcher():
    lm = _synthetic_landmarks()
    for pid in ("nose_tip", "double_eyelid", "v_line"):
        out = generate_sketch(lm, procedure_id=pid, intensity=0.5)
        assert out.shape == (512, 512)


def test_generate_sketch_unknown_id():
    lm = _synthetic_landmarks()
    with pytest.raises(ValueError):
        generate_sketch(lm, procedure_id="unknown_xyz")


def test_intensity_zero_vs_one_differs():
    """intensity=0과 1은 변형 강도 차이 → sketch 픽셀 위치 다름."""
    lm = _synthetic_landmarks()
    s0 = generate_nose_tip_sketch(lm, intensity=0.0)
    s1 = generate_nose_tip_sketch(lm, intensity=1.0)
    assert not np.array_equal(s0, s1)


def test_sketch_generators_keys():
    assert set(SKETCH_GENERATORS.keys()) >= {"nose_tip", "double_eyelid", "v_line"}
