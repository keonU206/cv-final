"""segmentation 패키지 — U-Net 얼굴 부위 세그멘테이션.

Heavy dependencies (torch, smp, albumentations) lazy-load 처리.
label_map만 numpy 의존이라 즉시 import 가능.
"""
from .label_map import (
    MAPPING,
    OURS,
    ORIGINAL_LABELS,
    remap,
)
from .heatmap import (
    landmark_heatmap,
    landmark_heatmap_multichannel,
    FACE_PART_GROUPS,
)

__all__ = [
    "MAPPING",
    "OURS",
    "ORIGINAL_LABELS",
    "remap",
    "landmark_heatmap",
    "landmark_heatmap_multichannel",
    "FACE_PART_GROUPS",
    "build_unet",
    "ComboLoss",
    "compute_metrics",
    "CelebAMaskHQDataset",
    "get_train_transform",
    "get_val_transform",
    "predict",
    "split_skin_by_landmarks",
    "predict_with_tta",
    "predict_with_tta_batch",
    "evaluate_with_tta",
]


def __getattr__(name: str):
    if name == "build_unet":
        from .unet import build_unet
        return build_unet
    if name == "ComboLoss":
        from .losses import ComboLoss
        return ComboLoss
    if name == "compute_metrics":
        from .metrics import compute_metrics
        return compute_metrics
    if name == "CelebAMaskHQDataset":
        from .data import CelebAMaskHQDataset
        return CelebAMaskHQDataset
    if name in ("get_train_transform", "get_val_transform"):
        from . import transforms
        return getattr(transforms, name)
    if name == "predict":
        from .inference import predict
        return predict
    if name == "split_skin_by_landmarks":
        from .postprocess import split_skin_by_landmarks
        return split_skin_by_landmarks
    if name in ("predict_with_tta", "predict_with_tta_batch", "evaluate_with_tta"):
        from . import tta
        return getattr(tta, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
