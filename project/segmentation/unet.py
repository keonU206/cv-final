"""segmentation_models_pytorch 기반 U-Net 래퍼.

구조:
- Encoder: ResNet-34 (ImageNet 사전학습) — 계층적 특징 추출
- Decoder: U-Net standard — skip connection으로 공간 정보 복원
- Output: (B, num_classes, H, W) logits
"""
from __future__ import annotations

try:
    import torch.nn as nn
    import segmentation_models_pytorch as smp
except ImportError as e:
    raise ImportError(
        "PyTorch + segmentation_models_pytorch가 필요합니다. "
        "`pip install torch segmentation-models-pytorch` 를 실행하세요."
    ) from e


def build_unet(
    num_classes: int = 6,
    encoder_name: str = "resnet34",
    encoder_weights: str = "imagenet",
    in_channels: int = 3,
    attention_type: str | None = None,
) -> nn.Module:
    """U-Net 모델 생성.

    Args:
        num_classes: 출력 클래스 수 (배경 포함).
        encoder_name: smp 지원 인코더 이름 (resnet34, resnet50 등).
        encoder_weights: 사전학습 가중치 ('imagenet' / None).
        in_channels: 입력 채널 수 (RGB=3, RGB+heatmap=4).
        attention_type: Decoder attention 모듈.
            None (기본) — 표준 U-Net
            'scse' — Spatial-Channel Squeeze & Excitation (Attention 강화)
                     Skip Connection 영역에 attention 적용 효과.

    Returns:
        torch.nn.Module. forward: (B, C, H, W) → (B, num_classes, H, W) logits.
    """
    return smp.Unet(
        encoder_name=encoder_name,
        encoder_weights=encoder_weights,
        in_channels=in_channels,
        classes=num_classes,
        decoder_attention_type=attention_type,
    )
