# Plan v2 — 성형 견적 시각화 + U-Net 세그멘테이션

> 작성일: 2026-05-15
> 작성자: kim
> 기반 문서: [research.md](research.md), [plan v1](plan_kim_0515_01.md)
> 변경 사유: 교수님 평가 기준 (40% 모델 설계, 15% CV 지표) 충족을 위해 **자체 학습 U-Net 세그멘테이션** 컴포넌트 추가
> 발표 일정:
> - **2026-05-18 (3일 후)**: 아이디어 제안 발표 (슬라이드만)
> - **2026-06-15 (1달 후)**: 최종 평가 (전체 구현 + 학습 모델 + 데모)

---

## 0. v1에서 무엇이 바뀌었나

| 항목 | v1 | **v2** |
|------|----|----|
| 마스크 생성 | MediaPipe 랜드마크 → convex hull | **U-Net 자체 학습 → 픽셀 단위 segmentation** |
| 추천 엔진 | 룰베이스 | 룰베이스 (유지) |
| 학습 컴포넌트 | 없음 | **U-Net (메인 deliverable)** |
| 평가 지표 | 없음 | **mIoU, Dice score, ablation study** |
| 해석 가능성 | 시각화만 | **Grad-CAM on U-Net encoder** |
| 데이터셋 | SC-FEGAN 샘플 + 팀원 사진 | **+ CelebAMask-HQ (30K, 19부위 라벨)** |
| 점수 기대치 | ~50/100 | **85~95/100** |

---

## 1. 새 파이프라인

```
[사용자 얼굴 사진]
       │
       ▼
[1. 얼굴 검출 + 정규화]   MediaPipe Tasks API
       │
       ▼
[2. 478 랜드마크 + 비율 분석]
       │
       ▼
[3. 룰베이스 추천 엔진]   → [(시술, 신뢰도, 견적)]
       │
       ▼
[4. ★ U-Net 세그멘테이션] ← 자체 학습 (CelebAMask-HQ)
       │  출력: 시술 부위 픽셀 mask (코/눈/턱/이마/입)
       ▼
[5. SC-FEGAN 추론]   ← 사전학습 (Week 1 검증 완료)
       │
       ▼
[6. Before/After + Grad-CAM 시각화]
```

**핵심**: 4번에서 만든 정밀 mask가 5번 SC-FEGAN의 입력으로 들어가서 **더 자연스러운 inpainting 결과**를 만들어냄.

---

## 2. 역할 분담 (3명) — DL 강도 1명 필수

| 역할 | 책임 | 메인 산출물 |
|------|------|------------|
| **A: 모델/엔진** | SC-FEGAN wrapper 클래스화<br>DiffFace-Edit PoC (백업) | `scfegan_wrapper/infer.py`, `diffface_wrapper/` |
| **B: 세그멘테이션 (메인 학습 담당)** | U-Net 설계 + 학습<br>CelebAMask-HQ 데이터로더<br>IoU/Dice 평가<br>Grad-CAM | `project/segmentation/` 모듈 전체 |
| **C: 분석/UI/통합** | MediaPipe + 추천 엔진<br>Streamlit UI<br>PDF 출력<br>발표 자료 | `face_analyzer/`, `recommender/`, `ui/streamlit_app.py` |

> **B 담당자가 PyTorch 또는 TF/Keras 경험 있어야 함**. 없으면 옵션 1 (얼굴형 분류)로 폴백 고려.

---

## 3. 새 디렉터리 구조

```
project/
├── face_analyzer/           # Week 1 완료
├── recommender/             # Week 1 완료
├── input_generator/
│   ├── mask.py              # convex hull 버전 (백업/비교용)
│   └── mask_unet.py         # ★ NEW: U-Net 추론 결과 사용
├── segmentation/            # ★ NEW (B 담당)
│   ├── __init__.py
│   ├── unet.py              # U-Net 모델 정의 (PyTorch 권장)
│   ├── data.py              # CelebAMask-HQ 데이터로더
│   ├── transforms.py        # augmentation
│   ├── train.py             # 학습 스크립트
│   ├── inference.py         # 추론 래퍼
│   ├── metrics.py           # IoU, Dice
│   ├── gradcam.py           # 해석 가능성 시각화
│   └── checkpoints/
│       └── unet_v1.pt       # 학습된 가중치
├── scfegan_wrapper/         # Week 2 (A)
├── diffface_wrapper/        # Week 3 (A)
├── ui/                      # Week 3-4 (C)
└── tests/

notebooks/
├── 01_env_check.ipynb       # ✅ 완료
├── 02_scfegan_smoke.ipynb   # ✅ 완료
├── 03_unet_train.ipynb      # ★ NEW: U-Net 학습 + 평가
├── 04_gradcam_viz.ipynb     # ★ NEW: Grad-CAM 시각화
└── 05_pipeline_e2e.ipynb    # ★ NEW: 전체 통합

docs/presentation/
├── proposal_outline.md      # ★ NEW: 5/18 발표 outline
├── final_outline.md         # 6/15 발표 outline (Week 4 작성)
└── slides/
```

---

## 4. U-Net 모델 설계 (B 담당 상세 가이드)

### 4.1 아키텍처
- **Base**: 표준 U-Net (Ronneberger et al., 2015)
- **Encoder**: ResNet-34 pretrained (transfer learning) 또는 vanilla 4-stage encoder
- **Decoder**: 4-stage upsampling + skip connection
- **Output**: 6 classes (background + 5 시술 부위)

### 4.2 클래스 매핑 (CelebAMask-HQ 19부위 → 우리 5부위)

| 우리 클래스 | CelebAMask-HQ 라벨 |
|------------|-------------------|
| 0: background | bg, hair, hat, cloth, ear_r, neck |
| 1: nose | nose |
| 2: eye (양쪽) | l_eye, r_eye |
| 3: mouth (입) | u_lip, l_lip, mouth |
| 4: jaw/chin (턱) | (skin의 하단 영역 — 후처리 필요) |
| 5: forehead (이마) | (skin의 상단 영역 — 후처리 필요) |

> ⚠️ "턱"과 "이마"는 CelebAMask-HQ에 직접 라벨이 없음 → **skin 영역에서 랜드마크로 분리** 또는 **CelebAMask-HQ의 skin 라벨을 그대로 쓰고 후처리**

### 4.3 학습 설정

```yaml
# segmentation/config.yaml (예시)
input_size: 256
batch_size: 16
epochs: 10
optimizer: Adam
learning_rate: 1e-4
loss: 0.5 * dice_loss + 0.5 * cross_entropy
augmentation:
  - horizontal_flip: 0.5
  - rotation: ±15deg
  - color_jitter: brightness=0.2, contrast=0.2
  - random_crop: 224x224
```

### 4.4 평가 지표 (15% 항목 대응)

```python
# metrics.py
- per_class_iou         # 5개 부위별 IoU
- mIoU                  # 평균 IoU (메인 지표)
- dice_score            # F1 유사
- pixel_accuracy
- confusion_matrix      # 부위 간 혼동
```

**목표 성능**: mIoU 0.75+, Dice 0.85+

### 4.5 Ablation Study (성능 최적화 — 15% 항목 추가 점수)

| 실험 | 변수 | 측정 |
|------|------|------|
| Baseline | aug 없음, lr=1e-4 | mIoU |
| + Aug | horizontal flip + rotation | mIoU 차이 |
| + Color jitter | + brightness/contrast | mIoU 차이 |
| Loss 비교 | CE only / Dice only / 혼합 | mIoU 비교 |

→ "Aug 적용 시 mIoU가 0.71 → 0.79로 향상" 같은 표 1개 만들면 만점.

### 4.6 Grad-CAM (15% 시각화)

```python
# gradcam.py
- U-Net encoder의 bottleneck 레이어에 hook
- 입력 이미지의 어느 부분이 "코 영역"으로 판단되는지 heatmap
- 슬라이드용 시각화 5장 (코/눈/입/턱/이마 각각)
```

---

## 5. 주차별 마일스톤 (4주 + 5/18 제안)

### 사전 (5/15 ~ 5/17) — 5/18 제안 발표 준비
| 담당 | 태스크 | DoD |
|------|--------|-----|
| All | 팀명 결정 + e-campus 게시판 등록 (~5/22) | 게시글 1건 |
| All | 5/18 발표 슬라이드 7~8장 작성 | `docs/presentation/slides/` |
| B (선택) | CelebAMask-HQ 다운로드 (~30GB) + 1 epoch PoC 학습 | 슬라이드 8번에 1장 |

### Week 2 (5/19 ~ 5/26) — 데이터 + U-Net PoC
| 담당 | 태스크 | DoD |
|------|--------|-----|
| B | CelebAMask-HQ 다운로드 완료 + `data.py` 데이터로더 | 1배치 정상 로드 |
| B | U-Net 모델 정의 (`unet.py`) | torchsummary 출력 OK |
| B | 1 epoch 학습 PoC | loss 감소 확인 |
| A | `scfegan_wrapper/infer.py` 클래스화 | E2E 함수 호출 |
| C | Streamlit 골격 v0 (업로드 + 표시만) | localhost 실행 |

### Week 3 (5/27 ~ 6/2) — 본격 학습 + 평가
| 담당 | 태스크 | DoD |
|------|--------|-----|
| B | 5~10 epoch 학습, mIoU/Dice 측정 | mIoU 0.75+ |
| B | Augmentation 추가 + ablation 1차 | 비교 표 |
| B | Grad-CAM 시각화 5장 | 이미지 저장 |
| A | DiffFace-Edit PoC | 코 변형 1장 |
| C | Streamlit + 추천 결과 + 마스크 시각화 | 데모 영상 30초 |

### Week 4 (6/3 ~ 6/9) — 통합 + 시각화 + PDF
| 담당 | 태스크 | DoD |
|------|--------|-----|
| All | `05_pipeline_e2e.ipynb` 전체 파이프라인 통과 | 사진→추천→U-Net→SC-FEGAN→결과 |
| B | Ablation 결과 확정 + 시각화 | 그래프/표 |
| C | PDF 견적서 출력 모듈 | 샘플 PDF |
| C | 최종 발표 슬라이드 작성 | 12~15장 |

### Buffer + 리허설 (6/10 ~ 6/14)
- 리허설 3회
- 폴백 영상/이미지 백업
- 6/15 발표

---

## 6. 평가 기준 충족 매핑

| 평가 항목 | 가중치 | 우리 대응 | 예상 점수 |
|----------|-------|----------|----------|
| 문제 정의 + 데이터 타당성 | 30% | 성형 견적 시각화 문제 명확 + CelebAMask-HQ (30K 표준 데이터셋) | 26~29/30 |
| 모델 설계 + 구현 | 40% | U-Net 자체 학습 + 계층적 특징 + skip connection | 32~38/40 |
| 성능 분석 + 최적화 | 15% | mIoU/Dice/Confusion Matrix + Augmentation ablation | 13~15/15 |
| 시각화 + 해석 | 15% | Segmentation overlay + Grad-CAM | 12~14/15 |
| **총합** | 100% | | **83~96** |

---

## 7. 리스크 + 대응

| 리스크 | 대응 |
|--------|------|
| CelebAMask-HQ 다운로드 실패 (30GB) | Hugging Face Datasets로 가져오기 / 부분 다운 |
| U-Net 학습 시간 부족 | input_size 256 → 128 줄이기, batch 늘리기 |
| mIoU 0.7 미달 | 더 깊은 encoder (ResNet-50), focal loss 시도 |
| Grad-CAM 안 나옴 | encoder 마지막 conv가 아닌 deeper layer hook |
| Colab GPU 시간 한도 | Colab Pro ($11.99/월) 결제 검토 |

---

## 8. plan v2 확정 후 다음 단계

1. **5/18 제안 발표 슬라이드 작성** (`docs/presentation/proposal_outline.md` 참고)
2. **팀 게시판 등록** (~5/22)
3. **B 담당자 확정** + CelebAMask-HQ 다운로드 시작
4. plan v2 검토 후 v3 (필요 시) 또는 구현 시작

---

*plan v2 끝. 5/18 발표 outline은 별도 문서.*
