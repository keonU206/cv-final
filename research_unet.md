# Research — U-Net 세그멘테이션 (Week 2)

> 작성일: 2026-05-18
> 작성자: kim
> 기반 문서: [plan_kim_0515_02.md](plan_kim_0515_02.md), [HANDOVER.md](docs/presentation/HANDOVER.md)
> 목적: Week 2 U-Net 학습 모듈 구현을 위한 사전 조사

---

## 0. TL;DR — 의사결정에 영향을 주는 핵심 사실

1. **CelebAMask-HQ는 부위별 PNG 마스크 파일 분리 저장** — `00000_skin.png`, `00000_nose.png` 식. 학습 전에 **단일 라벨맵으로 통합 필요** (저자 제공 `g_mask.py` 스크립트 활용).
2. **"턱"과 "이마" 라벨은 데이터셋에 없음** → `skin` 라벨에 포함되어 있음. **2가지 전략** 검토 (§5).
3. **`segmentation_models_pytorch`로 U-Net 정의는 3줄 끝** — 아키텍처 직접 구현 안 함.
4. **추천 Loss**: Dice + CrossEntropy Combo (α=β=0.5). class imbalance 대응.
5. **T4 GPU 학습 시간**: 256×256, batch 16, 5K subset → 1 epoch ~1분. 10 epoch on 24K full → ~50분.
6. **Hugging Face 미러 활용 권장** — `limsanky/celebamask-hq-256` (1.42GB, 이미 256 리사이즈됨).
7. **Grad-CAM은 `pytorch-grad-cam`** + `SemanticSegmentationTarget` 클래스 사용.

---

## 1. CelebAMask-HQ 데이터셋 상세

### 1.1 구조

```
CelebAMask-HQ/
├── CelebA-HQ-img/               # 30,000장 원본 (1024×1024 JPG)
│   ├── 0.jpg, 1.jpg, ..., 29999.jpg
├── CelebAMask-HQ-mask-anno/     # 마스크 (서브폴더 15개)
│   ├── 0/                       # 0~1999 이미지 마스크
│   │   ├── 00000_skin.png       # 512×512, 단일 채널 binary mask
│   │   ├── 00000_nose.png
│   │   ├── 00000_l_eye.png
│   │   └── ... (각 클래스별 PNG)
│   ├── 1/                       # 2000~3999
│   └── ... 14/
├── CelebA-HQ-to-CelebA-mapping.txt
└── face_parsing/                # 저자 제공 전처리/학습 코드
    ├── Data_preprocessing/g_mask.py   # ← 핵심 전처리 스크립트
    └── README.md
```

### 1.2 클래스 라벨 (인덱스 0–18)

| idx | label | idx | label | idx | label |
|-----|-------|-----|-------|-----|-------|
| 0 | background | 7 | r_brow | 14 | hat |
| 1 | skin | 8 | l_ear | 15 | ear_r (귀걸이) |
| 2 | nose | 9 | r_ear | 16 | neck_l (목걸이) |
| 3 | eye_g (안경) | 10 | mouth | 17 | neck |
| 4 | l_eye | 11 | u_lip (윗입술) | 18 | cloth |
| 5 | r_eye | 12 | l_lip (아랫입술) | | |
| 6 | l_brow | 13 | hair | | |

### 1.3 다운로드 옵션 (가장 빠른 순)

| 출처 | 크기 | 비고 |
|------|------|------|
| 🥇 **Hugging Face `limsanky/celebamask-hq-256`** | 1.42GB | **이미 256 리사이즈** → 학습용 권장 |
| 🥈 Hugging Face `liusq/CelebAMask-HQ` | ~30GB | 원본 1024×1024 (전체) |
| Kaggle `ipythonx/celebamaskhq` | ~30GB | Kaggle API로 다운로드 |
| 공식 Google Drive (저자) | ~30GB | 종종 quota 초과 발생 |
| 공식 Baidu Drive | ~30GB | 중국 외 접근 느림 |

→ **추천**: Hugging Face Datasets API로 `limsanky/celebamask-hq-256` 사용. Colab 30GB 디스크에 여유.

```python
from datasets import load_dataset
ds = load_dataset("limsanky/celebamask-hq-256")
```

### 1.4 전처리: 19 PNG → 단일 라벨맵 (`g_mask.py`)

저자가 제공하는 스크립트. 동작:
1. 빈 512×512 zeros 배열 생성
2. 18개 클래스 PNG를 순회하며 non-zero 픽셀에 클래스 인덱스 할당
3. 단일 채널 PNG로 저장 (픽셀값 0~18)

→ 이걸 데이터로더에 그대로 쓰지 않고, **우리 6 클래스로 remapping** 필요 (§5).

---

## 2. segmentation_models_pytorch (smp) 사용법

### 2.1 설치

```bash
pip install segmentation-models-pytorch
```

### 2.2 모델 정의 — **3줄 끝**

```python
import segmentation_models_pytorch as smp

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights="imagenet",
    in_channels=3,
    classes=6,           # background + 5 시술 부위
)
```

지원 인코더: ResNet (18/34/50), EfficientNet (b0-b7), MobileNet, VGG, DenseNet 등 500+.

### 2.3 입력 전처리

```python
preprocess = smp.encoders.get_preprocessing_fn('resnet34', pretrained='imagenet')
# preprocess(image)는 ImageNet 통계(mean/std)로 정규화함
```

### 2.4 Loss (smp 내장)

```python
loss_dice = smp.losses.DiceLoss(mode='multiclass', from_logits=True)
loss_ce = torch.nn.CrossEntropyLoss()
def combo_loss(pred, target):
    return 0.5 * loss_dice(pred, target) + 0.5 * loss_ce(pred, target)
```

### 2.5 모델 출력 형태

`model(image)` → `(B, C, H, W)` logits. `argmax(dim=1)` → `(B, H, W)` 픽셀별 클래스.

---

## 3. 학습 best practice

### 3.1 추천 하이퍼파라미터

| 파라미터 | 값 | 근거 |
|---------|---|------|
| Input size | 256×256 | 학습 속도 ↑, T4 메모리 여유 (512는 ~5x 느림) |
| Batch size | 16 | T4 16GB 메모리에 적정 (resnet-34 기준) |
| Optimizer | Adam | smp/U-Net 표준 |
| Learning rate | 1e-4 | smp 권장 |
| Scheduler | CosineAnnealingLR 또는 ReduceLROnPlateau | val mIoU 정체 시 lr 감소 |
| Epochs | 10–15 | 5K subset이면 5 epoch도 충분 |
| Weight decay | 1e-5 | 약한 L2 정규화 |

### 3.2 추천 Loss — Combo Loss (Dice + CE)

```python
# 0.5 * Dice + 0.5 * CrossEntropy
# - Dice: class imbalance 보정 (배경이 많은 경우)
# - CE: gradient smoothing (Dice 단독은 초기 불안정)
```

대안: Focal Loss (극단 class imbalance 시), Tversky Loss (precision/recall trade-off).

### 3.3 Augmentation (albumentations)

```python
import albumentations as A
import albumentations.pytorch as Apt

train_transform = A.Compose([
    A.Resize(256, 256),
    A.HorizontalFlip(p=0.5),                # ⚠️ §3.4 주의
    A.Affine(rotate=(-15, 15), p=0.5),
    A.RandomBrightnessContrast(p=0.3),
    A.GaussianBlur(blur_limit=(3, 5), p=0.2),
    A.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]),
    Apt.ToTensorV2()
])

val_transform = A.Compose([
    A.Resize(256, 256),
    A.Normalize(...),
    Apt.ToTensorV2()
])
```

### 3.4 HorizontalFlip 주의 — 얼굴 부위 좌/우 매핑

`l_eye` ↔ `r_eye` 같은 좌/우 라벨이 있는 데이터셋은 flip 시 라벨도 교환되어야 함.

→ **우리 6 클래스 매핑(§5)에서 l_eye와 r_eye를 하나의 `eye` 클래스로 통합 권장**.
→ 이러면 flip 무관 — 단순 horizontal flip 가능.

### 3.5 검증 지표 (학습 중 측정)

```python
# metrics.py
from torchmetrics.segmentation import MeanIoU, DiceScore

miou = MeanIoU(num_classes=6, include_background=False)
dice = DiceScore(num_classes=6, average='macro')

# 또는 smp 내장
import segmentation_models_pytorch as smp
# tp, fp, fn, tn = smp.metrics.get_stats(pred, target, mode='multiclass', num_classes=6)
# iou = smp.metrics.iou_score(tp, fp, fn, tn, reduction='macro')
```

---

## 4. T4 GPU 학습 시간 추정

| 시나리오 | 데이터 | 입력 | 배치 | 1 epoch | 10 epoch 전체 |
|---------|--------|------|------|---------|--------------|
| **PoC (Week 2 발표용)** | 5K subset | 256² | 16 | ~1분 | ~10분 |
| **본 학습 (Week 3)** | 24K full | 256² | 16 | ~5분 | ~50분 |
| 풀 해상도 (선택) | 24K full | 512² | 8 | ~20분 | ~3.5시간 |

> 추정 근거: ResNet-34 + U-Net 256² 입력 = ~약 22M 파라미터, T4 (16GB VRAM) 기준 약 30 img/sec 학습 처리량.

**전략**:
- Week 2: PoC 1 epoch on 5K → 슬라이드용 증명 (loss 감소 확인)
- Week 3: 10 epoch on 24K full → 본 학습 (점심 시간에 돌리기 좋음)
- Week 4: 결과 확정 후 ablation 1~2 epoch씩

---

## 5. 클래스 매핑 — 핵심 결정사항

### 5.1 우리 task의 5 시술 부위

코, 눈, 입, **턱**, **이마**. 그런데 턱/이마는 CelebAMask-HQ에 직접 라벨 없음 (`skin`에 포함).

### 5.2 전략 A — **5 클래스 학습 + 후처리** ⭐ 권장

학습은 데이터셋에 있는 라벨만 사용 → 후처리에서 MediaPipe 랜드마크로 turn/이마 분리.

**6 클래스 (학습 단계)**:
| idx | 우리 클래스 | CelebAMask-HQ 라벨 |
|-----|-----------|--------------------|
| 0 | background | bg, hair, hat, cloth, ear_r, neck_l, neck, l_ear, r_ear, eye_g |
| 1 | nose | nose |
| 2 | eye | l_eye, r_eye, l_brow, r_brow |
| 3 | mouth | mouth, u_lip, l_lip |
| 4 | skin | skin |
| 5 | (사용 안 함, 비워둠) | — |

**후처리 (추론 단계)**:
- skin 영역 + MediaPipe 랜드마크 → 턱 (chin landmark 152 아래) / 이마 (forehead landmark 10 위) 분리
- 시술별 마스크 = (해당 클래스 픽셀) ∩ (랜드마크 convex hull)

**장점**:
- 학습 데이터 깨끗 (가짜 라벨 안 만듦)
- skin 클래스가 크니까 IoU 안정적
- 발표 시 "데이터셋 라벨을 그대로 활용" 명분

**단점**:
- 추론 파이프라인이 약간 복잡 (mask + landmark 결합)

### 5.3 전략 B — 6 클래스 학습 (skin을 jaw/forehead로 강제 분리)

CelebAMask-HQ의 skin 마스크를 학습 시 자동으로 jaw/forehead로 분할 (landmark로 yi).

**6 클래스**:
| idx | 우리 클래스 |
|-----|-----------|
| 0 | background |
| 1 | nose |
| 2 | eye |
| 3 | mouth |
| 4 | jaw (skin 하단, 입술 아래) |
| 5 | forehead (skin 상단, 눈썹 위) |

**장점**: 추론 단순 (mask 그대로 사용)
**단점**: 라벨이 자동 생성이라 noisy. 학습 어려움.

### 5.4 결정 → **전략 A** 권장

이유:
- 학습 데이터 신뢰성 우선
- 후처리는 우리가 이미 가진 MediaPipe로 가능
- Grad-CAM에서 "skin이 어디인가"가 명확

---

## 6. Grad-CAM for U-Net

### 6.1 라이브러리

```bash
pip install grad-cam
```

### 6.2 SemanticSegmentationTarget 사용

```python
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import SemanticSegmentationTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

# 1. Hook할 레이어: U-Net encoder의 가장 깊은 layer (bottleneck 직전)
# smp.Unet의 경우 model.encoder.layer4 (ResNet-34 기준)
target_layers = [model.encoder.layer4[-1]]

cam = GradCAM(model=model, target_layers=target_layers)

# 2. 특정 클래스(예: nose=1)에 대한 CAM
nose_mask = (output.argmax(dim=1) == 1).float()
targets = [SemanticSegmentationTarget(category=1, mask=nose_mask)]

grayscale_cam = cam(input_tensor=image, targets=targets)
visualization = show_cam_on_image(image_np, grayscale_cam[0])
```

### 6.3 발표용 시각화 5장

코, 눈, 입, 턱(skin), 이마(skin) — 각 클래스에 대한 CAM heatmap.

> "왜 U-Net이 이 영역을 코로 판단했는지" — 결과 슬라이드의 핵심 임팩트.

---

## 7. 권장 디렉터리 구조 (plan v2 + 본 research 반영)

```
project/segmentation/
├── __init__.py
├── config.yaml                # 하이퍼파라미터 (lr, epoch, batch, etc.)
├── data.py                    # CelebAMaskHQ Dataset + DataLoader
├── transforms.py              # albumentations 파이프라인
├── unet.py                    # smp.Unet 래퍼 (3줄)
├── losses.py                  # ComboLoss = 0.5*Dice + 0.5*CE
├── metrics.py                 # mIoU, Dice, Confusion Matrix
├── train.py                   # 학습 루프 (PyTorch native)
├── inference.py               # 추론 함수 (model + remap)
├── gradcam.py                 # SemanticSegmentationTarget 시각화
├── postprocess.py             # MediaPipe landmark로 skin→jaw/forehead
└── checkpoints/
    └── unet_v1.pt
```

---

## 8. 5단계 워크플로우 다음 단계

1. **(현재) Research** ✅ — 본 문서
2. **Plan** — `plan_kim_0518_01.md` 작성 (다음 단계)
3. **Review** — 사용자 메모
4. **Implement** — 위 디렉터리 구조대로 코드 작성
5. **Refine** — PoC 결과 보고 조정

---

## 부록 A — 참고 자료

### 데이터셋
- [CelebAMask-HQ GitHub (공식)](https://github.com/switchablenorms/CelebAMask-HQ)
- [`limsanky/celebamask-hq-256` (HF Datasets)](https://huggingface.co/datasets/limsanky/celebamask-hq-256)
- [Dataset Ninja 페이지](https://datasetninja.com/celebamask-hq)
- [g_mask.py 전처리 스크립트](https://github.com/switchablenorms/CelebAMask-HQ/blob/master/face_parsing/Data_preprocessing/g_mask.py)

### 라이브러리
- [segmentation_models.pytorch](https://github.com/qubvel-org/segmentation_models.pytorch)
- [smp 공식 문서](https://segmentation-modelspytorch.readthedocs.io/)
- [Albumentations Semantic Segmentation 가이드](https://albumentations.ai/docs/3-basic-usage/semantic-segmentation/)
- [pytorch-grad-cam](https://github.com/jacobgil/pytorch-grad-cam)
- [SEG-GRAD-CAM (U-Net 특화)](https://github.com/linhaoqi027/SEG-GRAD-CAM)

### 튜토리얼
- [PyImageSearch U-Net Training in PyTorch](https://pyimagesearch.com/2021/11/08/u-net-training-image-segmentation-models-in-pytorch/)
- [Towards Data Science: U-Net 2D & 3D Segmentation](https://towardsdatascience.com/creating-and-training-a-u-net-model-with-pytorch-for-2d-3d-semantic-segmentation-model-building-6ab09d6a0862/)

### 손실함수
- [Combo Loss 논문 (CMIG 2019)](https://www2.cs.sfu.ca/~hamarneh/ecopy/cmig2019.pdf)
- [Unified Focal Loss (2021)](https://www.sciencedirect.com/science/article/pii/S0895611121001750)

### 유사 프로젝트
- [yakhyo/face-parsing (BiSeNet, CelebAMask)](https://github.com/yakhyo/face-parsing) — 학습 코드 참고
- [TracelessLe/FaceParsing.PyTorch (EHANet)](https://github.com/TracelessLe/FaceParsing.PyTorch)

---

*Research 끝. 다음은 `plan_kim_0518_01.md` 작성.*
