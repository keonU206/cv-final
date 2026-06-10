"""Refinement Loss — L1 + Perceptual (VGG19 features).

Johnson et al. 2016 ECCV. Perceptual Losses for Real-Time Style Transfer.
"""
from __future__ import annotations

from typing import Optional

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torchvision import models
except ImportError as e:
    raise ImportError("torch, torchvision 필요") from e

# 입력은 [-1, 1] 범위 가정 → VGG는 [0, 1] + ImageNet 정규화 기대
_IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
_IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


class VGGPerceptual(nn.Module):
    """VGG19 중간 features 추출 후 L2 distance 계산.

    사용 레이어 (Johnson 2016 기본 권장): relu1_2, relu2_2, relu3_3, relu4_3.
    """

    def __init__(self, weights: Optional[str] = "IMAGENET1K_V1") -> None:
        super().__init__()
        try:
            vgg = models.vgg19(weights=weights).features
        except TypeError:
            # 구버전 torchvision (weights= 미지원)
            vgg = models.vgg19(pretrained=(weights is not None)).features
        vgg.eval()
        for p in vgg.parameters():
            p.requires_grad = False

        # relu activations 인덱스 (vgg19): 3, 8, 17, 26
        self.slice1 = vgg[:4]    # ~relu1_2
        self.slice2 = vgg[4:9]   # ~relu2_2
        self.slice3 = vgg[9:18]  # ~relu3_3
        self.slice4 = vgg[18:27]  # ~relu4_3

        self.register_buffer("mean", _IMAGENET_MEAN)
        self.register_buffer("std", _IMAGENET_STD)

    def _normalize(self, x: "torch.Tensor") -> "torch.Tensor":
        # [-1, 1] → [0, 1] → ImageNet 정규화
        x = (x + 1.0) / 2.0
        return (x - self.mean) / self.std

    def _extract(self, x: "torch.Tensor") -> list:
        x = self._normalize(x)
        f1 = self.slice1(x)
        f2 = self.slice2(f1)
        f3 = self.slice3(f2)
        f4 = self.slice4(f3)
        return [f1, f2, f3, f4]

    def forward(
        self, pred: "torch.Tensor", target: "torch.Tensor"
    ) -> "torch.Tensor":
        with torch.no_grad():
            feats_t = self._extract(target)
        feats_p = self._extract(pred)
        loss = 0.0
        for fp, ft in zip(feats_p, feats_t):
            loss = loss + F.l1_loss(fp, ft)
        return loss


class RefinementLoss(nn.Module):
    """L1 + Perceptual 가중합.

    L = l1_weight * L1(pred, target) + perceptual_weight * VGG_Perceptual.
    """

    def __init__(
        self,
        l1_weight: float = 1.0,
        perceptual_weight: float = 0.1,
        use_perceptual: bool = True,
    ) -> None:
        super().__init__()
        self.l1_weight = l1_weight
        self.perceptual_weight = perceptual_weight
        self.use_perceptual = use_perceptual
        self.l1 = nn.L1Loss()
        self.perceptual = VGGPerceptual() if use_perceptual else None

    def forward(
        self, pred: "torch.Tensor", target: "torch.Tensor"
    ) -> dict:
        l1_loss = self.l1(pred, target)
        total = self.l1_weight * l1_loss
        out = {"l1": l1_loss.detach(), "total": total}
        if self.use_perceptual:
            p_loss = self.perceptual(pred, target)
            total = total + self.perceptual_weight * p_loss
            out["perceptual"] = p_loss.detach()
        out["total"] = total
        return out
