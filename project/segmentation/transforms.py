"""Albumentations 기반 augmentation 파이프라인.

- 학습용: flip + rotate + brightness/contrast + blur + normalize
- 검증용: resize + normalize (deterministic)

ImageNet 통계로 정규화 (ResNet-34 사전학습 인코더에 맞춤).
"""
from __future__ import annotations

try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
except ImportError as e:
    raise ImportError(
        "albumentations가 필요합니다. `pip install albumentations` 를 실행하세요."
    ) from e


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_train_transform(
    size: int = 256,
    horizontal_flip_p: float = 0.5,
    rotation_deg: int = 15,
    brightness_contrast_p: float = 0.3,
    gaussian_blur_p: float = 0.2,
    with_heatmap: bool = False,
) -> A.Compose:
    """학습용 augmentation 파이프라인.

    Args:
        with_heatmap: True 시 additional_targets에 heatmap 추가
                      (image와 동일하게 변환되도록).
    """
    transforms = [
        A.Resize(size, size),
        A.HorizontalFlip(p=horizontal_flip_p),
        A.Affine(rotate=(-rotation_deg, rotation_deg), p=0.5),
        A.RandomBrightnessContrast(p=brightness_contrast_p),
        A.GaussianBlur(blur_limit=(3, 5), p=gaussian_blur_p),
        A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ToTensorV2(),
    ]
    if with_heatmap:
        # heatmap을 mask로 취급 → Normalize 안 됨 ([0,1] 보존), Spatial 변환만 적용
        return A.Compose(
            transforms,
            additional_targets={"heatmap": "mask"},
        )
    return A.Compose(transforms)


def get_val_transform(size: int = 256, with_heatmap: bool = False) -> A.Compose:
    """검증/추론용 deterministic 파이프라인."""
    transforms = [
        A.Resize(size, size),
        A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ToTensorV2(),
    ]
    if with_heatmap:
        return A.Compose(
            transforms,
            additional_targets={"heatmap": "mask"},
        )
    return A.Compose(transforms)
