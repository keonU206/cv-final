"""성형 견적 시각화 데모 — Streamlit UI (v2).

두 가지 모드 지원:

1. **Pre-generated 모드 (발표용, 기본)** — samples/ 폴더의 SD Inpaint 결과 표시
   - 실시간 inference 없이 발표에서 안정적 데모
   - PDF 견적서 자동 생성

2. **Live 모드** — 사진 업로드 + 실시간 처리 (placeholder)
   - 사진 업로드 → MediaPipe 랜드마크 → 시뮬레이션
   - SC-FEGAN/Refinement ckpt 있으면 적용, 없으면 폴백

실행:
    streamlit run app/streamlit_demo.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

# cv-final 루트 import path 추가
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

from project.input_generator import compose_scfegan_input, load_procedures
from project.report import build_estimate, generate_estimate_pdf


# ─── 상수 ───
st.set_page_config(
    page_title="성형 견적 시각화 — CV Final",
    page_icon="✨",
    layout="wide",
)

SIZE = 512
DEFAULT_SAMPLES_DIR = PROJ_ROOT / "samples"
DEFAULT_REFINEMENT_CKPT = PROJ_ROOT / "checkpoints" / "refinement_best.pt"

# 시술 한글명
PROC_KO = {
    "nose_tip": "코끝 성형",
    "double_eyelid": "쌍커풀",
    "jaw_v_line": "V라인 (사각턱)",
}


# ─── 헬퍼: 랜드마크 추출 (mp.solutions + mp.tasks fallback) ───
@st.cache_resource
def _load_mediapipe():
    try:
        import mediapipe as mp
        return mp
    except ImportError:
        return None


def extract_landmarks(image_rgb: np.ndarray, size: int = 512) -> Optional[np.ndarray]:
    """mp.solutions (구) 또는 mp.tasks (신) 자동 fallback."""
    mp = _load_mediapipe()
    if mp is None:
        return None

    # 1차 시도: mp.solutions (mediapipe < 0.10.35)
    if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
        try:
            with mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True, max_num_faces=1, refine_landmarks=True,
            ) as fm:
                res = fm.process(image_rgb)
            if res.multi_face_landmarks:
                lms = res.multi_face_landmarks[0].landmark
                h, w = image_rgb.shape[:2]
                pts = np.array([[lm.x * w, lm.y * h] for lm in lms], dtype=np.float32)
                if w != size:
                    pts = pts * (size / w)
                return pts.astype(np.int32)
        except Exception:
            pass

    # 2차 시도: mp.tasks (mediapipe >= 0.10.35)
    try:
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        model_path = Path.home() / ".cache" / "mediapipe" / "face_landmarker.task"
        if not model_path.exists():
            st.warning(
                f"face_landmarker.task 모델 없음. 다운로드:\n"
                f"  https://storage.googleapis.com/mediapipe-models/face_landmarker/"
                f"face_landmarker/float16/1/face_landmarker.task\n"
                f"  → {model_path}"
            )
            return None

        base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
        options = mp_vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            num_faces=1,
        )
        detector = mp_vision.FaceLandmarker.create_from_options(options)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = detector.detect(mp_image)
        if not result.face_landmarks:
            return None
        lms = result.face_landmarks[0]
        pts = np.array(
            [[lm.x * size, lm.y * size] for lm in lms], dtype=np.int32,
        )
        return pts
    except Exception as e:
        st.error(f"랜드마크 추출 실패: {e}")
        return None


# ─── 헬퍼: Refinement 모델 로드 ───
@st.cache_resource
def load_refinement_model(ckpt_path: str):
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
    if model is None:
        return image_rgb
    try:
        import torch
        device = next(model.parameters()).device
        tensor = (torch.from_numpy(image_rgb).float() / 127.5 - 1.0)
        tensor = tensor.permute(2, 0, 1).unsqueeze(0).to(device)
        with torch.no_grad():
            out = model(tensor)[0]
        return ((out.clamp(-1, 1) + 1) * 127.5).byte().permute(1, 2, 0).cpu().numpy()
    except Exception as e:
        st.warning(f"Refinement 실행 실패 — 원본 반환: {e}")
        return image_rgb


# ─── 사이드바 ───
st.sidebar.title("⚙ 설정")
st.sidebar.markdown("---")

# 모드 선택 ⭐ NEW
mode = st.sidebar.radio(
    "데모 모드",
    options=["Pre-generated (발표용)", "Live (사진 업로드)"],
    help=(
        "Pre-generated: 사전 생성된 SD Inpaint 결과 표시 (발표 데모 권장)\n"
        "Live: 사진 업로드 + 실시간 처리 (ckpt 있을 시 inference)"
    ),
)

st.sidebar.markdown("---")

# Pre-generated 모드 설정
if mode.startswith("Pre"):
    samples_dir = st.sidebar.text_input(
        "Samples 폴더 경로",
        value=str(DEFAULT_SAMPLES_DIR),
        help=f"SD Inpaint 결과 PNG 위치. 기본: {DEFAULT_SAMPLES_DIR}",
    )
    samples_dir = Path(samples_dir)
    use_sd_only = st.sidebar.checkbox(
        "Refinement 적용 전 결과 사용",
        value=False,
        help="True면 sd_only_*.png, False면 sd_final_*.png 사용",
    )

# Live 모드 설정
else:
    ref_ckpt = st.sidebar.text_input(
        "Refinement ckpt 경로",
        value=str(DEFAULT_REFINEMENT_CKPT),
        help="없으면 폴백 (원본 그대로)",
    )
    intensity = st.sidebar.slider(
        "시술 강도 (intensity)", 0.0, 1.0, 0.6, 0.1,
    )
    seed = st.sidebar.number_input("Random seed", value=42, step=1)

st.sidebar.markdown("---")
patient_name = st.sidebar.text_input("환자 이름 (PDF용)", value="익명")
clinic_name = st.sidebar.text_input(
    "클리닉 이름 (PDF용)", value="CV-Final 가상 클리닉",
)


# ─── 메인 UI ───
st.title("✨ 성형 견적 시각화 시스템")
st.markdown(
    "**CV Final Project** · MediaPipe + 자체 학습 U-Net + "
    "Stable Diffusion Inpaint + Refinement Network"
)
st.markdown("---")


procedures_db = load_procedures()
proc_options = list(procedures_db.keys())


# ═══════════════════════════════════════
# Pre-generated 모드 (발표용)
# ═══════════════════════════════════════
if mode.startswith("Pre"):
    st.info(
        "📌 **Pre-generated 모드** — 사전 생성된 SD Inpaint 결과 표시. "
        "발표 데모용으로 안정적입니다."
    )

    # samples 폴더 검증
    original_path = samples_dir / "original_before.png"
    if not original_path.exists():
        st.error(
            f"❌ 입력 사진 없음: `{original_path}`\n\n"
            f"Drive `/MyDrive/cv-final-ckpts/samples/` 폴더를 "
            f"`{DEFAULT_SAMPLES_DIR}` 로 다운로드해주세요."
        )
        st.stop()

    # 시술 선택
    st.subheader("1️⃣ 시술 선택")
    available_procs = []
    for p in proc_options:
        prefix = "sd_only_" if use_sd_only else "sd_final_"
        if (samples_dir / f"{prefix}{p}.png").exists():
            available_procs.append(p)

    if not available_procs:
        st.error(f"❌ samples 폴더에 결과 PNG가 없습니다: `{samples_dir}`")
        st.stop()

    selected_procs = st.multiselect(
        "시뮬레이션할 시술",
        options=available_procs,
        default=available_procs,
        format_func=lambda p: f"{PROC_KO.get(p, p)} ({p})",
    )

    if selected_procs:
        st.markdown("---")
        st.subheader("2️⃣ 시뮬레이션 결과 (SD Inpaint)")

        # 원본 로드
        original = cv2.cvtColor(cv2.imread(str(original_path)), cv2.COLOR_BGR2RGB)

        before_paths = {}
        after_paths = {}

        for proc_id in selected_procs:
            name = PROC_KO.get(proc_id, proc_id)
            prefix = "sd_only_" if use_sd_only else "sd_final_"
            after_path = samples_dir / f"{prefix}{proc_id}.png"
            after_img = cv2.cvtColor(cv2.imread(str(after_path)), cv2.COLOR_BGR2RGB)

            st.markdown(f"### {name}")
            c1, c2 = st.columns(2)
            c1.image(original, caption="Before (원본)", use_container_width=True)
            c2.image(
                after_img,
                caption=f"After ({'SD 출력' if use_sd_only else 'SD + Refinement'})",
                use_container_width=True,
            )

            # PDF용
            before_paths[proc_id] = original_path
            after_paths[proc_id] = after_path

        # ─── PDF 견적서 ───
        st.markdown("---")
        st.subheader("3️⃣ 견적서 PDF")

        items = build_estimate(
            selected_procs,
            catalog=procedures_db,
            before_paths=before_paths,
            after_paths=after_paths,
        )

        total_min = sum(it.price_min for it in items)
        total_max = sum(it.price_max for it in items)
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("최소 견적", f"{total_min // 10000:,} 만원")
        col_b.metric(
            "평균 견적",
            f"{(total_min + total_max) // 20000:,} 만원",
            delta=f"+{(total_max - total_min) // 10000:,} 만원 범위",
        )
        col_c.metric("최대 견적", f"{total_max // 10000:,} 만원")

        pdf_path = Path(tempfile.gettempdir()) / "cv-final-demo" / "estimate.pdf"
        pdf_path.parent.mkdir(exist_ok=True)
        generate_estimate_pdf(
            items, pdf_path,
            patient_name=patient_name, clinic_name=clinic_name,
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 견적서 PDF 다운로드",
                f, file_name=f"{patient_name}_견적서.pdf",
                mime="application/pdf", type="primary",
            )


# ═══════════════════════════════════════
# Live 모드 (사진 업로드)
# ═══════════════════════════════════════
else:
    st.warning(
        "⚠ **Live 모드** — SD Inpaint는 로컬 환경 제약으로 실시간 추론 X. "
        "Refinement만 적용. 발표 데모는 Pre-generated 모드 권장."
    )

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("1️⃣ 사진 업로드")
        uploaded = st.file_uploader(
            "얼굴이 정면으로 보이는 사진",
            type=["jpg", "jpeg", "png", "webp"],
        )
    with col_right:
        st.subheader("2️⃣ 시술 선택")
        selected_procs = st.multiselect(
            "시뮬레이션할 시술",
            options=proc_options,
            default=["nose_tip"],
            format_func=lambda p: f"{PROC_KO.get(p, p)} ({p})",
        )

    if uploaded is not None:
        pil_img = Image.open(uploaded).convert("RGB")
        image_rgb = cv2.resize(np.array(pil_img), (SIZE, SIZE))

        st.markdown("---")
        if st.button("✨ 시뮬레이션 실행", type="primary"):
            with st.spinner("랜드마크 추출 중..."):
                landmarks = extract_landmarks(image_rgb, size=SIZE)

            if landmarks is None:
                st.error("얼굴 감지 실패")
                st.stop()

            st.success(f"✅ 478 랜드마크 추출 완료")
            ref_model = load_refinement_model(ref_ckpt)
            if ref_model is not None:
                st.info("✅ Refinement 모델 로드 OK")
            else:
                st.info("ℹ Refinement 모델 미로드 — 폴백 진행")

            before_paths = {}
            after_paths = {}

            for proc_id in selected_procs:
                with st.spinner(f"{proc_id} 처리 중..."):
                    composed = compose_scfegan_input(
                        image_rgb, landmarks, proc_id,
                        size=SIZE, intensity=intensity, seed=int(seed),
                    )
                    scfegan_out = composed["incomplete_image"]
                    refined = run_refinement(ref_model, scfegan_out)

                st.markdown(f"### {PROC_KO.get(proc_id, proc_id)}")
                c1, c2, c3 = st.columns(3)
                c1.image(image_rgb, caption="Before")
                c2.image(scfegan_out, caption="SD/SC-FEGAN (placeholder)")
                c3.image(refined, caption="After (Refinement)")

                tmpdir = Path(tempfile.gettempdir()) / "cv-final-demo"
                tmpdir.mkdir(exist_ok=True)
                bp = tmpdir / f"before_{proc_id}.jpg"
                ap = tmpdir / f"after_{proc_id}.jpg"
                cv2.imwrite(str(bp), cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(ap), cv2.cvtColor(refined, cv2.COLOR_RGB2BGR))
                before_paths[proc_id] = bp
                after_paths[proc_id] = ap

            # PDF
            st.markdown("---")
            st.subheader("3️⃣ 견적서 PDF")
            items = build_estimate(
                selected_procs, catalog=procedures_db,
                before_paths=before_paths, after_paths=after_paths,
            )
            total_min = sum(it.price_min for it in items)
            total_max = sum(it.price_max for it in items)
            st.metric(
                "예상 견적",
                f"{(total_min + total_max) // 20000:,} 만원",
                delta=f"{total_min // 10000:,} ~ {total_max // 10000:,} 만원",
            )
            pdf_path = Path(tempfile.gettempdir()) / "cv-final-demo" / "estimate.pdf"
            pdf_path.parent.mkdir(exist_ok=True)
            generate_estimate_pdf(
                items, pdf_path,
                patient_name=patient_name, clinic_name=clinic_name,
            )
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📄 견적서 PDF 다운로드",
                    f, file_name=f"{patient_name}_견적서.pdf",
                    mime="application/pdf", type="primary",
                )
    else:
        st.info("👆 사진을 업로드하면 시뮬레이션 시작합니다.")


st.markdown("---")
st.caption(
    "© 2026 CV Final Project · Stable Diffusion (CreativeML Open RAIL-M) · "
    "CelebAMask-HQ (학술 연구용)"
)
