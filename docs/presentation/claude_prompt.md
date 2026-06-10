# 새 Claude 세션 시작 시 — 복붙 프롬프트 템플릿

> 새로 합류하는 팀원이 본인 Claude 세션 시작 시 **아래 내용을 그대로 첫 메시지로 붙여넣기**.
> Claude는 이 한 번의 메시지로 프로젝트 전체 상황을 파악할 수 있다.

---

## 📋 사용법 (3가지 옵션)

### 옵션 A — 짧은 부트스트랩 (권장)

> 가장 빠른 방법. Claude가 `HANDOVER.md`를 직접 읽음.

```
나는 컴퓨터 비전 기말 프로젝트 팀에 새로 합류했어.

프로젝트 작업 디렉터리:
C:\Users\User\Documents\cv-final\

먼저 다음 두 파일을 읽고 전체 컨텍스트를 파악해줘:
1. docs/presentation/HANDOVER.md — 핸드오버 문서
2. plan_kim_0515_02.md — 현재 활성 plan (v2)

읽고 나서, 너가 이해한 내용을 한 문단으로 요약해주고
"무엇을 도와드릴까요?" 라고 물어줘.

아직 어떤 구현도 하지 마. 컨텍스트 파악만 먼저.
```

### 옵션 B — 슬라이드 작업 전용

> 발표자료(슬라이드)만 다듬을 때 사용.

```
나는 컴퓨터 비전 기말 프로젝트의 발표자료 담당이야.

작업 디렉터리: C:\Users\User\Documents\cv-final\

상황:
- 5/18 제안 발표는 이미 끝남
- 다음 마일스톤: 6/15 최종 발표 (Week 4 작업)
- 5/18 슬라이드 베이스: docs/presentation/proposal_slides.pptx (8장)
- 슬라이드 생성 코드: docs/presentation/generate.js (pptxgenjs)

먼저 docs/presentation/HANDOVER.md 를 읽고 프로젝트 전체 컨텍스트 파악해줘.

그 다음 docs/presentation/proposal_slides.pptx 와 generate.js 를 검토해서
- 디자인 톤(Midnight Executive 팔레트)
- 슬라이드 구조 (8장)
- 한글 폰트 (Malgun Gothic)
가 어떻게 구성되어 있는지 파악해줘.

아직 어떤 변경도 하지 마. 파악만 먼저.
```

### 옵션 C — Week 2 U-Net 학습 전용

> 모델 학습 담당 (B) 이 본인 Claude 시작할 때.

```
나는 컴퓨터 비전 기말 프로젝트의 세그멘테이션 모델 학습 담당이야.

작업 디렉터리: C:\Users\User\Documents\cv-final\

먼저 다음 3개 파일을 읽고 컨텍스트 파악:
1. docs/presentation/HANDOVER.md — 전체 핸드오버
2. plan_kim_0515_02.md — v2 plan (특히 §3 U-Net 모듈 설계, §4 학습 설정)
3. research.md — 사전 조사 (관련 자료 링크)

내 작업 범위:
- project/segmentation/ 디렉터리 전체 (현재 비어있음)
- notebooks/03_unet_train.ipynb (없음, 새로 만들어야 함)
- notebooks/04_gradcam_viz.ipynb (없음)
- 데이터셋: CelebAMask-HQ (30K장, github.com/switchablenorms/CelebAMask-HQ)
- 라이브러리: segmentation_models_pytorch (이미 결정됨)
- 평가: mIoU, Dice, Confusion Matrix, Ablation
- 환경: Colab T4 GPU + PyTorch

5단계 워크플로우 따라줘:
1. Research → research_unet.md 작성
2. Plan → plan_kim_MMDD_NN.md 작성 (구현 X)
3. Review (내가 메모)
4. Implement
5. Refine

지금 1단계만 시작. CelebAMask-HQ 데이터셋 구조 + segmentation_models_pytorch
사용법 + U-Net 학습 best practice 조사해서 research_unet.md 에 정리.
아직 코드 작성 X.
```

---

## 🔑 핵심 정보 (직접 복붙)

새 Claude가 HANDOVER.md를 못 읽는 환경이면 아래 핵심 정보만 복붙:

```
[프로젝트] 성형 견적 시각화 시스템 (컴퓨터 비전 기말, 3인 팀)

[Vision Task] Image Segmentation (메인) + Image Generation (보조)

[파이프라인]
1. MediaPipe Tasks API → 478 landmarks
2. 룰베이스 추천 (procedures.yaml 기반)
3. ★ U-Net 자체 학습 (CelebAMask-HQ 30K장, 5 부위)
4. SC-FEGAN 사전학습 GAN (시각화)
5. Grad-CAM + Before/After + PDF 견적서

[결정된 사항 — 다시 논의 X]
- U-Net: segmentation_models_pytorch 라이브러리 (ResNet-34 encoder)
- 데이터: CelebAMask-HQ (CVPR 2020)
- 평가: mIoU, Dice, Per-class IoU, Confusion Matrix, Ablation
- 해석: Grad-CAM on encoder bottleneck
- 환경: Colab T4 GPU + TF 2.x compat + Keras 2 강제 + tf-keras
- mediapipe==0.10.21 (legacy solutions API 회피, Tasks API 사용)

[알려진 함정]
- Python 3.12 + TF 1.x 비호환 → TF 2.x compat 모드 사용
- tf.contrib 없음 → sys.modules monkey-patch (02 노트북 cell-4)
- yaml.load(f) → yaml.safe_load(f) 필수 (PyYAML 6+)
- mediapipe.solutions 없음 → tasks API 사용
- Keras 3 + tf.layers.conv2d 비호환 → TF_USE_LEGACY_KERAS=1
- 한글 폰트: Malgun Gothic 또는 NanumGothic

[일정] Week 1 ✅ / Week 2 U-Net PoC / Week 3 본격 학습 / Week 4 통합 + 슬라이드
[발표] 6/15 최종 평가

[작업 디렉터리] C:\Users\User\Documents\cv-final\

[5단계 워크플로우]
Research (research.md) → Plan (plan_MMDD_NN.md) → Review → Implement → Refine
"아직 구현하지 마" 패턴 활용.
```

---

## 📞 문의

기존 팀원: kim · keonu206@gmail.com

기존 Claude 세션의 컨텍스트가 필요하면:
- `research.md` · `plan_kim_0515_02.md` · `HANDOVER.md` 3개 파일 확인
- 그것도 부족하면 기존 팀원에게 문의

## ⚠️ 새 Claude에게 주의시킬 점

1. **5단계 워크플로우** 준수 (계획 없이 구현 들어가지 말 것)
2. `plan_kim_MMDD_NN.md` 네이밍 규칙
3. 이미 결정된 사항을 다시 묻지 말 것 (HANDOVER §2 참조)
4. 알려진 함정 (§5) 무시하고 시간 낭비 X
5. 한글 폰트 / Colab 환경 / TF 호환성 주의
