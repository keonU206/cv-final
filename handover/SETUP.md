# 환경 셋업 — 새 PC에서 처음부터

> 이 문서대로 차례대로 따라하면 30분~1시간 안에 cv-final 프로젝트 실행 가능.
>
> **OS 가정**: Windows 11 (로컬) + Linux (Colab GPU)
> **Python**: 3.11 (로컬, 권장) / 3.12 (Colab 기본)

---

## 1단계. 사전 준비 (5분)

### 1-A. Python 설치 확인
```powershell
python --version
# 기대: Python 3.11.x 또는 3.10.x (3.13은 호환 안 됨)
```

없으면 https://www.python.org/downloads/ → 3.11.x 설치 (`Add to PATH` 체크).

### 1-B. Git 설치 확인
```powershell
git --version
```

없으면 https://git-scm.com/download/win

### 1-C. GitHub Personal Access Token (PAT) 발급
1. https://github.com/settings/tokens
2. **"Generate new token (classic)"**
3. Note: `cv-final-clone`, Expiration: **30 days**
4. Scope: ✅ **`repo`** 전체 체크
5. **Generate** → 토큰 복사 (한 번만 보임!)
6. 메모장에 임시 저장 + **앞뒤 공백 제거**

---

## 2단계. 저장소 Clone (5분)

```powershell
cd C:\Users\<YourName>\Documents
git clone https://<TOKEN>@github.com/keonU206/cv-final.git
# 예: git clone https://ghp_abc123xyz@github.com/keonU206/cv-final.git
cd cv-final
```

성공 시: `cv-final/` 폴더 생성됨 (30+ 파일, 13 노트북).

### Clone 실패 시
- **403/401**: 토큰 만료 또는 권한 없음 → kim (Owner)에게 collaborator 추가 요청
- **token에 공백 포함**: 메모장에서 토큰 다시 복사 (앞뒤 공백 X)

---

## 3단계. Python 가상환경 + 의존성 설치 (15-20분)

### 3-A. venv 생성
```powershell
cd C:\Users\<YourName>\Documents\cv-final
python -m venv .venv
.venv\Scripts\activate
# 프롬프트 앞에 (.venv) 표시되면 OK
```

### 3-B. pip 업그레이드
```powershell
python -m pip install --upgrade pip
```

### 3-C. requirements 설치
```powershell
pip install -r requirements.txt
```

⚠ **디스크 공간 5GB 이상 필요** (torch + torchvision + segmentation_models_pytorch).

### 3-D. 설치 검증
```powershell
python -c "import torch, segmentation_models_pytorch, streamlit, reportlab, mediapipe; print('✅ 모든 패키지 OK')"
```

### 자주 발생하는 문제

| 에러 | 원인 | 해결 |
|------|------|------|
| `No space left on device` | 디스크 부족 | `pip cache purge` + 다른 큰 파일 정리 |
| `torch 2.x not found` | Python 버전 너무 높음 | Python 3.11 사용 |
| `mediapipe 0.10.21 install fail` | Python 3.12 | `pip install mediapipe` (latest) |

---

## 4단계. 학습된 모델 다운로드 (5-10분)

### 4-A. Google Drive 접근
프로젝트 owner(kim)와 Drive 공유되어 있다고 가정. 안 되어 있으면 owner에게 공유 요청.

- Drive 폴더: `/MyDrive/cv-final-ckpts/`
- 파일: `refinement_best.pt`, `unet_*_best.pt`, `samples/*.png`

### 4-B. 로컬로 다운로드
방법 1: Drive 웹에서 직접 다운로드
```
1. https://drive.google.com 접속
2. cv-final-ckpts 폴더 우클릭 → 다운로드 (zip)
3. 압축 해제 → C:\Users\<YourName>\Documents\cv-final\
   - refinement_best.pt → checkpoints/refinement_best.pt
   - samples/*.png → samples/
```

방법 2: gdown (Colab/Linux 시)
```bash
pip install gdown
gdown --folder <Drive 공유 폴더 ID>
```

### 4-C. 폴더 구조 확인
```powershell
# 다음 경로에 파일들이 있어야 함:
cv-final\checkpoints\refinement_best.pt
cv-final\samples\original_before.png
cv-final\samples\sd_final_*.png  (3개)
cv-final\samples\beforeafter_*.png  (3개)
cv-final\samples\all_sd_results.png
```

---

## 5단계. 동작 검증 (5분)

### 5-A. 단위 테스트
```powershell
pytest project/tests/ -v
# 기대: 50+ tests PASS (torch 없으면 일부 skip OK)
```

### 5-B. PDF 견적서 샘플 생성
```powershell
python -c "from project.report import build_estimate, generate_estimate_pdf; items = build_estimate(['nose_tip', 'double_eyelid', 'jaw_v_line']); generate_estimate_pdf(items, 'test.pdf', patient_name='테스트', include_images=False); print('✅ PDF OK')"
```

→ `test.pdf` 파일 생성 확인.

### 5-C. Streamlit 실행
```powershell
streamlit run app/streamlit_demo.py
```

브라우저에서 http://localhost:8501 자동으로 열림.

- **Pre-generated 모드** (기본 선택) → samples/ PNG 표시
- **Live 모드** → 사진 업로드 + 실시간 처리 (placeholder)

`Ctrl+C`로 종료.

---

## 6단계. Colab 환경 셋업 (학습 담당자)

### 6-A. Colab Secrets 등록
1. Colab → 좌측 🔑 자물쇠 아이콘 → **Secrets**
2. 새 secret 추가:
   - Name: `GH_TOKEN`
   - Value: 발급한 PAT
   - **Notebook access**: 🟢 ON

### 6-B. Drive 마운트
모든 노트북 첫 셀에서:
```python
from google.colab import drive
drive.mount('/content/drive')
```

### 6-C. T4 GPU 설정
- Runtime → Change runtime type → **T4 GPU** → Save

### 6-D. Colab에서 노트북 열기
GitHub 직접 링크:
```
https://colab.research.google.com/github/keonU206/cv-final/blob/main/notebooks/<파일명>
```

예시 (현재 우선순위):
- 노트북 14: `14_gradcam.ipynb` (시각화)
- 노트북 15: `15_confusion_matrix.ipynb` (평가)

---

## 7단계. 자주 쓰는 명령 정리

### Git
```powershell
# 최신 코드 받기
git pull

# 변경사항 확인
git status

# 커밋 + 푸쉬
git add <files>
git commit -m "feat: 설명"
git push
```

### Python
```powershell
# 가상환경 활성화
.venv\Scripts\activate

# 테스트
pytest project/tests/ -v

# Streamlit
streamlit run app/streamlit_demo.py

# PDF 생성 모듈 import 테스트
python -c "from project.report import generate_estimate_pdf; print('OK')"
```

### Colab
```python
# Drive 마운트
from google.colab import drive
drive.mount('/content/drive')

# Repo clone (Token 사용)
from google.colab import userdata
token = userdata.get('GH_TOKEN').strip()
!git clone https://{token}@github.com/keonU206/cv-final.git /content/cv-final
%cd /content/cv-final
import sys; sys.path.insert(0, '/content/cv-final')
```

---

## 8단계. 트러블슈팅

### Streamlit 안 열림
- 포트 8501 사용 중 → `streamlit run ... --server.port 8502`

### `ModuleNotFoundError: No module named 'project'`
- cv-final 폴더 안에서 실행 안 함 → `cd cv-final` 먼저
- 또는 sys.path 추가: `import sys; sys.path.insert(0, '.')`

### PDF에 한글 깨짐 (Linux/Mac)
- Windows의 `malgun.ttf` 폰트 없음
- 자동 fallback (Helvetica) → 한글 표시 안 됨
- 해결: `project/report/pdf_generator.py`의 `_FONT_REGULAR_PATH`를 시스템 한글 폰트로 수정

### Colab에서 노트북 코드 옛 버전
- 페이지 새로고침 (F5) → "변경사항 무시"
- 또는 `Ctrl+Shift+R` (강제 새로고침)

### mediapipe 호환 안 됨
- 0.10.21 (mp.solutions) vs 0.10.35 (mp.tasks) 차이
- Streamlit/노트북 코드는 둘 다 fallback 처리됨
- 최신 노트북 14 → `face_landmarker.task` 자동 다운로드

---

## ✅ 셋업 완료 체크리스트

- [ ] Python 3.11 설치 + PATH 추가
- [ ] Git 설치
- [ ] GitHub PAT 발급 (공백 제거)
- [ ] cv-final repo clone 성공
- [ ] `.venv` 가상환경 생성 + 활성화
- [ ] `pip install -r requirements.txt` 완료
- [ ] `pytest project/tests/` 50+ PASS
- [ ] `checkpoints/refinement_best.pt` 다운로드
- [ ] `samples/` PNG 다운로드
- [ ] Streamlit 실행 + 브라우저 확인
- [ ] (학습 담당) Colab Secrets에 `GH_TOKEN` 등록
- [ ] (학습 담당) T4 GPU 선택

→ 다음: `CHECKLIST.md` (남은 작업)
