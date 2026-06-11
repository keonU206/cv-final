# 📥 인수인계 폴더 — 시작 가이드

> **새 팀원**: 이 파일부터 읽기 → 아래 순서로 진행
> **AI 에이전트**: `AGENT_BRIEF.md` 먼저 읽고 작업 시작

---

## 📂 파일 4개

| 순서 | 파일 | 분량 | 용도 |
|------|------|------|------|
| **1** | **`HANDOVER.md`** | ~15분 읽기 | 종합 인수인계 (반드시 정독) |
| 2 | `SETUP.md` | ~30분 실습 | 환경 셋업 step-by-step |
| 3 | `CHECKLIST.md` | ~5분 | 남은 작업 + 발표 일정 |
| 4 | `AGENT_BRIEF.md` | ~5분 | AI 에이전트용 1페이지 컨텍스트 |

---

## 🎯 30초 요약

- **프로젝트**: 성형 견적 시각화 (사진→분석→AI변형→PDF견적서)
- **기술**: PyTorch + U-Net + Stable Diffusion Inpaint + Streamlit
- **발표**: 2026-06-15 (D-3 남음)
- **현재 상태**: 코드 95% 완료, 슬라이드/리허설/Colab 노트북 실행만 남음
- **예상 점수**: 87 ~ 94 / 100

---

## 🚀 30분 안에 시작하기 (Quick Start)

### 1. 환경 셋업
```bash
git clone https://<TOKEN>@github.com/keonU206/cv-final.git
cd cv-final
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 동작 확인
```bash
pytest project/tests/ -v   # 50+ PASS 확인
streamlit run app/streamlit_demo.py   # 브라우저 열림
```

### 3. 결과물 다운로드
Drive `/MyDrive/cv-final-ckpts/samples/` → 로컬 `samples/` 폴더로 복사

→ 자세한 안내는 **`SETUP.md`** 참조

---

## 🎯 역할별 시작 가이드

### 🅰 코드/UI 담당
1. `HANDOVER.md` 정독
2. `SETUP.md` 따라서 로컬 환경 셋업
3. `app/streamlit_demo.py` 동작 확인
4. `CHECKLIST.md` §C (Streamlit 검증) 완료
5. `project/report/pdf_generator.py` 한번 살펴보기

### 🅱 학습/평가 담당 (Colab)
1. `HANDOVER.md` §4 (학습된 모델 위치) 확인
2. `SETUP.md` §6 (Colab 셋업) 따라하기
3. **Colab Secrets에 `GH_TOKEN` 등록 필수**
4. `CHECKLIST.md` §A (노트북 14, 15 실행) 진행

### 🅲 발표/슬라이드 담당
1. `HANDOVER.md` §6 (평가 기준 매핑) + §7 (슬라이드 구성) 정독
2. `plan_kim_0610_02.md` §3 (슬라이드 11장) + §6 (발표 멘트) 참조
3. `docs/presentation/references.pdf` 인용 자료 확인
4. `CHECKLIST.md` §D (슬라이드 작성) 진행

### 🅳 AI 에이전트 사용 시
1. **`AGENT_BRIEF.md` 먼저 읽기** (1페이지 컨텍스트)
2. 그 다음 `HANDOVER.md`
3. 사용자 패턴 인지: 한국어, "ㄱㄱ" 스타일, 표 형식 선호

---

## 📞 긴급 도움

- **Owner**: kim (keonu206@gmail.com)
- **GitHub**: https://github.com/keonU206/cv-final
- **이전 plan 파일들**: `cv-final/plan_kim_*.md` (시간 순)
- **최신 plan**: `plan_kim_0610_02.md`

---

## ⚠ 절대 하지 말 것 (Top 3)

1. **Drive 공유 설정 변경 X** (가이드라인)
2. **`git push --force` X** (commit 손실)
3. **SC-FEGAN 환경 재시도 X** (시간 낭비 확정)

---

## 📅 발표까지 남은 일정 (2026-06-15)

| 날짜 | 핵심 작업 |
|------|----------|
| **6/12 (오늘)** | Colab 노트북 14, 15 실행 + 결과 다운로드 |
| 6/13 | 발표 슬라이드 (11장) + 데모 영상 녹화 |
| 6/14 | 리허설 1차/2차 + 백업 |
| **6/15** | **발표** |

---

> **시작**: 위 [HANDOVER.md](./HANDOVER.md) 클릭 또는 동일 폴더에서 열기
