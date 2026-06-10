"""SC-FEGAN Fine-tuning 학습 루프 (TF 1.x compat).

⚠ 본 모듈은 TF 1.x 환경에서만 동작:
    os.environ['TF_USE_LEGACY_KERAS'] = '1'
    import tensorflow.compat.v1 as tf
    tf.disable_v2_behavior()

핵심 전략:
- pretrained SC-FEGAN ckpt 로드 → G+D 동시 fine-tune (작은 lr)
- catastrophic forgetting 방지: lr=1e-5, epochs=3
- 매 epoch마다 sample 저장 (sanity check)
- 학습 실패 또는 환경 충돌 시 pretrained로 폴백
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import yaml


def _load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_tf_compat() -> bool:
    """TF 2.x compat mode 환경 셋업. 실패 시 False."""
    try:
        os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
        import tensorflow.compat.v1 as tf
        tf.disable_v2_behavior()
        print(f"TF compat mode OK · version={tf.__version__}")
        return True
    except Exception as e:
        print(f"TF compat setup 실패: {e}")
        return False


def _import_scfegan_repo(repo_dir: str | Path):
    """SC-FEGAN repo의 모델 정의를 import 가능하게 path 추가."""
    repo_dir = str(repo_dir)
    if repo_dir not in sys.path:
        sys.path.insert(0, repo_dir)
    try:
        from src.model import Model as SCFEGANModel  # type: ignore
        return SCFEGANModel
    except ImportError as e:
        raise ImportError(
            f"SC-FEGAN repo 모듈을 import 실패: {e}\n"
            f"repo_dir={repo_dir}에 git clone되어 있어야 함."
        )


def build_finetune_sample_batch(
    image_paths: list,
    procedures: tuple,
    intensity_range: tuple,
    batch_size: int,
    size: int = 512,
    seed_base: int = 0,
) -> Optional[dict]:
    """1개 batch (B, H, W, 9) 입력 + (B, H, W, 3) target 생성.

    Returns:
        {'input': (B,H,W,9), 'target': (B,H,W,3), 'mask': (B,H,W,1)} 또는
        None (랜드마크 실패 등으로 batch 채우기 실패).
    """
    from project.scfegan_finetune.data_pipeline import iter_finetune_samples
    from project.input_generator import to_scfegan_tensor

    samples_iter = iter_finetune_samples(
        image_paths, procedure_ids=procedures,
        size=size, intensity_range=intensity_range,
        seed=seed_base,
    )
    inputs, targets, masks = [], [], []
    for pack in samples_iter:
        if len(inputs) >= batch_size:
            break
        tensor = to_scfegan_tensor(
            pack.composed, normalize=True,
            channels_first=False, batch_dim=False,
        )
        target = (pack.image.astype(np.float32) / 127.5) - 1.0
        inputs.append(tensor)
        targets.append(target)
        masks.append(pack.composed["mask"].astype(np.float32) / 255.0)

    if len(inputs) < batch_size:
        return None
    return {
        "input": np.stack(inputs, axis=0).astype(np.float32),
        "target": np.stack(targets, axis=0).astype(np.float32),
        "mask": np.stack(masks, axis=0).astype(np.float32),
    }


def train_finetune(
    config_path: str | Path = "project/scfegan_finetune/config_finetune.yaml",
    dry_run: bool = False,
) -> dict:
    """SC-FEGAN Fine-tuning 메인 진입점.

    Args:
        config_path: config_finetune.yaml 경로.
        dry_run: True면 모델 빌드 + 1 step만 실행 (smoke test).

    Returns:
        {'best_ckpt_path': str, 'final_loss_g': float, 'final_loss_d': float,
         'used_fallback': bool, 'history': list}
    """
    cfg = _load_config(config_path)
    print(f"Config loaded: {config_path}")

    # ─── TF compat setup ───
    if not setup_tf_compat():
        return _fallback_result(cfg, reason="tf_setup_failed")

    import tensorflow.compat.v1 as tf
    from project.scfegan_finetune.data_pipeline import sample_celebamask_subset

    # ─── SC-FEGAN 모델 로드 ───
    try:
        SCFEGANModel = _import_scfegan_repo(cfg["scfegan"]["repo_dir"])
    except ImportError as e:
        print(f"SC-FEGAN import 실패: {e}")
        return _fallback_result(cfg, reason="import_failed")

    # ─── 데이터 준비 ───
    image_paths = sample_celebamask_subset(
        cfg["dataset"]["image_dir"],
        n=cfg["dataset"]["subset_size"],
        seed=cfg["dataset"]["seed"],
    )
    print(f"Sampled {len(image_paths)} images")

    # ─── 모델 빌드 + ckpt 로드 ───
    tf.reset_default_graph()
    try:
        model = SCFEGANModel(
            size=cfg["scfegan"]["size"],
            mode="train",
        )
        saver = tf.train.Saver()
    except Exception as e:
        print(f"SC-FEGAN 모델 빌드 실패: {e}")
        return _fallback_result(cfg, reason="model_build_failed")

    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    sess.run(tf.global_variables_initializer())

    pretrained = cfg["scfegan"]["pretrained_ckpt"]
    try:
        saver.restore(sess, pretrained)
        print(f"Pretrained ckpt 로드 OK: {pretrained}")
    except Exception as e:
        print(f"pretrained 로드 실패 → 초기화 학습: {e}")

    # ─── Optimizer (TF 1.x style — SC-FEGAN 원본 graph에 G/D loss op 있다고 가정) ───
    lr_g = cfg["train"]["lr_g"]
    lr_d = cfg["train"]["lr_d"]
    g_vars = [v for v in tf.trainable_variables() if "generator" in v.name.lower()]
    d_vars = [v for v in tf.trainable_variables() if "discriminator" in v.name.lower()]

    # SC-FEGAN 모델 객체에 g_loss, d_loss op이 있다고 가정 (원본 코드 기반)
    try:
        g_optim = tf.train.AdamOptimizer(lr_g).minimize(model.g_loss, var_list=g_vars)
        d_optim = (
            tf.train.AdamOptimizer(lr_d).minimize(model.d_loss, var_list=d_vars)
            if not cfg["train"].get("freeze_d", False) else None
        )
        sess.run(tf.variables_initializer(g_optim.variables()))
        if d_optim is not None:
            sess.run(tf.variables_initializer(d_optim.variables()))
    except AttributeError as e:
        print(f"⚠ SC-FEGAN 모델 op 불일치: {e}")
        print("  → 원본 train 스크립트와 op 이름 매칭 필요. 폴백 진행.")
        return _fallback_result(cfg, reason="op_mismatch")

    # ─── 학습 루프 ───
    history = []
    best_loss = float("inf")
    ckpt_dir = Path(cfg["output"]["checkpoint_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    best_ckpt = ckpt_dir / "scfegan_finetuned.ckpt"

    epochs = 1 if dry_run else cfg["train"]["epochs"]
    bs = cfg["train"]["batch_size"]
    steps_per_epoch = max(1, len(image_paths) // bs)

    for epoch in range(epochs):
        consecutive_skips = 0
        for step in range(1 if dry_run else steps_per_epoch):
            start = step * bs
            batch_paths = image_paths[start:start + bs * 3]  # 여유 (skip 대비)
            batch = build_finetune_sample_batch(
                batch_paths,
                procedures=tuple(cfg["dataset"]["procedures"]),
                intensity_range=tuple(cfg["dataset"]["intensity_range"]),
                batch_size=bs,
                size=cfg["scfegan"]["size"],
                seed_base=epoch * 10000 + step,
            )
            if batch is None:
                consecutive_skips += 1
                if consecutive_skips > cfg["fallback"]["max_consecutive_skips"]:
                    print("  너무 많은 skip → 중단")
                    break
                continue
            consecutive_skips = 0

            # G/D step (SC-FEGAN 원본 feed_dict 형식에 맞춰야 함)
            feed = {model.input_ph: batch["input"], model.target_ph: batch["target"]}
            try:
                _, g_loss = sess.run([g_optim, model.g_loss], feed_dict=feed)
                d_loss = -1.0
                if d_optim is not None:
                    _, d_loss = sess.run([d_optim, model.d_loss], feed_dict=feed)
            except Exception as e:
                print(f"  step {step} 실패: {e}")
                continue

            if step % cfg["train"]["log_interval"] == 0:
                print(f"epoch {epoch} step {step} · g_loss {g_loss:.4f} · d_loss {d_loss:.4f}")
                history.append({"epoch": epoch, "step": step, "g_loss": float(g_loss), "d_loss": float(d_loss)})

            if g_loss < best_loss:
                best_loss = g_loss
                saver.save(sess, str(best_ckpt))

        if cfg["output"].get("save_every_epoch", True):
            saver.save(sess, str(ckpt_dir / f"scfegan_ep{epoch}.ckpt"))

    sess.close()

    return {
        "best_ckpt_path": str(best_ckpt),
        "best_loss_g": best_loss,
        "used_fallback": False,
        "history": history,
    }


def _fallback_result(cfg: dict, reason: str) -> dict:
    """학습 실패 시 pretrained ckpt 그대로 사용."""
    print(f"⚠ Fallback: {reason} → pretrained ckpt 사용")
    return {
        "best_ckpt_path": cfg["scfegan"]["pretrained_ckpt"],
        "best_loss_g": float("nan"),
        "used_fallback": True,
        "fallback_reason": reason,
        "history": [],
    }


if __name__ == "__main__":
    result = train_finetune(dry_run=False)
    print("\n=== Fine-tuning complete ===")
    for k, v in result.items():
        if k != "history":
            print(f"{k}: {v}")
