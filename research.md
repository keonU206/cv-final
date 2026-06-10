# Research — 성형 견적 시각화 프로젝트

> 작성일: 2026-05-15
> 작성자: kim (CV 기말 발표 프로젝트)
> 목표: SC-FEGAN을 시각화 엔진으로 활용한 **분석/추천형 성형 견적 시스템** 설계를 위한 사전 조사
> 시나리오 확정: **2번 (얼굴 분석 + 시술 추천 + SC-FEGAN 시각화)**

---

## 0. TL;DR — 의사결정에 영향을 주는 핵심 사실

1. **SC-FEGAN은 사용자가 그리는 마스크/스케치/컬러가 필수.** 자동 견적 시스템을 만들려면 이 입력들을 랜드마크에서 **자동 생성**하는 파이프라인이 필요하다.
2. **TF 1.13 + 최신 GPU는 거의 비호환.** Python 3.7 + CUDA 9/10 + cuDNN 7.4가 정식 조합. RTX 30/40 시리즈는 별도 작업(nvidia-tensorflow 포크)이 필요하고 RTX 40은 사실상 불가. **→ Plan B로 Google Colab(또는 CPU 추론) 준비 필수.**
3. **얼굴 랜드마크는 MediaPipe Face Mesh(468점)가 최적.** dlib(68점)보다 정밀하고, 시술별 마스크 영역을 픽셀 단위로 제어 가능.
4. **출력 해상도 한계 512×512, CelebA-HQ 편향.** 한국인 얼굴/저조도 사진에선 결과 품질 저하 가능 → 입력 정규화 + 결과 후처리 필요.
5. **백업 모델 후보로 DiffFace-Edit(2025) 검토 가치 있음.** 8개 얼굴 영역 편집을 지원하는 최신 디퓨전 기반 데이터셋/모델.

---

## 1. SC-FEGAN 분석 (코드 레벨 정독 결과)

### 1.1 리포 구조
```
SC-FEGAN/
├── demo.py           # PyQt5 GUI 메인 진입점
├── model.py          # TF 모델 정의 (Generator만, Discriminator는 추론에 불필요)
├── ops.py            # gated_conv / gated_deconv 연산
├── demo.yaml         # 설정 (INPUT_SIZE=512, BATCH_SIZE=1, CKPT_DIR)
├── requirements.txt  # TF 1.13.0rc2, PyQt5 5.12, opencv-python 4.0.0.21
├── ui/
│   ├── ui.py           # Qt Designer 자동 생성 UI
│   └── mouse_event.py  # 마우스 그리기 (마스크/스케치/컬러)
├── utils/config.py   # YAML 설정 로더
└── samples/          # 예제 입력 이미지 5장
```

### 1.2 네트워크 아키텍처
- **Generator**: U-Net 형태 + **Gated Convolution** (DeepFillv1 기반)
  - Encoder: 7단계 다운샘플링 (`gconv1_ds` ~ `gconv7_ds`), 채널 64→128→256→512→512→512→512
  - Bottleneck: 4단계 **Dilated Convolution** (rate=2,4,8,16) — 넓은 receptive field 확보
  - Decoder: 7단계 업샘플링 + skip connection (encoder feature와 concat)
  - 출력: `tanh` → [-1, 1] 범위, 512×512×3
- **Discriminator**: SN-PatchGAN (코드에는 없음 — 학습 코드 미공개, 추론에만 필요한 G만 제공)

### 1.3 입력 텐서 포맷 (가장 중요)
`model.py:88-91`에서 입력 9채널을 concat한다:

| 채널 | 내용 | 정규화 | 값 범위 |
|------|------|--------|---------|
| [:3] | RGB 이미지 (마스크 영역 0으로) | `img/127.5 - 1` | [-1, 1] |
| [3:4] | 스케치 (이진 라인) | 마스크와 곱셈 | {0, 1} |
| [4:7] | 컬러 스트로크 (BGR) | `color/127.5 - 1` | [-1, 1] |
| [7:8] | 마스크 (1=inpaint 영역) | — | {0, 1} |
| [8:9] | 노이즈 (마스크 영역만 random) | `cv2.randn / 255` | {0, 1} |

> **핵심 인사이트**: GUI를 거치지 않고 코드로 9채널 입력을 직접 만들어 `model.demo(batch)`만 호출하면 추론 가능. PyQt5 GUI는 **완전히 우회**해도 됨.

### 1.4 사전학습 모델
- **다운로드**: Google Drive (README의 링크) — `SC-FEGAN.ckpt.data-00000-of-00001`, `.index`, `.meta` 3개 파일
- **배치 위치**: `ckpt/SC-FEGAN.ckpt` (demo.yaml의 `CKPT_DIR`이 가리킴)
- **학습 데이터**: CelebA-HQ (서양인 위주, 정면/조명 균일) → **한국인 얼굴 편향 위험**
- **라이선스**: CC 4.0 BY-NC (비상업적 학술 용도만) — 발표 프로젝트는 OK, 상용화는 불가

### 1.5 환경 요구사항 (CRITICAL)
공식 TensorFlow 매트릭스 기준:
- **Python**: 3.5 ~ 3.7 (3.8+ 비호환)
- **CUDA**: 9.0 (TF 1.13 빌드 기준) / 10.0 도 일부 가능
- **cuDNN**: 7.4
- **OS**: Ubuntu 18.04 (개발자 환경), Windows 가능하지만 PyQt5+TF1.13 조합 트러블 多

**최신 GPU에서의 호환성 문제**:
- RTX 30 시리즈: `nvidia-tensorflow` (NVIDIA가 유지하는 TF1 포크, CUDA 11 지원) 사용 시 가능
- RTX 40 시리즈: CUDA 12.x 필요 → TF1.x **사실상 불가**
- 결론: 최신 노트북 GPU에서 그대로 못 돌릴 가능성이 매우 높음

**대안 환경**:
1. **Google Colab (강력 추천)** — Python 3.7 + 구버전 TF 설치 가능, T4 GPU 무료, 발표 직전 데모 안정성 ↑
2. CPU 추론: 512×512 이미지 1장당 추론 시간 약 10~30초 (CPU 사양에 따라). 발표 데모로는 답답하지만 동작은 함
3. Docker (`nvidia/cuda:10.0-cudnn7`) + 호스트 GPU passthrough
4. WSL2 + 구버전 CUDA — Windows 환경에서 시도해볼 수 있음

---

## 2. 얼굴 랜드마크 검출 컴포넌트 비교

### 2.1 후보 비교

| 항목 | dlib (68점) | MediaPipe Face Mesh (468/478점) | FAN (Face Alignment Network) |
|------|-------------|---------------------------------|-------------------------------|
| 랜드마크 수 | 68 | 468 (+10 iris = 478) | 68 (3D 가능) |
| 정확도 (300W mean error) | 3.78 | **3.12** | **2.96** (최고) |
| 속도 | 가장 빠름 (CPU) | 빠름 (모바일 30~100 FPS) | 무거움 (GPU 필요) |
| 출력 | 2D | **3D** (z좌표 포함) | 2D/3D |
| 설치 난이도 | 보통 (CMake 필요) | 쉬움 (`pip install mediapipe`) | 어려움 |
| 한국인 얼굴 강건성 | 보통 | 좋음 (다국가 데이터 학습) | 좋음 |

### 2.2 권장: **MediaPipe Face Mesh**

이유:
1. **랜드마크 밀도**: 시술 영역(코끝, 콧방울, 윗눈꺼풀, 입꼬리 등)을 픽셀 단위로 분리 가능. dlib 68점으론 부족.
2. **설치 단순**: `pip install mediapipe` 한 줄. TF1.13 환경과 분리해서 별도 venv로 운영 가능.
3. **3D 정보**: 얼굴 포즈 보정(정면 정규화)에 활용 가능 → 비스듬한 사진도 처리.

**핵심 랜드마크 인덱스 참고**:
- 눈: 33(왼쪽 외각), 263(오른쪽 외각), 133/362(내각)
- 입: 13(윗입술 중앙), 14(아랫입술 중앙), 61(왼 입꼬리), 291(오른 입꼬리)
- 코: 1(코끝), 168(미간), 2/98/327(콧방울)
- 얼굴 윤곽: 72개 점 (jaw line, 황금비 분석에 유용)

### 2.3 dlib 68점 영역 매핑 (백업/참고용)
| 부위 | 인덱스 |
|------|--------|
| Jaw/Chin | 0–16 |
| Right brow | 17–21 |
| Left brow | 22–26 |
| Nose | 27–35 |
| Right eye | 36–41 |
| Left eye | 42–47 |
| Mouth | 48–67 |

---

## 3. 시술 DB 설계

### 3.1 주요 시술 카테고리 + 견적 (2025 기준, 원화 환산)

> 출처: SeoulCosmeticSurgery, ClinicSeoul, PlacidWay 등 (USD → KRW 환율 1,350원 가정)

| 카테고리 | 세부 시술 | 영향 영역 | MediaPipe 랜드마크 | 예상 견적 (KRW) |
|---------|----------|-----------|---------------------|------------------|
| 코 | 코끝 성형 (tip) | 코끝 + 콧방울 | 1, 2, 98, 327, 19 | ₩4M ~ ₩8M |
| 코 | 풀 라이노 (콧대+코끝) | 콧대 전체 | 168, 6, 197, 195, 5, 4, 1 | ₩6M ~ ₩11M |
| 눈 | 쌍커풀 (절개/비절개) | 윗눈꺼풀 | 246, 161, 160, 159, 158, 157, 173 (좌) / 미러 (우) | ₩1.1M ~ ₩3.4M |
| 눈 | 앞트임 / 뒤트임 | 눈 안쪽/바깥쪽 | 133, 362 (앞) / 33, 263 (뒤) | ₩2M ~ ₩4M |
| 턱 | 사각턱 + V라인 | 양쪽 턱각 | 172, 136, 150, 149, 176, 148, 152 (jaw line) | ₩6M ~ ₩18M |
| 이마 | 이마 보형물 | 이마 영역 | 10, 109, 67, 103, 54, 21, 162, 127 | ₩6M ~ ₩13M |
| 입술 | 입술 축소/확대 | 입술 전체 | 61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291 | ₩2M ~ ₩5M |
| 광대 | 광대 축소 | 광대뼈 영역 | 234, 93, 132, 58, 172 (좌측) | ₩5M ~ ₩12M |

### 3.2 추천 로직 (룰베이스 v1)

발표용으로는 **얼굴 비율 분석 룰베이스**가 ML 학습 없이 즉시 적용 가능하고 설명도 쉬움.

**기준 비율**:
- 삼정오안 (三停五眼): 얼굴 세로 3등분 + 가로 5등분 (한국 미용성형 고전 기준)
- 황금비 1:1.618 — 얼굴 너비:길이, 미간:코길이 등
- E라인 (Ricketts line): 코끝-턱끝 연결선과 입술 거리

**추천 알고리즘 예**:
```
if 콧대길이 / 인중길이 < 0.95: 추천 = "콧대 연장"
if 윗눈꺼풀높이 < 평균-2σ:    추천 = "쌍커풀"
if 턱각 > 120°:                추천 = "사각턱"
if 미간거리 > 한쪽눈너비 * 1.1: 추천 = "앞트임"
```

각 추천에 **신뢰도 점수**(0~1)와 **예상 비용 범위**를 부여.

### 3.3 데이터 출처 신뢰도 주의
- 실제 클리닉 가격은 광고/패키지/환자 사정에 따라 크게 다름
- 발표용 데이터로 활용 시 **"평균 추정치"** 임을 명시하고, 출처를 슬라이드 각주에 표기 권장
- 한국공정거래위원회, 한국소비자원 데이터도 추가 확인 가능

---

## 4. 파이프라인 설계

### 4.1 End-to-End 흐름
```
[사용자 얼굴 사진]
       │
       ▼
[1. 얼굴 검출 + 정규화]   ← MediaPipe Face Detection
       │  (얼굴 영역 크롭, 정면 정렬, 512×512 리사이즈)
       ▼
[2. 랜드마크 추출]        ← MediaPipe Face Mesh (478점)
       │
       ▼
[3. 비율 분석]            ← 삼정오안, 황금비, E라인 계산
       │
       ▼
[4. 시술 추천 엔진]       ← 룰베이스 (비율 임계값 기반)
       │  → [(시술명, 신뢰도, 견적, 영향 영역)]
       ▼
[5. 시술별 자동 입력 생성] ← 4-1 ~ 4-3 (아래)
       │  → (mask, sketch, color, noise)
       ▼
[6. SC-FEGAN 추론]        ← TF 1.13 모델 호출
       │
       ▼
[7. Before/After 합성 + 견적 UI]
```

### 4.2 핵심 난제: 자동 마스크/스케치 생성

#### 4.2.1 마스크 자동 생성
시술별 랜드마크 인덱스 → Convex hull or Bezier curve → 모폴로지 dilate로 여유 영역 확보:
```python
# 예: 코끝 마스크
nose_tip_pts = landmarks[[1, 2, 98, 327, 19]]
hull = cv2.convexHull(nose_tip_pts)
mask = np.zeros((512, 512), dtype=np.uint8)
cv2.fillPoly(mask, [hull], 255)
mask = cv2.dilate(mask, kernel_15x15)  # 경계 여유
```

#### 4.2.2 스케치 자동 생성 — **가장 어려운 부분**
SC-FEGAN의 스케치는 "이상적 모양의 가이드 라인". 자동 생성 전략 후보:
- **(A) 변형 스케치**: 원본 랜드마크를 이상적 비율로 이동한 후 그 점들을 잇는 라인 그리기. 가장 직관적이고 구현 쉬움. 한계: 자연스러운 곡선 어려움
- **(B) Active Shape Model**: 평균 얼굴 형상 + 변형 파라미터. 정교하지만 학습 데이터 필요
- **(C) Hybrid**: 자동 생성 + 사용자 미세조정 슬라이더 (예: 코끝 높이 +5% 슬라이더)
- **권장**: (A) → (C)로 점진 발전

#### 4.2.3 컬러 스트로크
- 얼굴 평균 피부색 추출 (마스크 외부 영역) → 마스크 내부에 동일 색 채우기
- 입술/눈 같은 색이 다른 부위는 해당 부위 평균색 사용

### 4.3 모듈 책임 분리 (소스 코드 구조 제안)
```
project/
├── face_analyzer/      # MediaPipe 랜드마크 + 비율 분석
├── recommender/        # 룰베이스 시술 추천 + 견적 매핑
├── input_generator/    # 마스크/스케치/컬러 자동 생성
├── scfegan_wrapper/    # TF1.13 모델 추론 (별도 venv)
├── ui/                 # Streamlit 데모
└── data/
    ├── procedures.yaml # 시술 DB
    └── samples/        # 테스트 얼굴 이미지
```

> **TF1.13 환경 격리 팁**: `scfegan_wrapper`만 별도 venv/conda env에 두고, 다른 모듈은 모던 Python 3.10+ 환경에서. 둘 사이는 파일/REST로 통신.

---

## 5. 데모/UI 형태

### 5.1 후보 비교

| 옵션 | 장점 | 단점 |
|------|------|------|
| **Streamlit** | Python only, 빠른 프로토타입, before/after 슬라이더 위젯 풍부 | 실시간성 약함 |
| Gradio | HuggingFace 친화, 공유 쉬움 | 커스텀 UI 자유도 낮음 |
| Flask + JS | 자유도 최고 | 개발 시간 ↑ |
| PyQt5 (SC-FEGAN 기본) | 이미 코드 있음 | 데모 시 화면 공유 어색, 모던 UX 아님 |

### 5.2 권장: **Streamlit**

발표 데모 시나리오:
1. 사진 업로드
2. "분석 시작" 버튼 → 랜드마크 시각화 + 추천 시술 리스트 표시
3. 시술 선택 → before/after 슬라이더로 결과 비교
4. 견적 총합 표시 + PDF 출력 (선택)

### 5.3 발표 시 데모 안정성 팁
- 추론은 사전 캐시: 발표용 샘플 얼굴 2~3장은 미리 추론해두고 즉시 재생
- 라이브 추론도 보여주되 1장만, 백업으로 캐시 결과 준비
- Colab에서 돌릴 경우 발표 직전 런타임 재시작 + 모델 로드 미리

---

## 6. 리스크 및 대안 모델

### 6.1 발표 직전 터질 수 있는 리스크 TOP 5

| 리스크 | 가능성 | 영향 | 완화책 |
|--------|--------|------|--------|
| TF1.13 GPU 환경 안 잡힘 | **HIGH** | CRITICAL | Colab Plan B 사전 준비, CPU 추론도 동작 확인 |
| ckpt 다운로드 (Google Drive) 실패 | MED | HIGH | 발표 1주 전 미리 다운로드 + 백업 |
| 한국인 얼굴에서 출력 품질 저하 | HIGH | MED | 입력 정규화(조명/각도) 강화, 발표용 샘플은 잘 나오는 것만 선별 |
| 자동 스케치 생성 결과가 부자연스러움 | HIGH | MED | (C) Hybrid 옵션 — 슬라이더로 사용자 보정 |
| 추론 시간이 길어 데모 흐름 끊김 | MED | LOW | 캐시 + 로딩 애니메이션 |

### 6.2 SC-FEGAN 백업/대체 모델 후보

만약 SC-FEGAN이 끝까지 안 돌면 **즉시 갈아탈 수 있는** 대안:

1. **DiffFace-Edit** (arXiv 2601.13551, 2025) — 디퓨전 기반, **8개 얼굴 영역 부분 편집** 지원. 데이터셋 + 코드 공개. **최우선 대안.**
2. **InstructPix2Pix** (HuggingFace Diffusers) — 텍스트 명령어로 편집 ("make the nose smaller"). 정밀도 낮지만 즉시 사용 가능. 자동 견적 시스템 컨셉은 살릴 수 있음.
3. **StyleGAN3 + e4e/HyperStyle inversion** — 고해상도 + 얼굴 속성 편집 latent direction. 학습된 latent direction을 코/눈/턱에 매핑. 구현 복잡.
4. **DragGAN** — 사용자가 시작점/끝점을 클릭해서 변형. 직관적이지만 자동화는 별도 작업 필요.
5. **MaskGAN (CelebAMask-HQ)** — semantic mask 기반 편집. 우리 시나리오와 가장 유사한 컨트롤 방식.

> **권장 우선순위**: SC-FEGAN → DiffFace-Edit → InstructPix2Pix.
> 발표용 데모는 **시각 임팩트가 최우선**이므로, 1주 진행 후 SC-FEGAN 환경이 안정되지 않으면 즉시 DiffFace-Edit으로 피벗.

### 6.3 윤리/법적 고려
- 사진 동의: 발표용 샘플 얼굴은 본인 사진 or Unsplash 등 라이선스 명확한 이미지 사용
- "성형 견적"이라는 단어가 의료 광고 규제와 충돌 가능 → 발표 시 **"학술 데모, 의료 자문 아님"** 명시
- 라이선스: SC-FEGAN CC 4.0 BY-NC → 학술 발표는 OK, 상용/공개 배포 시 주의

---

## 7. 다음 단계 (plan.md에서 결정할 것들)

다음 단계인 `plan_kim_MMDD_NN.md` 작성 시 결정해야 할 항목:

1. **개발 환경 확정**: 로컬 (TF1.13 setup 시도) vs Colab (안전) 선택

2. **추천 엔진**: 룰베이스 vs ML — 발표 시간/난이도 트레이드오프
3. **자동 스케치 전략**: (A)/(B)/(C) 중 어느 것부터 구현
4. **데모 UI 범위**: Streamlit 기본 / 슬라이더 보정 / PDF 출력
5. **백업 모델 사전 검증 여부**: SC-FEGAN과 병행해 DiffFace-Edit도 작은 PoC 만들지?
6. **샘플 얼굴 데이터셋**: 본인/팀원 사진 vs 공개 데이터셋
7. **발표 데모 시나리오**: 어떤 케이스를 보여줄지 (코, 눈, 턱 등 3개 정도 추천)
8. **일정 분할**: 환경 셋업 → 랜드마크 모듈 → 추천 엔진 → SC-FEGAN 추론 래퍼 → UI → 통합

---

## 부록 A. 참고 자료

### SC-FEGAN
- 논문: [arXiv:1902.06838](https://arxiv.org/abs/1902.06838) (ICCV 2019)
- 리포: [github.com/run-youngjoo/SC-FEGAN](https://github.com/run-youngjoo/SC-FEGAN)
- 기반 (gated conv): [DeepFillv1](https://github.com/JiahuiYu/generative_inpainting)

### 얼굴 랜드마크
- [MediaPipe Face Mesh 공식 문서](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_mesh.md)
- [MediaPipe 478 landmarks reference](https://www.sanderdesnaijer.com/blog/mediapipe-face-mesh-landmarks)
- [dlib 68 landmarks tutorial (PyImageSearch)](https://pyimagesearch.com/2017/04/03/facial-landmarks-dlib-opencv-python/)
- [수술 환경에서의 얼굴 랜드마크 평가 (2025)](https://arxiv.org/html/2507.18248v1)

### 환경/호환성
- [TensorFlow 빌드 매트릭스](https://www.tensorflow.org/install/source)
- [nvidia-tensorflow (TF1 fork)](https://github.com/NVIDIA/tensorflow)
- [TF 1.15 on RTX 30 가이드 (Puget Systems)](https://www.pugetsystems.com/labs/hpc/How-To-Install-TensorFlow-1-15-for-NVIDIA-RTX30-GPUs-without-docker-or-CUDA-install-2005/)

### 한국 성형 견적
- [Korean Plastic Surgery 2025 Cost Guide (PlacidWay)](https://www.placidway.com/answer-detail/566921/How-much-does-plastic-surgery-cost-in-South-Korea)
- [Seoul Cosmetic Surgery — 전체 가격 리스트](https://seoulcosmeticsurgery.com/plastic-surgery-cost-in-korea/)
- [Clinic Seoul — 시술별 가격 (2026)](https://www.clinicseoul.net/korea-plastic-surgery-price-list/)

### 대안 모델
- [DiffFace-Edit (arXiv 2601.13551)](https://arxiv.org/abs/2601.13551) — 2025년, 디퓨전 기반 얼굴 부분 편집
- [StyleGAN survey (arXiv 2212.09102)](https://arxiv.org/abs/2212.09102)
- [InstructPix2Pix (HuggingFace)](https://huggingface.co/docs/diffusers/api/pipelines/pix2pix)

---

*이 문서는 plan.md 작성을 위한 기초 자료다. 구현 결정은 plan.md에서, 구현 자체는 plan 확정 후에 진행한다.*
