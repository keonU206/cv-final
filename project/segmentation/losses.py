"""Combo Loss = α·DiceLoss + β·CrossEntropyLoss.

- Dice: class imbalance 보정 (skin이 크고 nose가 작은 경우)
- CE: gradient smoothing (Dice 단독은 초기 학습 불안정)
- 권장: α = β = 0.5
"""
from __future__ import annotations

try:
    import torch
    import torch.nn as nn
    import segmentation_models_pytorch as smp
except ImportError as e:
    raise ImportError(
        "PyTorch + segmentation_models_pytorch가 필요합니다."
    ) from e


class ComboLoss(nn.Module):
    """Combined Dice + CrossEntropy Loss for multiclass segmentation."""

    def __init__(self, dice_weight: float = 0.5, ce_weight: float = 0.5):
        super().__init__()
        if dice_weight < 0 or ce_weight < 0:
            raise ValueError("Loss weights는 비음수여야 합니다.")
        self.dice = smp.losses.DiceLoss(mode="multiclass", from_logits=True)
        self.ce = nn.CrossEntropyLoss()
        self.dice_weight = dice_weight
        self.ce_weight = ce_weight

    def forward(self, pred_logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred_logits: (B, C, H, W) float, raw logits.
            target: (B, H, W) long, 클래스 인덱스 0~C-1.
        """
        return (
            self.dice_weight * self.dice(pred_logits, target)
            + self.ce_weight * self.ce(pred_logits, target)
        )
