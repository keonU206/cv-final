"""unet.build_unet 단위 테스트 — 표준 / Attention 모드 모두 검증."""
import pytest

torch = pytest.importorskip("torch")
smp = pytest.importorskip("segmentation_models_pytorch")

from project.segmentation.unet import build_unet


def test_build_unet_default():
    """기본 U-Net (3채널, attention 없음) 빌드."""
    model = build_unet(num_classes=6)
    assert isinstance(model, torch.nn.Module)
    x = torch.randn(2, 3, 64, 64)
    y = model(x)
    assert y.shape == (2, 6, 64, 64)


def test_build_unet_4_channel():
    """LM-guided 4채널 입력."""
    model = build_unet(num_classes=6, in_channels=4)
    x = torch.randn(1, 4, 64, 64)
    y = model(x)
    assert y.shape == (1, 6, 64, 64)


def test_build_unet_with_attention():
    """Attention U-Net (SCSE) — 표준 U-Net과 forward shape 동일."""
    model = build_unet(num_classes=6, attention_type="scse")
    x = torch.randn(1, 3, 64, 64)
    y = model(x)
    assert y.shape == (1, 6, 64, 64)


def test_build_unet_attention_with_landmark():
    """Attention + LM Heatmap 조합."""
    model = build_unet(num_classes=6, in_channels=4, attention_type="scse")
    x = torch.randn(1, 4, 64, 64)
    y = model(x)
    assert y.shape == (1, 6, 64, 64)


def test_attention_increases_parameters():
    """Attention 모듈 추가로 파라미터 수 증가."""
    m1 = build_unet(num_classes=6, attention_type=None)
    m2 = build_unet(num_classes=6, attention_type="scse")
    p1 = sum(p.numel() for p in m1.parameters())
    p2 = sum(p.numel() for p in m2.parameters())
    assert p2 > p1, "attention 모델은 파라미터가 더 많아야 함"
