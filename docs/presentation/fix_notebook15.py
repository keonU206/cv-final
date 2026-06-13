"""노트북 15 셀 구조 복구.

문제:
- NotebookEdit이 새 셀을 markdown으로 추가함
- 결과: cell #6, #8, #12가 markdown인데 코드 내용 가짐
- 옛 code 셀들 (#5, #7, #11)은 그대로 — 실제 실행되는 코드

해결:
1. 잘못된 markdown 셀들 삭제
2. 옛 code 셀들을 새 코드로 직접 교체
"""
import json
from pathlib import Path

NB_PATH = Path("notebooks/15_confusion_matrix.ipynb")
nb = json.loads(NB_PATH.read_text(encoding="utf-8"))

print(f"수정 전 셀 수: {len(nb['cells'])}")

# ─── 잘못된 markdown 셀들 삭제 (코드 내용 가짐) ───
DELETE_PATTERNS = [
    "from project.segmentation.data import CelebAMaskHQDataset",  # cell #6 (markdown)
    "from project.segmentation.evaluation import evaluate_model_o",  # cell #8 (markdown)
    "from project.segmentation.evaluation import model_ablation_t",  # cell #12 (markdown)
]


def is_bad_markdown(cell):
    if cell["cell_type"] != "markdown":
        return False
    src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
    return any(p in src for p in DELETE_PATTERNS)


# 잘못된 셀 인덱스
bad_indices = [i for i, c in enumerate(nb["cells"]) if is_bad_markdown(c)]
print(f"삭제할 잘못된 markdown 셀: {bad_indices}")

# 역순으로 삭제 (인덱스 변동 방지)
for idx in reversed(bad_indices):
    print(f"  삭제 #{idx}: {nb['cells'][idx]['cell_type']}")
    del nb["cells"][idx]


# ─── 옛 code 셀들을 새 코드로 교체 ───

# 새 코드 1: Validation Dataset (VAL_SUBSET = 500)
NEW_VAL_CODE = """from project.segmentation.data import CelebAMaskHQDataset
from project.segmentation.transforms import get_val_transform
from torch.utils.data import DataLoader

INPUT_SIZE = 256
VAL_SUBSET = 500  # 50 → 500 (10x). 통계적 신뢰성 + mIoU 안정성

# RGB val set (Baseline / Attention용)
val_tf_rgb = get_val_transform(size=INPUT_SIZE, with_heatmap=False)
val_ds_rgb = CelebAMaskHQDataset(
    split='val', transform=val_tf_rgb,
    subset_size=VAL_SUBSET,
    cache_dir='/content/data/celebamask',
    input_size=INPUT_SIZE,
    use_landmark=False,
)
val_dl_rgb = DataLoader(val_ds_rgb, batch_size=8, shuffle=False, num_workers=2)
print(f'RGB val: {len(val_ds_rgb)} (이전 50장 -> 500장)')

# 4채널 val set (LM-guided용) — mediapipe 필요
val_dl_lm = None
try:
    val_tf_lm = get_val_transform(size=INPUT_SIZE, with_heatmap=True)
    val_ds_lm = CelebAMaskHQDataset(
        split='val', transform=val_tf_lm,
        subset_size=VAL_SUBSET,
        cache_dir='/content/data/celebamask',
        input_size=INPUT_SIZE,
        use_landmark=True, landmark_sigma=3.0,
    )
    val_dl_lm = DataLoader(val_ds_lm, batch_size=8, shuffle=False, num_workers=2)
    print(f'LM val: {len(val_ds_lm)}')
except (ImportError, Exception) as e:
    print(f'LM val 생성 실패: {type(e).__name__}: {str(e)[:100]}')
    print('  -> LM-guided 평가 skip')

print(f'\\n예상 평가 시간: 약 9-10분 (T4 GPU, 500장 x 3 모델)')
"""

# 새 코드 2: 모델 평가 (3종 mIoU)
NEW_EVAL_CODE = """from project.segmentation.evaluation import evaluate_model_on_loader

CLASS_NAMES = ['background', 'nose', 'eye', 'mouth', 'skin', 'unused']
NUM_CLASSES = 6

# 의미 있는 클래스만 (background + unused 제외 / unused만 제외)
VALID_CLASS_IDX_5 = [0, 1, 2, 3, 4]  # 5-class (unused 제외)
VALID_CLASS_IDX_4 = [1, 2, 3, 4]      # 4-class (bg + unused 제외)

import numpy as np

results = {}
for name, cfg in MODELS_TO_EVAL.items():
    if not cfg['ckpt'].exists():
        print(f'skip {name} (ckpt 없음)')
        continue

    needs_lm = (cfg['in_channels'] == 4)
    if needs_lm and val_dl_lm is None:
        print(f'skip {name} (LM val 미준비)')
        continue

    print(f'\\n=== {name} 평가 중 ===')
    model = build_unet(
        num_classes=NUM_CLASSES,
        encoder_name='resnet34',
        encoder_weights=None,
        in_channels=cfg['in_channels'],
        attention_type=cfg['attention_type'],
    )
    model.load_state_dict(torch.load(cfg['ckpt'], map_location=device))

    val_dl = val_dl_lm if needs_lm else val_dl_rgb
    res = evaluate_model_on_loader(model, val_dl, NUM_CLASSES, device=device)

    # 추가 계산
    per_class = res['per_class_iou']
    res['mIoU_5class'] = float(np.array(per_class)[VALID_CLASS_IDX_5].mean())
    res['mIoU_4class'] = float(np.array(per_class)[VALID_CLASS_IDX_4].mean())

    results[name] = res

    print(f'  -- 종합 mIoU --')
    print(f'  6-class (전체):                      {res[\"mIoU\"]:.4f}')
    print(f'  5-class (unused 제외, 공식 보고용):  {res[\"mIoU_5class\"]:.4f}  *')
    print(f'  4-class (얼굴 부위만):               {res[\"mIoU_4class\"]:.4f}')
    print(f'  Mean Dice (6-class):                {res[\"mean_dice\"]:.4f}')
    print(f'  Overall Acc:                        {res[\"overall_accuracy\"]:.4f}')
    print(f'\\n  -- Per-class IoU --')
    for i, cname in enumerate(CLASS_NAMES):
        marker = '*' if i in [1, 2, 3] else ''
        print(f'    {cname:<12}: {res[\"per_class_iou\"][i]:.4f} {marker}')

print(f'\\n=== 평가 완료: {len(results)}개 모델 ===')
print(f'발표 보고용 권장: 5-class mIoU (unused 제외)')
"""

# 새 코드 3: Ablation 표 (mIoU 3종 컬럼)
NEW_ABLATION_CODE = """from project.segmentation.evaluation import model_ablation_table
import pandas as pd

# 기본 표
table_rows = model_ablation_table(results, CLASS_NAMES)

# 5-class, 4-class mIoU 컬럼 추가
for row, (name, res) in zip(table_rows, results.items()):
    row['mIoU_5class'] = round(res['mIoU_5class'], 4)
    row['mIoU_4class'] = round(res['mIoU_4class'], 4)

df = pd.DataFrame(table_rows)
mIoU_cols = ['Model', 'mIoU', 'mIoU_5class', 'mIoU_4class', 'Mean Dice', 'Overall Acc']
per_class_cols = [c for c in df.columns if c.startswith('IoU_')]
df = df[mIoU_cols + per_class_cols]

print('=== Model Ablation Table (mIoU 3종 + Per-class) ===')
print('mIoU 종류:')
print('  - mIoU        : 6-class 평균 (전체)')
print('  - mIoU_5class : 5-class 평균 (unused 제외, 공식 보고용 *)')
print('  - mIoU_4class : 4-class 평균 (얼굴 부위만)')
print()
print(df.to_string(index=False))

df.to_csv(OUTPUT_DIR / 'ablation_table.csv', index=False)
print(f'\\n저장: {OUTPUT_DIR / \"ablation_table.csv\"}')
df
"""

# 코드 교체 매핑 (첫줄 prefix로 찾기)
REPLACE_MAP = {
    "from project.segmentation.data import CelebAMaskHQDataset": NEW_VAL_CODE,
    "from project.segmentation.evaluation import evaluate_model_on_loader": NEW_EVAL_CODE,
    "from project.segmentation.evaluation import model_ablation_table": NEW_ABLATION_CODE,
}

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
    for prefix, new_src in REPLACE_MAP.items():
        if src.startswith(prefix):
            cell["source"] = new_src
            print(f"코드 교체: {prefix[:60]}...")
            break

print(f"\n수정 후 셀 수: {len(nb['cells'])}")
NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"저장: {NB_PATH}")
