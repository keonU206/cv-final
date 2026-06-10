"""End-to-end 추론: 이미지 + 랜드마크 → 시술별 마스크 dict.

사용 예 (Colab notebook):
    from project.segmentation import build_unet, get_val_transform, predict
    from project.segmentation.inference import load_checkpoint
    model = load_checkpoint('project/segmentation/checkpoints/unet_v1.pt')
    masks = predict(image_bgr, landmarks_478, model)
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

try:
    import torch
except ImportError as e:
    raise ImportError("PyTorch가 필요합니다.") from e

from .postprocess import get_procedure_masks


def load_checkpoint(
    ckpt_path: str | Path,
    num_classes: int = 6,
    encoder_name: str = "resnet34",
    device: Optional[str] = None,
):
    """학습된 가중치 로드. 추론 모드로 반환."""
    from .unet import build_unet

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = build_unet(
        num_classes=num_classes,
        encoder_name=encoder_name,
        encoder_weights=None,  # 추론 시엔 ImageNet 가중치 다운로드 불필요
    )
    state = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(state)
    model.to(device).eval()
    return model


def predict(
    image_bgr: np.ndarray,
    landmarks: np.ndarray,
    model,
    input_size: int = 256,
) -> dict[str, np.ndarray]:
    """E2E 추론.

    Args:
        image_bgr: (H, W, 3) BGR uint8. 정규화된 얼굴 이미지 (보통 512×512).
        landmarks: (478, 2) int32. MediaPipe 478점.
        model: 학습된 U-Net (eval mode).
        input_size: 모델 입력 크기 (config의 train.input_size와 일치).

    Returns:
        시술별 마스크 dict (postprocess.get_procedure_masks 참조).
        모든 마스크는 입력 이미지 크기로 리사이즈됨.
    """
    from .transforms import get_val_transform

    h, w = image_bgr.shape[:2]
    transform = get_val_transform(size=input_size)

    # BGR → RGB로 변환 (albumentations은 RGB 기대)
    image_rgb = image_bgr[..., ::-1]
    transformed = transform(image=image_rgb)
    img_tensor = transformed["image"].unsqueeze(0)  # (1, 3, S, S)

    device = next(model.parameters()).device
    img_tensor = img_tensor.to(device)

    with torch.no_grad():
        logits = model(img_tensor)
        pred = logits.argmax(dim=1).squeeze(0).cpu().numpy()  # (S, S) uint8

    # 모델 출력을 원본 이미지 크기로 리사이즈 (nearest, 라벨 보존)
    import cv2
    pred_resized = cv2.resize(
        pred.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST
    )

    # 시술별 마스크 분리
    masks = get_procedure_masks(pred_resized, landmarks)
    return masks
