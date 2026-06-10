# project/ — 성형 견적 시각화 코드

> 상위 문서: [research.md](../research.md), [plan_kim_0515_01.md](../plan_kim_0515_01.md)

## 모듈 구조

```
project/
├── face_analyzer/      # MediaPipe 478점 + 정규화 + 비율
├── recommender/        # 룰베이스 추천 + 시술 DB
├── input_generator/    # 자동 마스크 (sketch/color는 Week 2)
├── scfegan_wrapper/    # SC-FEGAN 추론 (Colab에서만 import)
├── diffface_wrapper/   # 백업 모델 PoC (Week 2)
├── ui/                 # Streamlit (Week 3)
└── tests/              # pytest
```

## 로컬 셋업 (분석/UI용, 3.10+)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r ../requirements.txt
pytest -v
```

## SC-FEGAN 환경 (Colab)

`notebooks/01_env_check.ipynb` → `02_scfegan_smoke.ipynb` 순서로 실행.

## Week 1 산출물

- `face_analyzer.detect_landmarks(img)` → (478, 2) 픽셀 좌표
- `face_analyzer.normalize_face(img)` → 512×512 정렬 이미지 + meta
- `face_analyzer.compute_ratios(landmarks)` → 비율 10개 dict
- `recommender.recommend(ratios, procs)` → 추천 리스트 (신뢰도 정렬)
- `input_generator.make_mask(landmarks, procedure)` → 512×512 binary mask
- 단위 테스트 3개: `test_rules.py`, `test_mask.py`, `test_ratios.py`
- Colab 노트북 2개: env_check, scfegan_smoke

## Week 2 예정

- `input_generator.sketch.py` — 자동 변형 스케치 (intensity 인자)
- `input_generator.color.py` — 평균 피부톤 스트로크 모듈화
- `scfegan_wrapper.infer.py` — 추론 함수화
- `diffface_wrapper` PoC — 백업 모델
- Streamlit v0 — 업로드 + 랜드마크 + 추천 표시
