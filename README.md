# CV Final · 성형 견적 시각화 시스템

> 2026 컴퓨터비전 기말 프로젝트 (3인 팀)
> SC-FEGAN + 자체 학습 U-Net을 결합한 자동 성형 시각화 + 견적 산출 파이프라인

---

## 파이프라인

```
사진 업로드
   ↓ MediaPipe 478 landmarks
   ↓ 규칙 기반 추천 (project/recommender)
   ↓
[Phase 7-A] 자동 Sketch / Color / Mask 생성 (project/input_generator)
   ↓
[Phase 7-C1] SC-FEGAN (fine-tuned on CelebAMask-HQ 2,000장)
   ↓
[Phase 7-B] Refinement Network (U-Net + L1 + Perceptual)
   ↓
[U-Net 분석] 부위별 segmentation (project/segmentation)
   ↓
Streamlit UI + PDF 견적서
```

## 폴더 구조

```
cv-final/
├── project/
│   ├── input_generator/      # 9채널 SC-FEGAN 입력 자동 생성 (Phase 7-A)
│   ├── segmentation/         # U-Net 학습 (Baseline / LM / Attention)
│   ├── recommender/          # 규칙 기반 시술 추천
│   ├── refinement/           # Refinement Network (Phase 7-B)
│   ├── scfegan_finetune/     # SC-FEGAN Fine-tuning (Phase 7-C1)
│   └── tests/                # 50+ unit tests
├── notebooks/                # Colab 학습 / 평가
│   ├── 03_unet_train.ipynb
│   ├── 05_lmunet_train.ipynb
│   ├── 06_tta_eval.ipynb
│   ├── 07_attention_train.ipynb
│   ├── 08_scfegan_integration.ipynb
│   ├── 09_refinement_train.ipynb
│   └── 10_scfegan_finetune.ipynb
├── docs/presentation/        # 발표 자료
└── plan_kim_*.md             # 단계별 계획서
```

## 주요 결과

| Phase | 모델 | 결과 |
|-------|------|------|
| 1 | Baseline U-Net | mIoU 0.680 |
| 2 | LM-guided U-Net (4채널) | mIoU 0.683 |
| 5 | TTA (Hflip + Rot±10°) | 0.683 (보합) |
| 6 | Attention U-Net (SCSE) | 0.683 (보합) |
| **7-A** | Bezier 자동 입력 생성 | ✅ 완료 |
| **7-B** | Refinement Network | 학습 예정 |
| **7-C1** | SC-FEGAN Fine-tuning | 학습 예정 |

핵심 발견: **U-Net 강화 plateau → GAN 강화(7-B/C1)로 전환**

## Colab 학습

```bash
# notebook 09: Refinement Network (≈2시간)
# notebook 10: SC-FEGAN Fine-tuning (≈4-6시간)
# pretrained ckpt: SC-FEGAN.ckpt → MyDrive/SC-FEGAN-ckpt/
```

## License

- 본 프로젝트 코드: 교육용 (학내 발표 한정)
- SC-FEGAN: CC BY-NC 4.0 (Jo & Park 2019 ICCV)
- CelebAMask-HQ: 학술 연구용 (Lee et al. 2020 CVPR)
