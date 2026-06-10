# Plan kim 0610-01 — D-5 압축 발표 준비

> **버전**: v0.1
> **작성일**: 2026-06-10
> **발표일**: 2026-06-15 (D-5)
> **이전 plan**: `plan_kim_0604_01.md` (Phase 7-A 완료, 7-B/C1 코드까지 완료)

---

## 0. 오늘 (6/10) 완료된 것

| 항목 | 상태 |
|------|------|
| Phase 7-A 자동 입력 생성 | ✅ 완료 (6/4) |
| Phase 7-B Refinement Network 코드 | ✅ **오늘 완료** |
| Phase 7-C1 SC-FEGAN Fine-tuning 코드 | ✅ **오늘 완료** |

### 6/10 신규 산출물

```
project/refinement/
  ├ model.py           ← 작은 U-Net + residual wrapper
  ├ losses.py          ← L1 + VGG19 Perceptual
  ├ data.py            ← Synthetic + Paired Dataset
  ├ train.py           ← 학습 루프 + early stop
  ├ config.yaml
  └ __init__.py

project/scfegan_finetune/
  ├ data_pipeline.py   ← CelebAMask-HQ → 9채널 입력 자동 생성
  ├ train_finetune.py  ← TF 2.x compat 학습 루프 + 폴백
  ├ config_finetune.yaml
  └ __init__.py

project/tests/test_refinement.py  ← 8 tests (smp 환경에서 통과)

notebooks/
  ├ 09_refinement_train.ipynb     ← Colab 학습용 (11 cells)
  └ 10_scfegan_finetune.ipynb     ← Colab 학습용 (14 cells)
```

---

## 1. 발표까지 남은 5일 일정

| 날짜 | 작업 | 산출물 |
|------|------|--------|
| **6/11 (D-4)** | Colab 학습 ⚡ | refinement_best.pt, scfegan_finetuned.ckpt |
| **6/12 (D-3)** | 결과 검증 + Streamlit UI + PDF 견적서 | app/streamlit_demo.py, report PDF |
| **6/13 (D-2)** | 발표 슬라이드 업데이트 (Phase 7 결과 추가) | proposal_slides.pptx v2 |
| **6/14 (D-1)** | 리허설 + 데모 영상 백업 녹화 | demo.mp4 |
| **6/15 (D-0)** | 최종 리허설 → **발표** | — |

---

## 2. 6/11 Colab 학습 — 병렬 실행 가이드

### 2-A. Refinement Network 학습 (2시간)
```python
# notebooks/09_refinement_train.ipynb 실행
# - 데이터: CelebAMask-HQ 500장 (synthetic noise)
# - 2 epochs, batch=8, T4
# - 산출물: project/refinement/checkpoints/refinement_best.pt
```

### 2-B. SC-FEGAN Fine-tuning 학습 (4-6시간)
```python
# notebooks/10_scfegan_finetune.ipynb 실행
# - 데이터: CelebAMask-HQ 2,000장
# - 3 epochs, batch=4, T4
# - 산출물: /content/drive/MyDrive/cv-final-ckpts/scfegan_finetuned/
```

⚠ **권장**: 두 Colab 노트북을 **다른 계정/세션**에서 병렬 실행하여 시간 단축.

⚠ **폴백**: SC-FEGAN 학습이 TF compat 환경에서 실패하면 `train_finetune.py`가 자동으로 pretrained ckpt를 반환. 발표 데모는 항상 가능.

---

## 3. 6/12 발표용 데모 준비

### 3-A. Streamlit UI (`app/streamlit_demo.py`)
- 사진 업로드 → 시술 선택 → 결과 시각화
- 백엔드: U-Net 분석 → recommender → SC-FEGAN inference → Refinement
- 견적 PDF 다운로드 버튼

### 3-B. PDF 견적서 (`project/report/pdf_generator.py`)
- reportlab 기반 (이미 `docs/presentation/generate_*.py` 패턴 보유)
- 시술 항목, 가격 범위 (procedures.yaml), Before/After 이미지 포함

---

## 4. 리스크 & 폴백

| 리스크 | 대응 |
|--------|------|
| Colab Pro 한도 소진 | 다른 Google 계정 + 학습 데이터 축소 (500장) |
| SC-FEGAN TF compat 실패 | 자동 폴백 (pretrained 사용), 발표 framing 변경 ("환경 제약으로 fine-tune 미반영") |
| Refinement 학습 시간 초과 | 1 epoch만 학습 + early stop |
| Streamlit UI 시간 부족 | Jupyter notebook 데모로 대체 (이미 08/09/10 노트북 있음) |
| 발표 슬라이드 시간 부족 | Phase 7 결과는 1-2장 추가만, 나머지 기존 슬라이드 유지 |

---

## 5. 발표 핵심 메시지 (디스커션 framing)

1. **"U-Net 강화는 plateau, GAN 강화로 전환"** — Architecture < Methodology
2. **"3-stage GAN cascade"** — SC-FEGAN(fine-tuned) + Refinement Network = 본격 GAN 강화
3. **"Bezier 곡선 기반 자동 입력 생성"** — 시술별 sketch/color 자동화로 사용자 입력 부담 제거

---

## 6. 체크리스트 (6/15 발표 전까지)

- [ ] 6/11: refinement_best.pt 학습 완료
- [ ] 6/11: scfegan_finetuned.ckpt 학습 완료 (또는 폴백)
- [ ] 6/12: 08_scfegan_integration.ipynb 재실행 (fine-tuned ckpt로)
- [ ] 6/12: Streamlit UI 동작 확인
- [ ] 6/12: PDF 견적서 1개 출력 확인
- [ ] 6/13: 슬라이드 Phase 7 결과 2장 추가
- [ ] 6/14: 리허설 1회 + 데모 영상 녹화
- [ ] 6/15: 최종 리허설 + 발표

---

> **Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>**
