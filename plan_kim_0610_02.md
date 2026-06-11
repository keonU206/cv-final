# Plan kim 0610-02 — D-5 최종 압축 (완성 우선 전략)

> **버전**: v0.1
> **작성일**: 2026-06-10 (D-5)
> **발표일**: 2026-06-15
> **이전 plan**: `plan_kim_0610_01.md`
> **전략**: 완벽 추구 X → **현재 결과로 완성** + **한계/강화 계획 명시**

---

## 0. 핵심 결정 (Locked-in)

| 항목 | 결정 | 사유 |
|------|------|------|
| SC-FEGAN | ❌ 포기 | TF 1.15 ↔ Python 3.12 호환 불가 |
| GAN 대체 | ✅ **SD Inpaint** (Rombach 2022) | PyTorch, 환경 안정 |
| 결과 변형 강도 | 보수적 (낮음) | identity 보존 trade-off |
| 추가 튜닝 | ❌ 안 함 | 발표 5일 남음 — 완성 우선 |
| 발표 framing | "현재 결과 + 한계 + 향후 강화 계획" | 학술 정직성 |

---

## 1. 현재 상태 (모두 동작)

| 컴포넌트 | 상태 | 비고 |
|---------|------|------|
| U-Net Baseline | ✅ mIoU 0.680 | unet_v1.pt |
| U-Net LM-guided | ✅ mIoU 0.683 | unet_lmguided_best.pt |
| U-Net Attention (SCSE) | ✅ mIoU 0.683 | unet_attention_best.pt |
| 자동 입력 생성 (Phase 7-A) | ✅ | sketch + mask + color + composer |
| Refinement Network (Phase 7-B) | ✅ val_l1 0.045 | refinement_best.pt |
| SD Inpaint (Phase 7-G) | ✅ 결과 PNG | runwayml/stable-diffusion-inpainting |
| Streamlit UI | ✅ | app/streamlit_demo.py |
| PDF 견적서 | ✅ | project/report/pdf_generator.py |

**가지고 있는 산출물**:
- 모든 학습 ckpt → `/MyDrive/cv-final-ckpts/`
- 시술별 결과 PNG → `/MyDrive/cv-final-ckpts/samples/`
- 50+ unit tests passed
- GitHub repo: https://github.com/keonU206/cv-final (Private)

---

## 2. 5일 압축 일정 (확정)

| 날짜 | 작업 | 산출물 |
|------|------|--------|
| **6/10 (오늘, D-5)** | plan 작성 + 발표 framing 정리 | plan_kim_0610_02.md |
| **6/11 (D-4)** | Streamlit 정적 이미지 통합 + PDF 견적서 테스트 | 데모 완성 |
| **6/12 (D-3)** | 발표 슬라이드 v1 작성 (11장) | slides v1 |
| **6/13 (D-2)** | 데모 영상 녹화 + 슬라이드 v2 | slides v2 + demo.mp4 |
| **6/14 (D-1)** | 리허설 1차 + 2차 + 백업 영상 | 발표 완전 준비 |
| **6/15 (D-0)** | **발표** | — |

---

## 3. 발표 슬라이드 구성 (11장, 15분)

| # | 제목 | 시간 | 핵심 메시지 |
|---|------|------|------------|
| 1 | 인트로 — 성형 견적 시각화 | 1분 | 문제 정의 |
| 2 | 시스템 아키텍처 | 1분 | 모듈식 파이프라인 |
| 3 | U-Net 분석 (3가지 모델 비교) | 2분 | mIoU plateau 발견 |
| 4 | **"Architecture < Methodology"** 발견 | 1분 | Early Stopping 가장 효과적 |
| 5 | 자동 입력 생성 (Phase 7-A) | 1분 | Bezier 곡선 시술별 가이드 |
| 6 | Refinement Network (Phase 7-B) | 1분 | L1 + VGG19 Perceptual |
| 7 | GAN 우회 — SC-FEGAN → **SD Inpaint** ⭐ | 2분 | 환경 제약 → 더 최신 기술 |
| 8 | 데모 (Streamlit + PDF) | 2분 | **라이브 또는 영상** |
| **9** | **한계 + 향후 강화 계획 ⭐⭐** | **2분** | **학술 정직성** |
| 10 | 결론 + 학습한 것 | 1분 | 모듈식 설계의 가치 |
| 11 | Q&A | 1분 | 5개 예상 질문 준비 |

---

## 4. 한계점 명시 (슬라이드 #9)

### 현재 발견된 한계

1. **SC-FEGAN 환경 제약**
   - TF 1.15 ↔ Python 3.12 비호환
   - 우회: SD Inpaint (Rombach 2022, CVPR)

2. **SD Inpaint 변형 강도 보수적**
   - identity 보존을 위한 의도된 trade-off
   - 시술 효과가 시각적으로 약하게 보일 수 있음

3. **시술별 prompt 정교화 부족**
   - 일반적 영어 prompt 사용
   - 한국인 얼굴 특화 미흡

4. **U-Net mIoU plateau (0.683)**
   - 3가지 강화 모두 동일 결과
   - Architecture만으로는 한계 — 학습 방법론 중요

---

## 5. 향후 강화 계획 (4가지, 슬라이드 #9 핵심) ⭐

### 5-1. ControlNet 도입 (정밀 제어)
**문제**: prompt만으로는 "코를 8px 위로" 같은 정확한 변형 어려움

**해결**: MediaPipe 478 랜드마크를 ControlNet 입력으로 → SD가 정확한 위치 변형

**참고**: Zhang, L., Rao, A., & Agrawala, M. (2023). *Adding Conditional Control to Text-to-Image Diffusion Models*. ICCV.

---

### 5-2. InstantID 또는 IP-Adapter (identity 보존)
**문제**: SD가 가끔 인종/얼굴 형태 바꿈

**해결**: 얼굴 특징 임베딩을 SD에 inject → 같은 사람 보장

**참고**:
- Wang, Q. et al. (2024). *InstantID: Zero-shot Identity-Preserving Generation in Seconds*. arXiv:2401.07519
- Ye, H. et al. (2023). *IP-Adapter: Text Compatible Image Prompt Adapter for Text-to-Image Diffusion Models*. arXiv:2308.06721

---

### 5-3. Korean Face Dataset Fine-tuning (도메인 적응)
**문제**: SD가 일반 얼굴 데이터로 학습 → 한국인 자연스러움 부족

**해결**: AI-Hub 한국인 얼굴 데이터 1만+ 장으로 LoRA fine-tuning

**참고**:
- Hu, E. J. et al. (2022). *LoRA: Low-Rank Adaptation of Large Language Models*. ICLR.
- AI-Hub. (2023). *한국인 얼굴 이미지 데이터셋*. https://aihub.or.kr

---

### 5-4. Multi-seed Ensemble + 사용자 선택 UI
**문제**: 단일 seed로 가끔 어색한 결과

**해결**: 시술별 5개 seed 자동 inference → Streamlit에 5장 표시 → 사용자가 선택

**구현 비용**: 1-2일 (기존 코드 확장)

---

## 6. 학술 framing template (발표용)

### 슬라이드 #7 (GAN 우회) 발표 멘트
```
"본 프로젝트는 SC-FEGAN(Jo & Park 2019, ICCV)을 GAN backbone으로 
계획했으나, TF 1.15 의존성으로 Python 3.12 환경에서 inference 
구축이 어려웠습니다. 동일한 task — mask-based facial inpainting — 을 
수행하는 더 최신 모델 Stable Diffusion Inpainting(Rombach et al. 
2022, CVPR)으로 우회했습니다. 이는 본 프로젝트의 **모듈식 설계** 
강점을 보여줍니다 — 자동 입력 생성, Refinement Network, 견적서 
모듈은 GAN backbone에 model-agnostic하게 작동합니다."
```

### 슬라이드 #9 (한계 + 향후) 발표 멘트
```
"현재 결과는 보수적 변형이라는 한계가 있으나, 이는 identity 
보존을 우선한 의도된 trade-off입니다. 향후 4가지 강화를 통해 
정밀한 제어와 강한 identity 보존을 동시 달성 가능합니다:

1. ControlNet 도입 — 랜드마크 기반 정밀 변형
2. InstantID — 강한 identity 보존
3. Korean Face LoRA — 한국인 자연스러움
4. Multi-seed UI — 사용자 선택 가능

이러한 강화는 모두 본 프로젝트의 **모듈식 설계** 위에서 
backbone만 교체하면 즉시 적용 가능합니다."
```

---

## 7. Q&A 대비 — 예상 질문 5개 + 답

### Q1. "왜 SC-FEGAN 안 썼나요?"
A: TF 1.15 의존, Python 3.12에서 protobuf 충돌. 더 최신 기술 SD Inpaint(2022)로 대체.

### Q2. "변형이 약해 보이는데?"
A: identity 보존을 위한 의도된 보수적 변형. ControlNet/InstantID 추가하면 정밀 제어 가능.

### Q3. "U-Net 3개 결과가 같던데?"
A: mIoU 0.683 plateau는 학술적 발견. "Architecture < Training Methodology" — 현대 CV 트렌드와 일치 (Bag of Tricks, He 2019).

### Q4. "Refinement Network 효과는?"
A: val_l1 0.045 달성. SD 출력의 artifact 제거 + 경계 자연스러움.

### Q5. "실제 사용 가능성?"
A: 의료 보조 도구 — **의사 상담의 시각적 보조**. 진단/처방 X.

---

## 8. 산출물 위치 (최종 정리)

```
GitHub: https://github.com/keonU206/cv-final
└── 코드 + 노트북 13개 + 50 tests

Drive: /MyDrive/
├── cv-final-ckpts/
│   ├── refinement_best.pt          (94 MB, Phase 7-B)
│   ├── unet_attention_best.pt      (94 MB)
│   ├── unet_lmguided_best.pt       (94 MB)
│   ├── unet_v1.pt                  (94 MB)
│   └── samples/
│       ├── all_sd_results.png      ← 메인 슬라이드 ⭐
│       ├── beforeafter_*.png × 3   ← 시술별 슬라이드 ⭐
│       ├── sd_final_*.png × 3      ← Streamlit/PDF
│       ├── sd_only_*.png × 3       ← Refinement 비교
│       └── original_before.png     ← 입력 자리
└── SC-FEGAN-ckpt/ (사용 안 함, 보관)
```

---

## 9. 다음 행동 (6/11 ~ 6/15)

### 6/11 (D-4)
- [ ] `app/streamlit_demo.py` 수정 — 정적 이미지 표시 모드 추가
- [ ] PDF 견적서에 SD 결과 통합 테스트
- [ ] Drive 백업 파일들 로컬 다운로드

### 6/12 (D-3)
- [ ] PowerPoint 또는 Google Slides 작성 (11장)
- [ ] 슬라이드 1~6 (이론/모델)
- [ ] 슬라이드 7~9 (GAN/데모/한계+계획)

### 6/13 (D-2)
- [ ] 데모 영상 녹화 (Streamlit + PDF 출력, 백업용)
- [ ] 슬라이드 디자인 마무리
- [ ] 팀원과 분담 확정

### 6/14 (D-1)
- [ ] 리허설 1차 (전체 시간 측정)
- [ ] 리허설 2차 (Q&A 연습)
- [ ] 백업 영상 USB/Drive 양쪽

### 6/15 (D-0)
- [ ] 최종 리허설 (발표 1시간 전)
- [ ] **발표**

---

## 10. 리스크 + 폴백

| 리스크 | 대응 |
|--------|------|
| 발표 당일 Streamlit 다운 | 백업 영상 재생 |
| Q&A 답 막힘 | 한계점 솔직히 인정 + 향후 계획 명시 |
| 슬라이드 시간 초과 | 슬라이드 #6, #10 단축 |
| Demo 영상 재생 실패 | PDF 견적서로 결과 대체 표시 |

---

> **Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>**
