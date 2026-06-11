"""project.segmentation.evaluation 단위 테스트."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from project.segmentation.evaluation import (
    compute_confusion_matrix,
    model_ablation_table,
    overall_accuracy,
    per_class_accuracy,
    per_class_dice,
    per_class_iou,
    plot_confusion_matrix,
)


def test_confusion_matrix_perfect_prediction():
    """완벽한 예측 → 대각만 채워짐."""
    target = torch.tensor([[[0, 1], [1, 2]]])  # (1, 2, 2)
    pred = torch.zeros(1, 3, 2, 2)  # logits, one-hot
    # target 픽셀 위치별 logit max 만들기
    pred[0, 0, 0, 0] = 5  # (0,0): class 0
    pred[0, 1, 0, 1] = 5  # (0,1): class 1
    pred[0, 1, 1, 0] = 5  # (1,0): class 1
    pred[0, 2, 1, 1] = 5  # (1,1): class 2
    conf = compute_confusion_matrix(pred, target, num_classes=3)
    assert conf.shape == (3, 3)
    assert conf[0, 0] == 1
    assert conf[1, 1] == 2
    assert conf[2, 2] == 1
    # off-diagonal == 0
    assert conf.sum() - np.diag(conf).sum() == 0


def test_confusion_matrix_all_wrong():
    """모두 0으로 예측한 경우."""
    target = torch.tensor([[[0, 1, 2]]])  # (1, 1, 3)
    pred = torch.zeros(1, 3, 1, 3)
    pred[:, 0, :, :] = 5  # 모두 class 0으로 예측
    conf = compute_confusion_matrix(pred, target, num_classes=3)
    assert conf[0, 0] == 1  # true 0, pred 0
    assert conf[1, 0] == 1  # true 1, pred 0
    assert conf[2, 0] == 1  # true 2, pred 0


def test_per_class_iou_perfect():
    conf = np.eye(3, dtype=np.int64) * 10
    iou = per_class_iou(conf)
    np.testing.assert_allclose(iou, [1.0, 1.0, 1.0], atol=1e-5)


def test_per_class_iou_partial():
    """class 0은 정확, class 1은 5개를 0으로 예측."""
    conf = np.array([
        [10, 0, 0],
        [5, 5, 0],
        [0, 0, 10],
    ])
    iou = per_class_iou(conf)
    # class 0: TP=10, FP=5, FN=0 → IoU = 10 / 15
    assert abs(iou[0] - 10/15) < 1e-5
    # class 1: TP=5, FP=0, FN=5 → IoU = 5 / 10
    assert abs(iou[1] - 0.5) < 1e-5
    # class 2: perfect
    assert abs(iou[2] - 1.0) < 1e-5


def test_per_class_dice():
    conf = np.array([
        [10, 0],
        [5, 5],
    ])
    dice = per_class_dice(conf)
    # class 0: 2*10 / (2*10 + 0 + 5) = 20/25
    assert abs(dice[0] - 20/25) < 1e-5
    # class 1: 2*5 / (2*5 + 5 + 0) = 10/15
    assert abs(dice[1] - 10/15) < 1e-5


def test_overall_accuracy():
    conf = np.array([
        [9, 1],
        [2, 8],
    ])
    acc = overall_accuracy(conf)
    assert abs(acc - 17/20) < 1e-5


def test_per_class_accuracy():
    conf = np.array([
        [9, 1],
        [2, 8],
    ])
    acc = per_class_accuracy(conf)
    assert abs(acc[0] - 0.9) < 1e-5
    assert abs(acc[1] - 0.8) < 1e-5


def test_plot_confusion_matrix(tmp_path):
    plt = pytest.importorskip("matplotlib.pyplot")
    conf = np.array([[10, 1], [2, 8]])
    save = tmp_path / "cm.png"
    fig = plot_confusion_matrix(
        conf, ["bg", "fg"], normalize=True, save_path=str(save),
    )
    assert save.exists()
    plt.close(fig)


def test_ablation_table_format():
    fake = {
        "Baseline": {
            "mIoU": 0.68,
            "mean_dice": 0.78,
            "overall_accuracy": 0.92,
            "per_class_iou": np.array([0.95, 0.60, 0.70]),
        },
        "Attention": {
            "mIoU": 0.683,
            "mean_dice": 0.79,
            "overall_accuracy": 0.93,
            "per_class_iou": np.array([0.96, 0.62, 0.71]),
        },
    }
    rows = model_ablation_table(fake, class_names=["bg", "nose", "eye"])
    assert len(rows) == 2
    assert rows[0]["Model"] == "Baseline"
    assert rows[0]["mIoU"] == 0.68
    assert "IoU_nose" in rows[0]
