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
          'support': list[int],          # 클래스별 정답 픽셀 수
          'confusion_matrix': np.ndarray (C, C),
        }

    Note:
        mIoU/Dice 평균은 **정답에 실제로 존재하는 클래스만** 대상으로 한다.
        라벨 매핑(label_map.py)상 한 번도 등장하지 않는 클래스
        (예: 'unused')를 평균에 넣으면 IoU 0이 섞여 점수가 부당하게
        낮아지므로 support==0 클래스는 제외한다. 이는 표준 mIoU 관례.
    """
    pred = pred_logits.argmax(dim=1)  # (B, H, W)

    tp, fp, fn, tn = smp.metrics.get_stats(
        pred, target, mode="multiclass", num_classes=num_classes
    )  # 각 (B, C)

    # 배치 내 클래스별 누적(micro) 후 IoU/Dice 계산 → 표본별 0/0 잡음 제거
    tp_c = tp.sum(dim=0).float()
    fp_c = fp.sum(dim=0).float()
    fn_c = fn.sum(dim=0).float()
    support = tp_c + fn_c                 # 클래스별 정답 픽셀 수 (C,)
    denom = tp_c + fp_c + fn_c
    iou_per_class = torch.where(denom > 0, tp_c / denom, torch.zeros_like(denom))
    dice_per_class = torch.where(
        denom > 0, 2.0 * tp_c / (tp_c + denom), torch.zeros_like(denom)
    )

    # 평균 대상: (배경 제외 옵션) AND (정답에 존재하는 클래스만)
    start = 1 if ignore_background else 0
    valid = [c for c in range(start, num_classes) if support[c] > 0]
    if valid:
        miou = float(sum(iou_per_class[c] for c in valid) / len(valid))
        dice_mean = float(sum(dice_per_class[c] for c in valid) / len(valid))
    else:
        miou = 0.0
        dice_mean = 0.0

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
        "support": support.tolist(),
        "confusion_matrix": cm,
    }
