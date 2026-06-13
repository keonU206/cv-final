"""CV Final 발표 슬라이드 자동 생성 (16장, 박한샘 교수 스타일 반영).

박한샘 교수 발표 패턴 (시계열 4조 + RAG 분석 기반):
- 목차 슬라이드 (01·02·03 챕터)
- "왜 이 문제?" 동기 슬라이드 별도
- 데이터 통계 강조
- 평가 지표 별도 슬라이드
- 한계 + 향후 명시
- 시연 슬라이드 명확
- 감사합니다 마무리

출력: 바탕화면\\발표자료_CV_Final\\발표슬라이드.pptx (16장)

실행:
    python docs/presentation/generate_pptx.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Pt

# ─── 경로 설정 ───
SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"
OUTPUT_DIR = Path("C:/Users/User/Desktop/발표자료_CV_Final")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PPTX_PATH = OUTPUT_DIR / "발표슬라이드_v4_최종.pptx"

# ─── 색상 ───
NAVY = RGBColor(0x1E, 0x27, 0x61)
ACCENT = RGBColor(0xF9, 0x61, 0x67)
CHARCOAL = RGBColor(0x2C, 0x3E, 0x50)
MUTED = RGBColor(0x7B, 0x8F, 0xA1)
LIGHT_BG = RGBColor(0xFA, 0xFB, 0xFD)
ICE = RGBColor(0xCA, 0xDC, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x48, 0xBB, 0x78)

FONT_BOLD = "맑은 고딕"
FONT_REGULAR = "맑은 고딕"

SLIDE_W = Cm(33.867)  # 16:9
SLIDE_H = Cm(19.05)


def make_pres():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def add_blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def add_text(slide, text, left, top, width, height,
             size=18, bold=False, color=CHARCOAL,
             align=PP_ALIGN.LEFT, font=FONT_REGULAR):
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


def add_image(slide, path, left, top, width=None, height=None):
    if Path(path).exists():
        return slide.shapes.add_picture(str(path), left, top, width=width, height=height)
    return None


def add_bullet_list(slide, items, left, top, width, height,
                    size=16, color=CHARCOAL, font=FONT_REGULAR):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = f"• {item}" if item and not item.startswith(("01", "02", "03", "04", "05", "  ")) else item
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = color
        p.space_after = Pt(6)
    return tb


def add_header(slide, chapter_num, title, subtitle=None):
    """챕터 번호 + 제목 헤더 (박한샘 스타일)."""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Cm(3.0))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    bar.shadow.inherit = False

    # 챕터 번호
    add_text(slide, chapter_num, Cm(1.0), Cm(0.4), Cm(4), Cm(1.0),
             size=14, bold=True, color=ACCENT, font=FONT_BOLD)
    # 제목
    add_text(slide, title, Cm(1.0), Cm(1.0), Cm(30), Cm(1.5),
             size=26, bold=True, color=WHITE, font=FONT_BOLD)
    if subtitle:
        add_text(slide, subtitle, Cm(1.0), Cm(2.3), Cm(30), Cm(0.7),
                 size=12, color=ICE, font=FONT_REGULAR)


def add_footer(slide, page_num, total=16):
    add_text(slide, f"{page_num} / {total}", Cm(30), Cm(18),
             Cm(3), Cm(0.8), size=10, color=MUTED, align=PP_ALIGN.RIGHT)
    add_text(slide, "CV Final · 성형 견적 시각화 시스템",
             Cm(1), Cm(18), Cm(15), Cm(0.8), size=10, color=MUTED)


# ═══════════════════════════════════════
# 슬라이드 생성 시작
# ═══════════════════════════════════════
prs = make_pres()
TOTAL = 16


# ━━━ Slide 1: 표지 ━━━
s = add_blank_slide(prs)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()

# 작은 분야 표기
add_text(s, "Computer Vision Final Project · 2026", Cm(2), Cm(4),
         Cm(30), Cm(0.8), size=14, color=ACCENT, align=PP_ALIGN.CENTER, bold=True)
# 메인 제목
add_text(s, "성형 견적 시각화 시스템",
         Cm(2), Cm(6.5), Cm(30), Cm(2.5),
         size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font=FONT_BOLD)
# 서브 제목
add_text(s, "U-Net 기반 얼굴 분석 + Stable Diffusion Inpainting",
         Cm(2), Cm(9.5), Cm(30), Cm(1.2),
         size=20, color=ICE, align=PP_ALIGN.CENTER)
# 팀 정보
add_text(s, "2026-06-15",
         Cm(2), Cm(13), Cm(30), Cm(1), size=14, color=ICE, align=PP_ALIGN.CENTER)
add_text(s, "kim · 팀원1 · 팀원2",
         Cm(2), Cm(14.5), Cm(30), Cm(1), size=14, color=ICE, align=PP_ALIGN.CENTER)


# ━━━ Slide 2: 목차 (NEW · 박한샘 패턴) ━━━
s = add_blank_slide(prs)
add_header(s, "CONTENTS", "목차", "프로젝트 발표 흐름")

chapters = [
    ("01.", "문제 정의 + 데이터셋", "왜 이 문제? · CelebAMask-HQ 30K"),
    ("02.", "시스템 아키텍처", "5단계 모듈식 파이프라인"),
    ("03.", "모델 설계", "U-Net 4종 · Refinement · SD Inpaint"),
    ("04.", "성능 분석 + 시각화", "Confusion Matrix · Grad-CAM · Feature Map"),
    ("05.", "데모 + 한계 + 향후", "Live 시연 · ControlNet 등"),
]
y = Cm(4.5)
for num, title, sub in chapters:
    add_text(s, num, Cm(3), y, Cm(3), Cm(1.5), size=32, bold=True, color=ACCENT)
    add_text(s, title, Cm(6), y, Cm(20), Cm(1.0), size=22, bold=True, color=NAVY)
    add_text(s, sub, Cm(6), y + Cm(1.0), Cm(25), Cm(0.7), size=13, color=MUTED)
    y += Cm(2.5)
add_footer(s, 2)


# ━━━ Slide 3: 문제 정의 (NEW · 박한샘 "왜 이 문제?" 패턴) ━━━
s = add_blank_slide(prs)
add_header(s, "01 · 문제 정의", "왜 성형 견적 시각화인가?")

# 사용자 페르소나 (왼쪽)
add_text(s, "현재 사용자의 어려움",
         Cm(1), Cm(3.5), Cm(15), Cm(1), size=18, bold=True, color=ACCENT)
add_bullet_list(s, [
    "상담 전 시술 결과를 예측 불가",
    "여러 부위 동시 시술 결과 시각화 X",
    "병원별 견적 차이 비교 어려움",
    "AI 보조 도구 부족",
], Cm(1), Cm(4.8), Cm(15), Cm(7), size=15)

# 해결 (오른쪽)
add_text(s, "본 프로젝트의 해결",
         Cm(17), Cm(3.5), Cm(15), Cm(1), size=18, bold=True, color=NAVY)
add_bullet_list(s, [
    "사진 1장 → AI 자동 분석",
    "시술 부위 자동 검출 (U-Net)",
    "변형 결과 시뮬레이션 (SD Inpaint)",
    "PDF 견적서 자동 생성",
], Cm(17), Cm(4.8), Cm(15), Cm(7), size=15)

# 키 메시지
add_text(s,
    '"사진 1장 → 시술 시뮬레이션 + 견적서"',
    Cm(1), Cm(13), Cm(32), Cm(1.5),
    size=22, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
add_text(s,
    "Vision Task 2가지 결합: Semantic Segmentation + Image Generation",
    Cm(1), Cm(15), Cm(32), Cm(1),
    size=14, color=CHARCOAL, align=PP_ALIGN.CENTER)
add_footer(s, 3)


# ━━━ Slide 4: 데이터셋 (강조 + 통계) ━━━
s = add_blank_slide(prs)
add_header(s, "01 · 데이터", "CelebAMask-HQ (Lee et al. 2020 CVPR)")

# 통계 박스 (3개 가로 배치)
stats = [
    ("30,000장", "고해상도 이미지", NAVY),
    ("1024×1024", "해상도", ACCENT),
    ("19-class", "픽셀 단위 mask", GREEN),
]
x_start = Cm(2)
for i, (val, label, col) in enumerate(stats):
    x = x_start + Cm(10.5) * i
    # 박스
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Cm(4.5),
                              Cm(9.5), Cm(4))
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT_BG
    box.line.color.rgb = col
    box.line.width = Pt(2.5)
    box.shadow.inherit = False
    add_text(s, val, x, Cm(5), Cm(9.5), Cm(1.8),
             size=36, bold=True, color=col, align=PP_ALIGN.CENTER)
    add_text(s, label, x, Cm(7.3), Cm(9.5), Cm(1),
             size=14, color=CHARCOAL, align=PP_ALIGN.CENTER)

# 데이터 활용 설명
add_text(s, "데이터 활용",
         Cm(1), Cm(10), Cm(15), Cm(1), size=18, bold=True, color=NAVY)
add_bullet_list(s, [
    "Semantic Segmentation 학습 — 6-class (bg + nose/eye/mouth/skin)",
    "MediaPipe 478 landmarks 자동 추출 → LM-guided 입력",
    "Hybrid dataset: mattymchen/celeba-hq + limsanky/celebamask-hq-256",
    "Train 27K / Val 3K (10% split)",
], Cm(1), Cm(11.2), Cm(31), Cm(6), size=14)
add_footer(s, 4)


# ━━━ Slide 5: 시스템 아키텍처 ━━━
s = add_blank_slide(prs)
add_header(s, "02 · 시스템", "5단계 모듈식 파이프라인")

stages = [
    ("1. 입력", "MediaPipe 478 landmarks", "Kartynnik 2019"),
    ("2. 자동 입력 생성", "Bezier sketch + mask + color", "Phase 7-A"),
    ("3. U-Net 분석", "ResNet-34 + SCSE Attention", "시술 부위 분석"),
    ("4. SD Inpaint", "Stable Diffusion 2022", "시술 후 변형 생성"),
    ("5. Refinement", "L1 + VGG19 Perceptual", "artifact 제거"),
]
y = Cm(4.0)
for i, (step, desc, ref) in enumerate(stages):
    # 번호 원
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL, Cm(2), y, Cm(1.5), Cm(1.5))
    circle.fill.solid()
    circle.fill.fore_color.rgb = NAVY
    circle.line.fill.background()
    circle.shadow.inherit = False
    add_text(s, str(i + 1), Cm(2), y + Cm(0.15), Cm(1.5), Cm(1.2),
             size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # 내용
    add_text(s, step, Cm(4.5), y, Cm(10), Cm(0.9), size=16, bold=True, color=NAVY)
    add_text(s, desc, Cm(15), y, Cm(15), Cm(0.9), size=14, color=CHARCOAL)
    add_text(s, ref, Cm(27), y, Cm(6), Cm(0.9), size=11, color=MUTED)
    # 화살표 (다음 단계 있을 때)
    if i < len(stages) - 1:
        arrow = s.shapes.add_shape(
            MSO_SHAPE.DOWN_ARROW, Cm(2.5), y + Cm(1.6),
            Cm(0.5), Cm(0.6),
        )
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = ACCENT
        arrow.line.fill.background()
        arrow.shadow.inherit = False
    y += Cm(2.5)

add_text(s,
    "→ 모듈식 설계: GAN backbone 교체 가능 (Model-Agnostic)",
    Cm(1), Cm(17), Cm(32), Cm(1), size=14, bold=True,
    color=ACCENT, align=PP_ALIGN.CENTER)
add_footer(s, 5)


# ━━━ Slide 6: U-Net 4종 + plateau ━━━
s = add_blank_slide(prs)
add_header(s, "03 · 모델 설계", "U-Net 4종 비교 · mIoU plateau")

# 큰 결과 박스 (500장 평가 기준, 5-class mIoU)
add_text(s,
    "Baseline 0.615  →  LM-guided 0.651 (+3.7%p ⭐)  →  Attention 0.652 (+0.03%p · plateau)",
    Cm(1), Cm(3.7), Cm(32), Cm(1.2),
    size=18, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
add_text(s,
    "※ 5-class mIoU (unused 제외, 공식 보고용) · 500장 평가",
    Cm(1), Cm(4.7), Cm(32), Cm(0.7),
    size=11, color=MUTED, align=PP_ALIGN.CENTER)

# 모델 비교 그래프
img_path = SAMPLES_DIR / "model_comparison_summary.png"
add_image(s, img_path, Cm(1), Cm(5.2), width=Cm(15))

add_text(s, "주요 발견",
         Cm(17), Cm(5.5), Cm(15), Cm(1), size=18, bold=True, color=NAVY)
add_bullet_list(s, [
    "LM 효과 (작은 영역):",
    "  eye +5.45%p, mouth +4.25%p, nose +3.62%p",
    "(Newell 2016 ECCV — Hourglass)",
    "",
    "Attention 효과: +0.03%p (plateau)",
    "(He 2019 \"Architecture < Methodology\")",
    "",
    "→ Early Stopping이 가장 효과적",
], Cm(17), Cm(6.7), Cm(16), Cm(10), size=12)
add_footer(s, 6)


# ━━━ Slide 7: 평가 지표 (NEW · 박한샘 패턴) ━━━
s = add_blank_slide(prs)
add_header(s, "04 · 평가 지표", "5가지 비전 모델 전용 지표")

metrics = [
    ("mIoU (5-class)", "mean IoU (unused 제외, 공식)", "공식 보고용", "0.6515 (Attention)"),
    ("mIoU (6-class)", "mean IoU (전체)", "TP / (TP+FP+FN) 평균", "0.5429"),
    ("Dice Score", "F1-score 등가 지표", "2·TP / (2·TP+FP+FN)", "0.6499"),
    ("Per-class IoU", "클래스별 어려움 분석", "각 클래스 IoU 추적", "eye 0.45 ↔ bg 0.89"),
    ("Overall Accuracy", "전체 픽셀 정확도", "diag sum / total", "0.8906"),
]
y = Cm(4)
for name, desc, formula, val in metrics:
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(1), y,
                              Cm(31), Cm(2.2))
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT_BG
    box.line.color.rgb = NAVY
    box.line.width = Pt(0.5)
    box.shadow.inherit = False

    add_text(s, name, Cm(1.5), y + Cm(0.4), Cm(7), Cm(1),
             size=16, bold=True, color=NAVY)
    add_text(s, desc, Cm(1.5), y + Cm(1.2), Cm(10), Cm(0.8),
             size=11, color=MUTED)
    add_text(s, formula, Cm(11), y + Cm(0.6), Cm(13), Cm(1),
             size=12, color=CHARCOAL)
    add_text(s, val, Cm(24), y + Cm(0.6), Cm(8), Cm(1),
             size=14, bold=True, color=ACCENT, align=PP_ALIGN.RIGHT)
    y += Cm(2.6)
add_footer(s, 7)


# ━━━ Slide 8: Feature Map (계층적 특징) ━━━
s = add_blank_slide(prs)
add_header(s, "04 · 시각화 (1/2)",
           "계층적 특징 추출 · Feature Map (Zeiler 2014 ECCV)")
add_text(s, "ResNet-34 Encoder 4-stage activation → CNN 계층적 특징 시각적 증명",
         Cm(1), Cm(3.5), Cm(32), Cm(1), size=16, bold=True, color=NAVY)

add_bullet_list(s, [
    "Layer 1 (64ch): edge, 색상 패치",
    "Layer 2 (128ch): texture, 부분 패턴",
    "Layer 3 (256ch): 얼굴 부위 윤곽",
    "Layer 4 (512ch): semantic abstraction",
    "",
    "해상도 256→8 (32배 ↓)",
    "채널 64→512 (8배 ↑)",
    "→ 공간 정보 → 의미 정보",
], Cm(1.5), Cm(4.7), Cm(13), Cm(11), size=13)

img_path = SAMPLES_DIR / "feature_maps_all.png"
add_image(s, img_path, Cm(15), Cm(4), width=Cm(18))
add_footer(s, 8)


# ━━━ Slide 9: Grad-CAM ━━━
s = add_blank_slide(prs)
add_header(s, "04 · 시각화 (2/2)",
           "Grad-CAM · 설명 가능한 비전 AI (Selvaraju 2017 ICCV)")
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
add_footer(s, 9)


# ━━━ Slide 10: 자동 입력 + Refinement ━━━
s = add_blank_slide(prs)
add_header(s, "03 · 보조 모듈", "자동 입력 생성 + Refinement Network")
add_text(s, "Phase 7-A: 자동 입력 생성",
         Cm(1), Cm(3.5), Cm(15), Cm(1), size=20, bold=True, color=NAVY)
add_bullet_list(s, [
    "MediaPipe 478 landmarks → Bezier 곡선",
    "시술별 mask (convex hull + dilate)",
    "Color guide (HSV 기반)",
    "9채널 SC-FEGAN 입력 자동 구성",
], Cm(1), Cm(4.8), Cm(15), Cm(7), size=14)

add_text(s, "Phase 7-B: Refinement Network",
         Cm(17), Cm(3.5), Cm(15), Cm(1), size=20, bold=True, color=ACCENT)
add_bullet_list(s, [
    "작은 U-Net + residual wrapper",
    "L1 + VGG19 Perceptual Loss (Johnson 2016)",
    "역할: SD 출력 artifact 제거 + 경계 자연스러움",
    "결과: val_l1 0.045",
    "Colab T4, 2 epochs",
], Cm(17), Cm(4.8), Cm(15), Cm(7), size=14)

# 박스 강조
add_text(s, "→ GAN backbone에 model-agnostic하게 작동",
         Cm(1), Cm(15), Cm(32), Cm(1),
         size=16, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
add_footer(s, 10)


# ━━━ Slide 11: SD Inpaint (GAN 우회) ━━━
s = add_blank_slide(prs)
add_header(s, "03 · GAN 우회",
           "SC-FEGAN → Stable Diffusion Inpaint (Rombach 2022 CVPR)")
add_text(s,
    "원 계획 SC-FEGAN (TF 1.15) → Python 3.12 비호환 → SD Inpaint로 우회",
    Cm(1), Cm(3.5), Cm(32), Cm(1),
    size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
img_path = SAMPLES_DIR / "all_sd_results.png"
add_image(s, img_path, Cm(1), Cm(4.5), width=Cm(32))
add_footer(s, 11)


# ━━━ Slide 12: Confusion Matrix + Per-class ━━━
s = add_blank_slide(prs)
add_header(s, "04 · 성능 분석",
           "Confusion Matrix + Per-class IoU")
img_path = SAMPLES_DIR / "confusion_matrices_all.png"
add_image(s, img_path, Cm(1), Cm(3.8), width=Cm(20))

add_text(s, "주요 패턴",
         Cm(22), Cm(4), Cm(11), Cm(1), size=18, bold=True, color=NAVY)
add_bullet_list(s, [
    "쉬움 (Big areas):",
    "  background: 0.889",
    "  skin: 0.635",
    "",
    "어려움 (Small areas):",
    "  nose: 0.695",
    "  mouth: 0.590",
    "  eye: 0.448 ⚠",
    "",
    "→ Class imbalance",
    "→ 모든 모델 동일 패턴",
    "→ 데이터 본질의 한계",
], Cm(22), Cm(5.2), Cm(11), Cm(12), size=12)
add_footer(s, 12)


# ━━━ Slide 13: Failure Case ━━━
s = add_blank_slide(prs)
add_header(s, "04 · Failure Case", "Sample-wise mIoU · Worst-5 분석")
add_bullet_list(s, [
    "Sample-wise mIoU (5-class, 50장):",
    "  평균: 0.6096",
    "  표준편차: 0.0920",
    "  최저: 0.4164 / 최고: 0.7418",
    "",
    "Best vs Worst 격차 (불안정성):",
    "  eye Δ=0.384 ⚠ (가장 불안정)",
    "  skin Δ=0.332, nose/mouth Δ=0.24",
    "  bg Δ=0.128 (가장 안정)",
    "",
    "→ eye가 데이터 다양성에 가장 민감",
    "",
    "향후 강화: CutMix, Hard Example Mining",
], Cm(1.5), Cm(4), Cm(15), Cm(13), size=12)
img_path = SAMPLES_DIR / "worst_5_samples.png"
add_image(s, img_path, Cm(17), Cm(4), width=Cm(16))
add_footer(s, 13)


# ━━━ Slide 14: Live 데모 ━━━
s = add_blank_slide(prs)
add_header(s, "05 · 시연", "Live 데모 · Colab T4 GPU")

add_text(s,
    "▶ 데모 시연",
    Cm(1), Cm(5), Cm(32), Cm(2),
    size=44, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
add_text(s,
    "Colab 노트북 13",
    Cm(1), Cm(8), Cm(32), Cm(1.2),
    size=24, color=ACCENT, align=PP_ALIGN.CENTER, bold=True)
add_text(s,
    "사진 업로드 → 478 랜드마크 → SD Inpaint (30 steps, ~30초) → Before/After",
    Cm(1), Cm(10.5), Cm(32), Cm(1),
    size=16, color=CHARCOAL, align=PP_ALIGN.CENTER)
add_text(s,
    "통합 변형: 코끝 + 쌍커풀 + V라인 동시 시뮬레이션",
    Cm(1), Cm(12), Cm(32), Cm(1),
    size=14, color=MUTED, align=PP_ALIGN.CENTER, bold=True)
add_text(s,
    "https://colab.research.google.com/github/keonU206/cv-final/blob/main/notebooks/13_sd_inpaint.ipynb",
    Cm(1), Cm(15), Cm(32), Cm(1),
    size=10, color=ACCENT, align=PP_ALIGN.CENTER)
add_footer(s, 14)


# ━━━ Slide 15: 한계 + 향후 + 결론 ━━━
s = add_blank_slide(prs)
add_header(s, "05 · 마무리", "한계 + 향후 강화 + 결론")

add_text(s, "현재 한계",
         Cm(1), Cm(3.5), Cm(15), Cm(1), size=18, bold=True, color=ACCENT)
add_bullet_list(s, [
    "U-Net mIoU plateau (~0.55)",
    "SD Inpaint 변형 강도 보수적",
    "한국인 얼굴 미특화",
    "SC-FEGAN 환경 호환 X",
], Cm(1), Cm(4.7), Cm(15), Cm(5), size=13)

add_text(s, "향후 강화 방향",
         Cm(17), Cm(3.5), Cm(15), Cm(1), size=18, bold=True, color=NAVY)
add_bullet_list(s, [
    "ControlNet (Zhang 2023 ICCV) — 정밀 제어",
    "InstantID (Wang 2024) — Identity 보존",
    "Korean Face LoRA (Hu 2022) — 도메인 적응",
    "Multi-seed Ensemble UI",
], Cm(17), Cm(4.7), Cm(15), Cm(5), size=13)

# 결론 박스
box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(1), Cm(11), Cm(31), Cm(6))
box.fill.solid()
box.fill.fore_color.rgb = LIGHT_BG
box.line.color.rgb = NAVY
box.line.width = Pt(1.5)
box.shadow.inherit = False

add_text(s, "🎯 결론",
         Cm(2), Cm(11.5), Cm(28), Cm(1), size=20, bold=True, color=NAVY)
add_bullet_list(s, [
    "모듈식 설계 → SC-FEGAN → SD Inpaint 교체로 model-agnostic 검증",
    '"Architecture < Methodology" — U-Net plateau 학술 발견',
    "Grad-CAM + Feature Map → '설명 가능한 비전 AI' 만족",
], Cm(2), Cm(12.8), Cm(28), Cm(5), size=14)
add_footer(s, 15)


# ━━━ Slide 16: 감사합니다 (NEW · 박한샘 패턴) ━━━
s = add_blank_slide(prs)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()

add_text(s, "감사합니다",
         Cm(1), Cm(6.5), Cm(32), Cm(3),
         size=72, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, font=FONT_BOLD)
add_text(s, "Thank You",
         Cm(1), Cm(10), Cm(32), Cm(1.5),
         size=24, color=ICE, align=PP_ALIGN.CENTER)
add_text(s, "Q & A",
         Cm(1), Cm(13), Cm(32), Cm(1.5),
         size=28, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
add_text(s, "github.com/keonU206/cv-final",
         Cm(1), Cm(16), Cm(32), Cm(0.8),
         size=12, color=ICE, align=PP_ALIGN.CENTER)


# ─── 저장 ───
prs.save(str(PPTX_PATH))
print(f"✅ 발표 슬라이드 생성 완료: {PPTX_PATH}")
print(f"   슬라이드 수: {len(prs.slides)}")
import os
print(f"   파일 크기: {os.path.getsize(PPTX_PATH) / 1024:.1f} KB")
print()
print("📋 새 구성 (박한샘 패턴 반영):")
print("  1. 표지")
print("  2. 목차 (NEW)")
print("  3. 문제 정의 (NEW · 사용자 페르소나)")
print("  4. 데이터셋 (3개 통계 박스 강조)")
print("  5. 시스템 아키텍처 (5단계 다이어그램)")
print("  6. U-Net 4종 + plateau")
print("  7. 평가 지표 (NEW · 5개 지표 박스)")
print("  8. Feature Map")
print("  9. Grad-CAM")
print("  10. 자동 입력 + Refinement")
print("  11. SD Inpaint")
print("  12. Confusion Matrix")
print("  13. Failure Case")
print("  14. Live 데모")
print("  15. 한계 + 향후 + 결론")
print("  16. 감사합니다 (NEW)")
