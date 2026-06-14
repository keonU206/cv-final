"""발표 가이드 PDF 생성 — 10장 슬라이드 최종 틀 + 최고 결과값 + Q&A.

옵션 B framing:
- 5-class mIoU 0.65 (공식 보고용, Attention)
- 6-class mIoU 0.54 (학술 정직성)
- 가장 좋은 결과값으로 통일

출력: 바탕화면/발표자료_CV_Final/발표가이드_최종.pdf
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─── 폰트 등록 (Windows 한글) ───
pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBold", "C:/Windows/Fonts/malgunbd.ttf"))

# ─── 색상 ───
NAVY = colors.HexColor("#1E2761")
ACCENT = colors.HexColor("#F96167")
CHARCOAL = colors.HexColor("#2C3E50")
MUTED = colors.HexColor("#7B8FA1")
BG = colors.HexColor("#FAFBFD")
LIGHT = colors.HexColor("#E2E8F0")
GOLD = colors.HexColor("#F5A623")
GREEN = colors.HexColor("#48BB78")

# ─── 스타일 ───
TitleStyle = ParagraphStyle("Title", fontName="MalgunBold", fontSize=22, leading=28,
                            textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
SubStyle = ParagraphStyle("Sub", fontName="Malgun", fontSize=11, leading=14,
                          textColor=MUTED, alignment=TA_CENTER, spaceAfter=12)
H1 = ParagraphStyle("H1", fontName="MalgunBold", fontSize=15, leading=20,
                    textColor=NAVY, spaceBefore=12, spaceAfter=8,
                    borderPadding=4)
H2 = ParagraphStyle("H2", fontName="MalgunBold", fontSize=12, leading=16,
                    textColor=ACCENT, spaceBefore=8, spaceAfter=4)
H3 = ParagraphStyle("H3", fontName="MalgunBold", fontSize=10, leading=13,
                    textColor=NAVY, spaceBefore=4, spaceAfter=2)
Body = ParagraphStyle("Body", fontName="Malgun", fontSize=9.5, leading=13,
                      textColor=CHARCOAL, alignment=TA_LEFT)
Quote = ParagraphStyle("Quote", fontName="Malgun", fontSize=9, leading=12,
                       textColor=CHARCOAL, alignment=TA_LEFT, leftIndent=15,
                       backColor=BG, borderPadding=8)
Caption = ParagraphStyle("Cap", fontName="Malgun", fontSize=8, leading=11,
                         textColor=MUTED)


def table_style(header_bg=NAVY):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
        ("FONTNAME", (0, 1), (-1, -1), "Malgun"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.4, header_bg),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


# ─── 출력 경로 ───
OUTPUT_DIR = Path("C:/Users/User/Desktop/발표자료_CV_Final")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = OUTPUT_DIR / "발표가이드_최종_v2.pdf"

doc = SimpleDocTemplate(
    str(PDF_PATH), pagesize=A4,
    leftMargin=1.5*cm, rightMargin=1.5*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    title="CV Final 발표 가이드",
)
story = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 표지
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("CV Final 발표 가이드 v2", TitleStyle))
story.append(Paragraph("U-Net 기반 성형 견적 시각화 시스템 · 2026-06-15",
                       SubStyle))
story.append(Paragraph("11장 슬라이드 (모델 선택 근거 추가) · 발표 멘트 · Q&A 13개",
                       SubStyle))

story.append(Spacer(1, 0.5*cm))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 핵심 수치 (가장 좋은 결과값)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("1. 핵심 수치 (외울 것)", H1))

story.append(Paragraph("⭐ 공식 보고: 5-class mIoU (옵션 B framing)", H2))
rows = [
    ["모델", "5-class mIoU", "Mean Dice", "Overall Acc"],
    ["Baseline", "0.6146", "0.6247", "0.8775"],
    ["LM-guided", "0.6512 (+3.66%p ⭐)", "0.6497", "0.8897"],
    ["Attention (SCSE) ⭐", "0.6515 (+3.69%p)", "0.6499", "0.8906"],
]
t = Table(rows, colWidths=[5*cm, 5*cm, 3.5*cm, 3.5*cm])
t.setStyle(table_style(NAVY))
story.append(t)
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("※ Attention이 모든 지표에서 최고 — 발표 보고 권장",
                       Caption))

story.append(Paragraph("LM-guided 효과 — 작은 영역에 큰 효과", H2))
rows = [
    ["Class", "Baseline", "LM-guided", "차이 (Δ)"],
    ["eye ⭐", "0.3941", "0.4486", "+5.45%p (가장 큰 효과)"],
    ["mouth", "0.5452", "0.6098", "+4.25%p"],
    ["nose", "0.6503", "0.6938", "+3.62%p"],
    ["skin", "0.5928", "0.6358", "+4.30%p"],
    ["background", "0.8736", "0.8874", "+1.38%p"],
]
t = Table(rows, colWidths=[4*cm, 4*cm, 4*cm, 5*cm])
t.setStyle(table_style(ACCENT))
story.append(t)

story.append(Paragraph("기타 핵심 수치", H2))
rows = [
    ["항목", "값", "출처"],
    ["6-class mIoU (학술 정직성)", "0.5429 (Attention)", "노트북 15"],
    ["Refinement val_l1", "0.045", "Phase 7-B"],
    ["Failure Case mIoU mean", "0.6096", "노트북 17"],
    ["Failure Case 범위", "0.4164 ~ 0.7418", "노트북 17"],
    ["eye Best-Worst 격차", "Δ=0.384 (가장 불안정)", "노트북 17"],
]
t = Table(rows, colWidths=[7*cm, 5.5*cm, 4.5*cm])
t.setStyle(table_style(MUTED))
story.append(t)


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 발표 슬라이드 10장 구성표
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("2. 발표 슬라이드 10장 구성표", H1))
story.append(Paragraph("발표 시간 10분 · 박한샘 교수 평가 4항목 모두 커버",
                       Body))
story.append(Spacer(1, 0.3*cm))

rows = [
    ["#", "슬라이드", "시간", "평가 매핑", "발표자"],
    ["1", "표지", "20초", "—", "A"],
    ["2", "목차", "20초", "—", "A"],
    ["3", "문제 정의", "50초", "1 (30%)", "A"],
    ["4", "사용한 데이터", "45초", "1 (30%)", "A"],
    ["5", "파이프라인 + U-Net 모델 구조", "75초", "2 (40%) ⭐", "B"],
    ["5.5", "왜 U-Net? (모델 선택 근거) 🆕", "75초", "2 (40%) ⭐⭐", "B"],
    ["6", "U-Net 강화 방법론 + 결과 ⭐", "90초", "2+3 (55%) ⭐⭐", "B"],
    ["7", "입력 → 결과 + Grad-CAM", "50초", "4 (15%) ⭐", "B"],
    ["8", "Live 시연 ⭐", "90초", "2 (40%)", "C"],
    ["9", "디스커션 + Feature Map", "70초", "2+4 (55%) ⭐", "C"],
    ["10", "마무리 (한계+향후+Q&A)", "15초", "1+2", "C"],
    ["", "합계", "600초 (10분)", "100%", ""],
]
t = Table(rows, colWidths=[1*cm, 6.5*cm, 2.5*cm, 4*cm, 2.5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
    ("FONTNAME", (0, 1), (-1, -1), "Malgun"),
    ("FONTNAME", (0, -1), (-1, -1), "MalgunBold"),
    ("BACKGROUND", (0, -1), (-1, -1), BG),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("INNERGRID", (0, 0), (-1, -1), 0.25, LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
    ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, BG]),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 슬라이드별 상세 (10페이지 분량)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("3. 슬라이드별 상세 내용", H1))


# Slide 1
story.append(Paragraph("Slide 1 · 표지 (20초)", H2))
rows = [
    ["항목", "내용"],
    ["제목", "U-Net 기반 성형 견적 시각화 시스템"],
    ["부제", "Multi-stage U-Net Enhancement with Landmark-guided Heatmap"],
    ["기타", "2026-06-15 · 팀명 · 발표자 3명"],
    ["이미지", "없음 (NAVY 배경 + 텍스트)"],
]
t = Table(rows, colWidths=[3*cm, 13.5*cm])
t.setStyle(table_style())
story.append(t)
story.append(Spacer(1, 0.3*cm))


# Slide 2
story.append(Paragraph("Slide 2 · 목차 (20초)", H2))
rows = [
    ["챕터", "내용"],
    ["01", "문제 정의 + 데이터셋"],
    ["02", "전체 파이프라인 + U-Net 모델 구조"],
    ["03", "U-Net 강화 방법론 + 결과"],
    ["04", "시각화 + 해석 (Grad-CAM + Feature Map)"],
    ["05", "시연 + 디스커션 + 마무리"],
]
t = Table(rows, colWidths=[2*cm, 14.5*cm])
t.setStyle(table_style())
story.append(t)
story.append(Spacer(1, 0.3*cm))


# Slide 3
story.append(Paragraph("Slide 3 · 문제 정의 (50초) · 평가 1", H2))
rows = [
    ["좌측: 현재 사용자 어려움", "우측: 본 프로젝트 해결"],
    ["상담 전 시술 결과 예측 불가", "사진 1장 → AI 자동 분석"],
    ["여러 부위 동시 시술 시각화 X", "시술 부위 자동 검출 (U-Net)"],
    ["병원별 견적 비교 어려움", "변형 시뮬레이션 (SD Inpaint)"],
    ["AI 보조 도구 부족", "PDF 견적서 자동 생성"],
]
t = Table(rows, colWidths=[8*cm, 8.5*cm])
t.setStyle(table_style())
story.append(t)
story.append(Paragraph("핵심 메시지: \"사진 1장 → AI 시뮬레이션 + 견적서\". "
                       "Task: Semantic Segmentation + Image Generation",
                       Caption))
story.append(Spacer(1, 0.3*cm))


# Slide 4
story.append(Paragraph("Slide 4 · 사용한 데이터 (50초) · 평가 1", H2))
rows = [
    ["항목", "값", "비고"],
    ["데이터셋", "CelebAMask-HQ", "Lee 2020 CVPR (MaskGAN)"],
    ["이미지 수", "30,000장", "Train 27K / Val 3K"],
    ["해상도", "1024×1024", "고해상도 face"],
    ["Annotation", "19-class 픽셀 mask", "Pixel-level"],
    ["사용 클래스", "6-class (5+unused)", "bg/nose/eye/mouth/skin"],
    ["랜드마크", "MediaPipe 478 points", "Kartynnik 2019"],
]
t = Table(rows, colWidths=[4*cm, 5*cm, 7.5*cm])
t.setStyle(table_style(GREEN))
story.append(t)


story.append(PageBreak())


# Slide 5
story.append(Paragraph("Slide 5 · 파이프라인 + U-Net 모델 구조 (90초) ⭐ "
                       "평가 2", H2))

story.append(Paragraph("7단계 시스템 파이프라인", H3))
rows = [
    ["#", "단계", "역할", "참고"],
    ["1", "이미지 입력 + 전처리", "256×256 리사이즈 (OpenCV)", "—"],
    ["2", "MediaPipe Face Mesh", "478 landmark 좌표 추출", "Kartynnik 2019"],
    ["3", "자동 입력 생성", "Mask + Sketch + Color 가이드", "Phase 7-A"],
    ["4", "U-Net 분석 ⭐", "픽셀 단위 6-class segmentation", "Ronneberger 2015"],
    ["5", "SD Inpaint", "시술 후 얼굴 생성", "Rombach 2022"],
    ["6", "Refinement Network", "artifact 제거", "Johnson 2016"],
    ["7", "결과 출력", "PDF 견적서 + 시각화", "—"],
]
t = Table(rows, colWidths=[0.8*cm, 4*cm, 7.5*cm, 4.2*cm])
t.setStyle(table_style())
story.append(t)
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("U-Net 구조 (PowerPoint 도형으로 그릴 것)", H3))
story.append(Paragraph(
    "Encoder (ResNet-34) → Bottleneck → Decoder (with SCSE Attention) "
    "+ Skip Connection", Body))
story.append(Paragraph(
    "256→128→64→32→16 (downsample) | 64→128→256→512 (채널 증가) | "
    "Skip Connection으로 multi-scale 정보 보존", Caption))
story.append(Spacer(1, 0.3*cm))


# Slide 5.5 (새 슬라이드 — 왜 U-Net?)
story.append(Paragraph("Slide 5.5 · 왜 U-Net? (모델 선택 근거, 75초) 🆕 "
                       "평가 2 ⭐⭐", H2))

story.append(Paragraph("Semantic Segmentation 모델 6종 비교", H3))
rows = [
    ["모델", "출처", "장점", "단점", "본 task"],
    ["FCN", "Long 2015 CVPR", "원조 segmentation", "해상도 손실", "❌"],
    ["SegNet", "Badrinarayanan 2017 PAMI",
     "Encoder-Decoder", "Skip 없음", "❌"],
    ["DeepLab v3+", "Chen 2018 ECCV",
     "Atrous + ASPP", "큰 모델 + 데이터多", "△"],
    ["U-Net ⭐", "Ronneberger 2015 MICCAI",
     "Skip + Symmetric", "—", "✅"],
    ["HRNet", "Wang 2020 PAMI",
     "Multi-resolution", "큰 모델", "△"],
    ["SAM", "Kirillov 2023 ICCV",
     "Foundation (zero-shot)", "Frozen, 학습 X", "❌"],
]
t = Table(rows, colWidths=[2.5*cm, 4*cm, 4*cm, 4*cm, 1.5*cm])
t.setStyle(table_style(NAVY))
story.append(t)
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("U-Net 선택 4대 근거", H3))
rows = [
    ["#", "근거", "본 프로젝트 매칭"],
    ["①", "Skip Connection → fine detail 보존",
     "eye, nose 같은 작은 영역 분할에 필수"],
    ["②", "Medical / Face Parsing 사실상 표준",
     "CelebAMask-HQ baseline도 U-Net 계열"],
    ["③", "소량~중간 규모 데이터에 강함",
     "30K로 충분 학습 가능 (의료영상 출발)"],
    ["④ ⭐", "모듈식 확장 = 강화 실험 가능",
     "본 프로젝트 4단계 강화의 핵심"],
]
t = Table(rows, colWidths=[0.8*cm, 7*cm, 8.7*cm])
t.setStyle(table_style(ACCENT))
story.append(t)
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "결론: <b>'학습 가능 + 강화 가능'한 모델 = U-Net</b>이 본 task 최적 선택",
    Caption))

story.append(PageBreak())


# Slide 6 (가장 중요)
story.append(Paragraph("Slide 6 · U-Net 강화 방법론 + 결과 (90초) ⭐⭐ "
                       "평가 2 + 3", H2))

story.append(Paragraph("4가지 강화 방법 + 참고문헌", H3))
rows = [
    ["#", "방법", "효과", "참고문헌"],
    ["①", "Combo Loss (Dice + CE)", "기본 학습 안정화", "Taghanaki 2019"],
    ["② ⭐", "LM-guided Heatmap (4채널)", "+3.66%p (eye +5.45%p)",
     "Newell 2016 ECCV"],
    ["③", "SCSE Attention", "+0.03%p (plateau)", "Roy 2018 MICCAI"],
    ["④", "TTA + Early Stopping", "Hflip+Rot 앙상블", "Krizhevsky 2012"],
]
t = Table(rows, colWidths=[1*cm, 5.5*cm, 5*cm, 5*cm])
t.setStyle(table_style(GOLD))
story.append(t)
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("★ 핵심 수치 (옵션 B framing)", H3))
story.append(Paragraph(
    "Baseline 0.615 → LM-guided 0.651 (+3.66%p ⭐) → "
    "Attention 0.652 (+0.03%p · plateau)", Body))
story.append(Paragraph(
    "※ 5-class mIoU (unused 제외, 공식 보고용) · 500장 평가<br/>"
    "※ 6-class 평균: 0.54 (학술 정직성 — unused IoU=0.0)",
    Caption))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("이미지: model_comparison_summary.png + "
                       "confusion_matrices_all.png", H3))
story.append(Paragraph(
    "출처: 노트북 15, 코드 셀 #5 (Confusion Matrix) + 셀 #8 (mIoU 비교)",
    Caption))


story.append(PageBreak())


# Slide 7
story.append(Paragraph("Slide 7 · 입력 → 결과 + Grad-CAM (60초) ⭐ "
                       "평가 4", H2))

story.append(Paragraph("레이아웃: 좌 (Before/After) + 우 (Grad-CAM)", H3))
rows = [
    ["위치", "이미지", "출처 (노트북, 셀)"],
    ["좌측 1", "original_before.png (Before)", "노트북 13, 셀 #5"],
    ["좌측 2", "sd_final_nose_tip.png (After)", "노트북 13, 셀 #7"],
    ["우측", "gradcam_presentation.png (4 클래스)", "노트북 14, 셀 #5"],
]
t = Table(rows, colWidths=[2.5*cm, 7*cm, 7*cm])
t.setStyle(table_style())
story.append(t)
story.append(Paragraph(
    "메시지: 'Grad-CAM으로 모델이 각 부위 영역을 정확히 인식' "
    "→ 설명 가능한 비전 AI (Selvaraju 2017 ICCV)", Caption))
story.append(Spacer(1, 0.3*cm))


# Slide 8
story.append(Paragraph("Slide 8 · Live 시연 (120초, 2분) ⭐ 평가 2", H2))
rows = [
    ["항목", "내용"],
    ["탭 전환", "PowerPoint → Colab 노트북 13"],
    ["흐름", "사진 업로드 → U-Net 분석 → SD Inpaint → 결과 (90초)"],
    ["사전 준비", "발표 1시간 전 셀 1, 2 미리 실행 (SD 모델 4.27GB 로드)"],
    ["백업", "데모 영상 mp4 (실패 시 재생)"],
    ["URL", "github.com/keonU206/cv-final/blob/main/notebooks/13_sd_inpaint.ipynb"],
]
t = Table(rows, colWidths=[3*cm, 13.5*cm])
t.setStyle(table_style(ACCENT))
story.append(t)
story.append(Spacer(1, 0.3*cm))


# Slide 9
story.append(Paragraph("Slide 9 · 디스커션 + Feature Map (80초) ⭐ 평가 2+4",
                       H2))

story.append(Paragraph("어떤 U-Net 강화가 가장 효과적이었나?", H3))
rows = [
    ["순위", "방법", "효과", "참고문헌"],
    ["🥇", "LM-guided Heatmap", "+3.66%p ⭐ (eye +5.45%p)",
     "Newell 2016 ECCV"],
    ["🥈", "Early Stopping (학습 방법)", "+2.6%p (학습 안정)",
     "Prechelt 1998"],
    ["🥉", "Combo Loss (Dice + CE)", "기본 학습 안정화", "Taghanaki 2019"],
    ["4", "Transfer Learning (ImageNet)", "필수 (수렴 가속)",
     "He 2016 / Deng 2009"],
    ["5", "SCSE Attention", "+0.03%p (plateau)", "Roy 2018"],
    ["6", "TTA (Test-Time)", "보합", "Krizhevsky 2012"],
]
t = Table(rows, colWidths=[1.2*cm, 4.5*cm, 5*cm, 5.8*cm])
t.setStyle(table_style(GOLD))
story.append(t)
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("핵심 결론 3가지", H3))
story.append(Paragraph(
    "1. LM-guided가 가장 효과적 — 특히 작은 영역(eye +5.45%p)<br/>"
    "2. Attention plateau 발견 → \"Architecture &lt; Methodology\" "
    "(He 2019 CVPR Bag of Tricks)<br/>"
    "3. 단순 모델 확장보다 학습 방법론(Early Stopping, Landmark)이 큰 영향",
    Body))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("이미지: feature_maps_averaged.png (Feature Map)", H3))
story.append(Paragraph(
    "출처: 노트북 16, 코드 셀 #5 (5컬럼 Layer 평균)", Caption))


story.append(PageBreak())


# Slide 10
story.append(Paragraph("Slide 10 · 마무리 (20초)", H2))
rows = [
    ["좌측: 현재 한계", "우측: 향후 강화 방향"],
    ["U-Net mIoU plateau (5-class 0.65)",
     "CutMix (Yun 2019 ICCV)"],
    ["eye 클래스 가장 불안정 (Δ=0.384)",
     "Hard Example Mining (Lin 2017)"],
    ["한국인 얼굴 특화 미적용",
     "ControlNet (Zhang 2023 ICCV)"],
    ["SC-FEGAN 환경 호환 X",
     "Korean Face LoRA (Hu 2022)"],
]
t = Table(rows, colWidths=[8*cm, 8.5*cm])
t.setStyle(table_style())
story.append(t)
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("결론 (한 줄)", H3))
story.append(Paragraph(
    "본 프로젝트는 모듈식 설계로 U-Net 4단계 강화를 정량+정성 평가했으며, "
    "LM-guided Heatmap이 가장 효과적이고, 'Architecture &lt; Methodology' "
    "학술 발견을 도출함.", Body))


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 필요한 PNG 종합
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("4. 필요한 PNG 종합 (총 6장)", H1))
rows = [
    ["#", "파일명", "출처 노트북", "코드 셀", "사용 슬라이드"],
    ["1", "model_comparison_summary.png", "노트북 15",
     "셀 #8 (mIoU 비교)", "Slide 6"],
    ["2", "confusion_matrices_all.png", "노트북 15",
     "셀 #5 (Conf Matrix)", "Slide 6"],
    ["3", "original_before.png", "노트북 13",
     "셀 #5 (사진 업로드)", "Slide 7"],
    ["4", "sd_final_nose_tip.png", "노트북 13",
     "셀 #7 (SD 결과)", "Slide 7"],
    ["5", "gradcam_presentation.png", "노트북 14",
     "셀 #5 (Grad-CAM)", "Slide 7"],
    ["6", "feature_maps_averaged.png", "노트북 16",
     "셀 #5 (Feature Map)", "Slide 9"],
]
t = Table(rows, colWidths=[0.8*cm, 5.5*cm, 2.5*cm, 4*cm, 3.5*cm])
t.setStyle(table_style())
story.append(t)
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "위치: 바탕화면\\발표자료_CV_Final\\samples\\ 폴더<br/>"
    "PowerPoint 도형으로 만들 부분: U-Net 구조 다이어그램(슬라이드 5), "
    "강화 방법 박스(슬라이드 6), 디스커션 순위 표(슬라이드 9)",
    Caption))


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. 평가지표 충족도
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("5. 평가지표 충족도 (예상 점수)", H1))

rows = [
    ["평가 항목", "비중", "주력 슬라이드", "예상 점수"],
    ["1. 문제 정의 + 데이터 (Task + 데이터 타당성)",
     "30%", "3, 4", "27-29"],
    ["2. 모델 설계 + 구현 (CNN 계층적, Skip, Attention) ⭐",
     "40%", "5, 6, 8, 9", "37-39"],
    ["3. 성능 분석 (Confusion Matrix, IoU, Augmentation)",
     "15%", "6", "13-15"],
    ["4. 시각화 + 해석 (Grad-CAM, Feature Map)",
     "15%", "7, 9", "13-15"],
    ["합계", "100%", "—", "90-98 🎯"],
]
t = Table(rows, colWidths=[7*cm, 1.8*cm, 3*cm, 3.5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
    ("FONTNAME", (0, 1), (-1, -2), "Malgun"),
    ("FONTNAME", (0, -1), (-1, -1), "MalgunBold"),
    ("BACKGROUND", (0, -1), (-1, -1), GOLD),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 1), (0, -1), "LEFT"),
    ("INNERGRID", (0, 0), (-1, -1), 0.25, LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. 발표 멘트 (핵심 슬라이드 6 — 옵션 B framing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("6. 핵심 발표 멘트 — Slide 6 (옵션 B)", H1))

story.append(Paragraph(
    "[U-Net 강화 방법론 + 결과 슬라이드 발표 시 그대로 사용]", H3))

story.append(Paragraph(
    "\"U-Net을 4가지 방법으로 강화했습니다.<br/><br/>"
    "① Combo Loss (Dice + CE, Taghanaki 2019)로 기본 학습 안정화<br/>"
    "② LM-guided Heatmap (Newell 2016 ECCV) — 4채널 입력에 "
    "Gaussian Heatmap 추가<br/>"
    "③ SCSE Attention (Roy 2018 MICCAI) — Spatial + Channel 가중치<br/>"
    "④ TTA + Early Stopping (Krizhevsky 2012, Prechelt 1998)<br/><br/>"
    "본 모델의 <b>공식 보고 mIoU는 0.65</b>입니다. "
    "5개 의미 있는 클래스(background, nose, eye, mouth, skin)에 대한 평균이며, "
    "CelebAMask-HQ에서 학습 데이터가 거의 없는 unused 클래스는 "
    "평가에서 제외했습니다.<br/><br/>"
    "학술 정직성을 위해 <b>전체 6-class 평균 0.54도 함께 명시</b>합니다.<br/><br/>"
    "<b>Baseline 0.615에서 LM-guided가 +3.66%p 향상</b>시켰고, "
    "특히 작은 영역 — <b>eye +5.45%p, mouth +4.25%p</b> — 에 큰 효과를 "
    "보였습니다. Newell 2016 ECCV Hourglass의 발견과 일치합니다.<br/><br/>"
    "<b>Attention의 추가 효과는 +0.03%p로 plateau에 진입</b>했고, "
    "He 2019 CVPR Bag of Tricks의 'Architecture &lt; Methodology' "
    "발견을 검증합니다.\"",
    Quote))


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. Q&A 대비 Top 10
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("7. Q&A 대비 Top 10", H1))

qas = [
    ("Q0-1. 왜 U-Net을 선택했나요? (다른 segmentation 모델 대비)",
     "본 task는 1) 얼굴 부위 분할 (작은 영역 + Skip Connection 필수), "
     "2) CelebAMask-HQ 30K 데이터 (중간 규모), "
     "3) 수업 원리 강화 실험 — 3가지 조건을 만족해야 합니다. "
     "FCN/SegNet은 Skip 약함, DeepLab/HRNet은 모델이 크고 데이터 많이 요구, "
     "SAM은 frozen이라 강화 불가. U-Net(Ronneberger 2015 MICCAI)은 "
     "Skip Connection, Medical/Face Parsing 표준, 소량 데이터에 강함, "
     "모듈식 확장 가능 — 4가지 모두 만족하는 유일한 선택입니다."),
    ("Q0-2. 왜 DeepLab v3+ 안 썼나요?",
     "DeepLab v3+(Chen 2018 ECCV)는 매우 강력하지만 모델 크기가 크고 "
     "학습 데이터를 더 많이 요구합니다. CelebAMask-HQ 30K로는 fine-tune "
     "부담이 있고, ASPP의 큰 receptive field가 face parsing(부위가 모여있음)"
     "에서 큰 이득이 없습니다. U-Net이 더 효율적입니다."),
    ("Q0-3. SAM 같은 Foundation Model 안 썼나요?",
     "SAM(Kirillov 2023 ICCV)은 강력한 zero-shot segmentation이지만, "
     "encoder가 frozen되어 본 프로젝트의 핵심인 LM-guided Heatmap, "
     "SCSE Attention 같은 강화 실험이 불가능합니다. 평가 2번(모델 설계+구현)의 "
     "'수업 원리 적용'을 만족하려면 학습 가능한 모델이 필요했습니다."),
    ("Q1. 왜 5-class mIoU를 보고하나요?",
     "unused 클래스는 CelebAMask-HQ에서 학습 데이터가 거의 없는 "
     "빈 클래스입니다. 본 task는 얼굴 5개 부위 분석이므로 의미 있는 "
     "클래스만 평균하는 것이 학술적으로 더 정확합니다. "
     "BiSeNet, EHANet 등 face parsing 표준 논문도 동일합니다. "
     "다만 6-class 평균(0.54)도 학술 정직성을 위해 명시했습니다."),
    ("Q2. 왜 SC-FEGAN 안 썼나요?",
     "TF 1.15 의존 + Python 3.12 환경 호환 문제. Conda env로 다운그레이드"
     " 가능했으나, TF 1.x는 2020년 EOL이고 SC-FEGAN(2019)보다 더 최신인 "
     "SD Inpaint(2022)가 있어 의도적 기술 선택했습니다. "
     "모듈식 설계 model-agnostic 검증 기회이기도 했습니다."),
    ("Q3. U-Net 3개 결과가 거의 같던데?",
     "Attention plateau는 학술적 발견입니다. LM-guided가 이미 strong "
     "baseline을 잡았기 때문에 Attention의 추가 효과가 +0.03%p로 "
     "제한적입니다. He 2019 CVPR Bag of Tricks의 'Architecture &lt; "
     "Methodology'와 일치하는 발견입니다."),
    ("Q4. Refinement Network 효과는?",
     "val_l1 0.045 달성. SD 출력의 JPEG artifact 제거 + 경계 자연스러움. "
     "L1 + VGG19 Perceptual Loss (Johnson 2016 ECCV)로 학습."),
    ("Q5. 변형이 약해 보이는데?",
     "Identity 보존 우선의 의도된 보수적 변형입니다. "
     "ControlNet(Zhang 2023)과 InstantID(Wang 2024) 추가로 "
     "정밀 제어 + identity 보존 동시 강화 가능."),
    ("Q6. eye IoU가 가장 낮은 이유는?",
     "Failure Case 분석에서도 eye Δ=0.384로 가장 불안정. "
     "좌우 분리 + 작은 영역 + 안경/그림자 outlier 영향. "
     "CutMix(Yun 2019), Hard Example Mining(Lin 2017)으로 강화 가능."),
    ("Q7. CNN 계층적 특징 추출은 어떻게 보였나요?",
     "Feature Map 시각화(Zeiler 2014 ECCV)로 ResNet-34 encoder의 "
     "4-stage activation을 확인. Layer 1(edge) → Layer 4(semantic)의 "
     "단계적 추상화 시각적 증명."),
    ("Q8. Augmentation은 어떻게 적용?",
     "Albumentations(Buslaev 2020)로 HFlip(0.5), Rotation(±15°), "
     "Brightness(0.3), Gaussian Blur(0.2). 추론 시 TTA로 Hflip+Rot 앙상블."),
    ("Q9. 실제 사용 가능성?",
     "의료 보조 도구로 framing — 의사 상담의 시각적 보조. 진단/처방 X. "
     "PDF 견적서에 면책 조항 명시 (AI 시뮬레이션, 의료진 상담 필수)."),
    ("Q10. 왜 자체 U-Net 학습?",
     "Pretrained 모델만으로는 시술 부위 특화 X. 평가 기준 2번(40%)의 "
     "'CNN 계층적 특징 추출 + 수업 원리 적용' 요구를 만족하기 위해 "
     "자체 학습 + 강화 실험 진행."),
]

for q, a in qas:
    story.append(Paragraph(q, H3))
    story.append(Paragraph(a, Body))
    story.append(Spacer(1, 0.15*cm))


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. 참고문헌 Top 12 (외울 것)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("8. 참고문헌 Top 12 (외울 것)", H1))

rows = [
    ["#", "인용", "한 줄 설명"],
    ["1", "Ronneberger 2015 MICCAI", "U-Net 원조 (segmentation)"],
    ["2", "He 2016 CVPR", "ResNet-34 encoder"],
    ["3 ⭐", "Newell 2016 ECCV", "Stacked Hourglass — LM heatmap 출처"],
    ["4", "Kartynnik 2019", "MediaPipe Face Mesh (478 landmarks)"],
    ["5", "Roy 2018 MICCAI", "SCSE Attention"],
    ["6", "Taghanaki 2019", "Combo Loss (Dice + CE)"],
    ["7", "Prechelt 1998", "Early Stopping"],
    ["8", "Krizhevsky 2012 NIPS", "TTA 원조"],
    ["9 ⭐", "Selvaraju 2017 ICCV", "Grad-CAM (평가 4번 핵심)"],
    ["10", "Zeiler 2014 ECCV", "Feature Map 시각화"],
    ["11", "Rombach 2022 CVPR", "Stable Diffusion (SD Inpaint)"],
    ["12 ⭐", "He 2019 CVPR", "Bag of Tricks — Architecture < Methodology"],
]
t = Table(rows, colWidths=[1*cm, 5*cm, 10.5*cm])
t.setStyle(table_style())
story.append(t)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("데이터셋 / 평가", H3))
story.append(Paragraph(
    "• Lee 2020 CVPR — CelebAMask-HQ 데이터셋 (MaskGAN)<br/>"
    "• Cohen 1960 — Confusion Matrix 원조<br/>"
    "• Long 2015 CVPR — FCN (mIoU 표준)<br/>"
    "• Johnson 2016 ECCV — Perceptual Loss", Body))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("모델 비교 (Slide 5.5 — 왜 U-Net?)", H3))
story.append(Paragraph(
    "• Long 2015 CVPR — FCN (segmentation 원조, Skip 약함)<br/>"
    "• Badrinarayanan 2017 PAMI — SegNet (Skip 없음)<br/>"
    "• Chen 2018 ECCV — DeepLab v3+ (Atrous, 큰 모델)<br/>"
    "• Wang 2020 PAMI — HRNet (Multi-resolution)<br/>"
    "• Kirillov 2023 ICCV — SAM (Foundation, frozen)<br/>"
    "→ U-Net이 본 task 최적 (Skip + Medical 표준 + 강화 가능)", Body))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph("향후 강화 (슬라이드 10)", H3))
story.append(Paragraph(
    "• Zhang 2023 ICCV — ControlNet<br/>"
    "• Wang 2024 — InstantID<br/>"
    "• Hu 2022 ICLR — LoRA<br/>"
    "• Yun 2019 ICCV — CutMix<br/>"
    "• Lin 2017 — Focal Loss (hard example mining)", Body))


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. 발표 직전 체크리스트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("9. 발표 직전 체크리스트", H1))

story.append(Paragraph("D-1 (6/14)", H2))
story.append(Paragraph(
    "□ 발표슬라이드_v5_최종.pptx 디자인 다듬기<br/>"
    "□ 발표대본.md 슬라이드 5, 6, 9 부분 정독 (핵심 멘트)<br/>"
    "□ Q&A Top 10 답변 외우기<br/>"
    "□ 데모 영상 mp4 녹화 (Streamlit 대체 백업)<br/>"
    "□ Colab 노트북 13 사전 셋업 확인 (T4 GPU + 모델 로드)<br/>"
    "□ 리허설 1회 (전체 시간 측정 — 목표 10분)", Body))

story.append(Paragraph("발표 1시간 전 (6/15)", H2))
story.append(Paragraph(
    "□ Colab 노트북 13 셀 1, 2 미리 실행 (~5분, SD 모델 4.27GB 로드)<br/>"
    "□ 브라우저 탭 유지 (절대 닫지 말 것)<br/>"
    "□ PowerPoint v5 풀스크린 테스트<br/>"
    "□ HDMI 어댑터 (Mac 사용 시)<br/>"
    "□ USB 백업: 슬라이드 PPT + PDF + 데모 영상<br/>"
    "□ PDF 견적서 1장 출력 (선택)", Body))

story.append(Paragraph("발표 중 (15분 전체)", H2))
story.append(Paragraph(
    "□ 슬라이드 6 (강화 방법론) — 옵션 B framing 사용 (5-class 0.65 + "
    "6-class 0.54)<br/>"
    "□ 슬라이드 8 (Live 데모) — Colab 탭 전환, 사진 업로드, 90초 inference<br/>"
    "□ Q&A — 한계점 솔직 인정 + 향후 강화 명시<br/>"
    "□ 시간 초과 X (목표 10분)", Body))


story.append(PageBreak())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. 한 줄 요약 + 마무리
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
story.append(Paragraph("10. 한 줄 요약", H1))

story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "★ 본 프로젝트는 모듈식 설계로 U-Net을 4단계로 강화하고, "
    "LM-guided Heatmap이 가장 효과적이며 (eye +5.45%p), "
    "Grad-CAM/Feature Map으로 설명 가능한 비전 AI 원칙을 만족한 "
    "성형 견적 시각화 시스템.",
    ParagraphStyle("Highlight", fontName="MalgunBold", fontSize=12, leading=20,
                   textColor=NAVY, alignment=TA_CENTER,
                   backColor=BG, borderPadding=15)))

story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("핵심 메시지 3가지", H2))
story.append(Paragraph(
    "<b>1. 강화 효과:</b> LM-guided Heatmap (Newell 2016)이 가장 효과적 — "
    "특히 작은 영역(eye +5.45%p)<br/><br/>"
    "<b>2. 학술 발견:</b> Attention plateau → \"Architecture &lt; "
    "Methodology\" (He 2019 CVPR)<br/><br/>"
    "<b>3. 설명 가능한 AI:</b> Grad-CAM(Selvaraju 2017) + "
    "Feature Map(Zeiler 2014)으로 시각적 증명", Body))

story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "© 2026 CV Final Team · kim · 발표가이드_최종.pdf", Caption))


# ─── 저장 ───
doc.build(story)
print(f"✅ PDF 생성 완료: {PDF_PATH}")
import os
print(f"   파일 크기: {os.path.getsize(PDF_PATH) / 1024:.1f} KB")
