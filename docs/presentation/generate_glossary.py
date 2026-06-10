"""발표 직전 들고 다닐 용어 사전 PDF — 컴팩트한 1-2장 카드 형태."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
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

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", fontName="MalgunBold", fontSize=16, leading=20,
                    textColor=NAVY, spaceBefore=8, spaceAfter=6)
H2 = ParagraphStyle("H2", fontName="MalgunBold", fontSize=11, leading=14,
                    textColor=ACCENT, spaceBefore=6, spaceAfter=3)
Body = ParagraphStyle("Body", fontName="Malgun", fontSize=8.5, leading=11,
                      textColor=CHARCOAL, alignment=TA_LEFT)
TitleStyle = ParagraphStyle("Title", fontName="MalgunBold", fontSize=20,
                            leading=26, textColor=NAVY, alignment=TA_CENTER,
                            spaceAfter=4)
SubStyle = ParagraphStyle("Sub", fontName="Malgun", fontSize=10, leading=14,
                          textColor=MUTED, alignment=TA_CENTER, italic=True,
                          spaceAfter=8)
Caption = ParagraphStyle("Cap", fontName="Malgun", fontSize=7.5, leading=10,
                         textColor=MUTED, italic=True)


def make_table(rows, col_widths):
    """3-column table style for glossary."""
    tbl = Table(rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
        ("FONTNAME", (0, 1), (-1, -1), "Malgun"),
        ("FONTNAME", (0, 1), (0, -1), "MalgunBold"),  # 첫 열만 굵게
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.4, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TEXTCOLOR", (0, 1), (0, -1), NAVY),
    ]))
    return tbl


doc = SimpleDocTemplate(
    "C:/Users/User/Documents/cv-final/docs/presentation/glossary.pdf",
    pagesize=A4, leftMargin=1.3*cm, rightMargin=1.3*cm,
    topMargin=1.3*cm, bottomMargin=1.3*cm,
    title="CV Final 용어 사전",
)
story = []

# 표지
story.append(Paragraph("성형 견적 시각화 — 용어 사전", TitleStyle))
story.append(Paragraph("발표 직전 빠른 참조 카드 · 2026-05-18", SubStyle))

# ─── 1. 모델 아키텍처 ───
story.append(Paragraph("1. 모델 아키텍처", H1))
data = [
    ["용어", "한 줄 정의", "우리 프로젝트"],
    ["CNN", "이미지 특징을 단계별 추출하는 신경망", "U-Net 백본"],
    ["U-Net ★", "Encoder+Decoder+Skip 세그멘테이션 망", "우리 학습 메인 모델"],
    ["ResNet-34", "34층 CNN, ImageNet 사전학습", "U-Net의 Encoder"],
    ["Encoder", "단계적 다운샘플링으로 특징 추출", "U-Net 앞부분"],
    ["Decoder", "다시 원본 크기로 복원", "U-Net 뒷부분"],
    ["Bottleneck", "Encoder 끝 가장 깊은 layer", "Grad-CAM hook 위치"],
    ["Skip Connection", "Encoder 얕은 층→Decoder 직접 전달", "공간 정보 보존"],
    ["계층적 특징", "Layer 지날수록 픽셀→의미 추상화", "CNN 핵심 (40% 어필)"],
    ["Receptive Field", "한 픽셀이 보는 원본 영역", "깊을수록 큼"],
]
story.append(make_table(data, [2.8*cm, 8*cm, 7.5*cm]))

# ─── 2. GAN (SC-FEGAN) ───
story.append(Paragraph("2. GAN 관련 (SC-FEGAN)", H1))
data = [
    ["용어", "정의", "우리 프로젝트"],
    ["GAN", "Generator vs Discriminator 경쟁 학습", "SC-FEGAN 베이스"],
    ["Generator", "가짜 이미지 생성기", "SC-FEGAN의 생성 네트워크"],
    ["Discriminator", "진짜/가짜 판별기", "추론 시 미사용"],
    ["Image Inpainting", "마스크 영역 자연스럽게 채우기", "SC-FEGAN의 일"],
    ["Gated Convolution", "마스크 인지형 conv 연산", "SC-FEGAN ops.py"],
    ["SC-FEGAN", "Sketch+Color+Mask로 얼굴 편집 GAN", "시각화 (학습 X)"],
]
story.append(make_table(data, [2.8*cm, 8*cm, 7.5*cm]))

# ─── 3. Vision Task ───
story.append(Paragraph("3. Vision Task 종류", H1))
data = [
    ["용어", "정의", "출력 / 비고"],
    ["Classification", "이미지 전체 → 한 클래스", "\"고양이\""],
    ["Detection", "객체 위치 + 클래스", "박스 여러 개"],
    ["Segmentation", "픽셀마다 클래스", "픽셀 단위 라벨맵"],
    ["Semantic Seg. ★", "같은 클래스는 같은 라벨", "우리 task"],
    ["Instance Seg.", "개별 인스턴스 구분", "안 씀"],
    ["Face Parsing", "얼굴 부위 segmentation 학술 용어", "우리가 하는 일"],
]
story.append(make_table(data, [2.8*cm, 8*cm, 7.5*cm]))
story.append(PageBreak())

# ─── 4. 학습 ───
story.append(Paragraph("4. 학습 (Training)", H1))
data = [
    ["용어", "정의", "우리 설정"],
    ["Loss Function", "예측-정답 차이 수치화", "Combo Loss"],
    ["Cross Entropy (CE)", "분류 표준 손실", "Combo 50%"],
    ["Dice Loss", "영역 겹침 기반, imbalance에 강함", "Combo 50%"],
    ["Combo Loss ★", "Dice + CE 가중합", "우리 손실"],
    ["Optimizer (Adam)", "gradient로 가중치 업데이트", "Adam, lr=1e-4"],
    ["Learning Rate (lr)", "한 step 업데이트 크기", "1e-4"],
    ["Batch Size", "한 번에 처리하는 이미지 수", "16"],
    ["Epoch", "전체 데이터 한 바퀴", "PoC 1, 본 학습 10"],
    ["Scheduler", "학습 중 lr 자동 조절", "CosineAnnealingLR"],
    ["Weight Decay", "과적합 방지 L2 정규화", "1e-5"],
    ["Transfer Learning ★", "사전학습 가중치 가져와 fine-tuning", "ResNet ImageNet"],
    ["Fine-tuning", "사전학습 모델 추가 학습", "우리가 하는 일"],
    ["Checkpoint (ckpt)", "학습 가중치 저장 파일", "unet_v1.pt"],
    ["Overfit", "학습 데이터에만 잘 맞음", "Aug로 방지"],
]
story.append(make_table(data, [3*cm, 8*cm, 7.3*cm]))

# ─── 5. 평가 지표 ───
story.append(Paragraph("5. 평가 지표", H1))
data = [
    ["용어", "정의", "공식 / 비고"],
    ["TP/FP/FN/TN", "True/False Positive/Negative", "정답·예측 조합"],
    ["IoU", "예측∩정답 / 예측∪정답", "TP/(TP+FP+FN)"],
    ["mIoU ★", "클래스별 IoU 평균 (배경 제외)", "메인 지표"],
    ["Dice Score", "F1 유사, 영역 겹침", "2·TP/(2·TP+FP+FN)"],
    ["Per-class IoU", "클래스별 IoU 표시", "약한 부위 분석"],
    ["Confusion Matrix", "정답 vs 예측 매트릭스", "클래스 혼동 분석"],
    ["Pixel Accuracy", "맞춘 픽셀 비율", "보조 지표"],
]
story.append(make_table(data, [3*cm, 8*cm, 7.3*cm]))
story.append(PageBreak())

# ─── 6. 해석 가능성 ───
story.append(Paragraph("6. 해석 가능성 (Explainable AI)", H1))
data = [
    ["용어", "정의", "우리 프로젝트"],
    ["Grad-CAM ★", "\"왜 이렇게 판단했나\" 시각화", "15% 어필 포인트"],
    ["Feature Map", "conv layer 중간 출력", "시각화 가능"],
    ["Heatmap", "픽셀별 활성화 강도 색상", "Grad-CAM 결과"],
    ["Explainable AI (XAI)", "모델 판단 근거 이해 분야", "평가 기준 명시"],
]
story.append(make_table(data, [3*cm, 8*cm, 7.3*cm]))

# ─── 7. 데이터 + Augmentation ───
story.append(Paragraph("7. 데이터 + Augmentation", H1))
data = [
    ["용어", "정의", "우리 프로젝트"],
    ["CelebAMask-HQ ★", "30K 얼굴 + 19부위 mask, CVPR 2020", "학습 데이터셋"],
    ["DataLoader", "데이터셋을 배치 단위 공급", "PyTorch 기본"],
    ["Augmentation", "학습 데이터 변형해 일반화 ↑", "flip, rotate 등"],
    ["Spatial Transform", "공간 변형 (mask도 동시 변형)", "flip, rotate"],
    ["Pixel Transform", "픽셀 값만 변형", "brightness, blur"],
    ["Albumentations", "augmentation 표준 라이브러리", "transforms.py"],
    ["Ablation Study", "컴포넌트 빼고 성능 비교", "aug 비교"],
]
story.append(make_table(data, [3*cm, 8*cm, 7.3*cm]))

# ─── 8. 라이브러리 ───
story.append(Paragraph("8. 라이브러리", H1))
data = [
    ["용어", "역할", "비고"],
    ["PyTorch", "딥러닝 프레임워크", "U-Net 학습"],
    ["TensorFlow (TF)", "또 다른 DL 프레임워크", "SC-FEGAN (legacy)"],
    ["Keras", "TF 상위 API", "TF 2.x 일부"],
    ["smp", "PyTorch segmentation 라이브러리", "U-Net 정의 3줄"],
    ["MediaPipe Tasks API", "Google 신형 얼굴 분석", "478 landmarks"],
    ["mp.solutions", "MediaPipe 구형 API", "우리 안 씀 (충돌)"],
    ["pytorch-grad-cam", "Grad-CAM 라이브러리", "Week 3"],
    ["OpenCV (cv2)", "이미지 처리 표준", "resize, draw"],
    ["HF datasets", "Hugging Face 데이터셋", "CelebAMask 다운로드"],
]
story.append(make_table(data, [3*cm, 8*cm, 7.3*cm]))
story.append(PageBreak())

# ─── 9. 환경 + 디버깅 ───
story.append(Paragraph("9. 환경 + Week 1 디버깅 흔적", H1))
data = [
    ["용어", "의미", "우리 함정"],
    ["Google Colab", "무료 클라우드 Jupyter", "메인 환경"],
    ["T4 GPU", "NVIDIA Tesla T4 (16GB)", "Colab 무료"],
    ["CUDA", "NVIDIA GPU 컴퓨팅", "12.x"],
    ["Drive Mount", "Colab에 Drive 연결", "코드/데이터 공유"],
    ["TF Compat Mode", "TF 2.x를 1.x처럼 쓰기", "SC-FEGAN 호환"],
    ["tf.contrib", "TF 1.x 보조 모듈 (제거됨)", "sys.modules stub"],
    ["Keras 2 강제", "TF_USE_LEGACY_KERAS=1", "tf.layers.conv2d 위해"],
]
story.append(make_table(data, [3*cm, 8*cm, 7.3*cm]))

# ─── 10. 우리 파이프라인 특화 ───
story.append(Paragraph("10. 파이프라인 특화 용어", H1))
data = [
    ["용어", "정의", "비고"],
    ["478 Landmarks", "MediaPipe 얼굴 점들", "468 face + 10 iris"],
    ["Convex Hull", "점들을 감싸는 볼록 다각형", "v1 거친 마스크"],
    ["Mask", "편집 영역 binary 이미지", "SC-FEGAN 입력"],
    ["Sketch", "SC-FEGAN의 가이드 라인", "변형 모양 지시"],
    ["9-channel input", "img+sketch+color+mask+noise", "SC-FEGAN 입력 포맷"],
    ["황금비", "1:1.618 얼굴 비율", "분석 기준"],
    ["삼정오안", "얼굴 세로 3등분 + 가로 5등분", "한국 미용 기준"],
    ["E-line", "코끝-턱끝 직선", "입술 위치 평가"],
    ["룰베이스", "if-else 시술 추천", "우리 추천 엔진"],
]
story.append(make_table(data, [3*cm, 8*cm, 7.3*cm]))

# ─── 11. 발표 TOP 10 ───
story.append(Paragraph("★ 발표에서 자주 입에 올릴 TOP 10", H1))
data = [
    ["#", "용어", "답변 시 표현"],
    ["1", "계층적 특징 추출", "Encoder가 단계적으로 추출"],
    ["2", "Skip Connection", "Decoder에 공간 정보 전달"],
    ["3", "mIoU", "배경 제외 클래스별 IoU 평균"],
    ["4", "Transfer Learning", "ImageNet 사전학습 ResNet-34"],
    ["5", "Combo Loss", "Dice + CrossEntropy 가중합"],
    ["6", "Ablation Study", "Augmentation 비교 실험"],
    ["7", "Grad-CAM", "Encoder bottleneck hook"],
    ["8", "Semantic Segmentation", "픽셀 단위 클래스 분류"],
    ["9", "CelebAMask-HQ", "CVPR 2020 표준 얼굴 데이터셋"],
    ["10", "Image Inpainting", "마스크 영역 채우기"],
]
story.append(make_table(data, [0.8*cm, 4.5*cm, 13.0*cm]))

story.append(Spacer(1, 8))
story.append(Paragraph(
    "이 문서는 빠른 참조용. 자세한 설명은 study_guide.pdf 참고.<br/>"
    "kim · 2026-05-18", Caption))

doc.build(story)
print("✅ Saved: glossary.pdf")
