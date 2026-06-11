# CV Final 프로젝트 인수인계 (D-3, 2026-06-12 기준)

> **새 팀원이 처음 봐도 cold start 가능하도록 작성.** 이 폴더 4개 파일만 읽으면 됨.
>
> **읽는 순서**: HANDOVER.md (지금) → SETUP.md → CHECKLIST.md → AGENT_BRIEF.md
>
> **발표**: 2026-06-15 (D-3 남음)

---

## 0. 한 줄 요약

> **성형 견적 시각화 시스템** — 사진 업로드 → MediaPipe 478 랜드마크 → U-Net 분석 → Stable Diffusion Inpaint으로 시술 후 시각화 → PDF 견적서 출력.

**기술 스택**: PyTorch + segmentation_models_pytorch + diffusers + Streamlit + ReportLab

**평가 기준** (박한샘 교수 공지):
1. 문제 정의 + 데이터 (30%)
2. 모델 설계 + 구현 (40%) ⭐
3. 성능 분석 (15%)
4. 시각화 + 해석 (15%)

**예상 점수**: 87 ~ 94 / 100

---

## 1. 프로젝트 큰 그림

### 시스템 아키텍처

```
사진 업로드
   ↓ MediaPipe Face Mesh (478 landmarks)
   ↓
[Phase 7-A] 자동 Sketch / Color / Mask 생성 (Bezier 곡선)
   ↓
[U-Net Segmentation] 시술 부위 분석 (Phase 1~6, 4가지 모델)
   ↓
[Phase 7-G] Stable Diffusion Inpaint (검은 마스크 → 변형된 얼굴)
   ↓
[Phase 7-B] Refinement Network (작은 U-Net + L1+VGG Perceptual)
   ↓
[Phase 7-D] Streamlit UI + ReportLab PDF 견적서
```

### 왜 SC-FEGAN 안 쓰나?
- 원 계획: SC-FEGAN (Jo & Park 2019, ICCV)
- 문제: TF 1.15 의존 → Python 3.12에서 inference 불가
- **우회**: 동일 task를 더 최신 SD Inpaint (Rombach 2022)로 대체
- 학술 framing: 모듈식 설계 강점 보여줌

---

## 2. 폴더 구조 (현재)

```
cv-final/
├── README.md                   ← 프로젝트 첫 페이지
├── requirements.txt            ← 의존성 (torch, smp, diffusers, streamlit, reportlab 등)
├── conftest.py                 ← pytest 설정
│
├── handover/                   ⭐ 이 폴더 (인수인계)
│   ├── HANDOVER.md             ← 지금 읽는 문서
│   ├── SETUP.md                ← 환경 셋업 step-by-step
│   ├── CHECKLIST.md            ← 남은 작업 체크리스트 (D-3)
│   └── AGENT_BRIEF.md          ← AI 에이전트용 1페이지 컨텍스트
│
├── project/
│   ├── face_analyzer/          478 랜드마크 + 비율 분석
│   ├── input_generator/        9채널 SC-FEGAN 입력 자동 생성 (sketch/color/mask/composer)
│   ├── segmentation/           U-Net + Grad-CAM + 평가
│   │   ├── unet.py             모델 빌더 (attention_type='scse' 지원)
│   │   ├── train.py            학습 루프 (Early Stopping)
│   │   ├── losses.py           Combo Loss (Dice + CE)
│   │   ├── metrics.py          mIoU, Dice
│   │   ├── data.py             CelebAMaskHQDataset
│   │   ├── transforms.py       Augmentation (Albumentations)
│   │   ├── heatmap.py          MediaPipe → Gaussian heatmap (LM-guided)
│   │   ├── tta.py              Test Time Augmentation
│   │   ├── inference.py        single image 추론
│   │   ├── postprocess.py      label remap
│   │   ├── label_map.py        19-class → 6-class
│   │   ├── gradcam.py          ⭐ Grad-CAM (Selvaraju 2017)
│   │   ├── evaluation.py       ⭐ Confusion Matrix + Per-class IoU + Ablation
│   │   └── config.yaml         학습 설정 (단일 진실 출처)
│   ├── recommender/            시술 추천 (procedures.yaml DB)
│   │   └── procedures.yaml     ⭐ 시술 정의 (가격, 마스크 인덱스 등)
│   ├── refinement/             Refinement Network (Phase 7-B)
│   │   ├── model.py            작은 U-Net + residual wrapper
│   │   ├── losses.py           L1 + VGG19 Perceptual
│   │   ├── data.py             Synthetic + Paired Dataset
│   │   ├── train.py            학습 진입점
│   │   └── config.yaml
│   ├── scfegan_finetune/       (참고용, 사용 안 함)
│   ├── report/                 ⭐ PDF 견적서 (Phase 7-D)
│   │   └── pdf_generator.py    환자 맞춤 견적서 생성
│   └── tests/                  50+ unit tests (전부 PASS)
│
├── app/
│   └── streamlit_demo.py       ⭐ 2-mode UI (Pre-generated / Live)
│
├── notebooks/                  13개 (Colab용)
│   ├── 03/05/07                U-Net 학습 (Baseline/LM/Attention)
│   ├── 06                      TTA 평가
│   ├── 08                      SC-FEGAN 통합 (참고)
│   ├── 09                      Refinement 학습 ✅
│   ├── 10                      SC-FEGAN Fine-tune (참고, 폐기)
│   ├── 11                      Pretrained vs Fine-tuned 비교 (참고)
│   ├── 12                      SC-FEGAN inference (참고, 환경 문제)
│   ├── 13                      ⭐ Stable Diffusion Inpaint (성공)
│   ├── 14                      ⭐ Grad-CAM 시각화 (평가 4번)
│   └── 15                      ⭐ Confusion Matrix + Ablation (평가 3번)
│
├── docs/presentation/          발표 자료 (PDF 4종)
│   ├── proposal_slides.pptx
│   ├── glossary.pdf
│   ├── study_guide.pdf
│   └── references.pdf
│
├── samples/                    Drive에서 다운로드한 SD 결과 PNG
│   ├── all_sd_results.png
│   ├── beforeafter_*.png × 3   (시술별 발표 슬라이드)
│   ├── sd_final_*.png × 3      (Streamlit/PDF용)
│   ├── sd_only_*.png × 3       (Refinement 비교용)
│   ├── original_before.png     (입력 자리)
│   ├── gradcam_*.png × 8       ⭐ 노트북 14 실행 후 추가
│   └── confusion_matrices_all.png  ⭐ 노트북 15 실행 후 추가
│
├── checkpoints/                학습된 모델 (Drive에서 다운로드)
│   └── refinement_best.pt
│
├── data/                       (Colab에서 자동 다운로드, 로컬 X)
├── plan_kim_*.md               6개 plan (5/15 ~ 6/10)
├── research.md / research_unet.md
└── SC-FEGAN/                   외부 repo (사용 안 함, .gitignore 처리)
```

---

## 3. 현재 상태 (6/12 기준)

### ✅ 완료된 작업

| Phase | 내용 | 결과 |
|-------|------|------|
| **Phase 1-6** | U-Net 4종 학습 | mIoU 0.680 ~ 0.683 |
| **Phase 7-A** | 자동 입력 생성 | 39 tests pass |
| **Phase 7-B** | Refinement Network | val_l1 0.045 (학습 완료) |
| **Phase 7-D** | PDF 견적서 + Streamlit | 9 tests pass |
| **Phase 7-G** | SD Inpaint 우회 | 결과 PNG 10장 (Drive 백업) |
| **Phase 7-H** | Grad-CAM | 9 tests pass (노트북 14) |
| **Phase 7-I** | Confusion Matrix + Ablation | 9 tests pass (노트북 15) |

### 🛠 진행 중

| 작업 | 상태 |
|------|------|
| 발표 슬라이드 작성 | 🟡 outline만 (plan_kim_0610_02.md 참조) |
| Colab 노트북 14, 15 실행 | 🟡 코드는 푸쉬됨, 실행은 미완료 |
| 데모 영상 녹화 | ⏳ 6/13 예정 |
| 리허설 | ⏳ 6/14 예정 |

### 🗑 폐기된 작업

- **SC-FEGAN Fine-tuning** (TF 1.15 환경 불가)
- **SC-FEGAN Inference** (Python 3.12 + protobuf 충돌)

---

## 4. 학습된 모델 위치

### Google Drive (`/MyDrive/cv-final-ckpts/`)

| 파일 | 크기 | 성능 | 사용처 |
|------|------|------|--------|
| `refinement_best.pt` | 94 MB | val_l1 0.045 | Streamlit/PDF, Refinement |
| `unet_v1.pt` | 94 MB | mIoU 0.680 (Baseline) | 노트북 15 평가 |
| `unet_lmguided_best.pt` | 94 MB | mIoU 0.683 (LM) | 노트북 15 평가 |
| `unet_attention_best.pt` | 94 MB | mIoU 0.683 (SCSE) | **Grad-CAM (노트북 14)** |
| `samples/*` | ~20장 PNG | SD Inpaint 결과 | 발표 슬라이드, Streamlit |

### SC-FEGAN ckpt (참고용, 사용 안 함)

`/MyDrive/SC-FEGAN-ckpt/SC-FEGAN.ckpt.{index,data-*}` — 환경 호환 안 됨. **삭제 X** (다른 환경에서 시도 가능성 있음).

---

## 5. GitHub Repo

```
https://github.com/keonU206/cv-final (Private)
```

- **Owner**: keonU206 (kim, keonu206@gmail.com)
- **Branch**: main (모두 여기에 push)
- **Commits**: 30+ (대부분 6/10에 폭풍 작업)

### 권한 부여 (새 팀원 추가)

1. https://github.com/keonU206/cv-final/settings/access
2. "Add people" → 팀원 GitHub username
3. 권한: Write (코드 수정 가능)

### Clone (PAT 필요)

```bash
git clone https://<TOKEN>@github.com/keonU206/cv-final.git
# 또는 Colab에서 google.colab.userdata.get('GH_TOKEN')
```

PAT 발급: https://github.com/settings/tokens → New token (classic) → `repo` scope

---

## 6. 평가 기준 매핑 (📊 발표 핵심)

박한샘 교수 공지 기준 + 우리 산출물:

### 1️⃣ 문제 정의 + 데이터 (30%)
- Task: Segmentation + Generation (성형 견적 시각화)
- 데이터셋: **CelebAMask-HQ** (Lee 2020 CVPR), 30K + 19-class mask
- 한국 성형 시장 동기, 의료 보조 도구 framing

### 2️⃣ 모델 설계 + 구현 (40%) ⭐ 최대 비중
- **U-Net 4종** (Baseline / LM-guided / Attention / TTA)
- **ResNet-34 Encoder** (계층적 특징 추출 → Grad-CAM으로 시각적 증명)
- **SCSE Attention** (Roy 2018 MICCAI)
- **Refinement Network** (작은 U-Net + Residual)
- **Stable Diffusion Inpaint** (Rombach 2022 CVPR)
- **Combo Loss** (Dice + CE, Taghanaki 2019)
- **Perceptual Loss** (VGG19, Johnson 2016 ECCV)

### 3️⃣ 성능 분석 (15%) — 노트북 15에서 다 보강
- **Confusion Matrix** (5x5, normalized)
- **Per-class IoU/Dice** (background/nose/eye/mouth/skin)
- **Ablation Table** (4 모델 × 지표)
- **Augmentation** 적용 (HFlip 0.5, Rotation 15°, Brightness, Blur)
- **Early Stopping** + **TTA**

### 4️⃣ 시각화 + 해석 (15%) — 노트북 14에서 다 보강
- **Grad-CAM** (Selvaraju 2017 ICCV) — U-Net이 어디 보는지
- **Before/After** (Stable Diffusion Inpaint 결과, 시술 3종)
- **Confusion Matrix heatmap**
- **Per-class IoU bar chart**

---

## 7. 발표 슬라이드 구성 (11장, 15분)

| # | 제목 | 평가 항목 | 자료 |
|---|------|----------|------|
| 1 | 인트로 — 성형 견적 시각화 | 1 | — |
| 2 | 데이터셋 (CelebAMask-HQ) | 1 | 통계 |
| 3 | 시스템 아키텍처 | 2 | 다이어그램 |
| 4 | U-Net 4종 + plateau 발견 | 2 | `model_comparison_summary.png` |
| 5 | **Grad-CAM 시각화** ⭐ | 4 | `gradcam_presentation.png` |
| 6 | 자동 입력 생성 + Refinement | 2 | sketch + mask |
| 7 | **GAN 우회 — SC-FEGAN → SD Inpaint** | 2 | `all_sd_results.png` |
| 8 | **Confusion Matrix + Ablation** ⭐ | 3 | `confusion_matrices_all.png`, ablation |
| 9 | **데모** (Streamlit + PDF) | 1+2 | 영상 또는 라이브 |
| 10 | **한계 + 향후 강화 계획** | 1+2 | ControlNet, InstantID, Korean LoRA |
| 11 | 결론 + Q&A | — | — |

자세한 발표 멘트: `plan_kim_0610_02.md` 의 §6 (학술 framing template)

---

## 8. Q&A 대비 (예상 질문 5개)

### Q1. "왜 SC-FEGAN 안 썼나요?"
A: TF 1.15 의존성 → Python 3.12에서 protobuf 충돌. 더 최신 기술 SD Inpaint(2022)로 대체.

### Q2. "변형이 약해 보이는데?"
A: identity 보존을 위한 의도된 보수적 변형. ControlNet/InstantID 추가하면 정밀 제어 가능.

### Q3. "U-Net 3개 결과가 같던데?"
A: mIoU 0.683 plateau는 학술적 발견. **"Architecture < Training Methodology"** — He 2019 (CVPR) *Bag of Tricks*와 일치.

### Q4. "Refinement Network 효과는?"
A: val_l1 0.045 달성. SD 출력의 artifact 제거 + 경계 자연스러움.

### Q5. "실제 사용 가능성?"
A: **의료 보조 도구** — 의사 상담의 시각적 보조. 진단/처방 X. 윤리적 한계 인지.

---

## 9. 남은 작업 (자세히는 CHECKLIST.md)

| 날짜 | 작업 | 담당 |
|------|------|------|
| 6/12 (오늘) | Colab 노트북 14, 15 실행 + PNG 다운로드 | 학습 담당 |
| 6/12 | 발표 슬라이드 v1 (11장) | 슬라이드 담당 |
| 6/13 | 데모 영상 녹화 + 슬라이드 마무리 | 영상/발표 담당 |
| 6/14 | 리허설 1차 + 2차 + 백업 영상 | 전원 |
| 6/15 | **발표** | 전원 |

---

## 10. 리스크 + 폴백

| 리스크 | 폴백 |
|--------|------|
| Colab GPU 한도 소진 | 다른 계정 또는 학습 데이터 축소 |
| 노트북 14, 15 실행 실패 | 코드는 syntax OK 검증됨. 모델 ckpt 경로 확인 |
| 발표 당일 Streamlit 다운 | 백업 영상 재생 |
| Q&A 답 막힘 | 한계점 솔직히 인정 + 향후 계획 명시 |
| 슬라이드 시간 초과 | 슬라이드 6, 10 단축 |

---

## 11. 기술적 의사결정 history (왜 이렇게 했나?)

| 결정 | 이유 |
|------|------|
| 자체 U-Net 학습 추가 | 모델 설계 40% 평가 항목 만족 |
| ResNet-34 encoder | 가벼움 + ImageNet pretrained |
| Combo Loss (Dice+CE) | Class imbalance + 정확도 |
| LM-guided (4채널) | "MediaPipe 랜드마크 활용" 차별화 |
| SCSE Attention | smp 한 줄 적용 가능 |
| **SD Inpaint** 채택 | SC-FEGAN 환경 불가 + 더 최신 기술 |
| Refinement Network | SD 출력 정제 + 학술적 깊이 |
| Streamlit Pre-gen 모드 | 발표 데모 안정성 |

---

## 12. 빠른 동작 검증 (새 환경에서)

```bash
# 1. clone + 의존성
git clone https://<TOKEN>@github.com/keonU206/cv-final.git
cd cv-final
pip install -r requirements.txt

# 2. 단위 테스트 (50+ 전부 PASS 확인)
pytest project/tests/ -v

# 3. PDF 견적서 샘플 생성
python -c "from project.report import build_estimate, generate_estimate_pdf; \
items = build_estimate(['nose_tip', 'double_eyelid', 'jaw_v_line']); \
generate_estimate_pdf(items, 'test.pdf', patient_name='테스트', include_images=False); \
print('PDF OK')"

# 4. Streamlit 데모
streamlit run app/streamlit_demo.py
```

→ 위 4단계 다 통과하면 환경 OK.

---

## 13. 연락 + 도움

- **Owner**: kim (keonu206@gmail.com)
- **Plan 문서**: `plan_kim_*.md` 6개 (시간 순)
- **가장 최신 plan**: `plan_kim_0610_02.md`
- **AI 에이전트 사용 시**: `AGENT_BRIEF.md` 먼저 읽혀주기

---

> **다음 읽을 문서**: `SETUP.md` (환경 셋업 step-by-step)
