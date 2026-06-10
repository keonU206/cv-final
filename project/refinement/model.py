"""Refinement Network — SC-FEGAN 출력 정제용 작은 U-Net.

Phase 7-B: SC-FEGAN의 출력(노이즈/경계 artifact 포함)을 입력받아
GT에 가까운 clean image를 복원하는 image-to-image translation 모델.

설계:
- segmentation_models_pytorch.Unet 기반 (resnet18 encoder, 가벼움)
- in_channels=3 (RGB) / classes=3 (RGB)
- activation=None → 학습 시 tanh 또는 sigmoid를 후처리에서 결정
- 총 파라미터 ~14M (학습 빠름, Colab T4 OK)
"""
from __future__ import annotations

from typing import Any

try:
    import segmentation_models_pytorch as smp
    import torch
    import torch.nn as nn
except ImportError as e:
    raise ImportError("segmentation_models_pytorch, torch 필요") from e


def build_refinement_net(
    encoder_name: str = "resnet18",
    encoder_weights: str | None = "imagenet",
    in_channels: int = 3,
    out_channels: int = 3,
) -> nn.Module:
    """Refinement U-Net 빌드.

    Args:
        encoder_name: smp encoder 이름 (기본 resnet18 — 가장 가벼움).
        encoder_weights: 사전학습 weights ('imagenet' 또는 None).
        in_channels: 입력 채널 (RGB=3).
        out_channels: 출력 채널 (RGB=3).

    Returns:
        nn.Module — forward(x: (B,3,H,W)) → (B,3,H,W).
    """
    model = smp.Unet(
        encoder_name=encoder_name,
        encoder_weights=encoder_weights,
        in_channels=in_channels,
        classes=out_channels,
        activation=None,  # raw logits; downstream에서 tanh 적용
    )
    return model


class RefinementWrapper(nn.Module):
    """U-Net 출력에 tanh + residual 연결 추가.

    output = clamp(input + delta, -1, 1)
        where delta = tanh(unet(input)) * residual_scale

    Args:
        backbone: build_refinement_net으로 만든 U-Net.
        residual_scale: residual 강도 (작을수록 보수적 정제, 기본 0.5).
    """

    def __init__(self, backbone: nn.Module, residual_scale: float = 0.5) -> None:
        super().__init__()
        self.backbone = backbone
        self.residual_scale = residual_scale

    def forward(self, x: "torch.Tensor") -> "torch.Tensor":
        delta = torch.tanh(self.backbone(x)) * self.residual_scale
        return torch.clamp(x + delta, -1.0, 1.0)


def build_refinement_wrapper(
    encoder_name: str = "resnet18",
    encoder_weights: str | None = "imagenet",
    residual_scale: float = 0.5,
) -> RefinementWrapper:
    """build_refinement_net + RefinementWrapper 일괄."""
    backbone = build_refinement_net(
        encoder_name=encoder_name,
        encoder_weights=encoder_weights,
        in_channels=3,
        out_channels=3,
    )
    return RefinementWrapper(backbone, residual_scale=residual_scale)
