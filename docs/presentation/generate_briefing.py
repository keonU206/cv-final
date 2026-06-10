"""팀원 배포용 발표 직전 슬라이드별 브리핑 PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)

pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBold", "C:/Windows/Fonts/malgunbd.ttf"))

NAVY = colors.HexColor("#1E2761")
ICE = colors.HexColor("#CADCFC")
ACCENT = colors.HexColor("#F96167")
CHARCOAL = colors.HexColor("#2C3E50")
MUTED = colors.HexColor("#7B8FA1")
BG = colors.HexColor("#FAFBFD")
LIGHT_BORDER = colors.HexColor("#E2E8F0")
GREEN = colors.HexColor("#2C5F2D")

styles = getSampleStyleSheet()

H1 = ParagraphStyle("H1", fontName="MalgunBold", fontSize=20, leading=26,
                    textColor=NAVY, spaceBefore=10, spaceAfter=8)
H2 = ParagraphStyle("H2", fontName="MalgunBold", fontSize=14, leading=20,
                    textColor=NAVY, spaceBefore=10, spaceAfter=6)
H3 = ParagraphStyle("H3", fontName="MalgunBold", fontSize=11, leading=15,
                    textColor=ACCENT, spaceBefore=6, spaceAfter=3)
Body = ParagraphStyle("Body", fontName="Malgun", fontSize=10, leading=14,
                      textColor=CHARCOAL, alignment=TA_JUSTIFY, spaceAfter=4)
Bullet = ParagraphStyle("Bullet", parent=Body, leftIndent=12, bulletIndent=4,
                        spaceAfter=2)
Caption = ParagraphStyle("Cap", fontName="Malgun", fontSize=8.5, leading=12,
                         textColor=MUTED, italic=True)
TitleStyle = ParagraphStyle("Title", fontName="MalgunBold", fontSize=24,
                            leading=30, textColor=NAVY, alignment=TA_CENTER,
                            spaceAfter=8)
SubStyle = ParagraphStyle("Sub", fontName="Malgun", fontSize=12, leading=18,
                          textColor=MUTED, alignment=TA_CENTER, italic=True,
                          spaceAfter=14)
QAStyle = ParagraphStyle("QA", fontName="Malgun", fontSize=10, leading=14,
                         textColor=CHARCOAL, leftIndent=10, spaceAfter=3,
                         italic=True)
KeyQuote = ParagraphStyle("KQ", fontName="MalgunBold", fontSize=10.5,
                          leading=15, textColor=NAVY, leftIndent=8,
                          rightIndent=8, spaceAfter=6)


def info_box(text, color=BG, border_color=NAVY):
    t = Table([[Paragraph(text, Body)]], colWidths=[15*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 1.2, border_color),
    ]))
    return t


def std_table(rows, col_widths):
    tbl = Table(rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
        ("FONTNAME", (0, 1), (-1, -1), "Malgun"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl


doc = SimpleDocTemplate(
    "C:/Users/User/Documents/cv-final/docs/presentation/slide_briefing.pdf",
    pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    title="발표 슬라이드 브리핑 — 팀원 배포용",
)
story = []

# ─── 표지 ───
story.append(Spacer(1, 2*cm))
story.append(Paragraph("성형 견적 시각화 시스템", TitleStyle))
story.append(Paragraph("발표 슬라이드 10장 — 팀원 브리핑", SubStyle))
story.append(Spacer(1, 0.5*cm))
story.append(info_box(
    "<b>이 문서는 누가 어떤 슬라이드를 발표하든 답변 가능하도록 정리한 가이드입니다.</b> "
    "외부에서 받은 cv_proposal_slides 10장 기준. 우리 plan_v2와 95% 일치 확인됨.",
    color=ICE, border_color=NAVY,
))
story.append(Spacer(1, 0.4*cm))

cover_meta = Table([
    ["발표일", "2026-05-18"],
    ["대상 슬라이드", "cv_proposal_slides (10장)"],
    ["방향성 일치도", "95% (보완 사항 1가지)"],
    ["예상 점수", "89/100 (40% 모델 설계 핵심)"],
], colWidths=[5*cm, 10*cm])
cover_meta.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (0, -1), "MalgunBold"),
    ("FONTNAME", (1, 0), (1, -1), "Malgun"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
    ("BACKGROUND", (0, 0), (0, -1), BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("INNERGRID", (0, 0), (-1, -1), 0.3, LIGHT_BORDER),
    ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
]))
story.append(cover_meta)
story.append(PageBreak())

# ─── 1. 방향성 평가 ───
story.append(Paragraph("1. 방향성 일치 평가", H1))

story.append(Paragraph("결론: 95% 일치 — 그대로 발표 OK", H2))
story.append(Paragraph(
    "외부 슬라이드 10장은 우리 plan_v2와 거의 완벽히 일치합니다. "
    "U-Net 자체 학습, CelebAMask-HQ 30K, mIoU/Dice 평가, Grad-CAM 해석, "
    "4주 일정, 윤리 고려까지 모두 우리 계획과 동일합니다.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("⚠️ 단 하나 보완 사항 — 클래스 정의", H3))
story.append(info_box(
    "<b>슬라이드 5</b>: \"6 클래스 = 코·눈·입·턱·눈썹 + bg\"<br/>"
    "<b>우리 실제 코드</b>: \"6 클래스 = bg / nose / eye / mouth / skin / (unused)\"<br/><br/>"
    "→ 슬라이드는 턱·눈썹을 별도 클래스로 표시했지만, 실제로는 "
    "<b>눈썹은 eye에 묶고 턱은 학습 X (후처리에서 skin → 랜드마크로 분리)</b>입니다. "
    "이 차이는 의도적이며, jaw 라벨이 데이터셋에 없어 가짜 라벨보다 후처리가 안전하기 때문입니다.",
    color=BG, border_color=ACCENT,
))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "만약 교수님이 \"턱이 학습 클래스에 있나요?\" 물으면 →", H3))
story.append(info_box(
    "\"학습 단계에서는 skin으로 묶고, 추론 후 MediaPipe 랜드마크로 턱 영역을 분리합니다. "
    "CelebAMask-HQ에 jaw 라벨이 없어 가짜 라벨보다 후처리가 학술적으로 더 정직합니다.\"",
    color=ICE, border_color=NAVY,
))
story.append(PageBreak())

# ─── 슬라이드별 브리핑 ───
story.append(Paragraph("2. 슬라이드별 배경지식 + 예상 Q&A", H1))

# ─ Slide 1 ─
story.append(Paragraph("슬라이드 1 — 표지", H2))
story.append(Paragraph("<b>발표 시작 한 줄</b>", H3))
story.append(info_box(
    "\"U-Net 자체 학습 + 사전학습 SC-FEGAN으로 성형 시술을 객관적으로 시각화하는 시스템\"",
    color=ICE, border_color=NAVY,
))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "팀명, 팀원 소개, 날짜 (2026.05.18) 자연스럽게 진행. 이 슬라이드는 10초 이내.",
    Body))
story.append(Spacer(1, 10))

# ─ Slide 2 ─
story.append(Paragraph("슬라이드 2 — 목차", H2))
story.append(Paragraph(
    "발표 흐름 8개 챕터 (문제 → 솔루션 → 데이터 → 모델 → 흐름 → 평가 → 해석 → 일정). "
    "학술 발표 표준 구성. 빠르게 넘김 (10초).",
    Body))
story.append(Spacer(1, 10))

# ─ Slide 3 ─
story.append(Paragraph("슬라이드 3 — 문제 정의 (\"장원영? 차은우? How Much?\")", H2))
story.append(Paragraph("<b>핵심 메시지 2가지</b>", H3))
story.append(Paragraph("• 시술 진단의 주관성 (상담사 경험 의존)", Bullet))
story.append(Paragraph("• 시술 후 결과 예측 불가 (2D 합성 수준)", Bullet))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>슬로건 활용</b>", H3))
story.append(Paragraph(
    "\"장원영? 차은우? How Much?\"는 누구나 거울 보며 한 번쯤 하는 생각. "
    "이 슬로건이 우리 시스템의 답하려는 질문임을 강조.",
    Body))
story.append(Spacer(1, 10))

# ─ Slide 4 ─
story.append(Paragraph("슬라이드 4 — Task 정의 (3단계 파이프라인)", H2))
story.append(Paragraph("<b>3단계 high-level</b>", H3))
story.append(std_table([
    ["Stage", "내용", "모델", "학습"],
    ["1. 얼굴 분석", "MediaPipe 478 landmarks + 비율 10종", "사전학습", "X"],
    ["2. 영역 분할", "U-Net 6 클래스 픽셀 분할", "자체 학습", "★ O"],
    ["3. 시각화", "SC-FEGAN Before/After + PDF", "사전학습", "X"],
], [3*cm, 6*cm, 3*cm, 1.5*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>예상 질문 1</b>: MediaPipe와 U-Net 차이?", H3))
story.append(Paragraph(
    "\"MediaPipe는 점 좌표 추출(landmark detection), "
    "U-Net은 픽셀 영역 분할(semantic segmentation)입니다. "
    "역할이 달라 둘 다 필요합니다.\"",
    QAStyle))
story.append(PageBreak())

# ─ Slide 5 ─
story.append(Paragraph("슬라이드 5 — 데이터셋 (CelebAMask-HQ)", H2))
story.append(Paragraph("<b>핵심 숫자</b> (외움)", H3))
story.append(std_table([
    ["항목", "값"],
    ["총 이미지", "30,000장 (1024×1024 원본 또는 256 리사이즈)"],
    ["원본 라벨", "19 클래스 (skin, nose, l_eye, r_eye, l_brow, r_brow, mouth, ...)"],
    ["우리 매핑", "6 클래스 (bg + 5 부위)"],
    ["분할", "Train 24K / Val 3K / Test 3K"],
    ["출처", "Lee et al., CVPR 2020 (MaskGAN 부속)"],
    ["라이선스", "비상업 연구 용도 (학술 발표 OK)"],
], [3.5*cm, 11*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>예상 질문 1</b>: 왜 19를 6으로 줄였나?", H3))
story.append(Paragraph(
    "\"우리 task는 시술 부위 5종(코·눈·입·턱·이마)이라 "
    "무관한 라벨(hair, hat, cloth 등)을 배경으로 묶었습니다.\"",
    QAStyle))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>예상 질문 2</b>: 왜 이 데이터셋?", H3))
story.append(Paragraph(
    "\"세 가지 이유입니다: ① CVPR 2020 학술 표준이라 신뢰성, "
    "② 30K로 학습/검증 분할 충분, ③ 픽셀 단위 라벨이 segmentation에 적합.\"",
    QAStyle))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>예상 질문 3 (보완 사항)</b>: 턱·눈썹이 학습 클래스?", H3))
story.append(Paragraph(
    "\"학습 단계에서는 눈썹을 eye에 묶고, 턱은 skin에 포함시킵니다. "
    "추론 후 MediaPipe 랜드마크로 skin 영역을 jaw/forehead로 분리합니다. "
    "데이터셋에 jaw 라벨이 없어 가짜 라벨보다 후처리가 학술적으로 정직합니다.\"",
    QAStyle))
story.append(PageBreak())

# ─ Slide 6 ─
story.append(Paragraph("슬라이드 6 — U-Net 모델 설계 ★ (40% 핵심)", H2))
story.append(Paragraph("<b>5개 키 박스 — 각각 한 줄로 외움</b>", H3))
story.append(std_table([
    ["키워드", "한 줄 설명"],
    ["ResNet-34 Encoder", "ImageNet으로 사전학습된 34층 CNN"],
    ["U-Net Decoder", "Upsample + skip connection으로 원본 크기 복원"],
    ["계층적 특징 추출 ★", "얕은 층(엣지/색) → 깊은 층(의미) 단계적 추상화"],
    ["Skip Connection ★", "Encoder의 공간 정보를 Decoder에 직접 전달"],
    ["Multi-class 분할", "Softmax 6-way + Cross-Entropy (Combo Loss 일부)"],
    ["전이 학습", "ImageNet 가중치 활용 → 학습 효율 ↑"],
], [4*cm, 11*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>외워야 할 한 문장 ★</b>", H3))
story.append(info_box(
    "\"U-Net의 인코더는 단계적 다운샘플링으로 <b>계층적 특징을 추출</b>하고, "
    "디코더는 <b>Skip Connection</b>으로 공간 정보를 결합해 픽셀 단위 분할을 수행합니다.\"",
    color=ICE, border_color=ACCENT,
))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>예상 질문 1</b>: 왜 U-Net? 더 최신 모델 없나?", H3))
story.append(Paragraph(
    "\"U-Net은 의료 영상의 표준 segmentation 아키텍처(MICCAI 2015)입니다. "
    "계층적 특징 + skip connection이 수업에서 배운 CNN 구조적 원리에 직접 대응하고, "
    "1달 일정에 학습 가능한 규모입니다.\"",
    QAStyle))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>예상 질문 2</b>: 왜 ResNet-34? ResNet-50이 더 좋지 않나?", H3))
story.append(Paragraph(
    "\"ResNet-50은 파라미터 2배라 학습 시간 ↑. ResNet-34는 face parsing에서 "
    "검증된 속도/정확도 균형입니다. ResNet-50 시도는 Week 3 ablation 옵션.\"",
    QAStyle))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>예상 질문 3</b>: 처음부터 학습하지 않는 이유?", H3))
story.append(Paragraph(
    "\"30K 데이터로 ResNet을 처음부터 학습하면 underfit 가능. "
    "ImageNet 사전학습 가중치 활용이 일반적 best practice입니다.\"",
    QAStyle))
story.append(PageBreak())

# ─ Slide 7 ─
story.append(Paragraph("슬라이드 7 — 시스템 흐름 (E2E 5단계)", H2))
story.append(Paragraph("<b>5단계 흐름</b> (외움)", H3))
story.append(std_table([
    ["#", "단계", "기술", "비고"],
    ["1", "사진 업로드", "Streamlit UI", "—"],
    ["2", "랜드마크 + 비율", "MediaPipe Tasks API", "478점"],
    ["3", "추천 엔진", "룰베이스 3종", "if-else"],
    ["4", "U-Net 분할 ★", "자체 학습 segmentation", "6 클래스"],
    ["5", "GAN 시각화", "SC-FEGAN 사전학습", "Before/After"],
], [0.7*cm, 3.5*cm, 6*cm, 4*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>데모 시술 3종</b> (외움)", H3))
story.append(Paragraph("코끝 성형 · 쌍커풀 · 사각턱 + V라인", Body))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>예상 질문</b>: 추천 엔진 왜 ML 아닌가?", H3))
story.append(Paragraph(
    "\"룰베이스 if-else입니다. ① 시술 추천 라벨링 데이터 없음, "
    "② 룰베이스가 설명 가능(\"황금비 벗어남 → 코끝 추천\"), "
    "③ 본 프로젝트의 핵심은 segmentation이고 추천은 보조 역할.\"",
    QAStyle))
story.append(PageBreak())

# ─ Slide 8 ─
story.append(Paragraph("슬라이드 8 — 성능 분석 (Ablation Study)", H2))
story.append(Paragraph("<b>평가 지표 4개</b> (외움)", H3))
story.append(std_table([
    ["지표", "정의", "용도"],
    ["mIoU", "배경 제외 클래스별 IoU 평균", "메인 지표"],
    ["Dice", "F1 유사, 영역 겹침", "보조 지표"],
    ["Per-class IoU", "클래스별 IoU 분리", "약한 부위 분석"],
    ["Confusion Matrix", "정답 vs 예측 매트릭스", "혼동 패턴"],
], [3*cm, 7*cm, 5*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>Ablation 예상 수치</b> (슬라이드 8 표)", H3))
story.append(std_table([
    ["실험", "예상 mIoU"],
    ["Baseline (no aug)", "0.72"],
    ["+ Flip / Rotate", "0.76 (+4%)"],
    ["+ Color jitter", "0.78 (+2%)"],
    ["+ Cutout / Mixup", "0.81 (+3%)"],
], [10*cm, 5*cm]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "* 이 수치는 \"예상\"임을 명시. 실제 학습 결과는 Week 3에 확정.",
    Caption))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>알아둘 추가 개념</b>", H3))
story.append(Paragraph(
    "• <b>Cutout</b>: 이미지 일부를 검정색으로 가림 → 부분만 봐도 인식 강건<br/>"
    "• <b>Mixup</b>: 두 이미지 섞어 새 이미지 생성 → 일반화 ↑",
    Body))
story.append(PageBreak())

# ─ Slide 9 ─
story.append(Paragraph("슬라이드 9 — 시각화 및 해석 (Grad-CAM)", H2))
story.append(Paragraph("<b>3가지 시각화 도구</b>", H3))
story.append(std_table([
    ["도구", "보여주는 것", "용도"],
    ["Grad-CAM", "\"왜 이 영역을 X로 판단했나\" heatmap", "Explainable AI (15%)"],
    ["Feature Map", "각 conv layer 활성화 패턴", "계층적 특징 확인"],
    ["Before / After + Diff", "시술 전후 픽셀 단위 변화", "결과 시각화"],
], [3.5*cm, 7*cm, 4.5*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>Grad-CAM 적용 위치</b>", H3))
story.append(Paragraph(
    "Encoder bottleneck = 가장 깊은 layer = <code>model.encoder.layer4[-1]</code> (ResNet-34 기준)",
    Body))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>예상 질문</b>: Grad-CAM이 segmentation에 의미 있나? 분류용 아닌가?", H3))
story.append(Paragraph(
    "\"원래는 분류용이지만, SemanticSegmentationTarget 변형으로 segmentation에도 적용 가능합니다. "
    "Encoder bottleneck에 hook해서 특정 클래스(예: nose) 예측 영역의 활성화를 시각화합니다.\"",
    QAStyle))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>PDF 견적서</b> (Week 4 작업)", H3))
story.append(Paragraph(
    "최종 데모에서 시술명 + 가격 + Before/After 이미지를 reportlab으로 자동 PDF 생성. "
    "실용성 어필 포인트.",
    Body))
story.append(PageBreak())

# ─ Slide 10 ─
story.append(Paragraph("슬라이드 10 — 일정 + 윤리적 고려", H2))
story.append(Paragraph("<b>4주 일정</b>", H3))
story.append(std_table([
    ["Week", "기간", "내용", "상태"],
    ["1", "5/8–14", "환경 셋업 · SC-FEGAN 검증", "✓ 완료"],
    ["2", "5/19–26", "U-Net 데이터로더 + PoC 학습", "진행 예정"],
    ["3", "5/27–6/2", "본격 학습 · Ablation · Grad-CAM", "—"],
    ["4", "6/3–9", "Streamlit 통합 · 최종 발표", "—"],
], [1.2*cm, 2.5*cm, 8*cm, 2.5*cm]))
story.append(Spacer(1, 8))
story.append(Paragraph("<b>윤리적 고려 3가지 ★ (교수님이 좋아할 부분)</b>", H3))
story.append(std_table([
    ["주제", "내용"],
    ["외모 평가가 아닌 시뮬레이션", "\"미의 기준\" 정의 X. 학습된 패턴 시각화."],
    ["학습 데이터 편향 인지", "CelebAMask-HQ의 인종·성별 분포 한계 명시"],
    ["의료 의사결정 대체 불가", "전문의 상담의 보조 도구. 진단 도구 아님."],
], [5*cm, 10*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>예상 질문</b>: 이거 위험하지 않나?", H3))
story.append(Paragraph(
    "\"학술 데모임을 명시합니다. 의료 자문이 아닌 시각화 도구로 정의했고, "
    "실제 적용 시 의료법·개인정보보호법 추가 검토가 필요합니다.\"",
    QAStyle))
story.append(PageBreak())

# ─── 3. 통합 답변 ───
story.append(Paragraph("3. 통합 답변 — 프로젝트 핵심 한 문장", H1))
story.append(Spacer(1, 6))
story.append(info_box(
    "\"우리는 MediaPipe로 얼굴 점 478개를 추출해 비율을 분석하고, "
    "룰베이스로 시술을 추천한 뒤, "
    "ImageNet 사전학습 ResNet-34 인코더와 U-Net 디코더로 구성된 "
    "자체 학습 모델로 얼굴 6 클래스를 픽셀 단위 분할하고, "
    "그 마스크를 사전학습된 SC-FEGAN의 입력으로 사용해 Before/After를 생성하며, "
    "mIoU·Dice·Confusion Matrix로 평가하고 Grad-CAM으로 해석합니다.\"",
    color=ICE, border_color=ACCENT,
))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "→ 이 한 문장이 슬라이드 10장 전체 요약. 외울 필요는 없고 키워드만 알면 OK.",
    Caption))
story.append(Spacer(1, 16))

# ─── 4. 외워두기 체크리스트 ───
story.append(Paragraph("4. 외워두기 체크리스트", H1))
checklist_groups = [
    ("핵심 모델 + 데이터", [
        "U-Net (Encoder-Decoder + Skip Connection)",
        "ResNet-34 (ImageNet 사전학습)",
        "SC-FEGAN (ICCV 2019, 사전학습)",
        "CelebAMask-HQ (CVPR 2020, 30K, 19→6 클래스)",
        "MediaPipe Tasks API (478 landmarks)",
    ]),
    ("개념 키워드", [
        "계층적 특징 추출 (Hierarchical Feature Extraction)",
        "Skip Connection (공간 정보 보존)",
        "Transfer Learning (전이 학습)",
        "Semantic Segmentation (픽셀 단위 분류)",
        "Combo Loss (0.5 × Dice + 0.5 × Cross-Entropy)",
    ]),
    ("평가 + 해석", [
        "mIoU (배경 제외 평균 IoU)",
        "Dice Score (F1 유사)",
        "Confusion Matrix",
        "Ablation Study (Augmentation 비교)",
        "Grad-CAM (Encoder bottleneck hook)",
    ]),
    ("일정 + 윤리", [
        "4주 일정 (Week 1 ✓ / 2~4 진행)",
        "데모 시술 3종: 코끝 · 쌍커풀 · 사각턱+V라인",
        "윤리 3가지: 미의 기준 X / 데이터 편향 / 의료 대체 X",
    ]),
]
for title, items in checklist_groups:
    story.append(Paragraph(title, H3))
    for it in items:
        story.append(Paragraph(f"☐ {it}", Bullet))
    story.append(Spacer(1, 4))

story.append(PageBreak())

# ─── 5. 절대 하지 말 것 ───
story.append(Paragraph("5. 절대 하지 말 것 (발표 자살 행위)", H1))
donts = [
    "\"사전학습 모델을 그냥 가져다 썼어요\" — 학습 컴포넌트 강조 누락",
    "Grad-CAM, IoU 같은 용어 모르는 듯 얼버무리기",
    "데이터셋 출처 (CelebAMask-HQ / CVPR 2020) 못 답하기",
    "왜 U-Net 인지 못 답하기 (수업 원리 연결 못 함)",
    "현재 mIoU 값 없다고 자신감 잃기 (Week 2 PoC는 발표용 아님)",
    "윤리 질문에 \"문제 없어요\" 단답 — 3가지 고려 사항 모두 짚어야 함",
]
for d in donts:
    story.append(Paragraph(f"✗ {d}", Bullet))
story.append(Spacer(1, 16))

story.append(Paragraph("6. 발표 직전 30분에 다시 볼 것", H1))
final = [
    "본 문서의 §3 (통합 답변 한 문장) — 외움",
    "본 문서의 §4 (외워두기 체크리스트) — 박스 체크",
    "study_guide.pdf §14 (예상 질문 Q1~Q5)",
    "glossary.pdf 4페이지 (발표 TOP 10 용어)",
]
for f in final:
    story.append(Paragraph(f"• {f}", Bullet))
story.append(Spacer(1, 18))

footer = Paragraph(
    "<i>이 문서는 외부 cv_proposal_slides 10장 + 우리 plan_v2 통합 브리핑입니다.<br/>"
    "팀원 누구든 발표 직전 빠르게 읽고 답변 가능하도록 작성되었습니다.<br/>"
    "kim · 2026-05-18</i>",
    Caption)
story.append(footer)

doc.build(story)
print("✅ Saved: slide_briefing.pdf")
