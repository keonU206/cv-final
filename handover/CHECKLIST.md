# 남은 작업 체크리스트 (D-3, 2026-06-12 기준)

> 발표: **2026-06-15 (D-3)**
> 모든 작업 6/14 자정 전 완료 목표.

---

## 🔥 우선순위 1 — 오늘(6/12) 끝낼 것

### A. Colab 노트북 실행 (학습/평가 담당)

#### A-1. 노트북 14 (Grad-CAM) — 30분
```
https://colab.research.google.com/github/keonU206/cv-final/blob/main/notebooks/14_gradcam.ipynb
```

**준비**:
- [ ] Colab Secrets에 `GH_TOKEN` 등록 (Notebook access ON)
- [ ] Runtime → T4 GPU 선택
- [ ] Drive 마운트
- [ ] `unet_attention_best.pt` Drive에 있는지 확인

**실행**:
- [ ] Runtime → Run all
- [ ] 셀 2 (사진 업로드)에서 영문 파일명 사진 업로드
- [ ] 셀 7 (시각화) 결과 확인 — 4 클래스 × 3 컬럼

**산출물 (`/MyDrive/cv-final-ckpts/samples/`)**:
- [ ] `gradcam_all_classes.png` — 4 클래스 × 3 컬럼
- [ ] `gradcam_presentation.png` — 1 + 4 가로 비교
- [ ] `gradcam_{nose,eye,mouth,skin}_overlay.png` × 4
- [ ] `gradcam_{nose,eye,mouth,skin}_heatmap.png` × 4

#### A-2. 노트북 15 (Confusion Matrix + Ablation) — 30분
```
https://colab.research.google.com/github/keonU206/cv-final/blob/main/notebooks/15_confusion_matrix.ipynb
```

**준비**:
- [ ] 3가지 U-Net ckpt Drive에 있는지 확인
  - `unet_v1.pt` (Baseline)
  - `unet_lmguided_best.pt`
  - `unet_attention_best.pt`

**실행**:
- [ ] Runtime → Run all
- [ ] 데이터셋 다운로드 (CelebAMask-HQ, 첫 실행만 ~5분)
- [ ] val 50장 평가 (~10분)

**산출물**:
- [ ] `confusion_matrices_all.png` — 모델별 5x5 Confusion Matrix
- [ ] `per_class_iou_comparison.png` — Bar chart
- [ ] `model_comparison_summary.png` — mIoU/Dice 비교
- [ ] `ablation_table.csv` — 표

### B. 결과 PNG 로컬 다운로드 (UI/발표 담당)

- [ ] Drive `cv-final-ckpts/samples/` → `cv-final/samples/` 폴더로 다운로드
- [ ] 다음 파일들 다 있는지 확인:
  - [ ] `original_before.png`
  - [ ] `sd_final_*.png` × 3
  - [ ] `beforeafter_*.png` × 3
  - [ ] `all_sd_results.png`
  - [ ] `gradcam_*.png` × 8 (노트북 14 실행 후)
  - [ ] `confusion_matrices_all.png` (노트북 15 실행 후)
  - [ ] `per_class_iou_comparison.png`
  - [ ] `model_comparison_summary.png`

### C. Streamlit 데모 검증 (UI 담당)

- [ ] `streamlit run app/streamlit_demo.py` 실행
- [ ] **Pre-generated 모드** (기본) 검증:
  - [ ] 시술 3종 자동 선택됨
  - [ ] Before/After 이미지 표시됨
  - [ ] 견적 메트릭 3개 (최소/평균/최대) 표시
  - [ ] **PDF 다운로드 버튼** 클릭 → 한글 견적서 다운로드 확인
- [ ] **Live 모드** 검증:
  - [ ] 사진 업로드 → 랜드마크 추출 OK
  - [ ] 시뮬레이션 실행 → 결과 표시 (placeholder)

---

## 🟡 우선순위 2 — 6/13 (D-2)

### D. 발표 슬라이드 작성 (11장)

`plan_kim_0610_02.md` 의 §3 슬라이드 구성 참조.

| # | 제목 | 자료 | 담당 |
|---|------|------|------|
| 1 | 인트로 | (없음) | |
| 2 | 데이터셋 | CelebAMask-HQ 통계 | |
| 3 | 시스템 아키텍처 | 다이어그램 | |
| 4 | U-Net 4종 + plateau | `model_comparison_summary.png` | |
| 5 | **Grad-CAM ⭐** | `gradcam_presentation.png` | |
| 6 | 자동 입력 + Refinement | sketch + mask + composer | |
| 7 | **GAN 우회 ⭐** | `all_sd_results.png` | |
| 8 | **Confusion Matrix ⭐** | `confusion_matrices_all.png` + ablation | |
| 9 | 데모 | 영상 또는 라이브 | |
| 10 | **한계 + 향후 강화** | (텍스트만) | |
| 11 | 결론 + Q&A | (없음) | |

**도구**: Google Slides (실시간 동시 편집) 또는 PowerPoint

체크리스트:
- [ ] 슬라이드 v1 완성 (11장)
- [ ] 각 슬라이드 1분~2분 시간 측정
- [ ] 폰트: 본문 24pt, 제목 36pt, 캡션 14pt
- [ ] 색상: NAVY (#1E2761), ACCENT (#F96167)
- [ ] 한글 폰트: 맑은 고딕 또는 노토 산스
- [ ] 참고문헌 슬라이드 (10번 안에) 포함

### E. 데모 영상 녹화 (백업용)

- [ ] OBS 또는 ZOOM 녹화로 Streamlit 데모 영상 (3-5분)
- [ ] 흐름: 사진 업로드 → 시술 선택 → 결과 표시 → PDF 다운로드
- [ ] mp4 형식, USB + Drive 둘 다 저장
- [ ] 발표 당일 Streamlit 다운 대비

---

## 🟢 우선순위 3 — 6/14 (D-1)

### F. 리허설

- [ ] **리허설 1차** (오전, 1시간)
  - [ ] 발표 전체 시간 측정 (목표 15분)
  - [ ] 슬라이드 흐름 점검
  - [ ] 데모 사전 셋업

- [ ] **리허설 2차** (저녁, 1시간)
  - [ ] Q&A 예상 질문 5개 답변 연습
  - [ ] 발표자 분담 확인

### G. 마지막 점검

- [ ] **백업 파일 USB 준비**:
  - [ ] 슬라이드 PPT + PDF 둘 다
  - [ ] 데모 영상 mp4
  - [ ] PDF 견적서 샘플 1개

- [ ] **장비 점검**:
  - [ ] 노트북 충전기
  - [ ] HDMI 어댑터 (Mac 사용 시)
  - [ ] 마이크 (필요 시)

---

## 🎯 6/15 (D-0) 발표 당일

### H. 발표 1시간 전

- [ ] Streamlit 미리 launch (한 번 새로고침 테스트)
- [ ] 슬라이드 풀스크린 테스트
- [ ] 데모 영상 백업 USB 꽂아두기
- [ ] PDF 견적서 미리 출력 (배포용?)
- [ ] 마지막 리허설 (10분)

### I. 발표 (15분)

발표자 분담 예시:
- 1-3분: 인트로 + 데이터 + 아키텍처 (발표자 1)
- 4-7분: U-Net 분석 + Grad-CAM (발표자 2)
- 8-12분: GAN 우회 + Confusion Matrix (발표자 3)
- 13-15분: 데모 + 한계 + Q&A (발표자 1)

### J. Q&A

- [ ] 5가지 예상 질문 답변 준비됨 (HANDOVER.md §8)
- [ ] 한계점 솔직히 인정 + 향후 계획 명시
- [ ] "모르겠다" 답변 시 "조사해서 메일로 답변드리겠습니다"

---

## 📊 평가 항목 매핑 체크

발표 후 다시 확인 — 각 평가 항목 우리가 다뤘는가?

### 1. 문제 정의 + 데이터 (30%)
- [ ] 슬라이드 1, 2에서 task + 데이터셋 명확히 제시
- [ ] CelebAMask-HQ 인용 (Lee 2020 CVPR)

### 2. 모델 설계 + 구현 (40%)
- [ ] U-Net 계층적 구조 설명 (encoder/decoder)
- [ ] ResNet-34 backbone 언급
- [ ] Combo Loss + Perceptual Loss 언급
- [ ] SCSE Attention 언급
- [ ] SD Inpaint 우회 학술 framing

### 3. 성능 분석 (15%)
- [ ] Confusion Matrix 표시 (슬라이드 8)
- [ ] Per-class IoU bar chart
- [ ] Augmentation 적용 명시
- [ ] mIoU plateau 학술 해석

### 4. 시각화 + 해석 (15%)
- [ ] Grad-CAM 시각화 (슬라이드 5)
- [ ] Selvaraju 2017 ICCV 인용
- [ ] Before/After 시각화
- [ ] "설명 가능한 비전 AI" 키워드 명시

---

## ⚠ 리스크 + 폴백

| 상황 | 폴백 |
|------|------|
| Colab GPU 한도 소진 | 다른 계정 (학습 담당자 본인 계정) |
| 노트북 14, 15 실행 실패 | kim에게 즉시 알리고 디버깅 |
| Streamlit 발표 당일 다운 | 데모 영상 재생 (백업 mp4) |
| 슬라이드 PPT 충돌 | PDF 백업으로 발표 |
| 질문에 답 못함 | "더 조사해서 메일로 답변드리겠습니다" |

---

## 📞 긴급 연락

- **kim (Owner)**: keonu206@gmail.com
- 코드 관련 문의 → GitHub Issues (또는 카톡)
- 학습 관련 문의 → 학습 담당자 (Colab 권한 있는 사람)

---

**오늘 우선 끝낼 것 (6/12)**:
1. ✅ A. 노트북 14, 15 Colab 실행
2. ✅ B. 결과 PNG 로컬 다운로드
3. ✅ C. Streamlit 데모 검증

→ 모두 완료되면 6/13에 슬라이드 + 영상 작업 시작.
