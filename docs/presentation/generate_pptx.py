"""CV Final 발표 슬라이드 자동 생성 (12장).

박한샘 교수님 평가 기준 매핑 + 실측 데이터 반영.
출력: 바탕화면\\발표자료_CV_Final\\발표슬라이드.pptx

실행:
    python docs/presentation/generate_pptx.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Inches, Pt

# ─── 경로 설정 ───
SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"
OUTPUT_DIR = Path("C:/Users/User/Desktop/발표자료_CV_Final")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PPTX_PATH = OUTPUT_DIR / "발표슬라이드.pptx"

# ─── 색상 팔레트 ───
NAVY = RGBColor(0x1E, 0x27, 0x61)
ACCENT = RGBColor(0xF9, 0x61, 0x67)
CHARCOAL = RGBColor(0x2C, 0x3E, 0x50)
MUTED = RGBColor(0x7B, 0x8F, 0xA1)
LIGHT_BG = RGBColor(0xFA, 0xFB, 0xFD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# ─── 폰트 ───
FONT_BOLD = "맑은 고딕"  # Windows 한글 폰트
FONT_REGULAR = "맑은 고딕"

# ─── 슬라이드 크기 (16:9) ───
SLIDE_W = Cm(33.867)
SLIDE_H = Cm(19.05)


def make_pres():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def add_blank_slide(prs):
    """빈 슬라이드 추가."""
    blank_layout = prs.slide_layouts[6]
    return prs.slides.add_slide(blank_layout)


def add_text(slide, text, left, top, width, height,
             size=18, bold=False, color=CHARCOAL, align=PP_ALIGN.LEFT, font=FONT_REGULAR):
    """텍스트 박스 추가."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def add_image(slide, image_path, left, top, width=None, height=None):
    """이미지 추가 (경로 존재 시)."""
    if Path(image_path).exists():
        return slide.shapes.add_picture(str(image_path), left, top, width=width, height=height)
    return None


def add_bullet_list(slide, items, left, top, width, height,
                    size=16, color=CHARCOAL, font=FONT_REGULAR):
    """불릿 리스트."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = f"• {item}"
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = color
        p.space_after = Pt(8)
    return tb


def add_header(slide, title, subtitle=None):
    """슬라이드 상단 제목 + 부제."""
    # 상단 NAVY 배경 띠
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Cm(3.0),
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False

    add_text(slide, title, Cm(1.0), Cm(0.5), Cm(30), Cm(1.5),
             size=28, bold=True, color=WHITE, font=FONT_BOLD)
    if subtitle:
        add_text(slide, subtitle, Cm(1.0), Cm(1.9), Cm(30), Cm(1.0),
                 size=14, color=RGBColor(0xCA, 0xDC, 0xFC), font=FONT_REGULAR)


def add_footer(slide, page_num, total=12):
    """하단 페이지 번호."""
    add_text(slide, f"{page_num} / {total}", Cm(30), Cm(18),
             Cm(3), Cm(0.8), size=10, color=MUTED, align=PP_ALIGN.RIGHT)
    add_text(slide, "CV Final · 성형 견적 시각화 시스템", Cm(1), Cm(18),
             Cm(15), Cm(0.8), size=10, color=MUTED)


# ─── 슬라이드 생성 시작 ───
prs = make_pres()


# ━━━ 슬라이드 1: 표지 ━━━
s = add_blank_slide(prs)
# 배경 NAVY
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()

add_text(s, "성형 견적 시각화 시스템",
         Cm(2), Cm(6), Cm(30), Cm(2.5),
         size=44, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font=FONT_BOLD)
add_text(s, "U-Net 기반 분석 + Stable Diffusion Inpainting",
         Cm(2), Cm(9), Cm(30), Cm(1.5),
         size=22, color=RGBColor(0xCA, 0xDC, 0xFC), align=PP_ALIGN.CENTER, font=FONT_REGULAR)
add_text(s, "Computer Vision 기말 프로젝트 · 2026-06-15",
         Cm(2), Cm(13), Cm(30), Cm(1),
         size=16, color=RGBColor(0xCA, 0xDC, 0xFC), align=PP_ALIGN.CENTER)
add_text(s, "kim · 팀원1 · 팀원2",
         Cm(2), Cm(15), Cm(30), Cm(1),
         size=14, color=RGBColor(0xCA, 0xDC, 0xFC), align=PP_ALIGN.CENTER)


# ━━━ 슬라이드 2: 데이터셋 ━━━
s = add_blank_slide(prs)
add_header(s, "1. 데이터셋 · 문제 정의", "Task: Segmentation + Generation")
add_text(s, "데이터셋: CelebAMask-HQ (Lee et al. 2020 CVPR)",
         Cm(1), Cm(3.5), Cm(30), Cm(1), size=20, bold=True, color=NAVY)
add_bullet_list(s, [
    "30,000장의 1024×1024 고해상도 얼굴 이미지",
    "19-class 픽셀 단위 mask annotation",
    "→ Semantic Segmentation에 직접 적합",
    "",
    "사용한 두 가지 Vision Task:",
    "  ① Semantic Segmentation — U-Net으로 얼굴 부위 분할",
    "  ② Image Generation (Inpainting) — Stable Diffusion 시술 후 변형",
    "",
    "응용: 성형 시술 시뮬레이션 + 의료 보조 도구",
], Cm(1.5), Cm(4.7), Cm(30), Cm(11), size=18)
add_footer(s, 2)


# ━━━ 슬라이드 3: 시스템 아키텍처 ━━━
s = add_blank_slide(prs)
add_header(s, "2. 시스템 아키텍처", "모듈식 설계 — Model-agnostic")
add_text(s, "파이프라인 흐름:",
         Cm(1), Cm(3.5), Cm(30), Cm(1), size=20, bold=True, color=NAVY)
add_bullet_list(s, [
    "사진 입력 → MediaPipe Face Mesh (478 landmarks, Kartynnik 2019)",
    "↓",
    "[Phase 7-A] 자동 Sketch/Color/Mask 생성 (Bezier 곡선)",
    "↓",
    "[U-Net Segmentation] 시술 부위 분석 (Phase 1~6, ResNet-34 encoder)",
    "↓",
    "[Phase 7-G] Stable Diffusion Inpaint (Rombach 2022 CVPR)",
    "↓",
    "[Phase 7-B] Refinement Network (L1 + VGG19 Perceptual, Johnson 2016)",
    "↓",
    "→ Before/After 시각화 + PDF 견적서",
], Cm(1.5), Cm(4.7), Cm(30), Cm(12), size=14)
add_footer(s, 3)


# ━━━ 슬라이드 4: U-Net 4종 + plateau ━━━
s = add_blank_slide(prs)
add_header(s, "3. U-Net 4종 모델 비교", "mIoU plateau 발견")
add_text(s,
    "Baseline 0.5123  →  LM-guided 0.5487 (+3.6%p)  →  Attention 0.5499 (+0.12%p)",
    Cm(1), Cm(3.5), Cm(32), Cm(1.2),
    size=22, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
add_bullet_list(s, [
    "Baseline: ResNet-34 + Combo Loss (Dice + CE, Taghanaki 2019)",
    "LM-guided: 4채널 입력 (RGB + Gaussian Heatmap, Newell 2016)",
    "Attention: SCSE Decoder (Roy 2018 MICCAI)",
    "",
    '핵심 발견: "Architecture < Methodology" (He 2019 CVPR Bag of Tricks)',
    "Early Stopping이 가장 효과적 — Architecture만으로는 plateau",
], Cm(1.5), Cm(4.8), Cm(20), Cm(11), size=16)
# 모델 비교 그래프 (있으면)
img_path = SAMPLES_DIR / "model_comparison_summary.png"
add_image(s, img_path, Cm(22), Cm(5), width=Cm(11))
add_footer(s, 4)


# ━━━ 슬라이드 5: Feature Map (계층적 특징 추출) ━━━
s = add_blank_slide(prs)
add_header(s, "4. 계층적 특징 추출", "Feature Map 시각화 (Zeiler 2014 ECCV)")
add_text(s,
    "ResNet-34 Encoder 4-stage activation → CNN 계층적 특징 시각적 증명",
    Cm(1), Cm(3.5), Cm(32), Cm(1), size=18, bold=True, color=NAVY)
add_bullet_list(s, [
    "Layer 1 (64ch): 저수준 — edge, 색상 패치",
    "Layer 2 (128ch): 중간 — texture, 부분 패턴",
    "Layer 3 (256ch): 고수준 — 얼굴 부위 윤곽",
    "Layer 4 (512ch): 최고수준 — semantic abstraction",
    "",
    "U-Net Skip Connection: localization + semantic 동시 보존",
], Cm(1.5), Cm(4.7), Cm(15), Cm(11), size=14)
img_path = SAMPLES_DIR / "feature_maps_all.png"
add_image(s, img_path, Cm(17), Cm(4.5), width=Cm(16))
add_footer(s, 5)


# ━━━ 슬라이드 6: Grad-CAM ━━━
s = add_blank_slide(prs)
add_header(s, "5. Grad-CAM 시각화", "설명 가능한 비전 AI (Selvaraju 2017 ICCV)")
add_bullet_list(s, [
    '"모델이 어디를 보고 판단했는가?" 시각적 증명',
    "encoder.layer4 hook → 클래스별 gradient × activation",
    "",
    "결과 패턴:",
    "  • '코' 클래스 → 코 영역 강하게 활성화",
    "  • '눈' 클래스 → 양쪽 눈 영역",
    "  • '입' 클래스 → 입 영역",
    "",
    "→ ResNet-34 encoder가 의미 있는 semantic 학습 확인",
], Cm(1.5), Cm(4), Cm(15), Cm(13), size=14)
img_path = SAMPLES_DIR / "gradcam_presentation.png"
add_image(s, img_path, Cm(17), Cm(5), width=Cm(16))
add_footer(s, 6)


# ━━━ 슬라이드 7: 자동 입력 + Refinement ━━━
s = add_blank_slide(prs)
add_header(s, "6. 자동 입력 생성 + Refinement Network", "Phase 7-A, 7-B")
add_text(s, "자동 입력 생성 (Phase 7-A)",
         Cm(1), Cm(3.5), Cm(15), Cm(1), size=20, bold=True, color=NAVY)
add_bullet_list(s, [
    "MediaPipe 478 landmarks → Bezier 곡선 sketch",
    "시술별 mask (convex hull + dilate)",
    "Color guide (HSV 기반)",
    "9채널 SC-FEGAN 입력 자동 구성",
], Cm(1), Cm(4.7), Cm(16), Cm(7), size=14)

add_text(s, "Refinement Network (Phase 7-B)",
         Cm(17), Cm(3.5), Cm(15), Cm(1), size=20, bold=True, color=ACCENT)
add_bullet_list(s, [
    "작은 U-Net + residual wrapper",
    "L1 + VGG19 Perceptual Loss (Johnson 2016 ECCV)",
    "역할: SD 출력의 artifact 제거 + 경계 자연스러움",
    "결과: val_l1 0.045 달성",
    "학습: 2 epochs on Colab T4",
], Cm(17), Cm(4.7), Cm(16), Cm(7), size=14)
add_footer(s, 7)


# ━━━ 슬라이드 8: SD Inpaint Before/After ━━━
s = add_blank_slide(prs)
add_header(s, "7. SC-FEGAN 우회 → Stable Diffusion Inpaint",
           "Rombach 2022 CVPR · 환경 제약 극복")
add_text(s,
    "기존 계획 SC-FEGAN (TF 1.15) → Python 3.12 비호환 → SD Inpaint 채택",
    Cm(1), Cm(3.5), Cm(32), Cm(1), size=16, bold=True, color=ACCENT)
img_path = SAMPLES_DIR / "all_sd_results.png"
add_image(s, img_path, Cm(1), Cm(4.5), width=Cm(32))
add_footer(s, 8)


# ━━━ 슬라이드 9: Confusion Matrix + Per-class ━━━
s = add_blank_slide(prs)
add_header(s, "8. 성능 분석 — Confusion Matrix & Per-class IoU",
           "평가 항목 3번 (15%)")
img_path = SAMPLES_DIR / "confusion_matrices_all.png"
add_image(s, img_path, Cm(1), Cm(3.8), width=Cm(20))

add_bullet_list(s, [
    "5가지 비전 지표 사용:",
    "  • mIoU, Per-class IoU",
    "  • Dice, Confusion Matrix",
    "  • Overall Accuracy",
    "",
    "Per-class IoU 패턴:",
    "  background: 0.89",
    "  skin: 0.64",
    "  nose: 0.69",
    "  mouth: 0.61",
    "  eye: 0.47 (가장 어려움)",
    "",
    "→ Class imbalance 한계",
], Cm(22), Cm(4), Cm(11), Cm(13), size=12)
add_footer(s, 9)


# ━━━ 슬라이드 10: Failure Case 분석 ━━━
s = add_blank_slide(prs)
add_header(s, "9. Failure Case 분석", "Sample-wise mIoU + Worst-5")
add_bullet_list(s, [
    "val 50장 sample-wise mIoU 측정",
    "Worst-5 추출 + 실패 원인 분석",
    "",
    "공통 실패 패턴:",
    "  • 측면 얼굴 (정면 학습 데이터)",
    "  • 안경/머리카락이 부위 가림",
    "  • 강한 조명 / 그림자",
    "",
    "향후 강화 방향:",
    "  • CutMix (Yun 2019 ICCV)",
    "  • Hard Example Mining (Lin 2017)",
    "  • Multi-task Learning",
], Cm(1.5), Cm(4), Cm(15), Cm(13), size=14)
img_path = SAMPLES_DIR / "worst_5_samples.png"
add_image(s, img_path, Cm(17), Cm(4), width=Cm(16))
add_footer(s, 10)


# ━━━ 슬라이드 11: 데모 시연 (Colab) ━━━
s = add_blank_slide(prs)
add_header(s, "10. Live 데모", "Colab T4 GPU · 실시간 SD Inpaint")
add_text(s,
    "▶ 데모 시연 — Colab 노트북 13",
    Cm(1), Cm(6), Cm(32), Cm(2),
    size=36, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
add_text(s,
    "사진 업로드 → 478 랜드마크 → SD Inpaint → Before/After",
    Cm(1), Cm(9), Cm(32), Cm(1.5),
    size=20, color=CHARCOAL, align=PP_ALIGN.CENTER)
add_text(s,
    "예상 시간: 약 2분 (T4 GPU, 30 inference steps)",
    Cm(1), Cm(11), Cm(32), Cm(1),
    size=14, color=MUTED, align=PP_ALIGN.CENTER)
add_text(s,
    "https://colab.research.google.com/github/keonU206/cv-final/blob/main/notebooks/13_sd_inpaint.ipynb",
    Cm(1), Cm(13), Cm(32), Cm(1),
    size=10, color=ACCENT, align=PP_ALIGN.CENTER)
add_footer(s, 11)


# ━━━ 슬라이드 12: 한계 + 향후 + 결론 ━━━
s = add_blank_slide(prs)
add_header(s, "11. 한계 + 향후 강화 + 결론")
add_text(s, "현재 한계",
         Cm(1), Cm(3.5), Cm(15), Cm(1), size=20, bold=True, color=ACCENT)
add_bullet_list(s, [
    "U-Net mIoU plateau (~0.55)",
    "SD Inpaint 변형 강도 보수적 (identity 보존 trade-off)",
    "한국인 얼굴 특화 미적용",
    "SC-FEGAN 환경 호환 X (Python 3.12)",
], Cm(1), Cm(4.7), Cm(15), Cm(6), size=14)

add_text(s, "향후 강화 방향",
         Cm(17), Cm(3.5), Cm(15), Cm(1), size=20, bold=True, color=NAVY)
add_bullet_list(s, [
    "ControlNet (Zhang 2023 ICCV) — 정밀 변형 제어",
    "InstantID (Wang 2024) — Identity 보존 강화",
    "Korean Face LoRA (Hu 2022) — 도메인 적응",
    "Multi-seed Ensemble + 사용자 선택 UI",
], Cm(17), Cm(4.7), Cm(15), Cm(6), size=14)

add_text(s, "결론",
         Cm(1), Cm(12), Cm(32), Cm(1), size=20, bold=True, color=NAVY)
add_bullet_list(s, [
    "모듈식 설계 강점 — SC-FEGAN → SD Inpaint 교체 시 model-agnostic 검증",
    '"Architecture < Methodology" 발견 (LM +3.6%p, Attention plateau)',
    "Grad-CAM + Feature Map으로 '설명 가능한 AI' 만족",
], Cm(1), Cm(13.2), Cm(32), Cm(5), size=14)
add_footer(s, 12)


# ─── 저장 ───
prs.save(str(PPTX_PATH))
print(f"✅ 발표 슬라이드 생성 완료: {PPTX_PATH}")
print(f"   슬라이드 수: {len(prs.slides)}")
import os
print(f"   파일 크기: {os.path.getsize(PPTX_PATH) / 1024:.1f} KB")
