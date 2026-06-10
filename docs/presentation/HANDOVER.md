# HANDOVER — 발표자료 작업을 이어받는 팀원에게

> 작성일: 2026-05-18
> 이 문서: **새로 합류하는 팀원이 본인 Claude에게 컨텍스트로 통째로 넘기는 문서**.
> 목적: 우리가 이미 결정한 사항 · 함정 · 산출물을 다시 논의하지 않게.

---

## 0. 한 줄 요약

3인 팀이 **컴퓨터 비전 기말 프로젝트로 "성형 견적 시각화 시스템"** 을 만든다.
**U-Net 자체 학습 세그멘테이션 + SC-FEGAN 사전학습 GAN 시각화** 의 파이프라인.
**5/18 제안 발표** + **6/15 최종 발표** 두 마일스톤.

## 1. 현재 상태 (2026-05-18 기준)

- ✅ **Week 1 완료**: Colab 환경 셋업, MediaPipe + SC-FEGAN 추론 검증 끝
- ✅ **plan v2 확정**: U-Net 자체 학습 추가 (점수 예상 89/100)
- ✅ **5/18 제안 발표 슬라이드 8장 완성**: `docs/presentation/proposal_slides.pptx`
- 🔜 **Week 2 시작 예정** (5/19~26): U-Net 데이터로더 + PoC 학습

## 2. 확정된 의사결정 (다시 논의 X)

| 항목 | 결정 |
|------|------|
| Vision Task | **Image Segmentation** (메인) + Image Generation (보조) |
| 메인 학습 모델 | **U-Net** (encoder: ResNet-34, decoder: U-Net) |
| 구현 라이브러리 | **`segmentation_models_pytorch`** (PyTorch) |
| 데이터셋 | **CelebAMask-HQ** (30K, 19부위 → 우리 5부위 + bg = 6클래스) |
| 시각화 모델 | **SC-FEGAN** (사전학습, 자체 학습 X) |
| 평가 지표 | mIoU, Dice Score, Per-class IoU, Confusion Matrix |
| 성능 최적화 | Augmentation Ablation Study |
| 해석 | Grad-CAM on encoder bottleneck |
| 개발 환경 | **Google Colab + T4 GPU** (TF 2.x compat + Keras 2 강제) |
| UI | Streamlit (Week 3~4 작업) |
| 추천 엔진 | 룰베이스 (`if 비율 임계값 초과 → 추천`) — ML 아님 |
| 자동 스케치 | Hybrid (자동 변형 + 사용자 슬라이더) |
| 백업 모델 | DiffFace-Edit (SC-FEGAN 안 되면 폴백) |
| 샘플 데이터 | 본인 사진 + FFHQ 일부 (각자 준비) |
| 데모 시술 3종 | **코끝 / 쌍커풀 / 사각턱+V라인** |

## 3. 평가 기준 대응 (교수님 평가표 기준 예상 점수)

| 항목 | 가중치 | 우리 대응 | 예상 점수 |
|------|-------|----------|----------|
| 문제 + 데이터 타당성 | 30% | CelebAMask-HQ 학술 표준 | 27/30 |
| 모델 설계 + 구현 | 40% | U-Net 자체 학습 + 계층적 특징 + skip connection | 35/40 |
| 성능 분석 + 최적화 | 15% | mIoU + Dice + Ablation | 14/15 |
| 시각화 + 해석 | 15% | Grad-CAM + Before/After overlay | 13/15 |
| **총합** | 100% | | **89/100** |

## 4. 파일 맵 (절대 경로)

```
C:\Users\User\Documents\cv-final\
│
├── research.md                          # 사전 조사 (SC-FEGAN, MediaPipe, 데이터셋 후보 등)
├── plan_kim_0515_01.md                  # v1 plan (deprecated)
├── plan_kim_0515_02.md                  # v2 plan (현재 활성)
├── requirements.txt                     # 로컬 개발 환경
├── conftest.py                          # pytest sys.path 설정
│
├── notebooks/
│   ├── 01_env_check.ipynb               # ✅ 검증 완료 (Colab 환경 + 모듈 검증)
│   └── 02_scfegan_smoke.ipynb           # ✅ 검증 완료 (SC-FEGAN 추론 smoke test)
│
├── project/
│   ├── face_analyzer/                   # ✅ 완료
│   │   ├── landmarks.py                 # MediaPipe Tasks API (478 landmarks)
│   │   ├── normalize.py                 # 얼굴 크롭 + 정렬 + 512 리사이즈
│   │   └── ratios.py                    # 비율 10개 (삼정·오안·E-line)
│   ├── recommender/                     # ✅ 완료
│   │   ├── rules.py                     # 룰베이스 추천
│   │   └── procedures.yaml              # 시술 DB (코끝/쌍커풀/사각턱 3종)
│   ├── input_generator/
│   │   └── mask.py                      # ✅ convex hull 마스크 (Week 1)
│   ├── segmentation/                    # 🔜 Week 2 작업 시작
│   │   └── (비어있음 — 아래 §6 참고)
│   ├── scfegan_wrapper/                 # 🔜 Week 2
│   ├── diffface_wrapper/                # 🔜 Week 3 (백업)
│   ├── ui/                              # 🔜 Week 3 (Streamlit)
│   └── tests/                           # ✅ 14개 unit test 통과
│
├── data/
│   ├── samples_team/                    # (git 제외, 팀원 사진)
│   ├── samples_public/                  # 공개 데이터셋 일부
│   └── outputs/
│       └── smoke_test_01.png            # Week 1 SC-FEGAN 결과
│
├── SC-FEGAN/                            # git clone 원본 (수정 X)
│   ├── model.py, ops.py, demo.py        # 원본 코드
│   ├── utils/config.py                  # ⚠️ yaml.safe_load 패치됨
│   └── ckpt/SC-FEGAN.ckpt.*             # (Google Drive에만 있음, 로컬 X)
│
└── docs/presentation/
    ├── HANDOVER.md                      # ← 이 문서
    ├── claude_prompt.md                 # 새 Claude 세션 부트스트랩 프롬프트
    ├── proposal_outline.md              # 5/18 발표 outline (텍스트)
    ├── proposal_slides.pptx             # 5/18 발표 슬라이드 8장 (편집 가능)
    ├── proposal_slides.pdf              # PDF 버전
    ├── generate.js                      # 슬라이드 생성 코드 (pptxgenjs)
    └── preview/slide-01.png ~ 08.png    # 슬라이드 미리보기
```

## 5. 이미 겪은 함정 (다시 만나지 말 것)

### 5.1 환경 함정

| 함정 | 증상 | 해결 |
|------|------|------|
| **Python 3.12 + TF 1.x 비호환** | `Failed to build wheels for nvidia-pyindex` | TF 1.x 설치 포기 → Colab 기본 TF 2.x + `tf.compat.v1` 모드 |
| **TF 2.x has no tf.contrib** | SC-FEGAN의 `tf.contrib.framework.load_variable` 실패 | sys.modules에 가짜 contrib 모듈 주입 (02 노트북 cell-4) |
| **Keras 3 has no tf.layers.conv2d** | `'conv2d' is not available with Keras 3` | `TF_USE_LEGACY_KERAS=1` + `pip install tf-keras` (02 노트북 cell-2) |
| **PyYAML 6+ requires Loader** | `yaml.load() missing Loader` | `yaml.safe_load(f)` 로 패치 (SC-FEGAN/utils/config.py) |
| **mediapipe 0.10.35 has no solutions** | `module 'mediapipe' has no attribute 'solutions'` | **Tasks API 사용** (legacy solutions 회피) |
| **mediapipe 0.10.21 protobuf 충돌** | `Failed to parse: node {...}` (graph parse error) | Tasks API (다른 코드 경로) 그대로 OK |

### 5.2 노트북 함정

- **`NotebookEdit`의 cell_id 사용 시 인덱스 혼동 주의**: Read로 먼저 확인 후 편집
- **Drive 마운트 후 `PROJECT_ROOT` 경로**: `/content/drive/MyDrive/cv-final` (본인 Drive 구조에 맞춰 확인)
- **`!pip install` 빨간 에러는 무시**: 다음 셀 진행 가능 (dependency conflict warning일 뿐)
- **런타임 재시작 필수 케이스**: TF 또는 mediapipe 버전 변경 후 → 무조건 재시작

### 5.3 한글 폰트 함정

- matplotlib 기본 폰트는 한글 X → `Mask (□□□)` 식으로 깨짐
- Streamlit/PPTX에서는 **Malgun Gothic** 또는 **나눔고딕** 사용 권장

## 6. Week 2~4 작업 큐

### Week 2 (5/19~5/26) — U-Net PoC

**담당 B (세그멘테이션)**:
- [ ] CelebAMask-HQ 다운로드 (~30GB, Hugging Face datasets 또는 GitHub 직접)
  - 출처: `github.com/switchablenorms/CelebAMask-HQ`
- [ ] `project/segmentation/data.py` — 데이터로더 작성 (PyTorch Dataset/DataLoader)
- [ ] `project/segmentation/unet.py` — `segmentation_models_pytorch.Unet` 래퍼 (3줄)
- [ ] `project/segmentation/transforms.py` — augmentation (albumentations 권장)
- [ ] `project/segmentation/train.py` — 학습 루프
- [ ] `project/segmentation/metrics.py` — IoU, Dice
- [ ] `notebooks/03_unet_train.ipynb` — Colab 학습 노트북 (T4 GPU)
- [ ] **1 epoch PoC 학습** (small subset 5K장 — 발표용 증명)

**담당 A (모델/엔진)**:
- [ ] `project/scfegan_wrapper/infer.py` — Week 1 노트북 코드를 클래스로 래핑
- [ ] DiffFace-Edit PoC 작은 노트북 (백업 모델)

**담당 C (UI/통합)**:
- [ ] Streamlit 골격 (`project/ui/streamlit_app.py`) — 업로드 + 표시만
- [ ] `procedures.yaml` 임계값 미세조정 (실제 사진으로 검증)

### Week 3 (5/27~6/2) — 본격 학습 + 평가

**B**:
- [ ] 본격 학습 5~10 epoch on full Train (24K)
- [ ] Ablation: aug 없음 vs 있음 mIoU 비교 (표 1개)
- [ ] **Grad-CAM 시각화 5장** (코/눈/입/턱/이마 각각)
- [ ] `notebooks/04_gradcam_viz.ipynb`

**A**: DiffFace-Edit PoC 1장 성공
**C**: Streamlit + 추천 결과 표시 + 마스크 시각화

### Week 4 (6/3~6/9) — 통합 + PDF + 슬라이드

**All**:
- [ ] `notebooks/05_pipeline_e2e.ipynb` — 사진 → 추천 → U-Net → SC-FEGAN → 결과
- [ ] **최종 발표 슬라이드 12~15장** (5/18 슬라이드 기반 확장)
- [ ] PDF 견적서 출력 (reportlab)
- [ ] 발표 리허설 3회

### 발표 (6/15)

## 7. 발표자료 작업 가이드 (5/18 이후)

### 7-1. 5/18 직후 — 슬라이드에 채워야 할 것

`docs/presentation/proposal_slides.pptx` 열어서:
- 슬라이드 1: `[팀명 입력]`, `[팀원1] · [팀원2] · [팀원3]` 채우기
- 슬라이드 8: 점선 placeholder 박스 안에 `data/outputs/smoke_test_01.png` 삽입

### 7-2. 6/15 최종 발표 슬라이드 (Week 4 작업)

최종 발표용 슬라이드 12~15장 예상 구성:
1. 표지 (팀명/팀원/날짜)
2. 문제 정의 + Motivation
3. 관련 연구 (선택)
4. 시스템 파이프라인 (5/18 기준)
5. U-Net 아키텍처 상세 (5/18 보다 깊게)
6. 데이터셋 분석 (sample 시각화 추가)
7. 학습 결과 — **loss curve, mIoU 그래프**
8. 평가 — **Confusion Matrix, Per-class IoU 표**
9. **Ablation Study 표**
10. **Grad-CAM 시각화**
11. **데모 (Before/After 갤러리)**
12. PDF 견적서 출력 예시
13. 한계 + 윤리적 고려
14. Q&A
15. (예비) 부록 / 참고문헌

## 8. 새 Claude 세션 시작 시 주의

1. **본 문서를 컨텍스트로 통째로 제공** (또는 `claude_prompt.md` 사용)
2. 새 Claude에게 결정 사항을 다시 묻지 말고 "확정"임을 분명히 전달
3. 5단계 워크플로우 (Research → Plan → Review → Implement → Refine) 준수
4. `plan` 작성 시 `plan_kim_MMDD_NN.md` 네이밍
5. "**아직 구현하지 마**" 패턴 활용 — plan 확정 후 구현
6. UI/슬라이드 작업 시 한글 폰트 (Malgun Gothic) 명시

## 9. 자주 쓰는 명령어

```bash
# 슬라이드 재생성
cd C:\Users\User\Documents\cv-final\docs\presentation
node generate.js

# PPTX → PNG (PowerShell + PowerPoint COM)
# PowerShell 스크립트 참조: 이 폴더의 generate.js 옆에 별도 .ps1 만들 것

# 단위 테스트
cd C:\Users\User\Documents\cv-final
python -m pytest project/tests/ -v
```

## 10. 외부 자원

- **SC-FEGAN 리포**: github.com/run-youngjoo/SC-FEGAN
- **CelebAMask-HQ**: github.com/switchablenorms/CelebAMask-HQ
- **segmentation_models_pytorch**: github.com/qubvel/segmentation_models.pytorch
- **pytorch-grad-cam**: github.com/jacobgil/pytorch-grad-cam
- **MediaPipe Tasks**: ai.google.dev/edge/mediapipe/solutions
- **ckpt 다운로드 (Google Drive)**: drive.google.com/open?id=1VPsYuIK_DY3Gw07LEjUhg2LwbEDlFpq1

---

*이 문서는 새 팀원의 Claude가 컨텍스트 없이 작업할 때 참고자료로 활용된다.
모르는 결정이 있다면 우리 팀에 문의할 것 (kim · keonu206@gmail.com).*
