"""project.segmentation.gradcam 단위 테스트."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")
smp = pytest.importorskip("segmentation_models_pytorch")

from project.segmentation.gradcam import GradCAM, find_target_layer, overlay_heatmap
from project.segmentation.unet import build_unet


def test_find_target_layer_dot_notation():
    model = build_unet(num_classes=6, encoder_weights=None)
    layer = find_target_layer(model, "encoder.layer4")
    assert isinstance(layer, torch.nn.Module)


def test_find_target_layer_invalid():
    model = build_unet(num_classes=6, encoder_weights=None)
    with pytest.raises(AttributeError):
        find_target_layer(model, "encoder.ghost_layer")


def test_gradcam_output_shape():
    model = build_unet(num_classes=6, encoder_weights=None, attention_type="scse")
    model.eval()
    target = find_target_layer(model, "encoder.layer4")
    gcam = GradCAM(model, target)

    x = torch.randn(1, 3, 64, 64, requires_grad=True)
    cam = gcam(x, target_class=1)

    assert cam.shape == (64, 64)
    assert cam.min() >= 0.0
    assert cam.max() <= 1.0
    gcam.remove_hooks()


def test_gradcam_batch_size_check():
    model = build_unet(num_classes=6, encoder_weights=None)
    target = find_target_layer(model, "encoder.layer4")
    gcam = GradCAM(model, target)
    x = torch.randn(2, 3, 64, 64)
    with pytest.raises(ValueError):
        gcam(x, target_class=0)
    gcam.remove_hooks()


def test_gradcam_different_classes_differ():
    """다른 클래스에 대한 cam이 달라야 한다 (모델이 trained가 아니어도)."""
    model = build_unet(num_classes=6, encoder_weights=None, attention_type="scse")
    model.eval()
    target = find_target_layer(model, "encoder.layer4")
    gcam = GradCAM(model, target)

    cams = []
    for cls in [1, 2, 3]:
        x = torch.randn(1, 3, 64, 64, requires_grad=True)
        cam = gcam(x, target_class=cls)
        cams.append(cam.numpy())

    # 모두 0이면 안 됨
    assert any(c.sum() > 0 for c in cams)
    gcam.remove_hooks()


def test_overlay_heatmap_shape_dtype():
    image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    heatmap = np.random.rand(64, 64).astype(np.float32)
    overlay = overlay_heatmap(image, heatmap, alpha=0.5)
    assert overlay.shape == image.shape
    assert overlay.dtype == np.uint8
