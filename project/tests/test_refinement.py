"""project.refinement 단위 테스트 — model / data / losses sanity check."""
import io

import numpy as np
import pytest

torch = pytest.importorskip("torch")
smp = pytest.importorskip("segmentation_models_pytorch")

from project.refinement.data import add_synthetic_noise
from project.refinement.model import (
    RefinementWrapper,
    build_refinement_net,
    build_refinement_wrapper,
)


def test_build_refinement_net_default():
    model = build_refinement_net()
    assert isinstance(model, torch.nn.Module)
    x = torch.randn(1, 3, 64, 64)
    y = model(x)
    assert y.shape == (1, 3, 64, 64)


def test_refinement_wrapper_residual_in_range():
    """wrapper 출력은 [-1, 1] 범위에 클램프되어야 함."""
    wrapped = build_refinement_wrapper(encoder_weights=None, residual_scale=0.5)
    x = torch.randn(1, 3, 64, 64).clamp(-1, 1)
    y = wrapped(x)
    assert y.shape == x.shape
    assert y.min() >= -1.0001
    assert y.max() <= 1.0001


def test_refinement_wrapper_param_count_reasonable():
    """resnet18 backbone 기준 < 20M 파라미터."""
    wrapped = build_refinement_wrapper(encoder_weights=None)
    n = sum(p.numel() for p in wrapped.parameters())
    assert n < 20_000_000
    assert n > 1_000_000


def test_refinement_wrapper_residual_zero_returns_input():
    """residual_scale=0이면 출력 = 입력 (학습 전 sanity)."""
    wrapped = build_refinement_wrapper(encoder_weights=None, residual_scale=0.0)
    x = torch.randn(1, 3, 64, 64).clamp(-0.9, 0.9)
    y = wrapped(x)
    assert torch.allclose(y, x, atol=1e-6)


def test_add_synthetic_noise_changes_image():
    rng = np.random.default_rng(0)
    img = rng.integers(0, 255, size=(128, 128, 3), dtype=np.uint8)
    noisy = add_synthetic_noise(img, seed=0)
    assert noisy.shape == img.shape
    assert noisy.dtype == np.uint8
    assert not np.array_equal(noisy, img)


def test_add_synthetic_noise_reproducible():
    rng = np.random.default_rng(7)
    img = rng.integers(0, 255, size=(64, 64, 3), dtype=np.uint8)
    a = add_synthetic_noise(img, seed=42, blur_p=0.0)
    b = add_synthetic_noise(img, seed=42, blur_p=0.0)
    np.testing.assert_array_equal(a, b)


def test_refinement_loss_forward_l1_only():
    """perceptual 끄고 L1만 — VGG 로드 안 함 (CPU 빠름)."""
    from project.refinement.losses import RefinementLoss

    loss_fn = RefinementLoss(use_perceptual=False)
    p = torch.randn(2, 3, 32, 32)
    t = torch.randn(2, 3, 32, 32)
    out = loss_fn(p, t)
    assert "l1" in out and "total" in out
    assert out["total"].item() > 0


def test_synthetic_dataset_with_tmpdir(tmp_path):
    """tmpdir에 가짜 이미지 만들어서 dataset 동작 확인."""
    import cv2

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    rng = np.random.default_rng(0)
    for i in range(3):
        img = rng.integers(0, 255, size=(64, 64, 3), dtype=np.uint8)
        cv2.imwrite(str(img_dir / f"{i}.png"), img)

    from project.refinement.data import SyntheticRefinementDataset

    ds = SyntheticRefinementDataset(image_dir=img_dir, size=64, seed=0)
    assert len(ds) == 3
    sample = ds[0]
    assert sample["input"].shape == (3, 64, 64)
    assert sample["target"].shape == (3, 64, 64)
    assert sample["input"].dtype == torch.float32
    assert sample["input"].min() >= -1.0001
    assert sample["input"].max() <= 1.0001
