# Plan — 성형 견적 시각화 프로젝트 (v0.1)

> 작성일: 2026-05-15
> 작성자: kim
> 기반 문서: [research.md](research.md)
> 발표일: **2026-06-15 (≈ 1개월, 4주 + 며칠 버퍼)**
> 팀: **3명** (역할 분담 아래 참조)
>
> ⚠️ 이 plan은 **검토 전 v0.1**. 구현 시작은 사용자가 메모/주석 단 뒤 v0.2로 업데이트 → 최종 승인 후.

---

## 0. 확정된 결정사항 (research.md 후 의사결정)

| 항목 | 결정 |
|------|------|
| 시나리오 | 분석/추천형 (사진 → 분석 → 추천 시술 → SC-FEGAN 시각화) |
| 개발 환경 | **Google Colab (T4 GPU 가정)** |
| 추천 엔진 | **룰베이스** (얼굴 비율 임계값 기반 if-else) |
| 자동 스케치 | **Hybrid** — 자동 변형(A) 베이스 + 사용자 슬라이더 보정 |
| 데모 UI | **Streamlit L3** — 업로드 + before/after + 슬라이더 + **PDF 견적서 출력** |
| 백업 모델 | **DiffFace-Edit PoC 병행** (1명 담당) |
| 샘플 얼굴 | **본인·팀원 + 공개 데이터셋(FFHQ 일부) 둘 다** |
| 데모 시술 3종 | **코 (코끝/콧대) + 쌍커풀 + 사각턱** |

---

## 1. 역할 분담 (3명, A/B/C로 표기)

| 역할 | 담당 | 메인 책임 | 보조 |
|------|------|----------|------|
| **A: 모델/엔진** | (kim?) | SC-FEGAN Colab 환경 + 추론 래퍼<br>DiffFace-Edit 백업 PoC | 발표용 모델 비교 슬라이드 |
| **B: 분석/추천** | | MediaPipe 랜드마크 + 비율 분석<br>룰베이스 추천 엔진<br>자동 마스크/스케치 생성 | 시술 DB(`procedures.yaml`) 큐레이션 |
| **C: UI/통합** | | Streamlit 데모 + 슬라이더<br>PDF 견적서 (`reportlab`)<br>통합 테스트 + 발표 자료 | 샘플 얼굴 데이터 수집 |

> 누가 A/B/C 할지는 plan 검토 시 채워 넣을 것.

---

## 2. 디렉터리 구조 (확정)

```
cv-final/
├── research.md
├── plan_kim_0515_01.md        ← 이 파일
├── SC-FEGAN/                  ← 원본 리포 (수정 최소화)
│   └── ckpt/SC-FEGAN.ckpt.*   ← 사전학습 모델 (구글드라이브에서 다운)
│
├── project/                   ← 우리 코드 루트
│   ├── face_analyzer/
│   │   ├── __init__.py
│   │   ├── landmarks.py        # MediaPipe 래퍼 → 478 landmarks
│   │   ├── normalize.py        # 얼굴 크롭 + 정면 정렬 + 512 리사이즈
│   │   └── ratios.py           # 황금비/삼정오안/E라인 계산
│   ├── recommender/
│   │   ├── __init__.py
│   │   ├── rules.py            # 임계값 기반 추천 로직
│   │   └── procedures.yaml     # 시술 DB (이름/마스크 인덱스/견적/임계값)
│   ├── input_generator/
│   │   ├── __init__.py
│   │   ├── mask.py             # 랜드마크 → convex hull → mask (512×512)
│   │   ├── sketch.py           # 자동 변형 라인 + 슬라이더 강도 인자
│   │   └── color.py            # 평균 피부톤 스트로크
│   ├── scfegan_wrapper/
│   │   ├── __init__.py
│   │   └── infer.py            # 9채널 텐서 빌드 + model.demo 호출
│   ├── diffface_wrapper/       ← 백업 (A 담당)
│   │   └── infer.py
│   ├── ui/
│   │   ├── streamlit_app.py
│   │   └── pdf_export.py       # reportlab 견적서 생성
│   └── tests/
│       ├── test_landmarks.py
│       ├── test_rules.py
│       └── test_mask.py
│
├── notebooks/
│   ├── 01_env_check.ipynb       # Colab 환경 검증
│   ├── 02_scfegan_smoke.ipynb   # SC-FEGAN 추론 PoC
│   └── 03_pipeline_e2e.ipynb    # 전체 파이프라인 통합 테스트
│
├── data/
│   ├── samples_team/            ← 팀원 사진 (git 제외)
│   ├── samples_public/          ← FFHQ 일부 (10장)
│   └── outputs/                 ← 추론 결과 저장
│
└── docs/
    ├── presentation/            ← 발표 슬라이드
    └── demo_script.md           ← 발표 데모 시나리오
```

> **TF1.13 환경 격리**: `scfegan_wrapper`는 **Colab 노트북 내부에서만 import**하고, 다른 모듈(`face_analyzer`, `recommender` 등)은 Python 3.10+ 환경에서 동작. Streamlit이 두 환경 사이를 잇는다.

---

## 3. 모듈 상세 설계

### 3.1 `face_analyzer/`
**역할**: 사진 → 478 랜드마크 + 비율 지표

```python
# landmarks.py
def detect_landmarks(image: np.ndarray) -> np.ndarray:
    """(H, W, 3) BGR → (478, 2) pixel coords. 얼굴 못 찾으면 raise."""

# normalize.py
def normalize_face(image: np.ndarray) -> tuple[np.ndarray, dict]:
    """크롭 + 정면 정렬 + 512×512 리사이즈. meta(원본 좌표↔정규화 좌표 매핑) 반환."""

# ratios.py
def compute_ratios(landmarks_478) -> dict:
    """리턴 예:
    {
      'face_h_w_ratio': 1.42,         # 얼굴 세로/가로
      'forehead_ratio': 0.31,         # 상안부 비율
      'midface_ratio':  0.34,
      'lowerface_ratio':0.35,
      'eye_width_ratio': 1.08,        # 미간/한쪽 눈너비
      'nose_length':    0.32,         # 정규화된 코 길이
      'nose_tip_height': 0.18,
      'jaw_angle_deg':  118.5,        # 양쪽 평균 턱각
      'e_line_offset':  -0.02,        # 입술이 E라인보다 안쪽(-)/바깥(+)
    }
    """
```

### 3.2 `recommender/`

**`procedures.yaml` 스키마**:
```yaml
- id: nose_tip
  name_ko: "코끝 성형"
  name_en: "Tip rhinoplasty"
  region: nose
  mask_landmarks: [1, 2, 19, 98, 327]   # MediaPipe 인덱스
  dilate_px: 15
  price_krw_min: 4000000
  price_krw_max: 8000000
  trigger:
    metric: nose_tip_height
    op: lt
    threshold: 0.15
  description: "코끝이 처져 보이는 경우 추천"

- id: double_eyelid
  name_ko: "쌍커풀"
  ...

- id: jaw_v_line
  name_ko: "사각턱 + V라인"
  ...
```

**`rules.py` 의사코드**:
```python
def recommend(ratios: dict, procedures: list) -> list[Recommendation]:
    out = []
    for p in procedures:
        metric = ratios[p['trigger']['metric']]
        if eval(f"{metric} {p['trigger']['op']} {p['trigger']['threshold']}"):
            confidence = compute_confidence(metric, p['trigger']['threshold'])
            out.append(Recommendation(
                procedure=p,
                confidence=confidence,
                price_range=(p['price_krw_min'], p['price_krw_max']),
                reasoning=f"{p['trigger']['metric']}={metric:.2f} → {p['description']}"
            ))
    return sorted(out, key=lambda r: -r.confidence)
```

### 3.3 `input_generator/`

**`mask.py`**:
```python
def make_mask(landmarks_478, procedure: dict, size: int = 512) -> np.ndarray:
    """리턴: (512, 512, 1) uint8 binary mask"""
    pts = landmarks_478[procedure['mask_landmarks']].astype(np.int32)
    hull = cv2.convexHull(pts)
    mask = np.zeros((size, size), dtype=np.uint8)
    cv2.fillPoly(mask, [hull], 255)
    k = procedure['dilate_px']
    mask = cv2.dilate(mask, np.ones((k, k), np.uint8))
    return mask[..., None]
```

**`sketch.py`** — Hybrid 핵심:
```python
def make_sketch(landmarks_478, procedure: dict,
                intensity: float = 0.5,  # 슬라이더 값 0~1
                size: int = 512) -> np.ndarray:
    """랜드마크를 이상적 비율로 'intensity'만큼 이동시킨 후 라인 그리기."""
    target_pts = compute_ideal_position(landmarks_478, procedure, intensity)
    sketch = np.zeros((size, size), dtype=np.uint8)
    for (p0, p1) in get_sketch_edges(procedure):
        cv2.line(sketch, tuple(target_pts[p0]), tuple(target_pts[p1]), 255, 1)
    return sketch[..., None]
```

**`color.py`**:
```python
def make_color_stroke(image, mask, procedure):
    """마스크 외부의 평균 피부톤을 마스크 내부 stroke로 채움."""
    skin = image[mask[..., 0] == 0]
    avg_bgr = np.median(skin, axis=0).astype(np.uint8)
    stroke = np.zeros_like(image)
    stroke[mask[..., 0] > 0] = avg_bgr
    return stroke
```

### 3.4 `scfegan_wrapper/infer.py`

```python
class SCFEGANInferencer:
    def __init__(self, ckpt_path):
        # TF 1.13 세션 초기화 (Colab에서만 import)
        self.config = Config('demo.yaml')
        self.model = Model(self.config)
        self.model.load_demo_graph(self.config)

    def infer(self, image, mask, sketch, color) -> np.ndarray:
        """9채널 텐서 빌드 → model.demo → 512×512×3 BGR uint8 출력."""
        image_n = image/127.5 - 1
        color_n = color/127.5 - 1
        noise = np.random.randint(0, 256, (512,512,1), dtype=np.uint8) / 255
        batch = np.concatenate([
            image_n[None],
            sketch[None],
            color_n[None],
            mask[None]/255,
            noise[None]
        ], axis=3).astype(np.float32)
        out = self.model.demo(self.config, batch)
        out = ((out[0] + 1) * 127.5).astype(np.uint8)
        return out
```

### 3.5 `ui/streamlit_app.py` (mock)

```
┌─────────────────────────────────────────────┐
│  성형 견적 시각화 데모                       │
├─────────────────────────────────────────────┤
│  [📷 사진 업로드]                            │
│  ─────────────────────────────────────       │
│  [원본]                  [랜드마크 시각화]    │
│                                              │
│  추천 시술:                                  │
│   ☑ 코끝 성형     신뢰도 0.82  ₩4~8M        │
│   ☐ 쌍커풀       신뢰도 0.45  ₩1.1~3.4M    │
│   ☑ 사각턱       신뢰도 0.71  ₩6~18M       │
│                                              │
│  강도 슬라이더:                              │
│   코끝   [====●----] 50%                    │
│   사각턱 [===●-----] 40%                    │
│                                              │
│  [✨ 시뮬레이션 실행]                        │
│  ─────────────────────────────────────       │
│  [Before]               [After]              │
│                                              │
│  총 견적: ₩10~26M                            │
│  [📄 PDF 견적서 다운로드]                    │
└─────────────────────────────────────────────┘
```

### 3.6 `ui/pdf_export.py`
- 라이브러리: **`reportlab`** (한글 지원, 이미지 임베드)
- 견적서 구성: 헤더(로고/날짜) + 사용자 사진 before/after + 추천 시술 표 + 합계 + 푸터(학술 데모 안내)

---

## 4. 주차별 마일스톤

### Week 1 (5/15 ~ 5/22) — 환경 + 스켈레톤
| 담당 | 태스크 | 산출물 | DoD |
|------|--------|--------|-----|
| A | Colab에 Python 3.7 + TF 1.13 환경 세팅, SC-FEGAN 리포 + ckpt 로드 | `01_env_check.ipynb` | model.demo가 더미 입력에 출력 반환 |
| A | SC-FEGAN smoke test (샘플 1장으로 수동 마스크 추론) | `02_scfegan_smoke.ipynb` | 출력 이미지 1장 |
| B | MediaPipe 환경 세팅 + 478점 랜드마크 검출 | `face_analyzer/landmarks.py` | 샘플 5장에서 시각화 OK |
| B | 비율 계산 모듈 (`ratios.py`) 기본 지표 5개 | `ratios.py` + `test_ratios.py` | 단위 테스트 통과 |
| C | `procedures.yaml` 3종 (코/쌍커풀/사각턱) 초안 | `procedures.yaml` | 임계값/견적 채움 |
| C | Streamlit 빈 골격 (업로드 + 표시만) | `streamlit_app.py` v0 | localhost 실행 OK |

### Week 2 (5/23 ~ 5/29) — 모듈 개별 구현
| 담당 | 태스크 | DoD |
|------|--------|-----|
| A | `scfegan_wrapper/infer.py` 클래스화 + Colab에서 함수 호출 가능 | 함수 1개로 추론 가능 |
| A | DiffFace-Edit PoC 작은 노트북 1개 | 코 부위 변형 1장 성공 |
| B | `recommender/rules.py` — 시술 3종 추천 로직 | 단위 테스트 3개 통과 |
| B | `input_generator/mask.py` — 시술 3종 마스크 자동 생성 | 시각화로 확인 |
| B | `input_generator/sketch.py` v1 — intensity=0.5 고정으로 변형 라인 | 시각화 OK |
| C | Streamlit에 랜드마크 시각화 + 추천 시술 리스트 표시 | 데모 영상 30초 |

### Week 3 (5/30 ~ 6/5) — 통합 + 슬라이더 + PDF
| 담당 | 태스크 | DoD |
|------|--------|-----|
| A+C | E2E 파이프라인 노트북 (`03_pipeline_e2e.ipynb`) | 사진→추천→추론→결과 1장 통과 |
| B | `sketch.py` v2 — intensity 슬라이더 반영 | 0.0~1.0 변화 시 결과 점진 변화 |
| C | Streamlit 슬라이더 위젯 추가 + 추론 트리거 | 슬라이더 동작 |
| C | `pdf_export.py` v1 — 견적서 PDF 생성 | 샘플 PDF 1장 |
| All | 팀 사진 + FFHQ 샘플 10장 추론 결과 검토 | 결과 갤러리 |

### Week 4 (6/6 ~ 6/12) — 발표 준비 + 버퍼
| 담당 | 태스크 | DoD |
|------|--------|-----|
| All | 발표 데모 시나리오 리허설 (1회 / 일) | 5분 안에 완주 |
| C | 발표 슬라이드 (10~15장) — 문제 정의 / 방법 / 결과 / 한계 | 슬라이드 완성 |
| A | 발표용 캐시된 추론 결과 3세트 준비 (코/눈/턱) | 즉시 재생 가능 |
| All | 폴백 시나리오: Colab 끊김 / 인터넷 끊김 대비 | 로컬 PDF + 영상 백업 |

### Buffer (6/13 ~ 6/14)
- 마지막 리허설, 버그 픽스, 슬라이드 수정

### 발표일 6/15

---

## 5. 리스크 관리 (research.md 6.1 기반 액션 매핑)

| 리스크 | 트리거 시점 | 대응 액션 |
|--------|-----------|----------|
| TF1.13 Colab 환경 깨짐 | Week 1 Day 2까지 환경 안 잡힘 | A가 `nvidia-tensorflow` + CUDA 10 명시 설치 스크립트 시도, 그래도 안 되면 CPU 추론으로 전환 |
| ckpt 다운로드 실패 (구글드라이브 quota) | 언제든 | A가 Week 1에 ckpt를 팀 공용 드라이브/Dropbox에 백업 |
| 한국인 얼굴 출력 품질 저하 | Week 3 결과 검토 시 | 입력 정규화 강화 (조명 보정, 정면 회전), 발표 샘플은 잘 나오는 것만 선별 |
| 자동 스케치 부자연스러움 | Week 2 말 | 슬라이더 기본값 조정, 디폴트 intensity 낮게 (0.3) |
| Streamlit 추론 시간 느림 | Week 3 | 발표용 결과 사전 캐시 (`@st.cache_data` + 디스크) |
| SC-FEGAN 끝까지 안 됨 | Week 2 말 결정점 | DiffFace-Edit으로 즉시 피벗 (A의 PoC 활용) |

**Week 2 말 GO/PIVOT 결정점**: SC-FEGAN E2E 1장이라도 못 나오면 DiffFace-Edit으로 메인 갈아탐.

---

## 6. 발표 시나리오 (5~7분 데모)

```
[0:00] 문제 정의: "성형 상담 전 사전 시뮬레이션의 필요성" (슬라이드 2장)
[0:30] 기술 개요: SC-FEGAN + MediaPipe + 룰베이스 (슬라이드 3장)
[1:30] 라이브 데모:
        1) 팀원 A 사진 업로드
        2) 랜드마크 + 비율 표시
        3) 추천 시술 3개 자동 표시
        4) 슬라이더 조절하며 before/after
        5) PDF 견적서 출력 시연
[4:00] 결과 갤러리 (사전 캐시된 케이스 3장)
[5:00] 한계 + 윤리 (저해상도, CelebA 편향, 의료 자문 아님)
[6:00] Q&A
```

**폴백**:
- 인터넷 끊김 → 미리 녹화된 데모 영상 1분 30초
- Colab 끊김 → 로컬에 저장된 결과 이미지 + PDF 표시

---

## 7. 체크리스트 (구현 시작 후 사용)

### Week 1
- [ ] A: Colab 환경 노트북 작성
- [ ] A: SC-FEGAN ckpt 다운로드 + 백업
- [ ] A: smoke test 1장 성공
- [ ] B: MediaPipe 설치 + 478점 시각화
- [ ] B: 비율 5개 계산 + 단위 테스트
- [ ] C: `procedures.yaml` 3종
- [ ] C: Streamlit 빈 골격

### Week 2
- [ ] A: `scfegan_wrapper.infer()` 함수화
- [ ] A: DiffFace-Edit PoC
- [ ] B: `rules.py` + 3종 추천 단위 테스트
- [ ] B: 마스크 3종 자동 생성
- [ ] B: 스케치 v1 (고정 intensity)
- [ ] C: Streamlit 랜드마크 + 추천 리스트

### Week 3
- [ ] A+C: E2E 노트북 통과
- [ ] B: 스케치 v2 (슬라이더 반영)
- [ ] C: Streamlit 슬라이더
- [ ] C: PDF 견적서 v1
- [ ] All: 결과 갤러리 검토

### Week 4
- [ ] All: 리허설 3회
- [ ] C: 발표 슬라이드
- [ ] A: 캐시 결과 3세트
- [ ] All: 폴백 영상/이미지 백업

### 발표 직전
- [ ] Colab 런타임 재시작 + 모델 로드
- [ ] 인터넷 백업 (휴대폰 핫스팟)
- [ ] PDF 견적서 샘플 출력 확인

---

## 8. plan 확정 후 다음 단계

1. 사용자가 이 파일에 직접 주석/메모 (예: `<!-- TODO: X 추가 -->` 또는 인라인 메모)
2. "메모 반영해서 업데이트해줘. **아직 구현하지 마**" 라고 요청 → v0.2
3. v0.2 최종 승인 후 "plan대로 전부 구현, Week 1부터 시작" 지시
4. 구현 진행 + 체크리스트 체크 + 타입 체크

---

*plan v0.1 끝. 검토 후 피드백 줘.*
