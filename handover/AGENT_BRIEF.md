# AI 에이전트용 1페이지 브리프

> **AI 에이전트가 처음 컨텍스트 받을 때 이 파일 + HANDOVER.md만 읽으면 작업 가능.**
> 사용자에게 새 컨텍스트로 전환 시 이 파일을 제일 먼저 보여주세요.

---

## 🎯 프로젝트 한 줄 정의

**CV Final** = 사진 → MediaPipe 478 랜드마크 → U-Net 분석 → Stable Diffusion Inpaint으로 시술 후 시각화 → ReportLab PDF 견적서 출력.

발표: **2026-06-15** (D-3).
GitHub: `https://github.com/keonU206/cv-final` (Private).
Owner: kim (keonu206@gmail.com).

---

## 🔑 절대 잊으면 안 되는 컨텍스트

### 평가 기준 (박한샘 교수)
1. 문제 정의 + 데이터 — **30%**
2. **모델 설계 + 구현** — **40% (최대 비중)**
3. 성능 분석 (Confusion Matrix, IoU 등) — **15%**
4. 시각화 + 해석 (Grad-CAM 등) — **15%**

### 우리 현재 점수 예상: **87 ~ 94 / 100**

### 핵심 기술 결정
- ❌ **SC-FEGAN 사용 X** (TF 1.15 ↔ Python 3.12 호환 불가)
- ✅ **Stable Diffusion Inpaint (Rombach 2022) 사용** — 동일 task, 더 최신 기술
- ✅ **자체 U-Net 학습 필수** (평가 40% 충족용)

### 핵심 학술 framing
- **"Architecture < Methodology"** — U-Net 강화 plateau (mIoU 0.683). Early Stopping이 가장 효과적. He 2019 CVPR과 일치.
- **모듈식 설계 강점** — GAN backbone 교체 가능 (SC-FEGAN → SD Inpaint). 인접 모듈 model-agnostic.

---

## 📦 학습된 모델 (Drive `/MyDrive/cv-final-ckpts/`)

| 파일 | 성능 | 비고 |
|------|------|------|
| `refinement_best.pt` | val_l1 0.045 | Phase 7-B |
| `unet_v1.pt` | mIoU 0.680 | Baseline |
| `unet_lmguided_best.pt` | mIoU 0.683 | 4채널 (LM heatmap) |
| `unet_attention_best.pt` | mIoU 0.683 | SCSE Attention |

---

## ✅ 완료된 작업 (Phase 별)

- **Phase 1-6**: U-Net 4종 학습 (Baseline/LM/TTA/Attention)
- **Phase 7-A**: 자동 입력 생성 (Bezier 곡선 sketch + mask + color + composer)
- **Phase 7-B**: Refinement Network (작은 U-Net + L1 + VGG19 Perceptual)
- **Phase 7-D**: PDF 견적서 + Streamlit 2-mode UI
- **Phase 7-G**: SD Inpaint (SC-FEGAN 우회, 시술별 PNG 10장 생성)
- **Phase 7-H**: Grad-CAM 시각화 (Selvaraju 2017) — 평가 4번 보강
- **Phase 7-I**: Confusion Matrix + Per-class IoU + Ablation — 평가 3번 보강

**총 GitHub commit**: 30+ (대부분 6/10 폭풍 작업)
**Unit tests**: 50+ PASS

---

## 🛠 진행 중 / 남은 작업

| 작업 | 상태 | 우선순위 |
|------|------|---------|
| Colab 노트북 14 (Grad-CAM) 실행 | 코드 푸시됨, 실행 미완료 | ⭐⭐⭐ |
| Colab 노트북 15 (Confusion Matrix) 실행 | 코드 푸시됨, 실행 미완료 | ⭐⭐⭐ |
| 발표 슬라이드 작성 (11장) | outline만 (`plan_kim_0610_02.md`) | ⭐⭐⭐ |
| 데모 영상 녹화 | 미시작 | ⭐⭐ |
| 리허설 1차/2차 | 6/14 예정 | ⭐⭐ |

---

## 📂 핵심 파일 위치

### 코드
- `app/streamlit_demo.py` — UI (Pre-generated + Live 모드)
- `project/report/pdf_generator.py` — 견적서 PDF
- `project/segmentation/unet.py` — U-Net 빌더
- `project/segmentation/gradcam.py` — Grad-CAM
- `project/segmentation/evaluation.py` — Confusion Matrix + IoU
- `project/refinement/model.py` — Refinement Network
- `project/input_generator/composer.py` — 9채널 SC-FEGAN 입력
- `project/recommender/procedures.yaml` — **시술 DB (가격, mask landmarks)**

### 문서
- `handover/HANDOVER.md` — 종합 인수인계 (필독)
- `handover/SETUP.md` — 환경 셋업 step-by-step
- `handover/CHECKLIST.md` — 남은 작업 체크리스트
- `plan_kim_0610_02.md` — D-5 압축 계획 + 발표 framing template
- `docs/presentation/references.pdf` — 참고문헌 정리

### 데이터
- `samples/` — SD Inpaint 결과 PNG (Drive에서 다운로드)
- `checkpoints/` — 로컬 학습 ckpt (Drive에서 다운로드)
- `/MyDrive/cv-final-ckpts/` — Drive 백업

---

## 🚨 사용자 패턴 (kim) — 알아두면 좋음

- **"ㄱㄱ" / "ㄱㄱㄱ"** = 빠른 진행 OK 신호 (의사결정 완료)
- **"바로 진행"** = 추가 질문 없이 코드 작성
- **"정리해줘"** = 표 형식으로 깔끔히 정리
- **한국어로 답변 선호** (코드 docstring + 답변 본문)
- **이모지 OK** (사용자가 자주 사용)
- 가이드라인 follow 강함 — `~/.claude/rules/guidelines.md` 확인

---

## ⚠ 절대 하지 말 것

1. **공유 설정 변경 X** — Drive 권한 (가이드라인)
2. **git push --force X** — 본인 commit 손실 위험
3. **--no-verify X** — pre-commit hooks 건너뛰지 말 것
4. **--amend X** — 새 commit 만들 것 (가이드라인)
5. **새 .md 파일 임의 생성 X** — 사용자가 명시적 요청 시만
6. **SC-FEGAN 환경 재시도 X** — 시간 낭비 확정 (이미 검증됨)

---

## 🎯 발표 핵심 메시지 (외워둘 것)

> "SC-FEGAN(2019)의 환경 제약을 발견하고 더 최신 SD Inpaint(2022)으로 우회. 본 프로젝트의 **모듈식 설계**는 GAN backbone 교체에 model-agnostic하게 작동. U-Net 시리즈에서 **'Architecture < Training Methodology'** 발견 — Early Stopping이 가장 효과적. **Grad-CAM**과 **Confusion Matrix**로 '설명 가능한 비전 AI' 원칙 만족."

---

## 🛠 즉시 사용 가능한 명령

### 새 환경 셋업
```bash
git clone https://<TOKEN>@github.com/keonU206/cv-final.git
cd cv-final
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
pytest project/tests/ -v  # 50+ PASS 확인
```

### Streamlit 데모
```bash
streamlit run app/streamlit_demo.py
```

### Colab 학습 노트북
```
https://colab.research.google.com/github/keonU206/cv-final/blob/main/notebooks/<filename>.ipynb
```

### PDF 견적서 생성
```python
from project.report import build_estimate, generate_estimate_pdf
items = build_estimate(['nose_tip', 'double_eyelid', 'jaw_v_line'])
generate_estimate_pdf(items, 'output.pdf', patient_name='환자')
```

---

## 📞 Q&A 대비 (외워둘 5가지)

1. **"왜 SC-FEGAN 안 썼나요?"** → TF 1.15 + Python 3.12 protobuf 충돌. SD Inpaint(2022)로 대체.
2. **"변형이 약해 보이는데?"** → identity 보존 trade-off. ControlNet 추가로 정밀 제어 가능.
3. **"U-Net 3개 결과 같던데?"** → Plateau 발견 = 학술적 발견. "Architecture < Methodology".
4. **"Refinement 효과?"** → val_l1 0.045. SD 출력 artifact 제거.
5. **"실제 사용 가능?"** → 의료 보조 도구. 진단/처방 X. 윤리적 한계 인지.

---

## 🎯 다음 작업 시작 시 우선순위

1. **새 팀원이 환경 셋업 중** → `SETUP.md` 단계별 안내
2. **노트북 14/15 실행 중 에러** → 가장 흔한 원인:
   - GH_TOKEN secret 없음 / 공백 포함 → `.strip()` 처리
   - mediapipe 0.10.35 충돌 → mp.tasks API (이미 처리됨)
   - ckpt 경로 없음 → Drive 확인
3. **발표 슬라이드 작성 중** → `plan_kim_0610_02.md` §3 (11장 구조) + §6 (발표 멘트)
4. **PDF/Streamlit 디버깅** → 로컬 `pytest project/tests/test_pdf_generator.py` 먼저

---

## 📚 핵심 참고문헌 (외워둘 10개)

| # | 인용 | 한 줄 |
|---|------|-------|
| 1 | Ronneberger 2015 MICCAI | U-Net 원조 |
| 2 | He 2016 CVPR | ResNet encoder |
| 3 | Roy 2018 MICCAI | SCSE Attention |
| 4 | **Rombach 2022 CVPR** | **Stable Diffusion** |
| 5 | Jo 2019 ICCV | SC-FEGAN (대체된 원 계획) |
| 6 | Kartynnik 2019 | MediaPipe Face Mesh |
| 7 | Johnson 2016 ECCV | Perceptual Loss |
| 8 | Lee 2020 CVPR | CelebAMask-HQ 데이터셋 |
| 9 | **Selvaraju 2017 ICCV** | **Grad-CAM** (평가 4번 핵심) |
| 10 | He 2019 CVPR | Bag of Tricks (Architecture<Methodology) |

향후 강화 (슬라이드 10번):
- Zhang 2023 ICCV (ControlNet) — 정밀 제어
- Wang 2024 (InstantID) — Identity 보존
- Hu 2022 ICLR (LoRA) — Korean Face fine-tuning

---

## ✅ 응답 시작 전 체크

새 컨텍스트로 시작 시:
1. `HANDOVER.md` 의 §3 (현재 상태) 확인 — 어느 Phase 까지 완료?
2. `CHECKLIST.md` 확인 — 오늘 우선순위 작업
3. `plan_kim_0610_02.md` 확인 — 가장 최신 계획
4. 사용자 답변 패턴 인지 (한국어, ㄱㄱ 스타일)
5. 가이드라인 follow (`~/.claude/rules/guidelines.md`)

---

> **사용자 (kim)에게 답변할 때**: 표 형식, 한국어, 간결하게. 평가기준 매핑 우선. 솔직한 한계 인정 + 학술 framing.
