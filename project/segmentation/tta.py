"""Test Time Augmentation (TTA) — 추론 시 여러 변형의 logits 평균.

학습 변경 X. 이미 학습된 model + image 받아서 더 안정적인 예측 생성.

전략:
    원본 + Horizontal Flip + Rotation ±10° → 4개 logits → 평균 → argmax

→ 평균 +1~2%p mIoU 향상 기대 (논문 표준).
"""
from __future__ import annotations

from typing import Optional

import numpy as np

try:
    import torch
    import torch.nn.functional as F
except ImportError as e:
    raise ImportError("PyTorch가 필요합니다.") from e


def _rotate_tensor(
    x: torch.Tensor, angle_deg: float, interpolation: str = "bilinear"
) -> torch.Tensor:
    """(B, C, H, W) 텐서를 각도만큼 회전.

    Args:
        x: (B, C, H, W) float tensor
        angle_deg: 회전 각도 (degree, 양수=반시계)
        interpolation: 'bilinear' (image) 또는 'nearest' (mask)

    Returns:
        같은 shape의 회전된 tensor.
    """
    if angle_deg == 0:
        return x

    B, C, H, W = x.shape
    theta = torch.tensor(np.deg2rad(angle_deg), dtype=x.dtype, device=x.device)
    cos_t = torch.cos(theta)
    sin_t = torch.sin(theta)

    # 2D affine matrix for grid_sample (batch_size 1 broadcast)
    affine = torch.tensor(
        [[cos_t, -sin_t, 0], [sin_t, cos_t, 0]],
        dtype=x.dtype, device=x.device,
    ).unsqueeze(0).expand(B, -1, -1)

    grid = F.affine_grid(affine, x.size(), align_corners=False)
    return F.grid_sample(
        x, grid, mode=interpolation, padding_mode="zeros", align_corners=False
    )


def predict_with_tta(
    model,
    image: torch.Tensor,
    device: Optional[str] = None,
    augmentations: Optional[list[str]] = None,
    rotation_deg: float = 10.0,
) -> torch.Tensor:
    """단일 이미지에 TTA 적용 → 평균 logits.

    Args:
        model: torch.nn.Module (eval mode 권장).
        image: (C, H, W) tensor. C=3 또는 4 (LM-guided).
        device: 'cuda' 또는 'cpu'.
        augmentations: 적용할 augmentation 목록.
                       ['original', 'hflip', 'rot+', 'rot-'] 중 부분집합.
                       None이면 전체 사용.
        rotation_deg: 회전 각도 (대칭).

    Returns:
        (num_classes, H, W) tensor — 평균 logits.
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    if augmentations is None:
        augmentations = ["original", "hflip", "rot+", "rot-"]

    model.eval()
    x = image.unsqueeze(0).to(device)  # (1, C, H, W)

    logits_sum = None
    n_augs = 0

    with torch.no_grad():
        for aug in augmentations:
            if aug == "original":
                x_aug = x
                logits = model(x_aug)
                logits_inv = logits

            elif aug == "hflip":
                x_aug = torch.flip(x, dims=[-1])
                logits = model(x_aug)
                # 좌우 반전을 logits에서 역변환
                logits_inv = torch.flip(logits, dims=[-1])

            elif aug == "rot+":
                x_aug = _rotate_tensor(x, +rotation_deg, "bilinear")
                logits = model(x_aug)
                # 역회전 (logits은 bilinear OK)
                logits_inv = _rotate_tensor(logits, -rotation_deg, "bilinear")

            elif aug == "rot-":
                x_aug = _rotate_tensor(x, -rotation_deg, "bilinear")
                logits = model(x_aug)
                logits_inv = _rotate_tensor(logits, +rotation_deg, "bilinear")

            else:
                raise ValueError(f"Unknown augmentation: {aug}")

            if logits_sum is None:
                logits_sum = logits_inv
            else:
                logits_sum = logits_sum + logits_inv
            n_augs += 1

    avg_logits = logits_sum / n_augs
    return avg_logits.squeeze(0)  # (C, H, W)


def predict_with_tta_batch(
    model,
    images: torch.Tensor,
    device: Optional[str] = None,
    augmentations: Optional[list[str]] = None,
    rotation_deg: float = 10.0,
) -> torch.Tensor:
    """배치 단위 TTA.

    Args:
        images: (B, C, H, W) tensor.

    Returns:
        (B, num_classes, H, W) tensor — 평균 logits.
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    if augmentations is None:
        augmentations = ["original", "hflip", "rot+", "rot-"]

    model.eval()
    x = images.to(device)

    logits_sum = None
    n_augs = 0

    with torch.no_grad():
        for aug in augmentations:
            if aug == "original":
                logits_inv = model(x)
            elif aug == "hflip":
                x_aug = torch.flip(x, dims=[-1])
                logits_inv = torch.flip(model(x_aug), dims=[-1])
            elif aug == "rot+":
                x_aug = _rotate_tensor(x, +rotation_deg, "bilinear")
                logits_inv = _rotate_tensor(model(x_aug), -rotation_deg, "bilinear")
            elif aug == "rot-":
                x_aug = _rotate_tensor(x, -rotation_deg, "bilinear")
                logits_inv = _rotate_tensor(model(x_aug), +rotation_deg, "bilinear")
            else:
                raise ValueError(f"Unknown augmentation: {aug}")

            if logits_sum is None:
                logits_sum = logits_inv
            else:
                logits_sum = logits_sum + logits_inv
            n_augs += 1

    return logits_sum / n_augs


def evaluate_with_tta(
    model,
    val_dl,
    device,
    num_classes: int = 6,
    augmentations: Optional[list[str]] = None,
) -> dict:
    """TTA로 val 셋 전체 평가.

    Returns:
        {'miou': float, 'dice': float}
    """
    from .metrics import compute_metrics

    model.eval()
    miou_sum = 0.0
    dice_sum = 0.0
    n_batches = 0

    for img, mask in val_dl:
        mask = mask.to(device)
        avg_logits = predict_with_tta_batch(
            model, img, device=device, augmentations=augmentations
        )
        m = compute_metrics(avg_logits, mask, num_classes=num_classes)
        miou_sum += m["miou"]
        dice_sum += m["dice"]
        n_batches += 1

    return {
        "miou": miou_sum / max(n_batches, 1),
        "dice": dice_sum / max(n_batches, 1),
    }
