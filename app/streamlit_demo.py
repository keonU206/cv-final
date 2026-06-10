"""성형 견적 시각화 데모 — Streamlit UI.

플로우:
1. 사진 업로드
2. MediaPipe 478 랜드마크 추출
3. 시술 선택 (procedures.yaml에서)
4. 각 시술별 9채널 입력 자동 생성
5. SC-FEGAN inference (ckpt 있을 시) → Refinement Network (ckpt 있을 시)
6. Before/After 시각화
7. PDF 견적서 다운로드

실행:
    streamlit run app/streamlit_demo.py

⚠ ckpt 미준비 시:
    - SC-FEGAN: incomplete_image를 그대로 표시 (placeholder)
    - Refinement: 식별식 (identity) → 통과
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

# Streamlit 환경에서는 cv-final 루트가 자동 import path에 없을 수 있음
PROJ_ROOT = Path(__file__).resolve().parents[1]
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

try:
    import streamlit as st
    import cv2
    from PIL import Image
except ImportError as e:
    raise ImportError(
        "필요 패키지: pip install streamlit opencv-python Pillow"
    ) from e

from project.input_generator import (
    compose_scfegan_input,
    load_procedures,
)
from project.report import build_estimate, generate_estimate_pdf


# ─── 페이지 설정 ───
st.set_page_config(
    page_title="성형 견적 시각화 — CV Final",
    page_icon="✨",
    layout="wide",
)

SIZE = 512
DEFAULT_REFINEMENT_CKPT = "checkpoints/refinement_best.pt"
DEFAULT_SCFEGAN_CKPT = "/content/drive/MyDrive/SC-FEGAN-ckpt/SC-FEGAN.ckpt"


# ─── 헬퍼: 랜드마크 추출 ───

@st.cache_resource
def _load_mediapipe():
    try:
        import mediapipe as mp
        return mp
    except ImportError:
        return None


def extract_landmarks(image_rgb: np.ndarray, size: int = 512) -> Optional[np.ndarray]:
    mp = _load_mediapipe()
    if mp is None:
        return None
    mp_face = mp.solutions.face_mesh
    with mp_face.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True,
    ) as fm:
        res = fm.process(image_rgb)
    if not res.multi_face_landmarks:
        return None
    lms = res.multi_face_landmarks[0].landmark
    h, w = image_rgb.shape[:2]
    pts = np.array([[lm.x * w, lm.y * h] for lm in lms], dtype=np.float32)
    if w != size:
        pts = pts * (size / w)
    return pts.astype(np.int32)


# ─── 헬퍼: 모델 로드 (try/except + cache) ───

@st.cache_resource
def load_refinement_model(ckpt_path: str):
    """Refinement Network 로드 — 실패 시 None."""
    try:
        import torch
        from project.refinement.model import build_refinement_wrapper
        if not Path(ckpt_path).exists():
            return None
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = build_refinement_wrapper(encoder_weights=None).to(device)
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        model.eval()
        return model
    except Exception as e:
        st.warning(f"Refinement 모델 로드 실패: {e}")
        return None


def run_refinement(model, image_rgb: np.ndarray) -> np.ndarray:
    """Refinement 적용 — model 없으면 원본 반환."""
    if model is None:
        return image_rgb
    try:
        import torch
        device = next(model.parameters()).device
        tensor = (torch.from_numpy(image_rgb).float() / 127.5 - 1.0)
        tensor = tensor.permute(2, 0, 1).unsqueeze(0).to(device)
        with torch.no_grad():
            out = model(tensor)[0]
        arr = ((out.clamp(-1, 1) + 1) * 127.5).byte().permute(1, 2, 0).cpu().numpy()
        return arr
    except Exception as e:
        st.warning(f"Refinement 실행 실패 — 원본 반환: {e}")
        return image_rgb


def run_scfegan_inference(composed: dict, ckpt_path: str) -> np.ndarray:
    """SC-FEGAN inference — ckpt 없으면 incomplete_image 폴백."""
    if not Path(ckpt_path + ".index").exists():
        return composed["incomplete_image"]
    # 실제 SC-FEGAN inference는 TF 1.x 환경 필요 (Streamlit에서 동시 로드 어려움)
    # → 발표 데모에서는 사전에 Colab에서 inference 후 결과 저장 → Streamlit에서 로드 권장
    st.info("ℹ SC-FEGAN inference는 별도 Colab에서 사전 실행 권장 (TF 1.x 환경)")
    return composed["incomplete_image"]


# ─── 사이드바: 설정 ───
st.sidebar.title("⚙ 설정")
st.sidebar.markdown("---")

ref_ckpt = st.sidebar.text_input(
    "Refinement ckpt 경로",
    value=DEFAULT_REFINEMENT_CKPT,
    help="학습 완료 시 자동 적용. 없으면 무시.",
)
sc_ckpt = st.sidebar.text_input(
    "SC-FEGAN ckpt 경로",
    value=DEFAULT_SCFEGAN_CKPT,
    help="없으면 incomplete_image 표시 (placeholder)",
)
intensity = st.sidebar.slider(
    "시술 강도 (intensity)", 0.0, 1.0, 0.6, 0.1,
    help="0=원본 유지, 1=최대 변형",
)
seed = st.sidebar.number_input("Random seed", value=42, step=1)

st.sidebar.markdown("---")
patient_name = st.sidebar.text_input("환자 이름 (PDF용)", value="익명")
clinic_name = st.sidebar.text_input("클리닉 이름 (PDF용)", value="CV-Final 가상 클리닉")


# ─── 메인 UI ───
st.title("✨ 성형 견적 시각화 시스템")
st.markdown("**CV Final Project** · MediaPipe + 자체 학습 U-Net + SC-FEGAN + Refinement Network")
st.markdown("---")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1️⃣ 사진 업로드")
    uploaded = st.file_uploader(
        "얼굴이 정면으로 보이는 사진 선택",
        type=["jpg", "jpeg", "png", "webp"],
    )

procedures_db = load_procedures()
proc_options = list(procedures_db.keys())

with col_right:
    st.subheader("2️⃣ 시술 선택")
    selected_procs = st.multiselect(
        "시뮬레이션할 시술 (복수 선택 가능)",
        options=proc_options,
        default=["nose_tip"],
        format_func=lambda p: f"{p} · {procedures_db[p].get('name_ko', p)}",
    )

if uploaded is not None:
    # 이미지 로드 + resize
    pil_img = Image.open(uploaded).convert("RGB")
    image_rgb = np.array(pil_img)
    image_rgb = cv2.resize(image_rgb, (SIZE, SIZE))

    st.markdown("---")
    st.subheader("3️⃣ 분석 시작")

    if st.button("✨ 시뮬레이션 실행", type="primary"):
        with st.spinner("랜드마크 추출 중..."):
            landmarks = extract_landmarks(image_rgb, size=SIZE)

        if landmarks is None:
            st.error("얼굴을 감지할 수 없습니다. 다른 사진을 사용해주세요.")
        else:
            st.success(f"✅ 478 랜드마크 추출 완료")

            # 모델 로드
            ref_model = load_refinement_model(ref_ckpt)
            if ref_model is not None:
                st.info(f"✅ Refinement 모델 로드 OK")
            else:
                st.info("ℹ Refinement 모델 미로드 (학습 전이거나 경로 없음). 폴백 진행.")

            # 시술별 처리
            after_paths_for_pdf = {}
            before_paths_for_pdf = {}

            for proc_id in selected_procs:
                with st.spinner(f"{proc_id} 처리 중..."):
                    composed = compose_scfegan_input(
                        image_rgb, landmarks, proc_id,
                        size=SIZE, intensity=intensity, seed=int(seed),
                    )
                    # SC-FEGAN inference
                    scfegan_out = run_scfegan_inference(composed, sc_ckpt)
                    # Refinement
                    refined = run_refinement(ref_model, scfegan_out)

                # 결과 표시
                st.markdown(f"### {procedures_db[proc_id].get('name_ko', proc_id)}")
                c1, c2, c3 = st.columns(3)
                c1.image(image_rgb, caption="Before", use_container_width=True)
                c2.image(scfegan_out, caption="SC-FEGAN 출력", use_container_width=True)
                c3.image(refined, caption="After (Refinement)", use_container_width=True)

                # PDF용 임시 저장
                tmpdir = Path(tempfile.gettempdir()) / "cv-final-demo"
                tmpdir.mkdir(exist_ok=True)
                before_path = tmpdir / f"before_{proc_id}.jpg"
                after_path = tmpdir / f"after_{proc_id}.jpg"
                cv2.imwrite(str(before_path), cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(after_path), cv2.cvtColor(refined, cv2.COLOR_RGB2BGR))
                before_paths_for_pdf[proc_id] = before_path
                after_paths_for_pdf[proc_id] = after_path

            # ─── PDF 견적서 ───
            st.markdown("---")
            st.subheader("4️⃣ 견적서 PDF")

            if st.session_state.get("pdf_clicked", False) or True:
                items = build_estimate(
                    selected_procs,
                    catalog=procedures_db,
                    before_paths=before_paths_for_pdf,
                    after_paths=after_paths_for_pdf,
                )

                # 합산 견적 미리 표시
                total_min = sum(it.price_min for it in items)
                total_max = sum(it.price_max for it in items)
                st.metric(
                    "예상 견적",
                    f"{(total_min + total_max) // 20000:,} 만원",
                    delta=f"{total_min // 10000:,} ~ {total_max // 10000:,} 만원",
                )

                # PDF 생성
                pdf_path = Path(tempfile.gettempdir()) / "cv-final-demo" / "estimate.pdf"
                generate_estimate_pdf(
                    items, pdf_path,
                    patient_name=patient_name,
                    clinic_name=clinic_name,
                )

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📄 견적서 PDF 다운로드",
                        f, file_name=f"{patient_name}_견적서.pdf",
                        mime="application/pdf",
                        type="primary",
                    )
else:
    st.info("👆 위에서 사진을 업로드하면 시뮬레이션을 시작합니다.")

st.markdown("---")
st.caption(
    "© 2026 CV Final Project · SC-FEGAN (CC BY-NC 4.0) · "
    "CelebAMask-HQ (학술 연구용)"
)
