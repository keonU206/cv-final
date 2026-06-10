"""발표 직전 학습용 PDF 생성 — 성형 견적 시각화 v1 vs v2 + 핵심 개념."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)

# ─── 한글 폰트 등록 ───
pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBold", "C:/Windows/Fonts/malgunbd.ttf"))

# ─── 색상 팔레트 (Midnight Executive — 슬라이드와 통일) ───
NAVY = colors.HexColor("#1E2761")
ICE = colors.HexColor("#CADCFC")
ACCENT = colors.HexColor("#F96167")
CHARCOAL = colors.HexColor("#2C3E50")
MUTED = colors.HexColor("#7B8FA1")
BG = colors.HexColor("#FAFBFD")
LIGHT_BORDER = colors.HexColor("#E2E8F0")

# ─── 스타일 ───
styles = getSampleStyleSheet()

H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontName="MalgunBold", fontSize=22, leading=28,
    textColor=NAVY, spaceBefore=12, spaceAfter=10, alignment=TA_LEFT,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontName="MalgunBold", fontSize=16, leading=22,
    textColor=NAVY, spaceBefore=14, spaceAfter=8, alignment=TA_LEFT,
)
H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"],
    fontName="MalgunBold", fontSize=13, leading=18,
    textColor=ACCENT, spaceBefore=8, spaceAfter=5,
)
Body = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontName="Malgun", fontSize=10.5, leading=16,
    textColor=CHARCOAL, alignment=TA_JUSTIFY, spaceAfter=4,
)
Bullet = ParagraphStyle(
    "Bullet", parent=Body,
    leftIndent=14, bulletIndent=4, spaceAfter=3,
)
Caption = ParagraphStyle(
    "Caption", parent=Body,
    fontSize=9, textColor=MUTED, italic=True, alignment=TA_LEFT,
)
TitleStyle = ParagraphStyle(
    "Title", fontName="MalgunBold", fontSize=28, leading=34,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=10,
)
SubTitleStyle = ParagraphStyle(
    "SubTitle", fontName="Malgun", fontSize=14, leading=20,
    textColor=MUTED, alignment=TA_CENTER, spaceAfter=20, italic=True,
)
KeyBoxStyle = ParagraphStyle(
    "KeyBox", fontName="MalgunBold", fontSize=11, leading=16,
    textColor=NAVY, leftIndent=8, rightIndent=8, spaceAfter=6,
)

# ─── 표 스타일 ───
TBL_HEADER = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("FONTNAME", (0, 1), (-1, -1), "Malgun"),
    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("INNERGRID", (0, 0), (-1, -1), 0.3, LIGHT_BORDER),
    ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
])

# ────────────────────────────────────────────────────────────
# 문서 빌드
# ────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    "C:/Users/User/Documents/cv-final/docs/presentation/study_guide.pdf",
    pagesize=A4,
    leftMargin=2.0*cm, rightMargin=2.0*cm,
    topMargin=2.0*cm, bottomMargin=2.0*cm,
    title="성형 견적 시각화 — 발표 학습 가이드",
    author="kim · CV Final Team",
)

story = []

# ═══ 표지 ═══
story.append(Spacer(1, 4*cm))
story.append(Paragraph("성형 견적 시각화 시스템", TitleStyle))
story.append(Paragraph("v1 vs v2 비교 + 발표 핵심 개념 정리", SubTitleStyle))
story.append(Spacer(1, 1*cm))

cover_meta = Table([
    ["발표일", "2026-05-18"],
    ["프로젝트", "컴퓨터 비전 기말 (3인 팀)"],
    ["주제", "Image Segmentation + Generation"],
    ["메인 학습 모델", "U-Net (ResNet-34 인코더)"],
    ["데이터셋", "CelebAMask-HQ (CVPR 2020, 30K장)"],
    ["예상 점수", "89/100 (v1 대비 +43)"],
], colWidths=[5*cm, 9*cm])
cover_meta.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (0, -1), "MalgunBold"),
    ("FONTNAME", (1, 0), (1, -1), "Malgun"),
    ("FONTSIZE", (0, 0), (-1, -1), 11),
    ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
    ("TEXTCOLOR", (1, 0), (1, -1), CHARCOAL),
    ("BACKGROUND", (0, 0), (0, -1), BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("INNERGRID", (0, 0), (-1, -1), 0.3, LIGHT_BORDER),
    ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
]))
story.append(cover_meta)
story.append(PageBreak())

# ═══ 목차 ═══
story.append(Paragraph("목차", H1))
toc = [
    "1. v1 모델 — 분석/추천형 (수정 전)",
    "2. v1 → v2 전환 이유 (평가 기준 분석)",
    "3. v2 모델 — U-Net 자체 학습 (현재)",
    "4. 핵심 개념 A — Segmentation Task",
    "5. 핵심 개념 B — U-Net 아키텍처",
    "6. 핵심 개념 C — SC-FEGAN (사전학습 GAN)",
    "7. 핵심 개념 D — MediaPipe Face Mesh",
    "8. 핵심 개념 E — 평가 지표 (IoU, Dice, mIoU)",
    "9. 핵심 개념 F — Loss Function (Combo Loss)",
    "10. 핵심 개념 G — Data Augmentation + Ablation",
    "11. 핵심 개념 H — Grad-CAM (해석 가능성)",
    "12. 핵심 개념 I — CelebAMask-HQ 데이터셋",
    "13. 핵심 개념 J — Transfer Learning",
    "14. 예상 질문 + 모범 답변",
    "15. 발표 시 강조 포인트",
]
for item in toc:
    story.append(Paragraph(f"• {item}", Bullet))
story.append(PageBreak())

# ═══ 1. v1 ═══
story.append(Paragraph("1. v1 모델 — 분석/추천형 (수정 전)", H1))

story.append(Paragraph("1.1 시스템 구조", H2))
story.append(Paragraph(
    "v1은 <b>사전학습 모델 3개를 조합한 파이프라인</b>으로, 자체 학습 컴포넌트가 없다. "
    "얼굴 분석은 MediaPipe, 추천은 룰베이스 if-else, 시각화는 SC-FEGAN을 그대로 사용.",
    Body))
story.append(Spacer(1, 6))

v1_pipeline = Table([
    ["단계", "기술", "역할"],
    ["1. 얼굴 검출", "MediaPipe Tasks API", "478 landmarks 추출"],
    ["2. 비율 분석", "Python (삼정·오안·E-line)", "10개 지표 계산"],
    ["3. 추천 엔진", "룰베이스 if-else (procedures.yaml)", "시술 3종 매칭"],
    ["4. 마스크 생성", "OpenCV Convex Hull", "거친 마스크 (랜드마크 기반)"],
    ["5. 시각화", "SC-FEGAN (사전학습 GAN)", "시술 후 얼굴 생성"],
], colWidths=[3*cm, 6*cm, 7*cm])
v1_pipeline.setStyle(TBL_HEADER)
story.append(v1_pipeline)
story.append(Spacer(1, 10))

story.append(Paragraph("1.2 특징", H2))
features_v1 = [
    "<b>학습 모델 없음</b>: 모든 컴포넌트가 사전학습 또는 룰베이스",
    "<b>구현 난이도 낮음</b>: 라이브러리 조합만으로 동작",
    "<b>마스크 정밀도 낮음</b>: Convex Hull은 다각형 외곽선만 그림",
    "<b>해석 가능성 없음</b>: 룰베이스는 if 조건만 보면 됨 (CNN 해석 불가)",
    "<b>평가 지표 없음</b>: 정답 라벨이 없어 정량 평가 불가",
]
for f in features_v1:
    story.append(Paragraph(f"• {f}", Bullet))
story.append(Spacer(1, 10))

story.append(Paragraph("1.3 한계점", H2))
story.append(Paragraph(
    "v1은 작동은 하지만 <b>학술 발표에서 어필할 포인트가 부족</b>하다. "
    "수업에서 배운 \"CNN 계층적 특징 추출\" 같은 구조적 원리를 직접 적용한 부분이 없고, "
    "성능 평가도 정량적으로 할 수 없다. SC-FEGAN의 결과 품질은 모델 자체의 한계지 "
    "우리가 개선할 수 있는 부분이 아니다.",
    Body))
story.append(PageBreak())

# ═══ 2. v1 → v2 ═══
story.append(Paragraph("2. v1 → v2 전환 이유 (평가 기준 분석)", H1))

story.append(Paragraph("2.1 교수님 평가 기준 (총 100%)", H2))
criteria = Table([
    ["평가 항목", "가중치", "내용"],
    ["문제 정의 + 데이터 타당성", "30%", "Task 명확, 데이터셋 양·질"],
    ["모델 설계 + 구현", "40%", "CNN 계층적 특징 추출, 구조적 원리 적용"],
    ["성능 분석 + 최적화", "15%", "Confusion Matrix, IoU, mAP, Augmentation"],
    ["시각화 + 해석", "15%", "Grad-CAM, Feature Map, 설명 가능한 AI"],
], colWidths=[6*cm, 2.5*cm, 7.5*cm])
criteria.setStyle(TBL_HEADER)
story.append(criteria)
story.append(Spacer(1, 10))

story.append(Paragraph("2.2 v1의 평가 점수 예상", H2))
story.append(Paragraph(
    "각 항목에 v1을 대입하면 <b>치명적 약점이 40% 항목에서 드러난다</b>:",
    Body))
v1_score = Table([
    ["항목", "v1 점수", "이유"],
    ["문제 + 데이터", "18 / 30", "자체 데이터셋 없음, 학술 표준 데이터 미사용"],
    ["모델 설계", "15 / 40", "사전학습 조합만, 자체 학습 X → 거의 빵점"],
    ["성능 분석", "5 / 15", "CV 표준 지표(IoU/mAP) 적용 불가"],
    ["시각화·해석", "8 / 15", "Grad-CAM 못 함 (CNN 미사용)"],
    ["합계", "46 / 100", "발표 시 \"학습한 모델이 뭐냐\" 질문에 답 없음"],
], colWidths=[5*cm, 2.5*cm, 8.5*cm])
v1_score.setStyle(TBL_HEADER)
story.append(v1_score)
story.append(Spacer(1, 10))

story.append(Paragraph("2.3 결정적 인용 — 교수님 원문", H2))
quote = Table([[Paragraph(
    "“CNN의 <b>계층적 특징 추출</b> 또는 기타 다른 방법들을 활용한 "
    "효율적 설계 등 <b>수업에서 배운 구조적 원리</b>를 적절히 적용했는가?”",
    Body)]], colWidths=[14*cm])
quote.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), BG),
    ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ("TOPPADDING", (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ("BOX", (0, 0), (-1, -1), 1.5, ACCENT),
]))
story.append(quote)
story.append(Spacer(1, 10))

story.append(Paragraph("2.4 해결책 — U-Net 자체 학습 추가", H2))
story.append(Paragraph(
    "교수님 평가 기준의 40% 항목을 충족시키려면 <b>자체 학습한 CNN</b>이 필요하다. "
    "옵션 후보 3개 (분류/세그멘테이션/탐지) 중 <b>세그멘테이션 (U-Net)</b>을 선택. "
    "이유: ① 우리 task(부위별 마스크 생성)에 자연스럽게 맞고, "
    "② U-Net의 \"계층적 특징 + skip connection\"이 교수님 원문에 가장 직접적으로 부합, "
    "③ 데이터셋(CelebAMask-HQ)이 학술 표준이라 30% 항목도 같이 충족.",
    Body))
story.append(PageBreak())

# ═══ 3. v2 ═══
story.append(Paragraph("3. v2 모델 — U-Net 자체 학습 (현재)", H1))

story.append(Paragraph("3.1 v1과의 차이 한눈에", H2))
diff = Table([
    ["항목", "v1 (수정 전)", "v2 (수정 후)"],
    ["학습 컴포넌트", "없음", "U-Net 자체 학습 ★"],
    ["마스크 생성", "Convex Hull (거친)", "픽셀 단위 세그멘테이션"],
    ["데이터셋", "샘플 5장", "CelebAMask-HQ 30K장"],
    ["평가 지표", "없음", "mIoU, Dice, Confusion Matrix"],
    ["성능 최적화", "없음", "Augmentation Ablation"],
    ["해석", "시각화만", "Grad-CAM"],
    ["점수 예상", "46 / 100", "89 / 100 (+43)"],
], colWidths=[4.5*cm, 5*cm, 6.5*cm])
diff.setStyle(TBL_HEADER)
story.append(diff)
story.append(Spacer(1, 12))

story.append(Paragraph("3.2 새 파이프라인 (5단계)", H2))
v2_pipe = Table([
    ["#", "단계", "기술", "학습 여부"],
    ["1", "얼굴 검출", "MediaPipe Tasks API (478 landmarks)", "사전학습"],
    ["2", "비율 분석 + 추천", "삼정·오안·E-line + 룰베이스", "—"],
    ["3", "★ 세그멘테이션", "U-Net (ResNet-34 인코더)", "자체 학습"],
    ["4", "시각화", "SC-FEGAN (사전학습 GAN)", "사전학습"],
    ["5", "결과 + 해석", "Before/After + Grad-CAM + PDF", "—"],
], colWidths=[0.7*cm, 3.5*cm, 7.8*cm, 3*cm])
v2_pipe.setStyle(TBL_HEADER)
story.append(v2_pipe)
story.append(Spacer(1, 10))

story.append(Paragraph("3.3 v2가 점수에 어떻게 기여하는지", H2))
contrib = Table([
    ["평가 항목", "v2 대응", "예상 점수"],
    ["문제 + 데이터 (30%)", "CelebAMask-HQ 학술 표준", "27 / 30"],
    ["모델 설계 (40%)", "U-Net 계층적 특징 + skip connection", "35 / 40"],
    ["성능 분석 (15%)", "mIoU + Dice + Confusion Matrix + Ablation", "14 / 15"],
    ["시각화·해석 (15%)", "Grad-CAM + Before/After overlay", "13 / 15"],
    ["합계", "—", "89 / 100"],
], colWidths=[5.5*cm, 7*cm, 2.5*cm])
contrib.setStyle(TBL_HEADER)
story.append(contrib)
story.append(PageBreak())

# ═══ 4. Segmentation ═══
story.append(Paragraph("4. 핵심 개념 A — Segmentation Task", H1))

story.append(Paragraph("4.1 세 가지 비전 task 비교", H2))
tasks_compare = Table([
    ["Task", "출력", "예시"],
    ["Classification (분류)", "이미지 → 한 클래스", "고양이? 강아지?"],
    ["Detection (탐지)", "이미지 → 여러 박스 + 클래스", "코=박스, 눈=박스 ..."],
    ["Segmentation (세그멘테이션)", "이미지 → 픽셀마다 클래스", "각 픽셀이 코/눈/입 ..."],
], colWidths=[6*cm, 5.5*cm, 4.5*cm])
tasks_compare.setStyle(TBL_HEADER)
story.append(tasks_compare)
story.append(Spacer(1, 10))

story.append(Paragraph("4.2 Semantic vs Instance Segmentation", H2))
story.append(Paragraph(
    "• <b>Semantic</b>: 같은 클래스는 같은 라벨 (예: 모든 \"눈\" 픽셀이 클래스 2)<br/>"
    "• <b>Instance</b>: 개별 인스턴스 구분 (왼쪽 눈, 오른쪽 눈 분리)<br/>"
    "→ <b>우리는 Semantic Segmentation</b>. 같은 부위는 한 클래스로 묶음.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("4.3 왜 Segmentation 인가", H2))
story.append(Paragraph(
    "성형 시술은 <b>특정 부위의 픽셀 영역</b>을 변형하는 작업. 박스(detection) 단위가 아니라 "
    "정확한 윤곽선이 필요하므로 픽셀 단위 분류인 Segmentation이 적합. 또한 SC-FEGAN의 "
    "입력으로 픽셀 마스크가 필요해 파이프라인 통합도 자연스럽다.",
    Body))
story.append(PageBreak())

# ═══ 5. U-Net ═══
story.append(Paragraph("5. 핵심 개념 B — U-Net 아키텍처", H1))

story.append(Paragraph("5.1 구조 개요", H2))
story.append(Paragraph(
    "U-Net은 의료 영상 세그멘테이션을 위해 2015년 Ronneberger 등이 발표한 아키텍처. "
    "이름은 \"U\" 모양으로 그려지는 encoder-decoder 구조에서 유래.",
    Body))
story.append(Spacer(1, 6))

unet_arch = Table([
    ["부분", "역할", "동작"],
    ["Encoder", "특징 추출", "Conv + Pool로 단계적 다운샘플링 (저수준 → 고수준)"],
    ["Bottleneck", "추상화 정점", "가장 깊은 특징 (공간 해상도 최소)"],
    ["Decoder", "공간 복원", "Upsample + Conv로 원본 크기까지 복원"],
    ["Skip Connection", "정보 결합", "Encoder의 같은 단계 특징을 Decoder에 직접 전달"],
], colWidths=[3.5*cm, 3.5*cm, 9*cm])
unet_arch.setStyle(TBL_HEADER)
story.append(unet_arch)
story.append(Spacer(1, 10))

story.append(Paragraph("5.2 왜 Skip Connection이 중요한가", H2))
story.append(Paragraph(
    "Encoder가 깊어질수록 <b>공간 정보가 사라짐</b> (downsampling으로 픽셀 위치 정보 손실). "
    "Decoder가 픽셀 단위 예측을 하려면 공간 정보가 필요한데, encoder의 얕은 층(공간 정보 풍부)"
    "에서 가져와 decoder에 직접 전달하는 것이 skip connection. <b>고수준 의미 + 저수준 위치</b>"
    "를 모두 활용 가능.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("5.3 우리의 구체적 구성", H2))
story.append(Paragraph(
    "• <b>Encoder</b>: ResNet-34 (ImageNet 사전학습) — Transfer Learning 활용<br/>"
    "• <b>Decoder</b>: U-Net 표준 (Upsample + Conv + skip concat)<br/>"
    "• <b>출력</b>: (B, 6, H, W) logits → argmax로 픽셀별 클래스 (0~5)<br/>"
    "• <b>구현</b>: segmentation_models_pytorch 라이브러리 (코드 3줄로 정의)",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("5.4 6 클래스 매핑 (교수님이 물어볼 가능성 있음)", H2))
classes_tbl = Table([
    ["우리 클래스", "원본 CelebAMask 라벨", "비고"],
    ["0: background", "bg, hair, hat, cloth, ear ...", "관심 없는 영역 통합"],
    ["1: nose", "nose", "코끝 성형 마스크"],
    ["2: eye", "l_eye, r_eye, l_brow, r_brow", "쌍커풀 시술 (눈썹 포함)"],
    ["3: mouth", "mouth, u_lip, l_lip", "입술 시술"],
    ["4: skin", "skin", "후처리에서 jaw/forehead 분리"],
    ["5: (unused)", "—", "여분 슬롯"],
], colWidths=[4*cm, 6*cm, 6*cm])
classes_tbl.setStyle(TBL_HEADER)
story.append(classes_tbl)
story.append(PageBreak())

# ═══ 6. SC-FEGAN ═══
story.append(Paragraph("6. 핵심 개념 C — SC-FEGAN (사전학습 GAN)", H1))

story.append(Paragraph("6.1 GAN이란", H2))
story.append(Paragraph(
    "<b>Generative Adversarial Network</b>. Generator(생성기)와 Discriminator(판별기) "
    "두 네트워크가 서로 경쟁하며 학습 → Generator가 진짜 같은 이미지를 만들도록 훈련된다.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("6.2 SC-FEGAN의 특징", H2))
story.append(Paragraph(
    "ICCV 2019 (Jo & Park) 논문. <b>마스크된 얼굴 영역에 사용자 가이드로 자연스러운 픽셀을 채워주는 GAN</b>. "
    "Image Inpainting의 변형으로 볼 수 있다.",
    Body))
story.append(Spacer(1, 6))

scfegan_input = Table([
    ["입력 채널", "내용", "역할"],
    ["1~3 (RGB)", "원본 이미지 (마스크 영역 0)", "변경하지 않을 부분"],
    ["4 (Sketch)", "이상적 모양의 가이드 라인", "변형 방향 지시"],
    ["5~7 (Color)", "원하는 색의 stroke", "색상 가이드"],
    ["8 (Mask)", "편집할 영역 (binary)", "어디를 채울지"],
    ["9 (Noise)", "랜덤 노이즈 (마스크 영역만)", "생성 다양성"],
], colWidths=[3*cm, 6*cm, 7*cm])
scfegan_input.setStyle(TBL_HEADER)
story.append(scfegan_input)
story.append(Spacer(1, 10))

story.append(Paragraph("6.3 우리는 왜 SC-FEGAN을 학습하지 않나", H2))
story.append(Paragraph(
    "GAN 학습은 일반적으로 <b>수주~수개월</b> 소요되고, 학습 안정성이 매우 까다롭다. "
    "1달 일정 + 3인 팀 규모로는 불가능. 따라서 시각화 도구로 그대로 활용하고, "
    "<b>학습 가능한 컴포넌트(U-Net)에 집중</b>하는 전략을 택했다.",
    Body))
story.append(PageBreak())

# ═══ 7. MediaPipe ═══
story.append(Paragraph("7. 핵심 개념 D — MediaPipe Face Mesh", H1))

story.append(Paragraph("7.1 무엇을 하나", H2))
story.append(Paragraph(
    "Google이 개발한 얼굴 분석 라이브러리. 얼굴 이미지에서 <b>478개의 3D 랜드마크</b>를 "
    "실시간으로 검출. 468개 face surface + 10개 iris.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("7.2 우리 사용 방식 — Tasks API", H2))
story.append(Paragraph(
    "MediaPipe에는 legacy <code>mp.solutions</code> API와 신형 <code>mp.tasks</code> API 두 가지가 있다. "
    "최신 mediapipe 빌드 (0.10.30+)에서는 solutions가 빠져있어, <b>Tasks API를 사용</b>한다. "
    "기능은 동일 (478점 추출).",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("7.3 핵심 랜드마크 인덱스 (코, 눈, 입, 턱)", H2))
landmarks = Table([
    ["부위", "인덱스", "용도"],
    ["코끝", "1", "코 영역 중심"],
    ["미간", "168", "얼굴 비율 분석"],
    ["왼눈 외각 / 내각", "33 / 133", "눈 영역 + flip 대응"],
    ["오른눈 외각 / 내각", "263 / 362", "동일"],
    ["윗입술 / 아랫입술", "13 / 14", "입술 변형"],
    ["턱끝", "152", "jaw 영역 분리 기준"],
    ["이마 상단", "10", "forehead 영역"],
], colWidths=[4*cm, 3*cm, 9*cm])
landmarks.setStyle(TBL_HEADER)
story.append(landmarks)
story.append(PageBreak())

# ═══ 8. Metrics ═══
story.append(Paragraph("8. 핵심 개념 E — 평가 지표", H1))

story.append(Paragraph("8.1 IoU (Intersection over Union)", H2))
story.append(Paragraph(
    "세그멘테이션의 표준 지표. 예측 영역과 정답 영역의 <b>겹치는 부분 / 합집합</b>. "
    "0~1 값, 1에 가까울수록 좋음.",
    Body))
iou_box = Table([[Paragraph(
    "<b>IoU = TP / (TP + FP + FN)</b><br/>"
    "TP: True Positive (정답이며 예측한 픽셀)<br/>"
    "FP: False Positive (정답 아닌데 예측한 픽셀)<br/>"
    "FN: False Negative (정답인데 놓친 픽셀)",
    Body)]], colWidths=[14*cm])
iou_box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), BG),
    ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("BOX", (0, 0), (-1, -1), 1, ICE),
]))
story.append(iou_box)
story.append(Spacer(1, 10))

story.append(Paragraph("8.2 mIoU (mean IoU)", H2))
story.append(Paragraph(
    "여러 클래스의 IoU 평균. 우리는 <b>배경(class 0) 제외 평균</b>을 사용 (배경이 너무 커서 무한 IoU↑).<br/>"
    "<b>목표</b>: mIoU > 0.75 (face parsing 표준 벤치마크)",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("8.3 Dice Score (F1 유사)", H2))
story.append(Paragraph(
    "<b>Dice = 2 × TP / (2 × TP + FP + FN)</b><br/>"
    "F1 score와 수학적으로 동등. IoU보다 작은 객체에 관대 (IoU=0.5는 Dice ≈ 0.67).",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("8.4 Confusion Matrix", H2))
story.append(Paragraph(
    "C×C 행렬 (C = 클래스 수). 행은 정답, 열은 예측. 대각선이 클수록 좋음. "
    "<b>클래스 간 혼동 패턴</b>을 보여줌 — 예: \"eye를 brow로 잘못 예측\".",
    Body))
story.append(PageBreak())

# ═══ 9. Loss ═══
story.append(Paragraph("9. 핵심 개념 F — Loss Function", H1))

story.append(Paragraph("9.1 Cross Entropy Loss (CE)", H2))
story.append(Paragraph(
    "분류 문제의 기본 손실. 픽셀마다 정답 클래스의 예측 확률 log → 평균. "
    "<b>장점</b>: gradient가 부드럽고 학습 안정적. <b>단점</b>: class imbalance에 민감.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("9.2 Dice Loss", H2))
story.append(Paragraph(
    "<b>1 - Dice score</b>. 작은 영역(예: 코)에도 비중을 줘서 <b>class imbalance에 강함</b>. "
    "<b>단점</b>: 초기 학습이 불안정 (예측이 모두 0이면 gradient 0).",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("9.3 Combo Loss — 우리가 선택한 것 ★", H2))
story.append(Paragraph(
    "두 손실의 가중합. <b>α × DiceLoss + β × CrossEntropyLoss</b> (α=β=0.5).<br/>"
    "<b>이점</b>: Dice가 imbalance 보정, CE가 초기 학습 안정화 (서로 보완).",
    Body))
story.append(Spacer(1, 8))

combo_box = Table([[Paragraph(
    "<b>예시</b>: skin 영역은 얼굴의 30%, nose 영역은 2%인 경우<br/>"
    "&nbsp;&nbsp;• CE 단독: 큰 영역(skin) 잘 맞추면 점수 높아 작은 영역(nose) 학습 부족<br/>"
    "&nbsp;&nbsp;• Dice 단독: 모든 영역 동등 비중이지만 초기 불안정<br/>"
    "&nbsp;&nbsp;• Combo: <b>두 단점 모두 해결</b>",
    Body)]], colWidths=[14*cm])
combo_box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), BG),
    ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("BOX", (0, 0), (-1, -1), 1, ACCENT),
]))
story.append(combo_box)
story.append(PageBreak())

# ═══ 10. Augmentation ═══
story.append(Paragraph("10. 핵심 개념 G — Data Augmentation + Ablation", H1))

story.append(Paragraph("10.1 왜 필요한가", H2))
story.append(Paragraph(
    "데이터셋이 한정적이면 모델이 학습 데이터에 <b>과적합(overfit)</b>됨. "
    "이미지 변형을 추가해 \"같은 의미의 다른 픽셀\"을 만들면 일반화 성능 ↑.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("10.2 우리 Augmentation 파이프라인 (albumentations)", H2))
aug_tbl = Table([
    ["타입", "변환", "확률"],
    ["Spatial (공간)", "Horizontal Flip (좌우 반전)", "0.5"],
    ["Spatial", "Rotation ±15도", "0.5"],
    ["Pixel (픽셀)", "Brightness/Contrast 조절", "0.3"],
    ["Pixel", "Gaussian Blur (3~5 kernel)", "0.2"],
], colWidths=[3*cm, 9*cm, 2*cm])
aug_tbl.setStyle(TBL_HEADER)
story.append(aug_tbl)
story.append(Spacer(1, 10))

story.append(Paragraph("10.3 Ablation Study (성능 분석 15% 항목)", H2))
story.append(Paragraph(
    "<b>Ablation</b> = 어떤 구성요소를 빼봤을 때 성능 차이 측정. 평가 기준 \"성능 최적화\" 항목 대응. "
    "Week 3에 다음 표를 만들 예정:",
    Body))
ablation_tbl = Table([
    ["실험", "Augmentation", "예상 mIoU"],
    ["Baseline", "없음", "0.70"],
    ["+ Spatial", "Flip + Rotation", "0.76 (+6%)"],
    ["+ Pixel", "+ Brightness/Contrast/Blur", "0.79 (+3%)"],
], colWidths=[4*cm, 6*cm, 4*cm])
ablation_tbl.setStyle(TBL_HEADER)
story.append(ablation_tbl)
story.append(Spacer(1, 8))
story.append(Paragraph(
    "→ \"Augmentation 적용 시 mIoU 9%p 향상\" 한 줄로 정량적 어필 가능.",
    Caption))
story.append(PageBreak())

# ═══ 11. Grad-CAM ═══
story.append(Paragraph("11. 핵심 개념 H — Grad-CAM (해석 가능성)", H1))

story.append(Paragraph("11.1 무엇인가", H2))
story.append(Paragraph(
    "<b>Gradient-weighted Class Activation Mapping</b>. CNN이 \"왜 이 부분을 그 클래스로 판단했는지\" "
    "픽셀 단위 heatmap으로 시각화. CVPR 2017 Selvaraju et al.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("11.2 작동 원리 (개념적)", H2))
story.append(Paragraph(
    "특정 클래스의 출력에 대한 <b>gradient를 마지막 conv layer까지 역전파</b>. "
    "각 채널이 클래스에 얼마나 기여하는지 가중치로 변환 후 heatmap으로 표시.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("11.3 우리 U-Net에서의 적용", H2))
story.append(Paragraph(
    "U-Net은 분류기와 달리 픽셀 단위 출력이라 약간 다르게 적용:<br/>"
    "• Hook 위치: <b>encoder의 가장 깊은 layer</b> (model.encoder.layer4[-1])<br/>"
    "• Target: <b>SemanticSegmentationTarget</b> 클래스 사용 (pytorch-grad-cam 제공)<br/>"
    "• 결과: 특정 클래스(예: nose)에 대한 영역별 활성화 heatmap",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("11.4 발표 시 임팩트", H2))
story.append(Paragraph(
    "최종 발표에서 5장의 Grad-CAM 시각화 (코/눈/입/턱/이마)를 보여주면: <br/>"
    "<b>\"AI가 사진의 이 부분을 보고 코로 판단했어요\"</b> 라는 명확한 설명 가능. "
    "교수님 평가 기준 \"설명 가능한 비전 AI\" 15% 항목 핵심 어필 포인트.",
    Body))
story.append(PageBreak())

# ═══ 12. CelebAMask-HQ ═══
story.append(Paragraph("12. 핵심 개념 I — CelebAMask-HQ 데이터셋", H1))

cmaskhq_meta = Table([
    ["항목", "내용"],
    ["출처", "Lee et al., CVPR 2020"],
    ["크기", "30,000장 (1024×1024 또는 256×256 미러)"],
    ["라벨", "19개 부위 (skin, nose, eye, mouth, hair, ...) 픽셀 단위 mask"],
    ["라이선스", "비상업 연구 용도 (학술 발표 OK)"],
    ["다운로드", "Hugging Face datasets (`limsanky/celebamask-hq-256`, 1.42GB)"],
    ["분할", "Train 24K / Val 3K / Test 3K"],
], colWidths=[3.5*cm, 11.5*cm])
cmaskhq_meta.setStyle(TBL_HEADER)
story.append(cmaskhq_meta)
story.append(Spacer(1, 10))

story.append(Paragraph("12.1 왜 이 데이터셋인가", H2))
story.append(Paragraph(
    "• <b>학술 표준</b>: CVPR 2020 게재 → 평가 기준의 \"질·양\" 어필<br/>"
    "• <b>픽셀 단위 정밀 라벨</b>: 세그멘테이션 학습에 적합<br/>"
    "• <b>충분한 양</b>: 30K = 학습/검증/테스트 분할 충분<br/>"
    "• <b>접근성</b>: Hugging Face 미러로 한 줄 다운로드",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("12.2 우리가 푼 문제 — 턱·이마 라벨 부재", H2))
story.append(Paragraph(
    "CelebAMask-HQ에는 <b>jaw와 forehead 라벨이 직접 없음</b> (skin에 묶임). "
    "해결: 학습은 5 클래스(bg/nose/eye/mouth/skin)만 진행하고, "
    "<b>추론 후 MediaPipe 랜드마크로 skin 영역을 jaw/forehead로 분리</b>. "
    "학습 데이터의 진정성을 유지하면서 우리 task에 맞춤.",
    Body))
story.append(PageBreak())

# ═══ 13. Transfer Learning ═══
story.append(Paragraph("13. 핵심 개념 J — Transfer Learning", H1))

story.append(Paragraph("13.1 개념", H2))
story.append(Paragraph(
    "이미 다른 task에서 <b>사전학습된 모델의 가중치를 가져와</b> 새 task에 적용. "
    "처음부터 학습할 때보다 <b>학습 데이터 적어도 잘 동작</b>, 학습 시간 ↓.",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("13.2 우리 U-Net의 적용", H2))
story.append(Paragraph(
    "• Encoder = <b>ResNet-34</b> + <b>ImageNet 사전학습 가중치</b><br/>"
    "  → ImageNet 100만 장으로 학습된 시각 특징(엣지/텍스처/형태)이 이미 들어있음<br/>"
    "• Decoder = 무작위 초기화 (face parsing은 ImageNet에 없는 task)<br/>"
    "• Fine-tuning: 전체 가중치를 우리 데이터로 추가 학습",
    Body))
story.append(Spacer(1, 8))

story.append(Paragraph("13.3 발표 시 강조 (왜 이게 의미 있는가)", H2))
story.append(Paragraph(
    "Transfer learning은 <b>현대 딥러닝의 표준 관행</b>이고 \"처음부터 학습\"보다 거의 항상 우월. "
    "교수님 질문 가능: \"왜 처음부터 학습하지 않았나?\" → \"30K 데이터로 ResNet을 처음부터 "
    "학습하면 underfit 가능. ImageNet 사전학습 가중치 활용이 일반적 best practice\".",
    Body))
story.append(PageBreak())

# ═══ 14. 예상 질문 + 답변 ═══
story.append(Paragraph("14. 예상 질문 + 모범 답변", H1))

qa_pairs = [
    ("Q1. 왜 SC-FEGAN을 직접 학습하지 않았나?",
     "GAN 학습은 수주~수개월 소요되고 학습 안정성이 까다롭다 (mode collapse, vanishing gradient). "
     "1달 일정에서는 불가능. <b>메인 학습 컴포넌트는 U-Net</b>이고, SC-FEGAN은 시각화 도구로 활용. "
     "이는 현대 딥러닝 프로젝트의 일반적 접근 — 작은 컴포넌트는 학습하고 큰 사전학습 모델은 그대로 활용."),

    ("Q2. 왜 U-Net인가? 더 최신 모델은 없나?",
     "① U-Net은 의료/세그멘테이션의 <b>표준 아키텍처</b> (Ronneberger 2015 CVPR). "
     "② 우리 task는 픽셀 단위 부위 분할이라 segmentation network가 자연스러움. "
     "③ \"계층적 특징 추출 + skip connection\"이 수업에서 배운 구조적 원리에 가장 직접적으로 대응. "
     "④ 1달 안에 학습/튜닝 가능한 규모."),

    ("Q3. 왜 ResNet-34 인코더인가? ResNet-50이 더 좋지 않나?",
     "ResNet-50은 더 깊지만 <b>parameter 수가 2배</b>이고 학습 시간 ↑. "
     "ResNet-34는 face parsing에서 검증된 trade-off (속도↔정확도 균형). "
     "Ablation으로 ResNet-50 시도는 Week 3 옵션 작업."),

    ("Q4. 30K 데이터셋이 너무 많지 않나?",
     "Week 2 PoC에는 5K subset부터 시작 (1 epoch ~1분). "
     "Week 3 본 학습에서 24K 전체 사용 (10 epoch ~50분). 점진적 확장으로 위험 관리."),

    ("Q5. mIoU가 낮으면 어떻게 할 건가?",
     "① Augmentation 강화 (Ablation 결과 보고 추가), "
     "② Loss 가중치 조정 (Dice 비중 ↑), "
     "③ Encoder를 더 깊게 (ResNet-50), "
     "④ Class weight로 작은 클래스(nose) 보강. 한계가 명확하면 발표에서 \"향후 과제\"로 명시."),

    ("Q6. 성형 윤리적 문제는?",
     "<b>학술 데모임을 명시</b>. 의료 자문이 아니라 시각화 도구. "
     "발표 슬라이드에 \"한계 및 윤리적 고려\" 섹션 포함 예정 (편향, 의료 검증 부재, 동의 등). "
     "실제 적용 시 의료법·개인정보보호법 등 추가 규제 필요."),

    ("Q7. CelebAMask-HQ는 서양인 위주. 한국인 얼굴에서 일반화 되나?",
     "정확한 답: <b>편향 가능성 있음</b>. 향후 한국인 얼굴 데이터(AI-Hub 등)로 추가 fine-tuning 필요. "
     "Week 4 한계점 슬라이드에 명시."),

    ("Q8. Grad-CAM이 Segmentation에서 의미 있나? 분류용 아닌가?",
     "원래는 분류용이지만 <b>SemanticSegmentationTarget</b> 변형으로 segmentation에도 적용 가능. "
     "Encoder의 가장 깊은 layer를 hook → 특정 클래스(예: nose)의 예측 영역에 대한 활성화 heatmap. "
     "\"AI가 이 부분을 보고 nose로 판단\"이라는 해석을 제공."),

    ("Q9. 룰베이스 추천은 왜 ML로 안 했나?",
     "① 시술 추천 라벨링된 데이터셋 없음 (의료 데이터는 비공개 + 라벨링 비용), "
     "② 룰베이스가 <b>설명 가능</b> (\"황금비 벗어남 ↓ → 코끝 성형 추천\"), "
     "③ 본 프로젝트의 핵심은 segmentation이고 추천은 보조."),

    ("Q10. v1 vs v2 무엇이 결정적으로 달라졌나?",
     "<b>U-Net 자체 학습 추가</b> — 이게 핵심. 평가 기준 40% \"모델 설계\" 항목 대응. "
     "더불어 학술 데이터셋(30%), CV 표준 지표(15%), Grad-CAM(15%) 모든 항목이 같이 개선."),
]

for q, a in qa_pairs:
    story.append(Paragraph(q, H3))
    story.append(Paragraph(a, Body))
    story.append(Spacer(1, 8))

story.append(PageBreak())

# ═══ 15. 발표 시 강조 포인트 ═══
story.append(Paragraph("15. 발표 시 강조 포인트", H1))

story.append(Paragraph("15.1 슬라이드 4 (U-Net) — 가장 중요 ★", H2))
story.append(Paragraph(
    "발표 시간 8장 중 <b>1분 이상 투자</b>. 다음 3개 키워드를 명시적으로 입에 올릴 것:<br/>"
    "&nbsp;&nbsp;① <b>계층적 특징 추출</b> (encoder)<br/>"
    "&nbsp;&nbsp;② <b>Skip Connection</b> (encoder↔decoder)<br/>"
    "&nbsp;&nbsp;③ <b>픽셀 단위 분류</b> (output)<br/>"
    "→ 교수님 평가 기준 \"CNN 구조적 원리\" 문장을 그대로 인용한 표현.",
    Body))
story.append(Spacer(1, 10))

story.append(Paragraph("15.2 슬라이드 5 (데이터셋) — 데이터 타당성 어필", H2))
story.append(Paragraph(
    "<b>\"CelebAMask-HQ는 CVPR 2020 학술 표준 데이터셋\"</b> 한 마디만 강조. "
    "30K 양 + 픽셀 단위 라벨 + 학술 출처 = 30% 항목 만점.",
    Body))
story.append(Spacer(1, 10))

story.append(Paragraph("15.3 슬라이드 6 (평가) — CV 지표 명시", H2))
story.append(Paragraph(
    "<b>mIoU, Dice, Confusion Matrix, Ablation</b>를 빠르게 나열. "
    "교수님 원문 \"Confusion Matrix, IoU, mAP\"에서 우리가 IoU 계열을 사용. "
    "+ Augmentation 비교표(예시) 보여주면 \"성능 최적화 시도\" 어필.",
    Body))
story.append(Spacer(1, 10))

story.append(Paragraph("15.4 자신 있게 말할 한 줄", H2))
story.append(Paragraph(
    "<b>\"U-Net의 계층적 특징 추출과 skip connection을 활용해 픽셀 단위 부위 분할을 자체 학습하고, "
    "그 결과를 사전학습된 SC-FEGAN의 입력으로 사용해 객관적이고 정밀한 시술 후 시각화를 제공합니다.\"</b>",
    Body))
story.append(Spacer(1, 10))

story.append(Paragraph("15.5 절대 하지 말 것", H2))
dont = [
    "\"사전학습 모델을 그냥 가져다 썼어요\" — 학습 컴포넌트 강조 누락",
    "Grad-CAM, IoU 같은 용어 모르는 듯 얼버무리기",
    "데이터셋 출처 못 답하기",
    "왜 U-Net 인지 못 답하기 (수업 원리 연결 못 함)",
    "현재 mIoU 값 없다고 자신감 잃기 (Week 2 PoC는 발표용 아님)",
]
for d in dont:
    story.append(Paragraph(f"✗ {d}", Bullet))
story.append(Spacer(1, 14))

# ═══ 부록 ═══
story.append(Paragraph("부록 — 참고 자료", H1))
refs = [
    "U-Net 원논문: Ronneberger et al., \"U-Net: Convolutional Networks for Biomedical Image Segmentation\" (MICCAI 2015)",
    "CelebAMask-HQ: Lee et al., \"MaskGAN: Towards Diverse and Interactive Facial Image Manipulation\" (CVPR 2020)",
    "SC-FEGAN: Jo & Park, \"SC-FEGAN: Face Editing GAN With User's Sketch and Color\" (ICCV 2019)",
    "Grad-CAM: Selvaraju et al., \"Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization\" (CVPR 2017)",
    "MediaPipe Face Mesh: Google, ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker",
    "segmentation_models_pytorch: github.com/qubvel-org/segmentation_models.pytorch",
    "pytorch-grad-cam: github.com/jacobgil/pytorch-grad-cam",
    "Combo Loss: Hashemi et al., \"Combo Loss: Handling Input and Output Imbalance in Multi-Organ Segmentation\" (CMIG 2019)",
]
for r in refs:
    story.append(Paragraph(f"• {r}", Bullet))
story.append(Spacer(1, 18))

footer = Paragraph(
    "<i>이 문서는 발표 직전 자료입니다. 항상 plan_kim_0518_01.md 및 research_unet.md를 참고하세요.<br/>"
    "작성: kim · 2026-05-18</i>",
    Caption)
story.append(footer)

# ─── 빌드 ───
doc.build(story)
print("✅ Saved: study_guide.pdf")
