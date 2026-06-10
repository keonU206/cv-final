"""U-Net 학습 루프 (PyTorch native).

기능:
- Baseline U-Net (in_channels=3) 또는 LM-guided U-Net (in_channels=4) 학습
- Early Stopping (val_mIoU 기반)
- Best checkpoint 저장 (val_best.pt)
- Combo Loss (Dice + CE)

사용법:
    python -m project.segmentation.train
    # 또는 Colab notebook에서 train(config_path=...) 호출
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

try:
    import torch
    from torch.utils.data import DataLoader
    from torch.optim.lr_scheduler import CosineAnnealingLR
except ImportError as e:
    raise ImportError("PyTorch가 필요합니다.") from e


def _load_config(config_path: str | Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def evaluate(model, val_dl, device, num_classes) -> dict:
    """검증 셋에서 평균 mIoU/Dice 계산."""
    from .metrics import compute_metrics

    model.eval()
    miou_sum, dice_sum, n_batches = 0.0, 0.0, 0
    with torch.no_grad():
        for img, mask in val_dl:
            img, mask = img.to(device), mask.to(device)
            pred = model(img)
            m = compute_metrics(pred, mask, num_classes=num_classes)
            miou_sum += m["miou"]
            dice_sum += m["dice"]
            n_batches += 1
    return {
        "miou": miou_sum / max(n_batches, 1),
        "dice": dice_sum / max(n_batches, 1),
    }


def train(
    config_path: str | Path = "project/segmentation/config.yaml",
    device: Optional[str] = None,
) -> dict:
    """학습 진입점. config.yaml 읽어서 학습 실행.

    Returns:
        {
            'final_miou': float,
            'final_dice': float,
            'best_miou': float,
            'best_epoch': int,
            'best_ckpt_path': str,
            'history': list[dict],
        }
    """
    cfg = _load_config(config_path)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # ─── Landmark flag ───
    model_cfg = cfg.get("model", {})
    use_landmark = bool(model_cfg.get("use_landmark", False))
    in_channels = 4 if use_landmark else 3
    print(f"use_landmark: {use_landmark} → in_channels={in_channels}")

    # Lazy imports
    from .data import CelebAMaskHQDataset
    from .losses import ComboLoss
    from .transforms import get_train_transform, get_val_transform
    from .unet import build_unet

    # ─── Data ───
    input_size = cfg["train"]["input_size"]
    landmark_sigma = float(cfg.get("heatmap", {}).get("sigma", 3.0))

    train_tf = get_train_transform(
        size=input_size,
        horizontal_flip_p=cfg["augmentation"]["horizontal_flip"],
        rotation_deg=cfg["augmentation"]["rotation_deg"],
        brightness_contrast_p=cfg["augmentation"]["brightness_contrast"],
        gaussian_blur_p=cfg["augmentation"]["gaussian_blur"],
        with_heatmap=use_landmark,
    )
    val_tf = get_val_transform(size=input_size, with_heatmap=use_landmark)

    subset = cfg["dataset"].get("subset_size")
    cache_dir = cfg["dataset"].get("cache_dir") or "/content/cv-final-cache"

    train_ds = CelebAMaskHQDataset(
        split="train", transform=train_tf,
        subset_size=subset, cache_dir=cache_dir,
        input_size=input_size,
        use_landmark=use_landmark, landmark_sigma=landmark_sigma,
    )
    val_ds = CelebAMaskHQDataset(
        split="val", transform=val_tf,
        subset_size=(subset // 8 if subset else None),
        cache_dir=cache_dir,
        input_size=input_size,
        use_landmark=use_landmark, landmark_sigma=landmark_sigma,
    )
    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}")

    train_dl = DataLoader(
        train_ds, batch_size=cfg["train"]["batch_size"], shuffle=True,
        num_workers=cfg["train"]["num_workers"], pin_memory=True,
    )
    val_dl = DataLoader(
        val_ds, batch_size=cfg["train"]["batch_size"], shuffle=False,
        num_workers=cfg["train"]["num_workers"], pin_memory=True,
    )

    # ─── Model ───
    attention_type = cfg["model"].get("attention_type", None)
    if attention_type in ("", "null", "none", "None"):
        attention_type = None  # YAML에서 null/빈 문자열 처리

    model = build_unet(
        num_classes=cfg["classes"]["num_classes"],
        encoder_name=cfg["model"]["encoder_name"],
        encoder_weights=cfg["model"]["encoder_weights"],
        in_channels=in_channels,
        attention_type=attention_type,
    ).to(device)
    print(
        f"Model: U-Net {cfg['model']['encoder_name']} "
        f"(in_channels={in_channels}, attention={attention_type})"
    )

    # ─── Loss + Optim ───
    loss_fn = ComboLoss(
        dice_weight=cfg["loss"]["dice_weight"],
        ce_weight=cfg["loss"]["ce_weight"],
    )
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg["train"]["lr"],
        weight_decay=cfg["train"]["weight_decay"],
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg["train"]["epochs"])

    # ─── Early Stopping 설정 ───
    es_cfg = cfg.get("early_stopping", {})
    es_enabled = bool(es_cfg.get("enabled", False))
    es_patience = int(es_cfg.get("patience", 5))
    if es_enabled:
        print(f"Early Stopping enabled: patience={es_patience}")

    # ─── Output 설정 ───
    ckpt_dir = Path(cfg["output"]["checkpoint_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    log_interval = cfg["output"]["log_interval"]
    save_every = cfg["output"].get("save_every_epoch", False)
    save_best_only = cfg["output"].get("save_best_only", True)

    # 모델 이름 (baseline / lmguided / attention / attention_lm)
    if attention_type and use_landmark:
        model_tag = "attention_lm"
    elif attention_type:
        model_tag = "attention"
    elif use_landmark:
        model_tag = "lmguided"
    else:
        model_tag = "baseline"
    best_ckpt = ckpt_dir / f"unet_{model_tag}_best.pt"

    # ─── Training loop ───
    history = []
    best_miou = 0.0
    best_epoch = -1
    patience_counter = 0

    for epoch in range(cfg["train"]["epochs"]):
        model.train()
        running_loss = 0.0
        for step, (img, mask) in enumerate(train_dl):
            img, mask = img.to(device), mask.to(device)
            pred = model(img)
            loss = loss_fn(pred, mask)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if step % log_interval == 0:
                print(
                    f"epoch {epoch} step {step}/{len(train_dl)} "
                    f"loss {loss.item():.4f}"
                )

        avg_loss = running_loss / len(train_dl)
        val_m = evaluate(model, val_dl, device, cfg["classes"]["num_classes"])
        print(
            f"epoch {epoch} done · avg_loss {avg_loss:.4f} · "
            f"val_mIoU {val_m['miou']:.4f} · val_Dice {val_m['dice']:.4f}"
        )
        history.append({"epoch": epoch, "loss": avg_loss, **val_m})

        scheduler.step()

        # ─── Best checkpoint ───
        if val_m["miou"] > best_miou:
            best_miou = val_m["miou"]
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), best_ckpt)
            print(f"  ★ new best: val_mIoU={best_miou:.4f} → saved {best_ckpt}")
        else:
            patience_counter += 1
            if es_enabled and patience_counter >= es_patience:
                print(
                    f"  ⏸ Early stopping at epoch {epoch} "
                    f"(no improvement for {es_patience} epochs)"
                )
                break

        # ─── Per-epoch save (선택) ───
        if save_every and not save_best_only:
            ep_ckpt = ckpt_dir / f"unet_{model_tag}_ep{epoch}.pt"
            torch.save(model.state_dict(), ep_ckpt)

    print(
        f"\n=== Training done ===\n"
        f"Best mIoU: {best_miou:.4f} at epoch {best_epoch}\n"
        f"Best ckpt: {best_ckpt}"
    )

    return {
        "final_miou": history[-1]["miou"],
        "final_dice": history[-1]["dice"],
        "best_miou": best_miou,
        "best_epoch": best_epoch,
        "best_ckpt_path": str(best_ckpt),
        "checkpoint_path": str(best_ckpt),  # backward compat with notebook
        "history": history,
        "model_tag": model_tag,
    }


if __name__ == "__main__":
    result = train()
    print("\n=== Training complete ===")
    print(result)
