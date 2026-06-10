# Plan kim 0604-01 — Phase 7 풀스택 GAN 강화 (C안)

> **버전**: v0.1 (draft, 리뷰 대기)
> **작성일**: 2026-06-04
> **발표일**: 2026-06-15 (D-11)
> **이전 plan**: `plan_kim_0518_02.md` (Phase 1~6 완료)
> **⚠️ 본 문서는 계획서임 — 아직 구현하지 마세요.**

---

## 0. 결정 사항 (Locked-in)

| 항목 | 선택 | 사유 |
|------|------|------|
| 강화 전략 | **C안** (7-A + 7-B + 7-C1) | "GAN 본체 강화" 명분 확보 |
| TF 1.x 처리 | **F1** (TF 2.x compat mode + tf-keras) | 이전 디버깅 노하우 보유 |
| Fine-tuning 데이터 | **2,000장** (균형) | 발표 일정 + 학습 안정성 균형 |

---

## 1. 현재 상태 (Phase 6까지 완료)

| Phase | 결과 | mIoU |
|-------|------|------|
| 1. Baseline U-Net | unet_baseline_best.pt | 0.680 |
| 2~4. LM-guided U-Net | unet_lmguided_best.pt | 0.683 |
| 5. TTA 평가 | (추론 단계) | 0.683 |
| 6. Attention U-Net | unet_attention_best.pt | 0.683 |

**핵심 발견**: U-Net 측 강화는 **plateau (0.683)** 도달 → 발표 디스커션에 "Architecture < Training Methodology" framing.

---

## 2. Phase 7 목표

SC-FEGAN 측면을 **3단계로 강화**하여 GAN 출력 품질 향상 + 학술적 정당성 확보.

```
[원본 사진]
   ↓ MediaPipe 478 landmarks
   ↓
[Phase 7-A] 자동 Sketch/Color/Mask 생성  ← 입력 자동화
   ↓
[SC-FEGAN] inpainting
   ↓
[Phase 7-C1] Fine-tuned G+D 추가 학습     ← GAN 본체 강화
   ↓
[Phase 7-B] Refinement Network            ← 출력 정제
   ↓
[최종 결과]
```

---

## 3. Phase 7-A — 자동 Sketch/Color 생성 (2일)

**목표**: 시술별 (`nose_tip` / `double_eyelid` / `v_line`) SC-FEGAN 9채널 입력을 자동 생성.

### 산출물

- [ ] `project/input_generator/color.py` — 시술별 색상 가이드 생성
- [ ] `project/input_generator/mask.py` — SC-FEGAN inpaint mask (시술 영역만)
- [ ] `project/input_generator/composer.py` — 9채널 입력 통합 (image + sketch + color + mask + noise)
- [ ] `tests/test_color.py`, `test_mask.py`, `test_composer.py`
- [ ] `notebooks/08_scfegan_integration.ipynb` — 시술별 Before/After 6장 시연

### 일정

| 날짜 | 작업 |
|------|------|
| 6/4 (오늘) | color.py + mask.py 작성 |
| 6/5 | composer.py + 테스트 3종 + 노트북 |

### 설계 메모

- `color.py`는 sketch 패턴 동일 (시술별 함수 + intensity 슬라이더)
- 색상은 원본 이미지에서 sample (피부톤 자동 매칭)
- mask는 시술 영역 dilate (Gaussian 5x5)

---

## 4. Phase 7-B — Refinement Network (3일)

**목표**: SC-FEGAN 출력 → 작은 U-Net으로 후처리 → artifact 제거.

### 산출물

- [ ] `project/refinement/model.py` — 작은 U-Net (in=3, out=3, depth=4)
- [ ] `project/refinement/data.py` — Dataset: (SC-FEGAN output, GT clean image) 쌍
- [ ] `project/refinement/losses.py` — L1 + Perceptual (VGG19 features)
- [ ] `project/refinement/train.py` — 학습 루프
- [ ] `project/refinement/config.yaml` — 학습 설정
- [ ] `notebooks/09_refinement_train.ipynb` — Colab 학습 노트북
- [ ] `tests/test_refinement_model.py`

### 일정

| 날짜 | 작업 | 비고 |
|------|------|------|
| 6/6 | 모델 + 데이터셋 + Loss 작성 | |
| 6/7 | 학습 (Colab T4, 1~2 epoch) | 7-C1 환경 셋업 병렬 ⚡ |
| 6/8 | 결과 검증 + Before/After 시각화 | |

### 학습 데이터

- CelebAMask-HQ 원본 500장을 GT로 두고
- SC-FEGAN으로 동일 영역 inpaint → noisy pair 500장 생성
- (input=SC-FEGAN out, target=원본)

---

## 5. Phase 7-C1 — SC-FEGAN Fine-tuning ⭐ (3일)

**목표**: SC-FEGAN G+D를 한국인 얼굴 위주로 추가 학습 → 도메인 적응.

### 산출물

- [ ] `project/scfegan_finetune/` 폴더 신설
- [ ] `train_finetune.py` — TF 2.x compat 학습 루프
- [ ] `config_finetune.yaml` — lr=1e-5, batch=4, epochs=3
- [ ] `data_pipeline.py` — CelebAMask-HQ 2,000장 + 시술별 augmentation
- [ ] `scfegan_finetuned.ckpt` — 학습된 체크포인트
- [ ] `notebooks/10_scfegan_finetune.ipynb` — Colab 학습 노트북
- [ ] `notebooks/11_pretrained_vs_finetuned.ipynb` — Before/After 비교

### 일정

| 날짜 | 작업 |
|------|------|
| 6/9 | 환경 셋업 (TF 2.x compat) + 데이터 파이프라인 + dry-run |
| 6/10 | Fine-tuning Day 1 (Generator 위주, Discriminator 고정) |
| 6/11 | Fine-tuning Day 2 + 결과 검증 + 폴백 결정 |

### 학습 전략 (F1)

```python
# 핵심 환경 설정
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

# ckpt 로드 → G 위주로 fine-tune
# learning_rate = 1e-5 (catastrophic forgetting 방지)
# batch_size = 4 (T4 메모리 제약)
# epochs = 3 (overfitting 방지)
```

### 학습 데이터 — 2,000장 선정 기준

- CelebAMask-HQ 30K 중 무작위 sampling
- 정면 (yaw < 15°), 무표정, 단일 인물 필터링
- 시술별 augmentation: nose/eye/jaw 영역 mask 다양화

---

## 6. 통합 + 발표 준비 (4일)

| 날짜 | 작업 |
|------|------|
| 6/12 | Streamlit UI (`app/streamlit_demo.py`) + PDF 견적서 (`project/report/pdf_generator.py`) |
| 6/13 | 발표 슬라이드 업데이트 (`docs/presentation/proposal_slides.pptx`) — Phase 7 결과 추가 |
| 6/14 | **리허설 ①** + 데모 영상 백업 녹화 |
| 6/15 | **리허설 ② → 발표** |

---

## 7. 리스크 + 폴백 매트릭스

| 리스크 | 발생 시점 | 폴백 |
|--------|----------|------|
| TF 1.x compat 실패 | 6/9 | F3 (head만 fine-tune) 전환, 7-C1 시간 1일 단축 |
| Fine-tuning 결과 나쁨 (mode collapse 등) | 6/11 | Pretrained ckpt 그대로 사용, "시도했음" framing |
| Refinement Net 학습 시간 초과 | 6/8 | epoch 줄이거나 inference-time VGG 정제로 대체 |
| Colab 무료 한도 소진 | 6/9 이후 | Colab Pro 결제 (한 달 $10) |
| Streamlit UI 시간 부족 | 6/12 | Jupyter notebook 데모로 대체 |

---

## 8. 산출물 디렉토리 구조 (예정)

```
cv-final/
├── project/
│   ├── input_generator/      # 7-A (sketch.py 이미 있음)
│   │   ├── sketch.py ✅
│   │   ├── color.py 🆕
│   │   ├── mask.py 🆕
│   │   └── composer.py 🆕
│   ├── refinement/           # 7-B
│   │   ├── model.py 🆕
│   │   ├── data.py 🆕
│   │   ├── losses.py 🆕
│   │   ├── train.py 🆕
│   │   └── config.yaml 🆕
│   ├── scfegan_finetune/     # 7-C1
│   │   ├── train_finetune.py 🆕
│   │   ├── data_pipeline.py 🆕
│   │   └── config_finetune.yaml 🆕
│   └── report/               # 발표 준비
│       └── pdf_generator.py 🆕
├── app/
│   └── streamlit_demo.py 🆕  # 발표 데모
├── notebooks/
│   ├── 08_scfegan_integration.ipynb 🆕
│   ├── 09_refinement_train.ipynb 🆕
│   ├── 10_scfegan_finetune.ipynb 🆕
│   └── 11_pretrained_vs_finetuned.ipynb 🆕
└── tests/
    ├── test_color.py 🆕
    ├── test_mask.py 🆕
    ├── test_composer.py 🆕
    └── test_refinement_model.py 🆕
```

---

## 9. 리뷰 체크리스트 (사용자가 확인)

- [ ] 일정 빡빡함 OK? (6/14 리허설 1일뿐)
- [ ] Phase 7-A 산출물 4개 OK? (color/mask/composer/노트북)
- [ ] Phase 7-B 학습 데이터 500장 OK? (더 늘릴지)
- [ ] Phase 7-C1 데이터 2,000장 OK? (5,000장으로 강화할지)
- [ ] Fine-tuning 실패 시 폴백 전략 OK?
- [ ] Streamlit UI 우선순위 OK? (notebook 데모로 대체 가능)

---

## 10. 다음 행동

1. **사용자 리뷰**: 본 문서에 직접 주석/메모 추가
2. **수정 반영**: "메모 반영해서 plan 업데이트해라. 아직 구현하지 마"
3. **확정 후 구현**: "plan대로 Phase 7-A부터 구현해라"

---

> **Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>**
