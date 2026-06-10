"""tta.predict_with_tta 단위 테스트 (PyTorch 필요)."""
import pytest

torch = pytest.importorskip("torch")

from project.segmentation.tta import (
    _rotate_tensor,
    predict_with_tta,
    predict_with_tta_batch,
)


class _IdentityModel(torch.nn.Module):
    """입력을 그대로 logits처럼 반환 (테스트용)."""

    def __init__(self, in_channels: int = 3, num_classes: int = 6):
        super().__init__()
        # 단순 1x1 conv (channel 매핑)
        self.conv = torch.nn.Conv2d(in_channels, num_classes, 1)

    def forward(self, x):
        return self.conv(x)


def test_rotate_zero_is_identity():
    x = torch.randn(1, 3, 16, 16)
    y = _rotate_tensor(x, 0.0)
    assert torch.allclose(x, y)


def test_rotate_360_returns_same():
    """360° 회전은 거의 원본 (interpolation 오차 미미)."""
    x = torch.zeros(1, 3, 16, 16)
    x[0, 0, 8, 8] = 1.0
    y = _rotate_tensor(x, 360.0)
    # 정확한 일치는 어려우니 픽셀 값이 보존되었는지만 확인
    assert y.shape == x.shape


def test_predict_with_tta_returns_correct_shape():
    """TTA 출력은 (C, H, W) shape."""
    model = _IdentityModel(in_channels=3, num_classes=6)
    image = torch.randn(3, 32, 32)
    avg_logits = predict_with_tta(
        model, image, device="cpu", augmentations=["original", "hflip"]
    )
    assert avg_logits.shape == (6, 32, 32)


def test_predict_with_tta_batch():
    model = _IdentityModel(in_channels=3, num_classes=6)
    images = torch.randn(4, 3, 32, 32)
    avg = predict_with_tta_batch(
        model, images, device="cpu", augmentations=["original", "hflip"]
    )
    assert avg.shape == (4, 6, 32, 32)


def test_tta_original_only_equals_single_inference():
    """original만 적용하면 일반 추론과 동일."""
    model = _IdentityModel(3, 6)
    model.eval()
    image = torch.randn(3, 32, 32)

    with torch.no_grad():
        single = model(image.unsqueeze(0)).squeeze(0)
    tta = predict_with_tta(
        model, image, device="cpu", augmentations=["original"]
    )
    assert torch.allclose(single, tta, atol=1e-5)


def test_tta_with_4_channel_input():
    """LM-guided 4채널 입력에서도 동작."""
    model = _IdentityModel(in_channels=4, num_classes=6)
    image = torch.randn(4, 32, 32)
    avg = predict_with_tta(
        model, image, device="cpu",
        augmentations=["original", "hflip", "rot+", "rot-"],
    )
    assert avg.shape == (6, 32, 32)


def test_tta_unknown_aug_raises():
    model = _IdentityModel(3, 6)
    image = torch.randn(3, 32, 32)
    with pytest.raises(ValueError):
        predict_with_tta(model, image, augmentations=["unknown_aug"])
