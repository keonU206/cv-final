const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
pres.author = "Team CV-Final";
pres.title = "성형 견적 시각화 시스템 - 제안 발표";

// ─── Color Palette: Midnight Executive ───
const C = {
  navy: "1E2761",       // primary (dark)
  ice: "CADCFC",        // secondary (light blue)
  white: "FFFFFF",
  charcoal: "2C3E50",   // body text
  muted: "7B8FA1",      // captions
  accent: "F96167",     // highlight (coral, used sparingly)
  bg: "FAFBFD"          // off-white for content bg
};

// ─── Fonts ───
const FONT_HEADER = "Malgun Gothic";
const FONT_BODY = "Malgun Gothic";

// Common helpers
function addAccentBar(slide) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: C.navy }, line: { type: "none" }
  });
}

function addTitle(slide, text, options = {}) {
  slide.addText(text, {
    x: 0.5, y: 0.3, w: 9.0, h: 0.7,
    fontFace: FONT_HEADER, fontSize: options.size || 28, bold: true,
    color: C.navy, align: "left", valign: "middle", margin: 0
  });
}

function addSlideNumber(slide, n, total) {
  slide.addText(`${n} / ${total}`, {
    x: 9.0, y: 0.1, w: 0.9, h: 0.25,
    fontFace: FONT_BODY, fontSize: 9, color: C.muted, align: "right", margin: 0
  });
}

const TOTAL = 8;

// ════════════════════════════════════════════════════════════════
// SLIDE 1 — TITLE (dark)
// ════════════════════════════════════════════════════════════════
const s1 = pres.addSlide();
s1.background = { color: C.navy };

// Decorative accent bar on top
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08,
  fill: { color: C.accent }, line: { type: "none" }
});

// Eyebrow text
s1.addText("컴퓨터 비전 기말 프로젝트 · 아이디어 제안", {
  x: 0.7, y: 1.0, w: 8.5, h: 0.4,
  fontFace: FONT_BODY, fontSize: 14, color: C.ice,
  align: "left", charSpacing: 4
});

// Main title
s1.addText("성형 견적 시각화 시스템", {
  x: 0.7, y: 1.5, w: 8.5, h: 1.1,
  fontFace: FONT_HEADER, fontSize: 44, bold: true, color: C.white,
  align: "left", valign: "top"
});

// Subtitle
s1.addText("U-Net 기반 얼굴 부위 세그멘테이션 + GAN 시각화", {
  x: 0.7, y: 2.6, w: 8.5, h: 0.5,
  fontFace: FONT_HEADER, fontSize: 20, color: C.ice,
  align: "left", italic: true
});

// Divider line
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0.7, y: 3.4, w: 1.5, h: 0.04,
  fill: { color: C.accent }, line: { type: "none" }
});

// Team info
s1.addText([
  { text: "팀명: ", options: { bold: true, color: C.white } },
  { text: "[팀명 입력]", options: { color: C.ice, breakLine: true } },
  { text: "팀원: ", options: { bold: true, color: C.white } },
  { text: "[팀원1] · [팀원2] · [팀원3]", options: { color: C.ice, breakLine: true } },
  { text: "지도: ", options: { bold: true, color: C.white } },
  { text: "박한샘 교수님", options: { color: C.ice } }
], {
  x: 0.7, y: 3.7, w: 8.5, h: 1.2,
  fontFace: FONT_BODY, fontSize: 14, valign: "top"
});

// Date (bottom right)
s1.addText("2026.05.18", {
  x: 7.5, y: 5.0, w: 2.0, h: 0.4,
  fontFace: FONT_BODY, fontSize: 12, color: C.ice, align: "right"
});

// ════════════════════════════════════════════════════════════════
// SLIDE 2 — 문제 정의
// ════════════════════════════════════════════════════════════════
const s2 = pres.addSlide();
s2.background = { color: C.bg };
addAccentBar(s2);
addTitle(s2, "문제 정의 — 왜 이 문제인가");

// Eyebrow
s2.addText("Problem Statement & Motivation", {
  x: 0.5, y: 1.0, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 11, color: C.muted, italic: true
});

// Left card — 현장의 한계
s2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.5, w: 4.4, h: 3.5,
  fill: { color: C.white }, line: { color: C.ice, width: 1 },
  shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 90, opacity: 0.08 }
});
s2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.5, w: 0.08, h: 3.5,
  fill: { color: C.navy }, line: { type: "none" }
});
s2.addText("현장의 한계", {
  x: 0.75, y: 1.65, w: 4.0, h: 0.4,
  fontFace: FONT_HEADER, fontSize: 18, bold: true, color: C.navy
});
s2.addText([
  { text: "① 시술 진단의 주관성", options: { bold: true, color: C.charcoal, breakLine: true, fontSize: 14 } },
  { text: "   상담사 경험에 의존", options: { color: C.muted, breakLine: true, fontSize: 12 } },
  { text: "   환자 본인도 판단 어려움", options: { color: C.muted, breakLine: true, fontSize: 12 } },
  { text: " ", options: { breakLine: true, fontSize: 8 } },
  { text: "② 시술 후 결과 예측의 한계", options: { bold: true, color: C.charcoal, breakLine: true, fontSize: 14 } },
  { text: "   기존: 2D 합성·모자이크 수준", options: { color: C.muted, breakLine: true, fontSize: 12 } },
  { text: "   실제 결과와 큰 괴리", options: { color: C.muted, fontSize: 12 } }
], {
  x: 0.75, y: 2.15, w: 4.1, h: 2.7,
  fontFace: FONT_BODY, valign: "top"
});

// Right card — 우리 가설
s2.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.5, w: 4.4, h: 3.5,
  fill: { color: C.navy }, line: { type: "none" },
  shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 90, opacity: 0.12 }
});
s2.addText("우리의 가설", {
  x: 5.35, y: 1.65, w: 4.0, h: 0.4,
  fontFace: FONT_HEADER, fontSize: 18, bold: true, color: C.white
});
s2.addText("AI가 얼굴 부위를 정밀 분할하고, 해당 영역을 변형 시각화한다면", {
  x: 5.35, y: 2.15, w: 4.0, h: 0.6,
  fontFace: FONT_BODY, fontSize: 12, color: C.ice, italic: true
});
s2.addText([
  { text: "→ ", options: { color: C.accent, bold: true } },
  { text: "객관적 진단 가능", options: { color: C.white, bold: true, breakLine: true, fontSize: 14 } },
  { text: "→ ", options: { color: C.accent, bold: true } },
  { text: "시술 후 결과 예측 가능", options: { color: C.white, bold: true, fontSize: 14 } }
], {
  x: 5.35, y: 2.85, w: 4.0, h: 1.0,
  fontFace: FONT_BODY, valign: "top"
});

// Task type badges (single row centered in card)
s2.addText("VISION TASK", {
  x: 5.35, y: 4.05, w: 4.0, h: 0.25,
  fontFace: FONT_BODY, fontSize: 9, color: C.ice, charSpacing: 4, align: "left"
});
s2.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 5.35, y: 4.35, w: 1.85, h: 0.4, rectRadius: 0.05,
  fill: { color: C.accent }, line: { type: "none" }
});
s2.addText("Segmentation", {
  x: 5.35, y: 4.35, w: 1.85, h: 0.4,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", margin: 0
});
s2.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 7.3, y: 4.35, w: 1.85, h: 0.4, rectRadius: 0.05,
  fill: { color: C.ice }, line: { type: "none" }
});
s2.addText("Generation", {
  x: 7.3, y: 4.35, w: 1.85, h: 0.4,
  fontFace: FONT_BODY, fontSize: 11, bold: true, color: C.navy, align: "center", valign: "middle", margin: 0
});

addSlideNumber(s2, 2, TOTAL);

// ════════════════════════════════════════════════════════════════
// SLIDE 3 — 솔루션 파이프라인
// ════════════════════════════════════════════════════════════════
const s3 = pres.addSlide();
s3.background = { color: C.bg };
addAccentBar(s3);
addTitle(s3, "솔루션 — End-to-End 파이프라인");

s3.addText("Pipeline Overview", {
  x: 0.5, y: 1.0, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 11, color: C.muted, italic: true
});

// Horizontal pipeline boxes
const pipeSteps = [
  { num: "1", title: "얼굴 검출", sub: "MediaPipe\nTasks API\n478 landmarks", highlight: false },
  { num: "2", title: "비율 분석", sub: "삼정·오안\nE-line\n룰베이스 추천", highlight: false },
  { num: "3", title: "U-Net\n세그멘테이션", sub: "★ 자체 학습\nCelebAMask-HQ\n5 시술 부위", highlight: true },
  { num: "4", title: "SC-FEGAN\n추론", sub: "사전학습 GAN\n512×512\n시술 후 얼굴", highlight: false },
  { num: "5", title: "시각화", sub: "Before/After\nGrad-CAM\nPDF 견적서", highlight: false }
];

const boxW = 1.65;
const boxH = 2.5;
const gap = 0.15;
const startX = 0.5;
const startY = 1.5;

pipeSteps.forEach((step, i) => {
  const x = startX + i * (boxW + gap);
  const isHighlight = step.highlight;

  // Card
  s3.addShape(pres.shapes.RECTANGLE, {
    x: x, y: startY, w: boxW, h: boxH,
    fill: { color: isHighlight ? C.navy : C.white },
    line: { color: isHighlight ? C.navy : C.ice, width: 1 },
    shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 90,
              opacity: isHighlight ? 0.18 : 0.06 }
  });

  // Number circle
  s3.addShape(pres.shapes.OVAL, {
    x: x + boxW/2 - 0.25, y: startY + 0.15, w: 0.5, h: 0.5,
    fill: { color: isHighlight ? C.accent : C.ice }, line: { type: "none" }
  });
  s3.addText(step.num, {
    x: x + boxW/2 - 0.25, y: startY + 0.15, w: 0.5, h: 0.5,
    fontFace: FONT_HEADER, fontSize: 18, bold: true,
    color: isHighlight ? C.white : C.navy,
    align: "center", valign: "middle", margin: 0
  });

  // Title
  s3.addText(step.title, {
    x: x + 0.05, y: startY + 0.75, w: boxW - 0.1, h: 0.7,
    fontFace: FONT_HEADER, fontSize: 13, bold: true,
    color: isHighlight ? C.white : C.navy,
    align: "center", valign: "top"
  });

  // Subtitle
  s3.addText(step.sub, {
    x: x + 0.1, y: startY + 1.5, w: boxW - 0.2, h: 1.0,
    fontFace: FONT_BODY, fontSize: 10,
    color: isHighlight ? C.ice : C.muted,
    align: "center", valign: "top"
  });

  // Arrow to next box
  if (i < pipeSteps.length - 1) {
    s3.addText("›", {
      x: x + boxW - 0.1, y: startY + boxH/2 - 0.25, w: 0.4, h: 0.5,
      fontFace: FONT_HEADER, fontSize: 28, bold: true, color: C.muted,
      align: "center", valign: "middle", margin: 0
    });
  }
});

// Bottom callout
s3.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.3, w: 9.0, h: 0.7,
  fill: { color: C.white }, line: { color: C.accent, width: 1 }
});
s3.addText([
  { text: "★ 메인 학습 컴포넌트: ", options: { bold: true, color: C.accent } },
  { text: "U-Net (Step 3) — 본 발표의 핵심 deliverable. SC-FEGAN은 사전학습 시각화 도구로 활용.", options: { color: C.charcoal } }
], {
  x: 0.7, y: 4.3, w: 8.6, h: 0.7,
  fontFace: FONT_BODY, fontSize: 12, valign: "middle"
});

addSlideNumber(s3, 3, TOTAL);

// ════════════════════════════════════════════════════════════════
// SLIDE 4 — U-Net 아키텍처 (★ 핵심)
// ════════════════════════════════════════════════════════════════
const s4 = pres.addSlide();
s4.background = { color: C.bg };
addAccentBar(s4);
addTitle(s4, "모델 설계 — U-Net 계층적 특징 추출");

s4.addText("Architecture: ResNet-34 Encoder + U-Net Decoder", {
  x: 0.5, y: 1.0, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 11, color: C.muted, italic: true
});

// U-Net Diagram (left half)
const diagX = 0.6;
const diagY = 1.5;

// Encoder boxes (descending size)
const encoderStages = [
  { w: 0.9, h: 0.45, label: "256" },
  { w: 0.75, h: 0.4, label: "128" },
  { w: 0.6, h: 0.35, label: "64" },
  { w: 0.45, h: 0.3, label: "32" }
];
const decoderStages = [
  { w: 0.45, h: 0.3, label: "32" },
  { w: 0.6, h: 0.35, label: "64" },
  { w: 0.75, h: 0.4, label: "128" },
  { w: 0.9, h: 0.45, label: "256" }
];

// Y stagger (descending then ascending)
const stageY = [diagY, diagY + 0.5, diagY + 1.0, diagY + 1.5];

// Encoder column
let encX = diagX;
encoderStages.forEach((stg, i) => {
  s4.addShape(pres.shapes.RECTANGLE, {
    x: encX, y: stageY[i] + (encoderStages[0].h - stg.h)/2, w: stg.w, h: stg.h,
    fill: { color: C.navy, transparency: i * 10 }, line: { color: C.navy, width: 1 }
  });
  s4.addText(stg.label, {
    x: encX, y: stageY[i] + (encoderStages[0].h - stg.h)/2, w: stg.w, h: stg.h,
    fontFace: FONT_BODY, fontSize: 9, bold: true, color: C.white,
    align: "center", valign: "middle", margin: 0
  });
  encX += stg.w + 0.05;
});

// Bottleneck
const bnX = encX;
const bnY = stageY[3] + (encoderStages[0].h - 0.25)/2;
s4.addShape(pres.shapes.RECTANGLE, {
  x: bnX, y: bnY, w: 0.4, h: 0.25,
  fill: { color: C.accent }, line: { type: "none" }
});
s4.addText("16", {
  x: bnX, y: bnY, w: 0.4, h: 0.25,
  fontFace: FONT_BODY, fontSize: 8, bold: true, color: C.white,
  align: "center", valign: "middle", margin: 0
});

// Decoder column
let decX = bnX + 0.45;
decoderStages.forEach((stg, i) => {
  const yIdx = 3 - i;
  s4.addShape(pres.shapes.RECTANGLE, {
    x: decX, y: stageY[yIdx] + (encoderStages[0].h - stg.h)/2, w: stg.w, h: stg.h,
    fill: { color: C.ice }, line: { color: C.navy, width: 1 }
  });
  s4.addText(stg.label, {
    x: decX, y: stageY[yIdx] + (encoderStages[0].h - stg.h)/2, w: stg.w, h: stg.h,
    fontFace: FONT_BODY, fontSize: 9, bold: true, color: C.navy,
    align: "center", valign: "middle", margin: 0
  });
  decX += stg.w + 0.05;
});

// Encoder/Decoder labels
s4.addText("Encoder", {
  x: diagX, y: diagY - 0.4, w: 3.2, h: 0.3,
  fontFace: FONT_HEADER, fontSize: 12, bold: true, color: C.navy,
  align: "center", charSpacing: 2
});
s4.addText("Decoder", {
  x: bnX + 0.5, y: diagY - 0.4, w: 3.2, h: 0.3,
  fontFace: FONT_HEADER, fontSize: 12, bold: true, color: C.navy,
  align: "center", charSpacing: 2
});

// Skip connection arrows — connect encoder right edge to decoder left edge at SAME level
// Encoder right edges and decoder left edges (computed from layout above):
const skipPairs = [
  { encRight: 1.50, decLeft: 5.90, y: 1.725, label: "256" },
  { encRight: 2.30, decLeft: 5.10, y: 2.225, label: "128" },
  { encRight: 2.95, decLeft: 4.45, y: 2.725, label: "64" }
];
skipPairs.forEach((p) => {
  s4.addShape(pres.shapes.LINE, {
    x: p.encRight, y: p.y, w: p.decLeft - p.encRight, h: 0,
    line: { color: C.accent, width: 1.2, dashType: "dash" }
  });
});

// Input arrow + label (left of encoder)
s4.addShape(pres.shapes.LINE, {
  x: 0.05, y: 1.725, w: 0.5, h: 0,
  line: { color: C.muted, width: 1.5, endArrowType: "triangle" }
});
s4.addText("Input", {
  x: 0.05, y: 1.45, w: 0.5, h: 0.25,
  fontFace: FONT_BODY, fontSize: 9, color: C.muted, align: "center", margin: 0, italic: true
});

// Output arrow + label (right of decoder)
s4.addShape(pres.shapes.LINE, {
  x: 6.85, y: 1.725, w: 0.5, h: 0,
  line: { color: C.muted, width: 1.5, endArrowType: "triangle" }
});
s4.addText("Output", {
  x: 6.85, y: 1.45, w: 0.5, h: 0.25,
  fontFace: FONT_BODY, fontSize: 9, color: C.muted, align: "center", margin: 0, italic: true
});

// Three principle boxes
const principles = [
  { num: "①", title: "계층적 특징 추출", desc: "단계적 다운샘플링\n저수준→고수준" },
  { num: "②", title: "Skip Connection", desc: "공간 정보 보존\nencoder→decoder" },
  { num: "③", title: "픽셀 단위 출력", desc: "6 클래스 분류\n(bg + 5 부위)" }
];

// Move principles down below diagram (limited space on right). Move to bottom:
const prinStartY = 3.7;
const prinBoxW = 2.85;
principles.forEach((p, i) => {
  const x = 0.5 + i * (prinBoxW + 0.15);
  s4.addShape(pres.shapes.RECTANGLE, {
    x: x, y: prinStartY, w: prinBoxW, h: 1.25,
    fill: { color: C.white }, line: { color: C.ice, width: 1 }
  });
  s4.addShape(pres.shapes.RECTANGLE, {
    x: x, y: prinStartY, w: 0.06, h: 1.25,
    fill: { color: C.accent }, line: { type: "none" }
  });
  s4.addText(p.num + " " + p.title, {
    x: x + 0.15, y: prinStartY + 0.1, w: prinBoxW - 0.2, h: 0.35,
    fontFace: FONT_HEADER, fontSize: 13, bold: true, color: C.navy
  });
  s4.addText(p.desc, {
    x: x + 0.15, y: prinStartY + 0.5, w: prinBoxW - 0.2, h: 0.7,
    fontFace: FONT_BODY, fontSize: 11, color: C.charcoal
  });
});

// Remove the inline right-side principles textbox (we moved them to bottom)
// (the addText above for "핵심 설계 원리" header at right is removed since we use bottom layout)

// Implementation note
s4.addText("구현: segmentation_models_pytorch 라이브러리 (PyTorch)", {
  x: 0.5, y: 5.05, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 10, color: C.muted, italic: true, align: "center"
});

addSlideNumber(s4, 4, TOTAL);

// ════════════════════════════════════════════════════════════════
// SLIDE 5 — 데이터셋
// ════════════════════════════════════════════════════════════════
const s5 = pres.addSlide();
s5.background = { color: C.bg };
addAccentBar(s5);
addTitle(s5, "데이터셋 — CelebAMask-HQ");

s5.addText("Dataset: Large-scale Annotated Face Parsing Dataset", {
  x: 0.5, y: 1.0, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 11, color: C.muted, italic: true
});

// Left — Stats cards
const statY = 1.5;
const stats = [
  { num: "30K", label: "고해상도 이미지\n1024 × 1024", color: C.navy },
  { num: "19", label: "부위별 라벨\n픽셀 단위 mask", color: C.accent },
  { num: "2020", label: "CVPR 학술 표준\nLee et al.", color: C.charcoal }
];
stats.forEach((s, i) => {
  const x = 0.5 + i * 1.55;
  s5.addShape(pres.shapes.RECTANGLE, {
    x: x, y: statY, w: 1.45, h: 1.5,
    fill: { color: C.white }, line: { color: C.ice, width: 1 },
    shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 90, opacity: 0.06 }
  });
  s5.addText(s.num, {
    x: x, y: statY + 0.15, w: 1.45, h: 0.7,
    fontFace: FONT_HEADER, fontSize: 30, bold: true, color: s.color,
    align: "center", valign: "middle"
  });
  s5.addText(s.label, {
    x: x + 0.1, y: statY + 0.9, w: 1.25, h: 0.55,
    fontFace: FONT_BODY, fontSize: 10, color: C.muted,
    align: "center", valign: "top"
  });
});

// Dataset description below stats
s5.addText([
  { text: "라이선스: ", options: { bold: true, color: C.charcoal } },
  { text: "비상업 연구 용도 (학술 발표 OK)", options: { color: C.muted, breakLine: true } },
  { text: "출처: ", options: { bold: true, color: C.charcoal } },
  { text: "github.com/switchablenorms/CelebAMask-HQ", options: { color: C.muted } }
], {
  x: 0.5, y: 3.1, w: 5.1, h: 0.7,
  fontFace: FONT_BODY, fontSize: 11, valign: "top"
});

// Right — Class mapping table
s5.addText("우리 task 클래스 매핑 (5 부위)", {
  x: 5.7, y: 1.5, w: 3.8, h: 0.35,
  fontFace: FONT_HEADER, fontSize: 13, bold: true, color: C.navy
});

const tableData = [
  [
    { text: "우리 클래스", options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center", fontSize: 10 } },
    { text: "CelebAMask-HQ 라벨", options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center", fontSize: 10 } }
  ],
  [{ text: "코", options: { fontSize: 10 } }, { text: "nose", options: { fontSize: 10 } }],
  [{ text: "눈", options: { fontSize: 10 } }, { text: "l_eye, r_eye", options: { fontSize: 10 } }],
  [{ text: "입", options: { fontSize: 10 } }, { text: "u_lip, l_lip, mouth", options: { fontSize: 10 } }],
  [{ text: "턱", options: { fontSize: 10 } }, { text: "skin (랜드마크 분리)", options: { fontSize: 10 } }],
  [{ text: "이마", options: { fontSize: 10 } }, { text: "skin (랜드마크 분리)", options: { fontSize: 10 } }]
];

s5.addTable(tableData, {
  x: 5.7, y: 1.9, w: 3.8, colW: [1.2, 2.6],
  border: { pt: 0.5, color: C.ice },
  fontFace: FONT_BODY,
  align: "left", valign: "middle"
});

// Train/Val/Test split bottom row
const splitY = 4.3;
s5.addText("데이터 분할", {
  x: 0.5, y: splitY, w: 2.0, h: 0.35,
  fontFace: FONT_HEADER, fontSize: 12, bold: true, color: C.navy
});

const splits = [
  { label: "Train", size: 24000, w: 6.4, color: C.navy },
  { label: "Val", size: 3000, w: 0.8, color: C.accent },
  { label: "Test", size: 3000, w: 0.8, color: C.muted }
];
let splitX = 0.5;
splits.forEach((sp, i) => {
  s5.addShape(pres.shapes.RECTANGLE, {
    x: splitX, y: splitY + 0.4, w: sp.w, h: 0.4,
    fill: { color: sp.color }, line: { type: "none" }
  });
  s5.addText(`${sp.label} ${(sp.size/1000).toFixed(0)}K`, {
    x: splitX, y: splitY + 0.4, w: sp.w, h: 0.4,
    fontFace: FONT_BODY, fontSize: 10, bold: true, color: C.white,
    align: "center", valign: "middle", margin: 0
  });
  splitX += sp.w + 0.05;
});

addSlideNumber(s5, 5, TOTAL);

// ════════════════════════════════════════════════════════════════
// SLIDE 6 — 평가 방법
// ════════════════════════════════════════════════════════════════
const s6 = pres.addSlide();
s6.background = { color: C.bg };
addAccentBar(s6);
addTitle(s6, "평가 + 성능 분석 + 해석");

s6.addText("Evaluation, Optimization & Interpretability", {
  x: 0.5, y: 1.0, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 11, color: C.muted, italic: true
});

// Three columns
const colY = 1.5;
const colH = 3.3;
const colW = 2.95;
const cols = [
  {
    title: "정량 지표",
    badge: "Metrics",
    color: C.navy,
    items: [
      "mIoU (mean IoU)",
      "Dice Score (F1 유사)",
      "Per-class IoU",
      "Confusion Matrix",
      "Pixel Accuracy"
    ]
  },
  {
    title: "성능 최적화",
    badge: "Optimization",
    color: C.accent,
    items: [
      "Augmentation 비교",
      "  · horizontal flip",
      "  · rotation ±15°",
      "  · color jitter",
      "Ablation study 표"
    ]
  },
  {
    title: "해석 가능성",
    badge: "Explainability",
    color: C.charcoal,
    items: [
      "Grad-CAM",
      "  encoder bottleneck hook",
      "Feature Map 시각화",
      "예측 mask overlay",
      "부위별 heatmap"
    ]
  }
];

cols.forEach((col, i) => {
  const x = 0.5 + i * (colW + 0.13);

  // Card
  s6.addShape(pres.shapes.RECTANGLE, {
    x: x, y: colY, w: colW, h: colH,
    fill: { color: C.white }, line: { color: C.ice, width: 1 },
    shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 90, opacity: 0.06 }
  });

  // Top color band
  s6.addShape(pres.shapes.RECTANGLE, {
    x: x, y: colY, w: colW, h: 0.1,
    fill: { color: col.color }, line: { type: "none" }
  });

  // Title
  s6.addText(col.title, {
    x: x + 0.15, y: colY + 0.25, w: colW - 0.3, h: 0.4,
    fontFace: FONT_HEADER, fontSize: 16, bold: true, color: C.navy
  });

  // Badge
  s6.addText(col.badge, {
    x: x + 0.15, y: colY + 0.7, w: colW - 0.3, h: 0.25,
    fontFace: FONT_BODY, fontSize: 9, italic: true, color: col.color, charSpacing: 2
  });

  // Items
  const itemList = col.items.map((item, idx) => ({
    text: item,
    options: {
      breakLine: idx < col.items.length - 1,
      fontSize: 11,
      color: item.startsWith("  ") ? C.muted : C.charcoal,
      bullet: !item.startsWith("  ")
    }
  }));
  s6.addText(itemList, {
    x: x + 0.2, y: colY + 1.1, w: colW - 0.3, h: 2.3,
    fontFace: FONT_BODY, valign: "top"
  });
});

// Bottom — Demo plan
s6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 5.0, w: 9.0, h: 0.35,
  fill: { color: C.navy }, line: { type: "none" }
});
s6.addText("최종 데모: 사진 업로드 → 추천 시술 → U-Net 마스크 → SC-FEGAN After → PDF 견적서 자동 생성", {
  x: 0.5, y: 5.0, w: 9.0, h: 0.35,
  fontFace: FONT_BODY, fontSize: 11, color: C.white, align: "center", valign: "middle", margin: 0
});

addSlideNumber(s6, 6, TOTAL);

// ════════════════════════════════════════════════════════════════
// SLIDE 7 — 일정 + 역할
// ════════════════════════════════════════════════════════════════
const s7 = pres.addSlide();
s7.background = { color: C.bg };
addAccentBar(s7);
addTitle(s7, "일정 + 역할 분담");

s7.addText("Roadmap to Final Presentation & Team Distribution", {
  x: 0.5, y: 1.0, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 11, color: C.muted, italic: true
});

// Timeline at top
const tlY = 1.5;
const weeks = [
  { label: "Week 1", date: "5/8–14", desc: "환경 셋업\n파이프라인 검증", done: true },
  { label: "Week 2", date: "5/19–26", desc: "데이터로더\nU-Net PoC", done: false },
  { label: "Week 3", date: "5/27–6/2", desc: "본격 학습\nGrad-CAM", done: false },
  { label: "Week 4", date: "6/3–9", desc: "통합\nPDF 출력", done: false },
  { label: "발표", date: "6/15", desc: "최종 평가", done: false, isMilestone: true }
];

const tlBoxW = 1.65;
const tlGap = 0.15;
weeks.forEach((w, i) => {
  const x = 0.5 + i * (tlBoxW + tlGap);
  const bgC = w.isMilestone ? C.accent : (w.done ? C.navy : C.white);
  const txtC = w.isMilestone || w.done ? C.white : C.navy;
  const subC = w.isMilestone || w.done ? C.ice : C.muted;

  s7.addShape(pres.shapes.RECTANGLE, {
    x: x, y: tlY, w: tlBoxW, h: 1.5,
    fill: { color: bgC }, line: { color: w.done || w.isMilestone ? bgC : C.ice, width: 1 }
  });

  // Done badge
  if (w.done) {
    s7.addShape(pres.shapes.OVAL, {
      x: x + tlBoxW - 0.35, y: tlY + 0.1, w: 0.25, h: 0.25,
      fill: { color: C.accent }, line: { type: "none" }
    });
    s7.addText("✓", {
      x: x + tlBoxW - 0.35, y: tlY + 0.1, w: 0.25, h: 0.25,
      fontFace: FONT_HEADER, fontSize: 12, bold: true, color: C.white,
      align: "center", valign: "middle", margin: 0
    });
  }

  s7.addText(w.label, {
    x: x + 0.1, y: tlY + 0.15, w: tlBoxW - 0.5, h: 0.3,
    fontFace: FONT_HEADER, fontSize: 13, bold: true, color: txtC
  });
  s7.addText(w.date, {
    x: x + 0.1, y: tlY + 0.45, w: tlBoxW - 0.2, h: 0.25,
    fontFace: FONT_BODY, fontSize: 9, color: subC
  });
  s7.addText(w.desc, {
    x: x + 0.1, y: tlY + 0.75, w: tlBoxW - 0.2, h: 0.7,
    fontFace: FONT_BODY, fontSize: 10, color: txtC, valign: "top"
  });
});

// Role distribution table
const roleY = 3.3;
s7.addText("역할 분담", {
  x: 0.5, y: roleY, w: 3.0, h: 0.35,
  fontFace: FONT_HEADER, fontSize: 14, bold: true, color: C.navy
});

const roleData = [
  [
    { text: "역할", options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
    { text: "메인 책임", options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
    { text: "산출물", options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } }
  ],
  [
    { text: "A · 모델/엔진" },
    { text: "SC-FEGAN wrapper + DiffFace 백업 PoC" },
    { text: "scfegan_wrapper/, diffface_wrapper/" }
  ],
  [
    { text: "B · 세그멘테이션 ★", options: { bold: true, color: C.accent } },
    { text: "U-Net 학습 + 평가 + Grad-CAM" },
    { text: "project/segmentation/ 전체" }
  ],
  [
    { text: "C · 분석/UI" },
    { text: "MediaPipe + 추천 + Streamlit + PDF" },
    { text: "ui/, face_analyzer/, recommender/" }
  ]
];

s7.addTable(roleData, {
  x: 0.5, y: roleY + 0.4, w: 9.0, colW: [2.0, 3.5, 3.5], rowH: 0.4,
  border: { pt: 0.5, color: C.ice },
  fontFace: FONT_BODY, fontSize: 11,
  align: "left", valign: "middle"
});

addSlideNumber(s7, 7, TOTAL);

// ════════════════════════════════════════════════════════════════
// SLIDE 8 — Week 1 PoC (검증 증거)
// ════════════════════════════════════════════════════════════════
const s8 = pres.addSlide();
s8.background = { color: C.bg };
addAccentBar(s8);
addTitle(s8, "Week 1 PoC — 사전 검증 완료");

s8.addText("Validated Components Before Proposal", {
  x: 0.5, y: 1.0, w: 9.0, h: 0.3,
  fontFace: FONT_BODY, fontSize: 11, color: C.muted, italic: true
});

// Left — Validated checklist
const chkX = 0.5;
const chkY = 1.5;
s8.addShape(pres.shapes.RECTANGLE, {
  x: chkX, y: chkY, w: 4.4, h: 3.4,
  fill: { color: C.white }, line: { color: C.ice, width: 1 },
  shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 90, opacity: 0.06 }
});

s8.addText("검증된 구성요소", {
  x: chkX + 0.2, y: chkY + 0.15, w: 4.0, h: 0.35,
  fontFace: FONT_HEADER, fontSize: 15, bold: true, color: C.navy
});

const checks = [
  "Colab 환경 셋업 (TF 2.x compat + Keras 2)",
  "MediaPipe Tasks API · 478 landmarks 검출",
  "얼굴 비율 분석 10개 지표",
  "룰베이스 추천 엔진 (시술 3종)",
  "SC-FEGAN 사전학습 모델 로드 (190MB)",
  "9채널 입력 → SC-FEGAN 추론 (2초/장)",
  "Before/After 시각화 파이프라인"
];

const checkItems = checks.map((c, idx) => ([
  { text: "✓ ", options: { color: C.accent, bold: true } },
  { text: c, options: { color: C.charcoal, breakLine: idx < checks.length - 1 } }
])).flat();

s8.addText(checkItems, {
  x: chkX + 0.2, y: chkY + 0.6, w: 4.0, h: 2.7,
  fontFace: FONT_BODY, fontSize: 11, valign: "top", paraSpaceAfter: 4
});

// Right — Demo result placeholder
const demoX = 5.1;
const demoY = 1.5;
s8.addShape(pres.shapes.RECTANGLE, {
  x: demoX, y: demoY, w: 4.4, h: 3.4,
  fill: { color: C.white }, line: { color: C.ice, width: 1 },
  shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 90, opacity: 0.06 }
});

s8.addText("실제 결과 (SC-FEGAN 추론)", {
  x: demoX + 0.2, y: demoY + 0.15, w: 4.0, h: 0.35,
  fontFace: FONT_HEADER, fontSize: 15, bold: true, color: C.navy
});

// Image placeholder
s8.addShape(pres.shapes.RECTANGLE, {
  x: demoX + 0.2, y: demoY + 0.6, w: 4.0, h: 2.1,
  fill: { color: C.ice }, line: { color: C.navy, width: 1, dashType: "dash" }
});
s8.addText("[ Before / After 캡처 삽입 ]\nsmoke_test_01.png\n발표 직전 교체", {
  x: demoX + 0.2, y: demoY + 0.6, w: 4.0, h: 2.1,
  fontFace: FONT_BODY, fontSize: 11, color: C.navy, italic: true,
  align: "center", valign: "middle"
});

s8.addText([
  { text: "추천: ", options: { bold: true, color: C.charcoal } },
  { text: "사각턱 + V라인 (신뢰도 0.67)  ·  ", options: { color: C.muted } },
  { text: "추론 시간: ", options: { bold: true, color: C.charcoal } },
  { text: "2.1초 (T4 GPU)", options: { color: C.muted } }
], {
  x: demoX + 0.2, y: demoY + 2.8, w: 4.0, h: 0.5,
  fontFace: FONT_BODY, fontSize: 10, valign: "top"
});

// Bottom call-to-action
s8.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 5.0, w: 9.0, h: 0.35,
  fill: { color: C.navy }, line: { type: "none" }
});
s8.addText("→ Week 2부터 U-Net 학습 본격 진행 (CelebAMask-HQ + segmentation_models_pytorch)", {
  x: 0.5, y: 5.0, w: 9.0, h: 0.35,
  fontFace: FONT_BODY, fontSize: 11, color: C.white, align: "center", valign: "middle", margin: 0, italic: true
});

addSlideNumber(s8, 8, TOTAL);

// ─── Save ───
pres.writeFile({ fileName: "proposal_slides.pptx" })
  .then(name => console.log(`✅ Saved: ${name}`))
  .catch(err => console.error("❌ Error:", err));
