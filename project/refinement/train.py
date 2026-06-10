"""Refinement Network 학습 루프 (PyTorch native).

기능:
- SyntheticRefinementDataset (또는 PairedRefinementDataset) 로드
- L1 + Perceptual (VGG19) loss
- Early stopping (val_l1 기반)
- Best checkpoint 저장 + epoch별 sample 시각화 저장

사용:
    python -m project.refinement.train
    또는 Colab notebook에서 train(config_path=...) 호출
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

try:
    import numpy as np
    import torch
    from torch.utils.data import DataLoader, random_split
except ImportError as e:
    raise ImportError("torch 필요") from e


def _load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save_samples(
    inputs: "torch.Tensor",
    preds: "torch.Tensor",
    targets: "torch.Tensor",
    out_path: Path,
    n_samples: int = 4,
) -> None:
    """첫 N개 sample을 (input, pred, target) 가로 비교로 저장."""
    import cv2

    n = min(n_samples, inputs.shape[0])
    rows = []
    for i in range(n):
        triple = torch.cat([inputs[i], preds[i], targets[i]], dim=2)  # (3, H, 3W)
        img = ((triple.cpu().clamp(-1, 1) + 1.0) * 127.5).byte()
        img = img.permute(1, 2, 0).numpy()
        rows.append(img)
    stacked = np.concatenate(rows, axis=0)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), cv2.cvtColor(stacked, cv2.COLOR_RGB2BGR))


def evaluate(model, val_dl, loss_fn, device) -> dict:
    """val 셋에서 평균 L1, perceptual, total 계산."""
    model.eval()
    l1_sum, p_sum, total_sum, n = 0.0, 0.0, 0.0, 0
    with torch.no_grad():
        for batch in val_dl:
            inp = batch["input"].to(device)
            tgt = batch["target"].to(device)
            pred = model(inp)
            losses = loss_fn(pred, tgt)
            l1_sum += losses["l1"].item()
            if "perceptual" in losses:
                p_sum += losses["perceptual"].item()
            total_sum += losses["total"].item()
            n += 1
    return {
        "val_l1": l1_sum / max(n, 1),
        "val_perceptual": p_sum / max(n, 1),
        "val_total": total_sum / max(n, 1),
    }


def train(
    config_path: str | Path = "project/refinement/config.yaml",
    device: Optional[str] = None,
) -> dict:
    cfg = _load_config(config_path)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    from .data import PairedRefinementDataset, SyntheticRefinementDataset
    from .losses import RefinementLoss
    from .model import build_refinement_wrapper

    # ─── Data ───
    ds_cfg = cfg["dataset"]
    if ds_cfg["mode"] == "synthetic":
        ds = SyntheticRefinementDataset(
            image_dir=ds_cfg["image_dir"],
            size=ds_cfg["size"],
            gaussian_sigma=ds_cfg["gaussian_sigma"],
            jpeg_quality=ds_cfg["jpeg_quality"],
            subset_size=ds_cfg.get("subset_size"),
            seed=ds_cfg.get("seed", 0),
        )
    elif ds_cfg["mode"] == "paired":
        ds = PairedRefinementDataset(
            root=ds_cfg["paired_root"], size=ds_cfg["size"]
        )
    else:
        raise ValueError(f"unknown dataset mode: {ds_cfg['mode']}")

    val_n = max(1, int(len(ds) * ds_cfg["val_split_ratio"]))
    train_ds, val_ds = random_split(
        ds, [len(ds) - val_n, val_n],
        generator=torch.Generator().manual_seed(ds_cfg.get("seed", 0)),
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
    model = build_refinement_wrapper(
        encoder_name=cfg["model"]["encoder_name"],
        encoder_weights=cfg["model"]["encoder_weights"],
        residual_scale=cfg["model"]["residual_scale"],
    ).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model params: {n_params:,}")

    # ─── Loss + Optim ───
    loss_fn = RefinementLoss(
        l1_weight=cfg["loss"]["l1_weight"],
        perceptual_weight=cfg["loss"]["perceptual_weight"],
        use_perceptual=cfg["loss"]["use_perceptual"],
    ).to(device)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg["train"]["lr"],
        weight_decay=cfg["train"]["weight_decay"],
    )

    # ─── Early Stopping ───
    es_cfg = cfg.get("early_stopping", {})
    es_enabled = bool(es_cfg.get("enabled", False))
    es_patience = int(es_cfg.get("patience", 3))
    es_metric = es_cfg.get("metric", "val_l1")

    # ─── Output ───
    ckpt_dir = Path(cfg["output"]["checkpoint_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    sample_dir = Path(cfg["output"].get("sample_save_dir", ckpt_dir / "samples"))
    best_ckpt = ckpt_dir / "refinement_best.pt"

    # ─── Train loop ───
    history = []
    best_metric = float("inf")
    best_epoch = -1
    patience_counter = 0

    grad_clip = cfg["train"].get("grad_clip")

    for epoch in range(cfg["train"]["epochs"]):
        model.train()
        running = {"l1": 0.0, "perceptual": 0.0, "total": 0.0}
        for step, batch in enumerate(train_dl):
            inp = batch["input"].to(device)
            tgt = batch["target"].to(device)
            pred = model(inp)
            losses = loss_fn(pred, tgt)

            optimizer.zero_grad()
            losses["total"].backward()
            if grad_clip:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()

            running["l1"] += losses["l1"].item()
            if "perceptual" in losses:
                running["perceptual"] += losses["perceptual"].item()
            running["total"] += losses["total"].item()

            if step % cfg["output"]["log_interval"] == 0:
                print(
                    f"epoch {epoch} step {step}/{len(train_dl)} "
                    f"l1 {losses['l1'].item():.4f} "
                    f"total {losses['total'].item():.4f}"
                )

        n_b = len(train_dl)
        train_avg = {k: v / n_b for k, v in running.items()}
        val_m = evaluate(model, val_dl, loss_fn, device)
        print(
            f"epoch {epoch} done · train_l1 {train_avg['l1']:.4f} · "
            f"val_l1 {val_m['val_l1']:.4f} · val_total {val_m['val_total']:.4f}"
        )
        history.append({"epoch": epoch, **{f"train_{k}": v for k, v in train_avg.items()}, **val_m})

        # ─── Sample 저장 ───
        if cfg["output"].get("sample_every_epoch", False):
            model.eval()
            with torch.no_grad():
                vb = next(iter(val_dl))
                vp = model(vb["input"].to(device))
            _save_samples(
                vb["input"], vp, vb["target"],
                sample_dir / f"epoch_{epoch:02d}.png",
            )

        # ─── Best 저장 ───
        m_now = val_m[es_metric]
        if m_now < best_metric:
            best_metric = m_now
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), best_ckpt)
            print(f"  ★ new best ({es_metric}={best_metric:.4f}) → {best_ckpt}")
        else:
            patience_counter += 1
            if es_enabled and patience_counter >= es_patience:
                print(f"  ⏸ Early stop at epoch {epoch}")
                break

    print(
        f"\n=== Refinement done ===\n"
        f"Best {es_metric}: {best_metric:.4f} at epoch {best_epoch}\n"
        f"Best ckpt: {best_ckpt}"
    )

    return {
        "best_metric": best_metric,
        "best_epoch": best_epoch,
        "best_ckpt_path": str(best_ckpt),
        "history": history,
    }


if __name__ == "__main__":
    result = train()
    print("\n=== Training complete ===")
    print(result)
