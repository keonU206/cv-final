# 발표 슬라이드 브리핑 — 팀원 배포용

> 외부 cv_proposal_slides 10장 + 우리 plan_v2 통합 가이드
> 작성: 2026-05-18 · 발표일: 2026-05-18

---

## ✅ 결론: 방향성 95% 일치 — 그대로 발표 OK

외부 슬라이드 10장은 우리 plan_v2와 거의 완벽히 일치. U-Net 자체 학습, CelebAMask-HQ 30K, mIoU/Dice 평가, Grad-CAM 해석, 4주 일정, 윤리 고려까지 모두 동일.

### ⚠️ 단 하나 보완 사항 — 클래스 정의

| 슬라이드 5 표시 | 우리 실제 코드 |
|----------------|---------------|
| 6 클래스 = 코·눈·입·턱·눈썹 + bg | 6 클래스 = bg / nose / eye / mouth / skin / (unused) |

→ 슬라이드는 턱·눈썹을 별도 클래스로 표시했지만, **눈썹은 eye에 묶고 턱은 학습 X (후처리에서 skin → 랜드마크로 분리)**. jaw 라벨이 데이터셋에 없어 가짜 라벨보다 후처리가 안전하기 때문.

**Q: "턱이 학습 클래스에 있나요?"**
> *"학습 단계에서는 skin으로 묶고, 추론 후 MediaPipe 랜드마크로 턱 영역을 분리합니다. CelebAMask-HQ에 jaw 라벨이 없어 가짜 라벨보다 후처리가 학술적으로 더 정직합니다."*

---

# 슬라이드별 배경지식 + 예상 Q&A

## 슬라이드 1 — 표지

**발표 시작 한 줄**:
> *"U-Net 자체 학습 + 사전학습 SC-FEGAN으로 성형 시술을 객관적으로 시각화하는 시스템"*

팀명, 팀원 소개, 날짜 (2026.05.18). 10초.

---

## 슬라이드 2 — 목차

8개 챕터 (문제 → 솔루션 → 데이터 → 모델 → 흐름 → 평가 → 해석 → 일정). 학술 발표 표준. 빠르게 넘김.

---

## 슬라이드 3 — 문제 정의 ("장원영? 차은우? How Much?")

**핵심 메시지 2가지**:
- 시술 진단의 주관성 (상담사 경험 의존)
- 시술 후 결과 예측 불가 (2D 합성 수준)

**슬로건 활용**: "장원영? 차은우? How Much?"는 누구나 거울 보며 한 번쯤 하는 생각.

---

## 슬라이드 4 — Task 정의 (3단계 파이프라인)

| Stage | 내용 | 모델 | 학습 |
|-------|------|------|------|
| 1. 얼굴 분석 | MediaPipe 478 landmarks + 비율 10종 | 사전학습 | X |
| 2. 영역 분할 | U-Net 6 클래스 픽셀 분할 | 자체 학습 | ★ O |
| 3. 시각화 | SC-FEGAN Before/After + PDF | 사전학습 | X |

**Q: MediaPipe와 U-Net 차이?**
> *"MediaPipe는 점 좌표 추출(landmark detection), U-Net은 픽셀 영역 분할(semantic segmentation)입니다. 역할이 달라 둘 다 필요합니다."*

---

## 슬라이드 5 — 데이터셋 (CelebAMask-HQ)

| 항목 | 값 |
|------|---|
| 총 이미지 | 30,000장 (1024×1024 또는 256 리사이즈) |
| 원본 라벨 | 19 클래스 (skin, nose, l_eye, r_eye, l_brow, ...) |
| 우리 매핑 | 6 클래스 (bg + 5 부위) |
| 분할 | Train 24K / Val 3K / Test 3K |
| 출처 | Lee et al., CVPR 2020 (MaskGAN 부속) |
| 라이선스 | 비상업 연구 용도 (학술 발표 OK) |

**Q1: 왜 19를 6으로 줄였나?**
> *"우리 task는 시술 부위 5종이라 무관한 라벨(hair, hat, cloth 등)을 배경으로 묶었습니다."*

**Q2: 왜 이 데이터셋?**
> *"세 가지 이유: ① CVPR 2020 학술 표준 신뢰성, ② 30K로 학습/검증 분할 충분, ③ 픽셀 단위 라벨이 segmentation에 적합."*

**Q3: 턱·눈썹이 학습 클래스?** → 위 ⚠️ 섹션 답변 참조.

---

## 슬라이드 6 — U-Net 모델 설계 ★ (40% 점수 핵심)

| 키워드 | 한 줄 설명 |
|--------|----------|
| **ResNet-34 Encoder** | ImageNet 사전학습된 34층 CNN |
| **U-Net Decoder** | Upsample + skip connection으로 원본 크기 복원 |
| **계층적 특징 추출 ★** | 얕은 층(엣지/색) → 깊은 층(의미) 단계적 추상화 |
| **Skip Connection ★** | Encoder의 공간 정보를 Decoder에 직접 전달 |
| **Multi-class 분할** | Softmax 6-way + Cross-Entropy (Combo Loss 일부) |
| **전이 학습** | ImageNet 가중치 활용으로 효율적 학습 |

**외워야 할 한 문장 ★**:
> *"U-Net의 인코더는 단계적 다운샘플링으로 **계층적 특징을 추출**하고, 디코더는 **Skip Connection**으로 공간 정보를 결합해 픽셀 단위 분할을 수행합니다."*

**Q1: 왜 U-Net? 더 최신 모델 없나?**
> *"U-Net은 의료 영상의 표준 segmentation 아키텍처(MICCAI 2015)입니다. 계층적 특징 + skip connection이 수업에서 배운 CNN 구조적 원리에 직접 대응하고, 1달 일정에 학습 가능한 규모입니다."*

**Q2: 왜 ResNet-34?**
> *"ResNet-50은 파라미터 2배라 학습 시간 ↑. ResNet-34는 face parsing에서 검증된 속도/정확도 균형입니다."*

**Q3: 처음부터 학습 안 하는 이유?**
> *"30K로 ResNet 처음부터 학습하면 underfit 가능. ImageNet 사전학습 활용이 일반적 best practice입니다."*

---

## 슬라이드 7 — 시스템 흐름 (E2E 5단계)

| # | 단계 | 기술 | 비고 |
|---|------|------|------|
| 1 | 사진 업로드 | Streamlit UI | — |
| 2 | 랜드마크 + 비율 | MediaPipe Tasks API | 478점 |
| 3 | 추천 엔진 | 룰베이스 3종 | if-else |
| 4 | U-Net 분할 ★ | 자체 학습 segmentation | 6 클래스 |
| 5 | GAN 시각화 | SC-FEGAN 사전학습 | Before/After |

**데모 시술 3종** (외움): **코끝 성형 · 쌍커풀 · 사각턱 + V라인**

**Q: 추천 엔진 왜 ML 아닌가?**
> *"룰베이스 if-else입니다. ① 시술 추천 라벨링 데이터 없음, ② 룰베이스가 설명 가능, ③ 본 프로젝트의 핵심은 segmentation이고 추천은 보조."*

---

## 슬라이드 8 — 성능 분석 (Ablation Study)

**평가 지표 4개**:

| 지표 | 정의 | 용도 |
|------|------|------|
| **mIoU** | 배경 제외 클래스별 IoU 평균 | 메인 지표 |
| **Dice** | F1 유사, 영역 겹침 | 보조 지표 |
| **Per-class IoU** | 클래스별 IoU 분리 | 약한 부위 분석 |
| **Confusion Matrix** | 정답 vs 예측 매트릭스 | 혼동 패턴 |

**Ablation 예상 수치** (슬라이드 8 표):

| 실험 | 예상 mIoU |
|------|-----------|
| Baseline (no aug) | 0.72 |
| + Flip / Rotate | 0.76 (+4%) |
| + Color jitter | 0.78 (+2%) |
| + Cutout / Mixup | 0.81 (+3%) |

*이 수치는 "예상"임을 명시. 실제는 Week 3에 확정.*

**추가 알아둘 개념**:
- **Cutout**: 이미지 일부를 검정색으로 가림 → 부분만 봐도 인식 강건
- **Mixup**: 두 이미지 섞어 새 이미지 생성 → 일반화 ↑

---

## 슬라이드 9 — 시각화 및 해석 (Grad-CAM)

| 도구 | 보여주는 것 | 용도 |
|------|----------|------|
| **Grad-CAM** | "왜 이 영역을 X로 판단했나" heatmap | Explainable AI (15%) |
| **Feature Map** | 각 conv layer 활성화 패턴 | 계층적 특징 확인 |
| **Before / After + Diff** | 시술 전후 픽셀 단위 변화 | 결과 시각화 |

**Grad-CAM 적용 위치**: Encoder bottleneck = `model.encoder.layer4[-1]` (ResNet-34 기준)

**Q: Grad-CAM이 segmentation에 의미 있나?**
> *"원래 분류용이지만 SemanticSegmentationTarget 변형으로 segmentation에 적용 가능. Encoder bottleneck에 hook해서 특정 클래스(예: nose) 예측 영역의 활성화를 시각화합니다."*

**PDF 견적서** (Week 4 작업): 최종 데모에서 시술명 + 가격 + Before/After를 reportlab으로 자동 PDF 생성.

---

## 슬라이드 10 — 일정 + 윤리적 고려

**4주 일정**:

| Week | 기간 | 내용 | 상태 |
|------|------|------|------|
| 1 | 5/8–14 | 환경 셋업 · SC-FEGAN 검증 | ✓ 완료 |
| 2 | 5/19–26 | U-Net 데이터로더 + PoC 학습 | 진행 예정 |
| 3 | 5/27–6/2 | 본격 학습 · Ablation · Grad-CAM | — |
| 4 | 6/3–9 | Streamlit 통합 · 최종 발표 | — |

**윤리적 고려 3가지 ★** (교수님이 좋아할 부분):

| 주제 | 내용 |
|------|------|
| 외모 평가가 아닌 시뮬레이션 | "미의 기준" 정의 X. 학습된 패턴 시각화. |
| 학습 데이터 편향 인지 | CelebAMask-HQ의 인종·성별 분포 한계 명시 |
| 의료 의사결정 대체 불가 | 전문의 상담의 보조 도구. 진단 도구 아님. |

**Q: 이거 위험하지 않나?**
> *"학술 데모임을 명시합니다. 의료 자문이 아닌 시각화 도구로 정의했고, 실제 적용 시 의료법·개인정보보호법 추가 검토가 필요합니다."*

---

# 🎯 통합 답변 — 프로젝트 핵심 한 문장

> *"우리는 MediaPipe로 얼굴 점 478개를 추출해 비율을 분석하고, 룰베이스로 시술을 추천한 뒤, ImageNet 사전학습 ResNet-34 인코더와 U-Net 디코더로 구성된 자체 학습 모델로 얼굴 6 클래스를 픽셀 단위 분할하고, 그 마스크를 사전학습된 SC-FEGAN의 입력으로 사용해 Before/After를 생성하며, mIoU·Dice·Confusion Matrix로 평가하고 Grad-CAM으로 해석합니다."*

→ 슬라이드 10장 전체 요약. 외울 필요는 없고 키워드만 알면 OK.

---

# 📋 외워두기 체크리스트

## 핵심 모델 + 데이터
- ☐ U-Net (Encoder-Decoder + Skip Connection)
- ☐ ResNet-34 (ImageNet 사전학습)
- ☐ SC-FEGAN (ICCV 2019, 사전학습)
- ☐ CelebAMask-HQ (CVPR 2020, 30K, 19→6 클래스)
- ☐ MediaPipe Tasks API (478 landmarks)

## 개념 키워드
- ☐ 계층적 특징 추출 (Hierarchical Feature Extraction)
- ☐ Skip Connection (공간 정보 보존)
- ☐ Transfer Learning (전이 학습)
- ☐ Semantic Segmentation (픽셀 단위 분류)
- ☐ Combo Loss (0.5 × Dice + 0.5 × Cross-Entropy)

## 평가 + 해석
- ☐ mIoU (배경 제외 평균 IoU)
- ☐ Dice Score (F1 유사)
- ☐ Confusion Matrix
- ☐ Ablation Study (Augmentation 비교)
- ☐ Grad-CAM (Encoder bottleneck hook)

## 일정 + 윤리
- ☐ 4주 일정 (Week 1 ✓ / 2~4 진행)
- ☐ 데모 시술 3종: 코끝 · 쌍커풀 · 사각턱+V라인
- ☐ 윤리 3가지: 미의 기준 X / 데이터 편향 / 의료 대체 X

---

# 🚨 절대 하지 말 것

- ✗ "사전학습 모델을 그냥 가져다 썼어요" — 학습 컴포넌트 강조 누락
- ✗ Grad-CAM, IoU 같은 용어 모르는 듯 얼버무리기
- ✗ 데이터셋 출처 (CelebAMask-HQ / CVPR 2020) 못 답하기
- ✗ 왜 U-Net 인지 못 답하기
- ✗ 현재 mIoU 값 없다고 자신감 잃기 (Week 2 PoC는 발표용 아님)
- ✗ 윤리 질문에 "문제 없어요" 단답 — 3가지 모두 짚어야 함

---

# 📚 발표 직전 30분에 다시 볼 것

1. 본 문서 §통합 답변 (한 문장) — 외움
2. 본 문서 §외워두기 체크리스트 — 박스 체크
3. study_guide.pdf §14 (예상 질문 Q1~Q5)
4. glossary.pdf 4페이지 (발표 TOP 10 용어)

---

*kim · 2026-05-18*
