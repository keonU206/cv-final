# Plan — U-Net 세그멘테이션 구현 (Week 2)

> 작성일: 2026-05-18
> 작성자: kim
> 기반 문서: [research_unet.md](research_unet.md), [plan_kim_0515_02.md](plan_kim_0515_02.md)
> 범위: **Week 2 (5/19~5/26) 구현 계획**
> ⚠️ 이 plan은 **검토 전 v0.1**. 구현 시작은 사용자 메모 → v0.2 → 최종 승인 후.

---

## 0. 확정 결정 (research_unet.md 후)

| 항목 | 결정 |
|------|------|
| 클래스 매핑 | **전략 A (5 학습 클래스 + 후처리)** — bg/nose/eye/mouth/skin |
| 데이터셋 | **`limsanky/celebamask-hq-256` (Hugging Face)** — 1.42GB, 256² |
| 학습 라이브러리 | `segmentation_models_pytorch` (PyTorch) |
| 인코더 | ResNet-34 + ImageNet 사전학습 |
| Loss | Combo: `0.5 * DiceLoss + 0.5 * CrossEntropyLoss` |
| 입력 크기 | 256×256 |
| 배치 크기 | 16 |
| Optimizer | Adam, lr=1e-4, weight_decay=1e-5 |
| Scheduler | CosineAnnealingLR |
| PoC epochs | 1 (5K subset) — Week 2 마감용 |
| 본 학습 epochs | 10 (24K full) — Week 3 |
| Augmentation | albumentations: flip + rotate ±15 + brightness/contrast |
| Grad-CAM | `pytorch-grad-cam`, hook on `model.encoder.layer4[-1]` |
| 환경 | Colab T4 GPU |

---

## 1. 디렉터리 구조 (확정)

```
project/segmentation/
├── __init__.py
├── config.yaml              # 하이퍼파라미터 (단일 진실 출처)
├── data.py                  # CelebAMaskHQ Dataset 클래스
├── transforms.py            # albumentations 파이프라인
├── label_map.py             # 19 → 5 클래스 remapping 로직
├── unet.py                  # smp.Unet 래퍼
├── losses.py                # ComboLoss
├── metrics.py               # mIoU, Dice, Confusion Matrix
├── train.py                 # 학습 루프 (Python 스크립트)
├── inference.py             # 추론 함수 (model + postprocess 통합)
├── postprocess.py           # skin → jaw/forehead (MediaPipe 랜드마크 활용)
├── gradcam.py               # SemanticSegmentationTarget 시각화
└── checkpoints/             # 학습된 가중치 (gitignore)
    └── unet_v1.pt

notebooks/
└── 03_unet_train.ipynb      # Colab에서 train.py 실행 + 결과 시각화
```

> 13개 파일이지만 각 50~100줄 정도라 부담 없음.
> `gradcam.py`는 Week 3로 미뤄도 OK (PoC에 불필요).

---

## 2. 모듈별 상세 설계

### 2.1 `config.yaml` (단일 진실 출처)

```yaml
# 데이터
dataset:
  name: limsanky/celebamask-hq-256
  cache_dir: /content/data/celebamask
  subset_size: 5000          # PoC: 5K, 본 학습: 24000

# 클래스 매핑
classes:
  num_classes: 6             # bg + 5 (skin은 후처리에서 분리)
  names: [background, nose, eye, mouth, skin, unused]

# 학습
train:
  input_size: 256
  batch_size: 16
  epochs: 1                  # PoC. 본 학습 시 10
  lr: 1.0e-4
  weight_decay: 1.0e-5
  optimizer: adam
  scheduler: cosine

# Loss
loss:
  dice_weight: 0.5
  ce_weight: 0.5

# Augmentation
augmentation:
  horizontal_flip: 0.5
  rotation_deg: 15
  brightness_contrast: 0.3
  gaussian_blur: 0.2

# Output
checkpoint_dir: project/segmentation/checkpoints
log_interval: 50             # 50 step마다 loss 출력
```

### 2.2 `label_map.py` — 19 → 5 클래스 매핑

```python
"""CelebAMask-HQ 19 클래스 → 우리 5 학습 클래스 매핑."""

# CelebAMask-HQ 원본 인덱스 (0=bg, 1=skin, ..., 18=cloth)
ORIGINAL_LABELS = {
    'background': 0, 'skin': 1, 'nose': 2, 'eye_g': 3,
    'l_eye': 4, 'r_eye': 5, 'l_brow': 6, 'r_brow': 7,
    'l_ear': 8, 'r_ear': 9, 'mouth': 10, 'u_lip': 11,
    'l_lip': 12, 'hair': 13, 'hat': 14, 'ear_r': 15,
    'neck_l': 16, 'neck': 17, 'cloth': 18,
}

# 우리 학습 클래스 (5개 + bg)
OURS = {
    'background': 0, 'nose': 1, 'eye': 2,
    'mouth': 3, 'skin': 4,
}

# 매핑 테이블 (19 → 6)
MAPPING = {
    0: 0,   # bg → bg
    1: 4,   # skin → skin
    2: 1,   # nose → nose
    3: 0,   # eye_g (안경) → bg
    4: 2,   # l_eye → eye
    5: 2,   # r_eye → eye
    6: 2,   # l_brow → eye (눈썹은 눈 영역에 합침)
    7: 2,   # r_brow → eye
    8: 0,   # l_ear → bg
    9: 0,   # r_ear → bg
    10: 3,  # mouth → mouth
    11: 3,  # u_lip → mouth
    12: 3,  # l_lip → mouth
    13: 0,  # hair → bg
    14: 0,  # hat → bg
    15: 0,  # ear_r → bg
    16: 0,  # neck_l → bg
    17: 0,  # neck → bg
    18: 0,  # cloth → bg
}

def remap(label_19: np.ndarray) -> np.ndarray:
    """19 클래스 라벨맵 → 5 클래스(+bg) 라벨맵."""
    result = np.zeros_like(label_19)
    for src, dst in MAPPING.items():
        result[label_19 == src] = dst
    return result
```

### 2.3 `data.py` — Dataset 클래스

```python
class CelebAMaskHQDataset(Dataset):
    """CelebAMask-HQ Hugging Face dataset 래퍼 + 19→5 remapping."""

    def __init__(self, split: str, transform=None, subset_size=None):
        """
        Args:
            split: 'train' / 'val' / 'test'
            transform: albumentations.Compose
            subset_size: None이면 전체, 정수면 그만큼만 사용
        """
        self.ds = load_dataset("limsanky/celebamask-hq-256", split=split)
        if subset_size:
            self.ds = self.ds.select(range(subset_size))
        self.transform = transform

    def __getitem__(self, idx):
        item = self.ds[idx]
        image = np.array(item['image'])         # (256, 256, 3) uint8
        mask_19 = np.array(item['mask'])        # (256, 256) uint8, 0~18
        mask_5 = remap(mask_19)                 # (256, 256) uint8, 0~4

        if self.transform:
            t = self.transform(image=image, mask=mask_5)
            image, mask_5 = t['image'], t['mask']

        return image, mask_5.long()

    def __len__(self):
        return len(self.ds)
```

> ⚠️ HF 데이터셋 정확한 컬럼 이름 (`image`, `mask`) 확인 필요 (Week 2 첫날 검증).

### 2.4 `transforms.py` — albumentations 파이프라인

```python
def get_train_transform(size=256):
    return A.Compose([
        A.Resize(size, size),
        A.HorizontalFlip(p=0.5),
        A.Affine(rotate=(-15, 15), p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.GaussianBlur(blur_limit=(3, 5), p=0.2),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])

def get_val_transform(size=256):
    return A.Compose([
        A.Resize(size, size),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])
```

### 2.5 `unet.py` — 모델

```python
def build_unet(num_classes=6, encoder='resnet34') -> nn.Module:
    return smp.Unet(
        encoder_name=encoder,
        encoder_weights='imagenet',
        in_channels=3,
        classes=num_classes,
    )
```

### 2.6 `losses.py` — Combo Loss

```python
class ComboLoss(nn.Module):
    def __init__(self, dice_weight=0.5, ce_weight=0.5):
        super().__init__()
        self.dice = smp.losses.DiceLoss(mode='multiclass', from_logits=True)
        self.ce = nn.CrossEntropyLoss()
        self.dw, self.cw = dice_weight, ce_weight

    def forward(self, pred, target):
        return self.dw * self.dice(pred, target) + self.cw * self.ce(pred, target)
```

### 2.7 `metrics.py` — IoU, Dice, Confusion Matrix

```python
def compute_metrics(pred_logits, target, num_classes=6):
    """
    Args:
        pred_logits: (B, C, H, W)
        target: (B, H, W) long

    Returns dict: {miou, dice, per_class_iou, confusion_matrix}
    """
    pred = pred_logits.argmax(dim=1)
    tp, fp, fn, tn = smp.metrics.get_stats(
        pred, target, mode='multiclass', num_classes=num_classes
    )
    iou = smp.metrics.iou_score(tp, fp, fn, tn, reduction='none')
    dice = smp.metrics.f1_score(tp, fp, fn, tn, reduction='none')
    # confusion matrix는 sklearn 사용
    cm = confusion_matrix(target.flatten().cpu(), pred.flatten().cpu(),
                          labels=list(range(num_classes)))
    return {
        'miou': iou[1:].mean().item(),    # bg 제외
        'dice': dice[1:].mean().item(),
        'per_class_iou': iou.tolist(),
        'confusion_matrix': cm,
    }
```

### 2.8 `train.py` — 학습 루프

```python
def train(config_path='project/segmentation/config.yaml'):
    cfg = yaml.safe_load(open(config_path))

    # data
    train_ds = CelebAMaskHQDataset('train', get_train_transform(),
                                   subset_size=cfg['dataset']['subset_size'])
    val_ds = CelebAMaskHQDataset('validation', get_val_transform())
    train_dl = DataLoader(train_ds, batch_size=cfg['train']['batch_size'],
                          shuffle=True, num_workers=2)
    val_dl = DataLoader(val_ds, batch_size=cfg['train']['batch_size'],
                        num_workers=2)

    # model + loss + optimizer
    model = build_unet(num_classes=cfg['classes']['num_classes']).cuda()
    loss_fn = ComboLoss(cfg['loss']['dice_weight'], cfg['loss']['ce_weight'])
    optim = torch.optim.Adam(model.parameters(), lr=cfg['train']['lr'],
                             weight_decay=cfg['train']['weight_decay'])
    sched = CosineAnnealingLR(optim, T_max=cfg['train']['epochs'])

    # train loop
    for ep in range(cfg['train']['epochs']):
        model.train()
        for step, (img, mask) in enumerate(train_dl):
            img, mask = img.cuda(), mask.cuda()
            pred = model(img)
            loss = loss_fn(pred, mask)
            optim.zero_grad(); loss.backward(); optim.step()
            if step % cfg['log_interval'] == 0:
                print(f'epoch {ep} step {step} loss {loss.item():.4f}')

        # val
        model.eval()
        val_metrics = evaluate(model, val_dl)
        print(f'epoch {ep} val: {val_metrics}')

        sched.step()

        # save
        torch.save(model.state_dict(),
                   f'{cfg["checkpoint_dir"]}/unet_ep{ep}.pt')
```

### 2.9 `postprocess.py` — skin → jaw/forehead

```python
def split_skin_by_landmarks(skin_mask, landmarks):
    """
    skin 픽셀 영역을 MediaPipe 랜드마크로 jaw/forehead로 분리.

    Args:
        skin_mask: (H, W) uint8 binary, U-Net 출력의 skin 클래스
        landmarks: (478, 2) MediaPipe 출력

    Returns:
        jaw_mask: (H, W) uint8 — 입술 아래 영역
        forehead_mask: (H, W) uint8 — 눈썹 위 영역
    """
    chin_y = landmarks[152, 1]       # 턱 끝
    lip_bottom_y = landmarks[14, 1]  # 아랫입술
    brow_top_y = min(landmarks[55, 1], landmarks[285, 1])  # 눈썹 위
    forehead_top_y = landmarks[10, 1]                       # 이마 top

    jaw_mask = skin_mask.copy()
    jaw_mask[:lip_bottom_y, :] = 0   # 입술 아래만 남김

    forehead_mask = skin_mask.copy()
    forehead_mask[brow_top_y:, :] = 0  # 눈썹 위만 남김

    return jaw_mask, forehead_mask
```

### 2.10 `inference.py` — 통합 추론

```python
def predict(image_bgr, model, landmarks):
    """E2E: 이미지 + 랜드마크 → 6개 부위 마스크 dict."""
    # preprocess
    transform = get_val_transform()
    img = transform(image=image_bgr)['image'].unsqueeze(0).cuda()

    # U-Net
    with torch.no_grad():
        logits = model(img)
        pred = logits.argmax(dim=1).squeeze(0).cpu().numpy()  # (H, W)

    # extract per-class masks
    masks = {}
    for i, name in enumerate(['background', 'nose', 'eye', 'mouth', 'skin']):
        masks[name] = (pred == i).astype(np.uint8) * 255

    # split skin → jaw + forehead
    jaw, forehead = split_skin_by_landmarks(masks['skin'], landmarks)
    masks['jaw'] = jaw
    masks['forehead'] = forehead

    return masks  # dict of {name: (H, W) uint8}
```

### 2.11 `gradcam.py` — Week 3 (PoC 단계엔 skip)

```python
def visualize_class_cam(model, image_tensor, class_idx):
    """Grad-CAM for class — returns RGB heatmap overlay."""
    target_layers = [model.encoder.layer4[-1]]
    cam = GradCAM(model=model, target_layers=target_layers)

    output = model(image_tensor)
    mask = (output.argmax(dim=1) == class_idx).float()
    targets = [SemanticSegmentationTarget(category=class_idx, mask=mask)]

    grayscale_cam = cam(input_tensor=image_tensor, targets=targets)
    return grayscale_cam[0]
```

---

## 3. `notebooks/03_unet_train.ipynb` 구성 (Colab)

```
1. (markdown) 제목 + 목표
2. (code) GPU 확인 + 의존성 설치
   !pip install segmentation-models-pytorch albumentations datasets pytorch-grad-cam
3. (code) Drive 마운트 + 경로 설정
4. (code) sys.path 추가 (project/segmentation import)
5. (code) HF datasets로 CelebAMask 다운로드 (캐시)
6. (code) Dataset 동작 확인 (1배치 시각화)
7. (markdown) 학습
8. (code) train(config_path) 호출 → PoC 1 epoch
9. (code) loss curve 시각화
10. (code) val mIoU/Dice 출력
11. (markdown) 결과 시각화
12. (code) 샘플 5장에 대한 예측 mask overlay
```

---

## 4. Week 2 일정 (5/19~5/26)

| 날짜 | 담당 | 작업 | DoD |
|------|------|------|-----|
| **5/19 (월)** | B | HF 데이터셋 다운로드 + Dataset 클래스 검증 (`data.py`) | 1배치 시각화 |
| 5/19 | B | `label_map.py` + remapping 단위 테스트 | 19→5 매핑 OK |
| 5/20 (화) | B | `transforms.py` + `unet.py` 작성 | 모델 forward 1배치 통과 |
| 5/21 (수) | B | `losses.py` + `metrics.py` | 단위 테스트 통과 |
| 5/22 (목) | B | `train.py` 작성 + 1 step 학습 검증 | loss 출력 OK |
| 5/23 (금) | B | **PoC 1 epoch on 5K subset** (Colab T4) | val mIoU > 0 |
| 5/24 (토) | B | 결과 시각화 + checkpoint 저장 | unet_v1.pt |
| 5/25 (일) | All | 통합 회의 + 결과 검토 | Week 2 종료 |
| 5/26 (월) | All | Week 3 계획 확정 | plan v3 (필요시) |

> 병행: A는 SC-FEGAN wrapper 클래스화, C는 Streamlit 골격 (별도 진행).

---

## 5. 평가 기준 매핑 (어떤 작업이 어떤 점수에 기여)

| 작업 | 평가 항목 | 점수 기여 |
|------|----------|----------|
| `data.py` + label_map | 데이터 타당성 (30%) | 우리 task에 맞게 클래스 재구성 |
| `unet.py` + Combo loss | 모델 설계 (40%) | smp 라이브러리 + 자체 loss 결정 |
| `metrics.py` | 성능 분석 (15%) | mIoU/Dice/Confusion Matrix |
| Augmentation ablation (Week 3) | 성능 분석 (15%) | aug 있을 때 vs 없을 때 mIoU 비교 |
| `gradcam.py` (Week 3) | 시각화/해석 (15%) | "왜 이 부분을 nose로?" 시각화 |
| `postprocess.py` | 시각화 (15%) | jaw/forehead 분리 시각화 |

---

## 6. 리스크 + 대응

| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| HF 데이터셋 컬럼 이름 다름 | MED | Week 2 첫날 `print(ds[0].keys())` 검증 |
| 256² 학습이 너무 빨라 underfit | LOW | epochs 늘리거나 lr 낮춤 |
| skin 클래스가 너무 커서 다른 클래스 미학습 | MED | Focal Loss 시도 또는 class weight |
| GPU 메모리 부족 | LOW | batch 16 → 8 또는 input 256 → 128 |
| 5/23 PoC 결과 mIoU < 0.5 | MED | 학습 더 돌림, lr 조정, 또는 augmentation 축소 |
| jaw/forehead 분리가 부정확 | HIGH | 후처리 파라미터(랜드마크 인덱스) 조정 |

---

## 7. 단위 테스트 계획

| 테스트 | 파일 | 검증 |
|--------|------|------|
| `test_label_map.py` | label_map | MAPPING 완전성 (0~18 모두 매핑) |
| `test_data.py` | data | Dataset 1 sample 반환 shape 확인 |
| `test_transforms.py` | transforms | image/mask 동시 변환 OK |
| `test_unet.py` | unet | (B, 3, 256, 256) → (B, 6, 256, 256) |
| `test_losses.py` | losses | Combo loss 계산 결과 finite |
| `test_metrics.py` | metrics | mIoU ∈ [0, 1] |
| `test_postprocess.py` | postprocess | skin → jaw + forehead, 합쳐서 원래 skin 영역 |

---

## 8. 체크리스트 (구현 시작 후 사용)

### 환경
- [ ] Colab T4 런타임 + Drive 마운트 OK
- [ ] `pip install segmentation-models-pytorch albumentations datasets pytorch-grad-cam` 완료

### 코드 작성
- [ ] `config.yaml` 작성
- [ ] `label_map.py` + 단위 테스트
- [ ] `data.py` + 1배치 시각화 검증
- [ ] `transforms.py`
- [ ] `unet.py`
- [ ] `losses.py`
- [ ] `metrics.py`
- [ ] `train.py` (1 step 검증)
- [ ] `postprocess.py`
- [ ] `inference.py`
- [ ] `__init__.py` 작성 (lazy import)

### 노트북
- [ ] `notebooks/03_unet_train.ipynb` 작성
- [ ] PoC 1 epoch 학습 성공
- [ ] val mIoU 출력 > 0
- [ ] 샘플 예측 시각화 5장

### 검증
- [ ] 모든 단위 테스트 통과
- [ ] Week 2 결과 캡처 (loss curve + 예측 1장)
- [ ] checkpoint `unet_v1.pt` Drive에 저장

---

## 9. plan v0.1 → v0.2 → 구현 흐름

1. **(현재) plan v0.1** — 너 검토
2. 사용자 메모/주석 → "메모 반영해서 업데이트, **아직 구현하지 마**"
3. plan v0.2 작성
4. v0.2 최종 승인 → "plan대로 구현 시작"
5. 5/19~5/24 구현 (위 일정대로)
6. Week 2 결과 리뷰 → Week 3 plan (별도 작성)

---

## 부록 — 한 줄 명령어 모음

```bash
# 의존성 설치 (Colab)
!pip install -q segmentation-models-pytorch albumentations datasets pytorch-grad-cam

# 데이터셋 다운로드 (HF)
from datasets import load_dataset
ds = load_dataset("limsanky/celebamask-hq-256")

# 학습 (Python 스크립트)
python -m project.segmentation.train

# 단위 테스트
pytest project/tests/test_segmentation*.py -v
```

---

*plan v0.1 끝. 검토 후 피드백 줘. 구현은 v0.2 확정 후.*
