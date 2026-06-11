"""Confusion Matrix + Per-class IoU/Dice + Model Comparison.

평가 항목 3번 (성능 분석 및 최적화, 15%) 보강용.

핵심 함수:
- compute_confusion_matrix: (B, C, H, W) pred + (B, H, W) target → (C, C)
- per_class_iou / per_class_dice: confusion matrix → per-class 지표
- plot_confusion_matrix: matplotlib heatmap 시각화
- evaluate_model_on_loader: 모델 + DataLoader → 모든 지표
- model_ablation_table: dict of metrics → 비교 표
"""
from __future__ import annotations

from typing import Optional

try:
    import numpy as np
    import torch
except ImportError as e:
    raise ImportError("numpy, torch 필요") from e


def compute_confusion_matrix(
    pred: "torch.Tensor",
    target: "torch.Tensor",
    num_classes: int,
) -> "np.ndarray":
    """예측 + 정답 → (num_classes, num_classes) confusion matrix.

    Args:
        pred: (B, C, H, W) logits 또는 (B, H, W) class indices.
        target: (B, H, W) class indices [0, num_classes).
        num_classes: 클래스 개수.

    Returns:
        (num_classes, num_classes) np.int64 — conf[i, j] = i를 j로 예측한 픽셀 수.
    """
    if pred.dim() == 4:
        pred_cls = pred.argmax(dim=1)  # (B, H, W)
    else:
        pred_cls = pred

    pred_np = pred_cls.flatten().cpu().numpy().astype(np.int64)
    target_np = target.flatten().cpu().numpy().astype(np.int64)

    # 유효 범위 필터 (label에 -1이나 ignore 있을 때)
    valid = (target_np >= 0) & (target_np < num_classes)
    pred_np, target_np = pred_np[valid], target_np[valid]

    # np.bincount로 효율적 계산
    flat_index = target_np * num_classes + pred_np
    conf = np.bincount(flat_index, minlength=num_classes**2).reshape(
        num_classes, num_classes,
    )
    return conf


def per_class_iou(conf_mat: "np.ndarray", eps: float = 1e-7) -> "np.ndarray":
    """Confusion matrix → per-class IoU.

    IoU_i = TP / (TP + FP + FN)
          = conf[i, i] / (sum(conf[i, :]) + sum(conf[:, i]) - conf[i, i])
    """
    tp = np.diag(conf_mat).astype(np.float64)
    fn = conf_mat.sum(axis=1) - tp  # row sum - diag
    fp = conf_mat.sum(axis=0) - tp  # col sum - diag
    iou = tp / (tp + fp + fn + eps)
    return iou


def per_class_dice(conf_mat: "np.ndarray", eps: float = 1e-7) -> "np.ndarray":
    """Confusion matrix → per-class Dice.

    Dice_i = 2*TP / (2*TP + FP + FN)
    """
    tp = np.diag(conf_mat).astype(np.float64)
    fn = conf_mat.sum(axis=1) - tp
    fp = conf_mat.sum(axis=0) - tp
    dice = (2 * tp) / (2 * tp + fp + fn + eps)
    return dice


def per_class_accuracy(conf_mat: "np.ndarray", eps: float = 1e-7) -> "np.ndarray":
    """Per-class accuracy (recall) = TP / (TP + FN)."""
    tp = np.diag(conf_mat).astype(np.float64)
    total = conf_mat.sum(axis=1)  # 해당 클래스의 실제 픽셀 수
    return tp / (total + eps)


def overall_accuracy(conf_mat: "np.ndarray", eps: float = 1e-7) -> float:
    """전체 픽셀 정확도 = sum(TP) / sum(all)."""
    tp_sum = np.diag(conf_mat).sum()
    total = conf_mat.sum()
    return float(tp_sum / (total + eps))


def evaluate_model_on_loader(
    model: "torch.nn.Module",
    data_loader,
    num_classes: int,
    device: Optional[str] = None,
    max_batches: Optional[int] = None,
) -> dict:
    """모델을 DataLoader 전체에 inference → confusion matrix + 지표 dict.

    Args:
        model: 학습된 segmentation 모델 (eval 모드 자동 적용).
        data_loader: DataLoader, batch는 (image, mask) tuple 또는 dict.
        num_classes: 클래스 개수.
        device: 'cuda' 또는 'cpu'. None이면 자동.
        max_batches: 빠른 테스트용 batch 제한. None이면 전체.

    Returns:
        {
            'confusion_matrix': (C, C) np.ndarray,
            'per_class_iou': (C,) np.ndarray,
            'per_class_dice': (C,) np.ndarray,
            'per_class_accuracy': (C,) np.ndarray,
            'mIoU': float,
            'mean_dice': float,
            'overall_accuracy': float,
            'num_samples': int,
        }
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()

    conf = np.zeros((num_classes, num_classes), dtype=np.int64)
    n_samples = 0

    with torch.no_grad():
        for i, batch in enumerate(data_loader):
            if max_batches is not None and i >= max_batches:
                break

            if isinstance(batch, dict):
                img, mask = batch["image"], batch["mask"]
            else:
                img, mask = batch

            img, mask = img.to(device), mask.to(device)
            pred = model(img)
            conf += compute_confusion_matrix(pred, mask, num_classes)
            n_samples += img.shape[0]

    return {
        "confusion_matrix": conf,
        "per_class_iou": per_class_iou(conf),
        "per_class_dice": per_class_dice(conf),
        "per_class_accuracy": per_class_accuracy(conf),
        "mIoU": float(per_class_iou(conf).mean()),
        "mean_dice": float(per_class_dice(conf).mean()),
        "overall_accuracy": overall_accuracy(conf),
        "num_samples": n_samples,
    }


def plot_confusion_matrix(
    conf_mat: "np.ndarray",
    class_names: list,
    normalize: bool = True,
    title: str = "Confusion Matrix",
    save_path: Optional[str] = None,
    figsize: tuple = (8, 7),
):
    """Confusion matrix heatmap 시각화.

    Args:
        conf_mat: (C, C) np.ndarray.
        class_names: 길이 C 리스트.
        normalize: True면 row 정규화 (recall 값으로 표시).
        title: 제목.
        save_path: 저장 경로 (옵션).
        figsize: matplotlib figure 크기.

    Returns:
        matplotlib Figure.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError("matplotlib 필요") from e

    if normalize:
        row_sums = conf_mat.sum(axis=1, keepdims=True)
        mat = conf_mat.astype(np.float64) / (row_sums + 1e-7)
        fmt = ".2f"
        cbar_label = "Normalized (recall per class)"
    else:
        mat = conf_mat.astype(np.int64)
        fmt = "d"
        cbar_label = "Pixel count"

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(mat, cmap="Blues", interpolation="nearest")

    # 셀에 숫자 표시
    n = len(class_names)
    thresh = mat.max() * 0.6
    for i in range(n):
        for j in range(n):
            color = "white" if mat[i, j] > thresh else "black"
            ax.text(j, i, format(mat[i, j], fmt), ha="center", va="center",
                    color=color, fontsize=11)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted", fontsize=13)
    ax.set_ylabel("True", fontsize=13)
    ax.set_title(title, fontsize=14)

    plt.colorbar(im, ax=ax, label=cbar_label)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig


def model_ablation_table(
    results_by_model: dict,
    class_names: list,
) -> "list[dict]":
    """여러 모델 평가 결과 → 비교 표 (list of dict).

    Args:
        results_by_model: {model_name: result_dict from evaluate_model_on_loader}
        class_names: 클래스 이름 (per-class IoU 표시용).

    Returns:
        list of dict — pandas DataFrame으로 변환 가능한 형식.
    """
    rows = []
    for name, res in results_by_model.items():
        row = {
            "Model": name,
            "mIoU": round(res["mIoU"], 4),
            "Mean Dice": round(res["mean_dice"], 4),
            "Overall Acc": round(res["overall_accuracy"], 4),
        }
        for i, cname in enumerate(class_names):
            row[f"IoU_{cname}"] = round(res["per_class_iou"][i], 4)
        rows.append(row)
    return rows
