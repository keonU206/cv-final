"""평가 지표: mIoU, Dice Score, Per-class IoU, Confusion Matrix.

평가 기준 (15% 항목) 대응:
- mIoU: 메인 지표 (배경 제외 평균)
- Dice: F1 유사 (per-class)
- Confusion Matrix: 클래스 간 혼동 분석
"""
from __future__ import annotations

import numpy as np

try:
    import torch
    import segmentation_models_pytorch as smp
except ImportError as e:
    raise ImportError(
        "PyTorch + segmentation_models_pytorch가 필요합니다."
    ) from e


def compute_metrics(
    pred_logits: torch.Tensor,
    target: torch.Tensor,
    num_classes: int = 6,
    ignore_background: bool = True,
) -> dict:
    """배치 단위 지표 계산.

    Args:
        pred_logits: (B, C, H, W) float logits.
        target: (B, H, W) long, 클래스 인덱스.
        num_classes: 전체 클래스 수.
        ignore_background: True면 mIoU/Dice 평균에서 클래스 0 제외.

    Returns:
        {
          'miou': float,
          'dice': float,
          'per_class_iou': list[float],
          'per_class_dice': list[float],
          'confusion_matrix': np.ndarray (C, C),
        }
    """
    pred = pred_logits.argmax(dim=1)  # (B, H, W)

    tp, fp, fn, tn = smp.metrics.get_stats(
        pred, target, mode="multiclass", num_classes=num_classes
    )
    iou = smp.metrics.iou_score(tp, fp, fn, tn, reduction="none")    # (B, C)
    dice = smp.metrics.f1_score(tp, fp, fn, tn, reduction="none")   # (B, C)

    iou_per_class = iou.mean(dim=0)    # (C,)
    dice_per_class = dice.mean(dim=0)  # (C,)

    if ignore_background:
        miou = iou_per_class[1:].mean().item()
        dice_mean = dice_per_class[1:].mean().item()
    else:
        miou = iou_per_class.mean().item()
        dice_mean = dice_per_class.mean().item()

    # Confusion Matrix (CPU numpy)
    pred_flat = pred.flatten().cpu().numpy()
    target_flat = target.flatten().cpu().numpy()
    cm = np.zeros((num_classes, num_classes), dtype=np.int64)
    for t in range(num_classes):
        for p in range(num_classes):
            cm[t, p] = int(((target_flat == t) & (pred_flat == p)).sum())

    return {
        "miou": miou,
        "dice": dice_mean,
        "per_class_iou": iou_per_class.tolist(),
        "per_class_dice": dice_per_class.tolist(),
        "confusion_matrix": cm,
    }
