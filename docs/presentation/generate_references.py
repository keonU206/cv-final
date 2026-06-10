"""모델 강화 방법 + 참고문헌 PDF — 교수님 피드백 / 발표 준비용.

내용:
- U-Net 측 강화 5단계 (Early Stopping, LM Heatmap, SCSE Attention, TTA, Combo Loss)
- SC-FEGAN 측 강화 계획 (Auto Sketch/Color, Refinement Network, Poisson Blending)
- 각 강화 방법별 참고 논문 (저자/연도/학회/링크)
- BibTeX 엔트리
- TOP 10 외워야 할 인용
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether,
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
CODE_BG = colors.HexColor("#F4F6FA")

TitleStyle = ParagraphStyle("Title", fontName="MalgunBold", fontSize=20,
                            leading=26, textColor=NAVY, alignment=TA_CENTER,
                            spaceAfter=4)
SubStyle = ParagraphStyle("Sub", fontName="Malgun", fontSize=10, leading=14,
                          textColor=MUTED, alignment=TA_CENTER, italic=True,
                          spaceAfter=10)
H1 = ParagraphStyle("H1", fontName="MalgunBold", fontSize=15, leading=20,
                    textColor=NAVY, spaceBefore=10, spaceAfter=6,
                    borderPadding=4)
H2 = ParagraphStyle("H2", fontName="MalgunBold", fontSize=11, leading=14,
                    textColor=ACCENT, spaceBefore=8, spaceAfter=4)
H3 = ParagraphStyle("H3", fontName="MalgunBold", fontSize=9.5, leading=12,
                    textColor=NAVY, spaceBefore=4, spaceAfter=2)
Body = ParagraphStyle("Body", fontName="Malgun", fontSize=8.5, leading=12,
                      textColor=CHARCOAL, alignment=TA_LEFT)
Cite = ParagraphStyle("Cite", fontName="Malgun", fontSize=8, leading=11,
                      textColor=CHARCOAL, alignment=TA_LEFT,
                      leftIndent=10)
Code = ParagraphStyle("Code", fontName="Malgun", fontSize=7.5, leading=10,
                      textColor=CHARCOAL, alignment=TA_LEFT,
                      backColor=CODE_BG, borderPadding=4,
                      leftIndent=4, rightIndent=4)
Caption = ParagraphStyle("Cap", fontName="Malgun", fontSize=7.5, leading=10,
                         textColor=MUTED, italic=True)


def make_table(rows, col_widths):
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
        ("FONTNAME", (0, 1), (-1, -1), "Malgun"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.4, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TEXTCOLOR", (0, 1), (0, -1), NAVY),
    ]))
    return tbl


doc = SimpleDocTemplate(
    "C:/Users/User/Documents/cv-final/docs/presentation/references.pdf",
    pagesize=A4, leftMargin=1.3*cm, rightMargin=1.3*cm,
    topMargin=1.3*cm, bottomMargin=1.3*cm,
    title="CV Final 모델 강화 + 참고문헌",
)
story = []

# ── 표지 ──
story.append(Paragraph("성형 견적 시각화 — 모델 강화 + 참고문헌", TitleStyle))
story.append(Paragraph("U-Net & SC-FEGAN 측면 강화 방법 정리 · 2026-06-01", SubStyle))

# ─────────────────────────────────────────────
# 1. 요약 한눈표
# ─────────────────────────────────────────────
story.append(Paragraph("1. 한눈에 보는 강화 요약", H1))

rows = [
    ["모델", "강화 방법", "상태", "효과 / 결과"],
    ["U-Net", "Combo Loss (Dice+CE)", "✅ 완료",
     "기본 학습 안정화. baseline mIoU 0.654"],
    ["U-Net", "Early Stopping (patience=5)", "✅ 완료",
     "오버피팅 방지. +2.6%p (0.654 → 0.680)"],
    ["U-Net", "LM-guided Heatmap (4채널)", "✅ 완료",
     "MediaPipe 478점 → Gaussian heatmap. ~0.683 (보합)"],
    ["U-Net", "SCSE Attention", "✅ 완료",
     "Decoder block에 SCSE 모듈. ~0.683 (보합)"],
    ["U-Net", "TTA (Hflip + Rot±10°)", "✅ 완료",
     "추론 시 평균 앙상블. ~0.683 (보합)"],
    ["SC-FEGAN", "자동 Sketch/Color 생성", "🛠 진행중",
     "랜드마크 → Bezier 곡선. 시술별 가이드라인"],
    ["SC-FEGAN", "Refinement Network", "📌 계획",
     "L1 + Perceptual Loss로 후처리 정제 (4일)"],
    ["SC-FEGAN", "Poisson Blending", "📌 계획",
     "경계 부드럽게 합성 (Pérez 2003)"],
]
story.append(make_table(rows, [2.5*cm, 4.3*cm, 1.8*cm, 7.7*cm]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "💡 핵심 발견: U-Net에서 가장 큰 향상은 <b>아키텍처</b>가 아닌 "
    "<b>학습 방법론(Early Stopping)</b>이었음. "
    "→ 발표 디스커션 포인트: \"Architecture &lt; Training Methodology\"",
    Caption,
))

# ─────────────────────────────────────────────
# 2. U-Net 측 강화 방법 (논문 포함)
# ─────────────────────────────────────────────
story.append(Paragraph("2. U-Net 측 강화 방법 + 참고문헌", H1))

# 2-1. Baseline
story.append(Paragraph("2.1 Baseline U-Net (Encoder + Decoder)", H2))
story.append(Paragraph(
    "ResNet-34 ImageNet pretrained encoder + U-Net decoder. "
    "segmentation_models_pytorch 라이브러리.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Ronneberger, O., Fischer, P., &amp; Brox, T. (2015). "
    "<b>U-Net: Convolutional Networks for Biomedical Image Segmentation.</b> "
    "MICCAI 2015. arXiv:1505.04597",
    Cite,
))
story.append(Paragraph(
    "• He, K., Zhang, X., Ren, S., &amp; Sun, J. (2016). "
    "<b>Deep Residual Learning for Image Recognition.</b> "
    "CVPR 2016. (ResNet-34 encoder 출처)",
    Cite,
))
story.append(Paragraph(
    "• Deng, J. et al. (2009). <b>ImageNet: A Large-Scale Hierarchical Image "
    "Database.</b> CVPR 2009. (Transfer learning weights)",
    Cite,
))

# 2-2. Combo Loss
story.append(Paragraph("2.2 Combo Loss (Dice + Cross-Entropy)", H2))
story.append(Paragraph(
    "Class imbalance 완화 + 픽셀 정확도 둘 다 잡기 위해 0.5/0.5 가중합.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Taghanaki, S. A. et al. (2019). <b>Combo loss: Handling input and "
    "output imbalance in multi-organ segmentation.</b> "
    "Computerized Medical Imaging and Graphics, 75, 24-33.",
    Cite,
))
story.append(Paragraph(
    "• Milletari, F., Navab, N., &amp; Ahmadi, S. A. (2016). "
    "<b>V-Net: Fully Convolutional Neural Networks for Volumetric Medical "
    "Image Segmentation.</b> 3DV 2016. (Dice Loss 원조)",
    Cite,
))

# 2-3. Early Stopping
story.append(Paragraph("2.3 Early Stopping ⭐ (가장 효과 큰 강화)", H2))
story.append(Paragraph(
    "val_mIoU가 N epoch 동안 개선 없으면 학습 중단 + best checkpoint 저장. "
    "Phase 1에서 final이 아닌 best ckpt 저장으로 +2.6%p 향상.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Prechelt, L. (1998). <b>Early Stopping — But When?</b> "
    "In Neural Networks: Tricks of the Trade (pp. 55-69). Springer.",
    Cite,
))
story.append(Paragraph(
    "• Goodfellow, I., Bengio, Y., &amp; Courville, A. (2016). "
    "<b>Deep Learning.</b> MIT Press. (Chapter 7.8: Early Stopping)",
    Cite,
))

# 2-4. LM Heatmap
story.append(Paragraph("2.4 Landmark-guided Heatmap (4채널 입력)", H2))
story.append(Paragraph(
    "MediaPipe Face Mesh 478 랜드마크 → Gaussian heatmap (σ=3) → "
    "RGB와 concat하여 4채널 입력. 모델에 \"여기가 코다/눈이다\" 사전 정보 제공.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Newell, A., Yang, K., &amp; Deng, J. (2016). <b>Stacked Hourglass "
    "Networks for Human Pose Estimation.</b> ECCV 2016. "
    "(Gaussian heatmap representation 원조)",
    Cite,
))
story.append(Paragraph(
    "• Kartynnik, Y., Ablavatski, A., Grishchenko, I., &amp; Grundmann, M. "
    "(2019). <b>Real-time Facial Surface Geometry from Monocular Video on "
    "Mobile GPUs.</b> CVPR Workshop. (MediaPipe Face Mesh)",
    Cite,
))
story.append(Paragraph(
    "• Bulat, A., &amp; Tzimiropoulos, G. (2017). <b>How far are we from "
    "solving the 2D &amp; 3D Face Alignment problem?</b> ICCV 2017. "
    "(Landmark heatmap → segmentation 활용)",
    Cite,
))

# 2-5. SCSE Attention
story.append(Paragraph("2.5 SCSE Attention (Spatial + Channel SE)", H2))
story.append(Paragraph(
    "U-Net Decoder의 각 블록에 Squeeze-and-Excitation 모듈 추가. "
    "smp 라이브러리의 decoder_attention_type=\"scse\" 옵션으로 한 줄 적용.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Roy, A. G., Navab, N., &amp; Wachinger, C. (2018). "
    "<b>Concurrent Spatial and Channel Squeeze &amp; Excitation in Fully "
    "Convolutional Networks.</b> MICCAI 2018. arXiv:1803.02579",
    Cite,
))
story.append(Paragraph(
    "• Hu, J., Shen, L., &amp; Sun, G. (2018). <b>Squeeze-and-Excitation "
    "Networks.</b> CVPR 2018. (SE 블록 원조)",
    Cite,
))
story.append(Paragraph(
    "• Oktay, O. et al. (2018). <b>Attention U-Net: Learning Where to Look "
    "for the Pancreas.</b> MIDL 2018. arXiv:1804.03999 "
    "(Attention Gate 원조 — SCSE 대체 선택지)",
    Cite,
))

# 2-6. TTA
story.append(Paragraph("2.6 TTA (Test Time Augmentation)", H2))
story.append(Paragraph(
    "추론 시 원본 + 좌우반전 + 회전(±10°) → 4개 예측의 평균. "
    "학습 비용 없이 추론 정확도 약간 향상.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Krizhevsky, A., Sutskever, I., &amp; Hinton, G. E. (2012). "
    "<b>ImageNet Classification with Deep Convolutional Neural Networks.</b> "
    "NIPS 2012. (TTA 원조 — 10-crop)",
    Cite,
))
story.append(Paragraph(
    "• Shanmugam, D., Blalock, D., Balakrishnan, G., &amp; Guttag, J. (2021). "
    "<b>Better Aggregation in Test-Time Augmentation.</b> ICCV 2021. "
    "arXiv:2011.11156",
    Cite,
))
story.append(Paragraph(
    "• Wang, G. et al. (2019). <b>Aleatoric uncertainty estimation with "
    "test-time augmentation for medical image segmentation with "
    "convolutional neural networks.</b> Neurocomputing, 338, 34-45.",
    Cite,
))

story.append(PageBreak())

# ─────────────────────────────────────────────
# 3. SC-FEGAN 측 강화 방법
# ─────────────────────────────────────────────
story.append(Paragraph("3. SC-FEGAN 측 강화 방법 + 참고문헌", H1))

# 3-0. SC-FEGAN 본체
story.append(Paragraph("3.1 SC-FEGAN 원 논문", H2))
story.append(Paragraph(
    "Sketch + Color + Mask 9채널 조건 GAN inpainting. "
    "CelebA-HQ에서 학습된 pretrained checkpoint 사용.",
    Body,
))
story.append(Paragraph(
    "• Jo, Y., &amp; Park, J. (2019). <b>SC-FEGAN: Face Editing Generative "
    "Adversarial Network with User's Sketch and Color.</b> ICCV 2019. "
    "arXiv:1902.06838 · License: CC BY-NC 4.0",
    Cite,
))

# 3-2. Auto Sketch/Color
story.append(Paragraph("3.2 자동 Sketch/Color 생성 (Phase 7-A)", H2))
story.append(Paragraph(
    "랜드마크 → 시술별 \"이상적 위치\"로 변형 → Bezier 곡선으로 가이드 라인. "
    "nose_tip / double_eyelid / v_line 시술별 자동 생성. "
    "intensity 슬라이더 (0.0~1.0)로 변형 강도 조절.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Cao, C., Weng, Y., Lin, S., &amp; Zhou, K. (2013). <b>3D Shape "
    "Regression for Real-time Facial Animation.</b> ACM TOG (SIGGRAPH 2013). "
    "(랜드마크 → 변형 가이드)",
    Cite,
))
story.append(Paragraph(
    "• Bezier, P. (1968). <b>How Renault Uses Numerical Control for Car "
    "Body Design and Tooling.</b> SAE Paper 680010. (베지어 곡선 원조)",
    Cite,
))
story.append(Paragraph(
    "• Sangkloy, P. et al. (2017). <b>Scribbler: Controlling Deep Image "
    "Synthesis with Sketch and Color.</b> CVPR 2017. "
    "(Sketch+Color → 이미지 생성 패러다임)",
    Cite,
))

# 3-3. Refinement Network
story.append(Paragraph("3.3 Refinement Network (Phase 7-B, 계획)", H2))
story.append(Paragraph(
    "SC-FEGAN 출력 → 작은 U-Net으로 후처리 정제. "
    "L1 + Perceptual (VGG) Loss로 학습. 경계 artifact 제거 + 자연스러움 향상.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Johnson, J., Alahi, A., &amp; Fei-Fei, L. (2016). <b>Perceptual "
    "Losses for Real-Time Style Transfer and Super-Resolution.</b> "
    "ECCV 2016. arXiv:1603.08155 (VGG Perceptual Loss 원조)",
    Cite,
))
story.append(Paragraph(
    "• Yu, J. et al. (2019). <b>Free-Form Image Inpainting with Gated "
    "Convolution.</b> ICCV 2019. (DeepFillv2 — 2-stage refinement 구조)",
    Cite,
))
story.append(Paragraph(
    "• Ledig, C. et al. (2017). <b>Photo-Realistic Single Image "
    "Super-Resolution Using a Generative Adversarial Network.</b> "
    "CVPR 2017. (SRGAN — Perceptual + Adversarial 조합)",
    Cite,
))

# 3-4. Poisson Blending
story.append(Paragraph("3.4 Poisson Blending (경계 자연스러움)", H2))
story.append(Paragraph(
    "GAN 출력 영역을 원본 얼굴에 합성할 때 색상/조명 경계 자연스럽게 처리.",
    Body,
))
story.append(Paragraph("참고:", H3))
story.append(Paragraph(
    "• Pérez, P., Gangnet, M., &amp; Blake, A. (2003). "
    "<b>Poisson Image Editing.</b> ACM Transactions on Graphics "
    "(SIGGRAPH 2003), 22(3), 313-318.",
    Cite,
))
story.append(Paragraph(
    "• Burt, P. J., &amp; Adelson, E. H. (1983). <b>A multiresolution "
    "spline with application to image mosaics.</b> ACM TOG, 2(4), 217-236. "
    "(Laplacian Pyramid Blending — 대체 선택지)",
    Cite,
))

# ─────────────────────────────────────────────
# 4. 데이터셋 / 도구 인용
# ─────────────────────────────────────────────
story.append(Paragraph("4. 데이터셋 &amp; 도구", H1))

rows = [
    ["항목", "출처 (저자 / 연도 / 학회)", "비고"],
    ["CelebAMask-HQ",
     "Lee, C.-H. et al. (2020). MaskGAN: Towards Diverse and "
     "Interactive Facial Image Manipulation. CVPR.",
     "30K images, 19-class mask"],
    ["MediaPipe Face Mesh",
     "Kartynnik, Y. et al. (2019). CVPR Workshop.",
     "478 landmarks, real-time"],
    ["segmentation_models_pytorch",
     "Iakubovskii, P. (2019). GitHub. github.com/qubvel/"
     "segmentation_models.pytorch",
     "U-Net + SCSE 구현"],
    ["PyTorch",
     "Paszke, A. et al. (2019). NeurIPS.",
     "프레임워크"],
    ["Albumentations",
     "Buslaev, A. et al. (2020). Information 11(2), 125.",
     "Augmentation"],
    ["Grad-CAM (분석)",
     "Selvaraju, R. R. et al. (2017). ICCV.",
     "Attention 영역 시각화"],
]
story.append(make_table(rows, [3.5*cm, 8.3*cm, 4.5*cm]))

# ─────────────────────────────────────────────
# 5. BibTeX 엔트리 (복붙용)
# ─────────────────────────────────────────────
story.append(Paragraph("5. BibTeX (논문 작성 시 복붙용)", H1))

bibtex_entries = [
    ("U-Net", """@inproceedings{ronneberger2015unet,
  title={U-Net: Convolutional Networks for Biomedical Image Segmentation},
  author={Ronneberger, Olaf and Fischer, Philipp and Brox, Thomas},
  booktitle={MICCAI},
  year={2015},
}"""),
    ("SC-FEGAN", """@inproceedings{jo2019scfegan,
  title={SC-FEGAN: Face Editing Generative Adversarial Network
         with User's Sketch and Color},
  author={Jo, Youngjoo and Park, Jongyoul},
  booktitle={ICCV},
  year={2019},
}"""),
    ("SCSE Attention", """@inproceedings{roy2018scse,
  title={Concurrent Spatial and Channel Squeeze \\& Excitation in Fully
         Convolutional Networks},
  author={Roy, Abhijit Guha and Navab, Nassir and Wachinger, Christian},
  booktitle={MICCAI},
  year={2018},
}"""),
    ("CelebAMask-HQ", """@inproceedings{lee2020maskgan,
  title={MaskGAN: Towards Diverse and Interactive Facial Image Manipulation},
  author={Lee, Cheng-Han and Liu, Ziwei and Wu, Lingyun and Luo, Ping},
  booktitle={CVPR},
  year={2020},
}"""),
    ("MediaPipe Face Mesh", """@inproceedings{kartynnik2019mediapipe,
  title={Real-time Facial Surface Geometry from Monocular Video on Mobile GPUs},
  author={Kartynnik, Yury and Ablavatski, Artsiom and
          Grishchenko, Ivan and Grundmann, Matthias},
  booktitle={CVPR Workshop},
  year={2019},
}"""),
    ("Perceptual Loss", """@inproceedings{johnson2016perceptual,
  title={Perceptual Losses for Real-Time Style Transfer and Super-Resolution},
  author={Johnson, Justin and Alahi, Alexandre and Fei-Fei, Li},
  booktitle={ECCV},
  year={2016},
}"""),
    ("Poisson Blending", """@article{perez2003poisson,
  title={Poisson Image Editing},
  author={P{\\'e}rez, Patrick and Gangnet, Michel and Blake, Andrew},
  journal={ACM Transactions on Graphics (SIGGRAPH)},
  volume={22}, number={3}, pages={313--318}, year={2003},
}"""),
]

for tag, bib in bibtex_entries:
    story.append(Paragraph(f"<b>{tag}</b>", H3))
    # reportlab의 Paragraph는 줄바꿈을 <br/>로
    bib_html = bib.replace("\n", "<br/>").replace(" ", "&nbsp;")
    story.append(Paragraph(bib_html, Code))
    story.append(Spacer(1, 3))

story.append(PageBreak())

# ─────────────────────────────────────────────
# 6. TOP 10 외워야 할 인용 (발표용)
# ─────────────────────────────────────────────
story.append(Paragraph("6. TOP 10 — 발표 / Q&amp;A 대비 외울 인용", H1))
story.append(Paragraph(
    "발표 중 \"왜 이 방법?\"이라는 질문에 즉답할 수 있도록 저자/연도/학회 "
    "한 줄 단위로 기억하세요.",
    Body,
))
story.append(Spacer(1, 4))

rows = [
    ["#", "분야", "외울 한 줄", "왜 중요한가"],
    ["1", "Segmentation",
     "Ronneberger 2015 MICCAI · U-Net",
     "프로젝트 핵심 아키텍처"],
    ["2", "Backbone",
     "He 2016 CVPR · ResNet",
     "Encoder 출처"],
    ["3", "Attention",
     "Roy 2018 MICCAI · SCSE",
     "Attention 강화 출처"],
    ["4", "Attention 비교",
     "Hu 2018 CVPR · SE-Net",
     "SCSE의 모태"],
    ["5", "Loss",
     "Taghanaki 2019 · Combo Loss",
     "Dice+CE 가중합 정당화"],
    ["6", "Early Stopping",
     "Prechelt 1998 · Tricks of Trade",
     "오버피팅 방지 근거"],
    ["7", "Landmark",
     "Kartynnik 2019 · MediaPipe",
     "478점 추출 도구"],
    ["8", "Heatmap",
     "Newell 2016 ECCV · Hourglass",
     "Gaussian heatmap 원조"],
    ["9", "GAN",
     "Jo 2019 ICCV · SC-FEGAN",
     "GAN inpainting 본체"],
    ["10", "Refinement",
     "Johnson 2016 ECCV · Perceptual Loss",
     "Refinement Net loss 근거"],
]
story.append(make_table(rows, [0.8*cm, 2.3*cm, 6.5*cm, 6.4*cm]))

story.append(Spacer(1, 8))

# ─────────────────────────────────────────────
# 7. 발표 디스커션 포인트
# ─────────────────────────────────────────────
story.append(Paragraph("7. 발표 디스커션 포인트 (학술적 framing)", H1))

story.append(Paragraph("7.1 \"Architecture &lt; Training Methodology\"", H2))
story.append(Paragraph(
    "LM Heatmap (Newell 2016), SCSE Attention (Roy 2018), TTA "
    "(Shanmugam 2021) 모두 적용했으나 mIoU 0.683에서 plateau. "
    "가장 큰 향상은 Early Stopping (+2.6%p). "
    "→ <b>현대 CV 트렌드와 일치하는 발견</b>: \"Bag of Tricks\" "
    "(He 2019 CVPR), \"Revisiting ResNets\" (Bello 2021 NeurIPS) 등에서도 "
    "동일한 결론.",
    Body,
))

story.append(Paragraph("7.2 \"Why two models, not one?\"", H2))
story.append(Paragraph(
    "U-Net (분석) + SC-FEGAN (생성) 분리 설계 = <b>관심 분리 원칙</b>. "
    "한 모델로 다 하면 (1) 학습 데이터 부족 (2) failure mode 진단 불가. "
    "Cascade GAN (Wang 2018 CVPR), Two-Stage Inpainting (Yu 2018 CVPR) "
    "등에서 검증된 패턴.",
    Body,
))

story.append(Paragraph("7.3 \"Why CelebAMask-HQ?\"", H2))
story.append(Paragraph(
    "30K 고해상도(1024×1024) face + 19-class mask = 얼굴 부위별 학습 가능. "
    "SC-FEGAN의 학습 데이터와 동일 → domain shift 최소화 (Lee 2020 CVPR).",
    Body,
))

# ─────────────────────────────────────────────
# 8. 빠른 링크 모음
# ─────────────────────────────────────────────
story.append(Paragraph("8. 빠른 링크", H1))

rows = [
    ["자원", "URL"],
    ["U-Net 원논문", "arxiv.org/abs/1505.04597"],
    ["SC-FEGAN 코드", "github.com/run-youngjoo/SC-FEGAN"],
    ["SCSE Attention", "arxiv.org/abs/1803.02579"],
    ["smp 라이브러리", "github.com/qubvel/segmentation_models.pytorch"],
    ["MediaPipe", "developers.google.com/mediapipe/solutions/vision/face_landmarker"],
    ["CelebAMask-HQ", "github.com/switchablenorms/CelebAMask-HQ"],
    ["Perceptual Loss",
     "cs.stanford.edu/people/jcjohns/papers/eccv16/JohnsonECCV16.pdf"],
    ["Albumentations", "albumentations.ai"],
]
story.append(make_table(rows, [4.5*cm, 11.8*cm]))

story.append(Spacer(1, 10))
story.append(Paragraph(
    "© CV Final Team · kim · 2026-06-01 · references.pdf",
    Caption,
))

doc.build(story)
print("✅ references.pdf 생성 완료")
print("→ C:/Users/User/Documents/cv-final/docs/presentation/references.pdf")
