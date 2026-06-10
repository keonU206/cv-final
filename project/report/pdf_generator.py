"""성형 견적서 PDF 생성 — 환자 맞춤형 보고서.

입력:
- 선택된 시술 리스트 (procedure_ids)
- Before/After 이미지 경로 (선택)
- 환자 이름 (선택, 기본 익명)

출력:
- A4 PDF: 표지 / 시술 항목 표 / Before-After 비교 / 총액 / 푸터

procedures.yaml의 price_krw_min/max + name_ko + description을 활용.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import yaml

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        Image as RLImage,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError as e:
    raise ImportError("reportlab 필요: pip install reportlab") from e


# ─── 색상 팔레트 (다른 PDF generator와 일관성) ───
NAVY = colors.HexColor("#1E2761")
ICE = colors.HexColor("#CADCFC")
ACCENT = colors.HexColor("#F96167")
CHARCOAL = colors.HexColor("#2C3E50")
MUTED = colors.HexColor("#7B8FA1")
BG = colors.HexColor("#FAFBFD")
LIGHT_BORDER = colors.HexColor("#E2E8F0")
GREEN = colors.HexColor("#48BB78")

# ─── 폰트 — Windows 기본 (한글) ───
_FONT_REGULAR_PATH = "C:/Windows/Fonts/malgun.ttf"
_FONT_BOLD_PATH = "C:/Windows/Fonts/malgunbd.ttf"
_FONT_REGULAR = "Malgun"
_FONT_BOLD = "MalgunBold"
_FONT_REGISTERED = False


def _ensure_fonts():
    """Windows 한글 폰트 등록 (1회만)."""
    global _FONT_REGISTERED, _FONT_REGULAR_PATH, _FONT_BOLD_PATH
    if _FONT_REGISTERED:
        return
    if Path(_FONT_REGULAR_PATH).exists():
        pdfmetrics.registerFont(TTFont(_FONT_REGULAR, _FONT_REGULAR_PATH))
        pdfmetrics.registerFont(TTFont(_FONT_BOLD, _FONT_BOLD_PATH))
    else:
        # Linux/Colab 폴백 — 기본 Helvetica 사용 (한글 깨짐 가능)
        _FONT_REGULAR_PATH = _FONT_BOLD_PATH = None
    _FONT_REGISTERED = True


def _font(bold: bool = False) -> str:
    """현재 환경에 맞는 폰트 이름 반환."""
    _ensure_fonts()
    if _FONT_REGULAR_PATH is None:
        return "Helvetica-Bold" if bold else "Helvetica"
    return _FONT_BOLD if bold else _FONT_REGULAR


# ─── 데이터 클래스 ───

@dataclass
class EstimateItem:
    """견적서 한 항목."""

    procedure_id: str
    name_ko: str
    name_en: str
    price_min: int
    price_max: int
    description: str = ""
    region: str = ""
    before_path: Optional[Path] = None
    after_path: Optional[Path] = None

    @property
    def price_avg(self) -> int:
        return (self.price_min + self.price_max) // 2

    def price_range_str(self) -> str:
        """가격 범위 문자열 (한국어 만원 단위)."""
        mn = self.price_min // 10000
        mx = self.price_max // 10000
        return f"{mn:,} ~ {mx:,} 만원"


# ─── procedures.yaml 로더 ───

DEFAULT_PROCEDURES_YAML = (
    Path(__file__).resolve().parents[1] / "recommender" / "procedures.yaml"
)


def load_procedure_catalog(
    yaml_path: str | Path = DEFAULT_PROCEDURES_YAML,
) -> dict[str, dict]:
    """procedures.yaml → {id: procedure_dict}."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        items = yaml.safe_load(f)
    return {item["id"]: item for item in items}


def build_estimate(
    procedure_ids: list[str],
    catalog: Optional[dict[str, dict]] = None,
    before_paths: Optional[dict[str, Path]] = None,
    after_paths: Optional[dict[str, Path]] = None,
) -> list[EstimateItem]:
    """선택된 시술 id 리스트 → EstimateItem 리스트.

    Args:
        procedure_ids: 환자가 선택한 시술 id 리스트.
        catalog: procedures.yaml 로드 결과 (없으면 자동 로드).
        before_paths: {procedure_id: Path} — Before 이미지.
        after_paths: {procedure_id: Path} — After 이미지.

    Returns:
        EstimateItem 리스트.

    Raises:
        ValueError: 알 수 없는 procedure_id.
    """
    catalog = catalog or load_procedure_catalog()
    before_paths = before_paths or {}
    after_paths = after_paths or {}

    items = []
    for pid in procedure_ids:
        if pid not in catalog:
            raise ValueError(f"unknown procedure_id: {pid}")
        p = catalog[pid]
        items.append(EstimateItem(
            procedure_id=pid,
            name_ko=p.get("name_ko", pid),
            name_en=p.get("name_en", pid),
            price_min=int(p.get("price_krw_min", 0)),
            price_max=int(p.get("price_krw_max", 0)),
            description=p.get("description", ""),
            region=p.get("region", ""),
            before_path=before_paths.get(pid),
            after_path=after_paths.get(pid),
        ))
    return items


# ─── PDF 생성 ───

def _make_styles():
    return {
        "title": ParagraphStyle(
            "title", fontName=_font(bold=True), fontSize=22, leading=28,
            textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
        ),
        "sub": ParagraphStyle(
            "sub", fontName=_font(), fontSize=11, leading=14,
            textColor=MUTED, alignment=TA_CENTER, italic=True, spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "h1", fontName=_font(bold=True), fontSize=14, leading=18,
            textColor=NAVY, spaceBefore=10, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2", fontName=_font(bold=True), fontSize=11, leading=14,
            textColor=ACCENT, spaceBefore=6, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body", fontName=_font(), fontSize=9, leading=12,
            textColor=CHARCOAL, alignment=TA_LEFT,
        ),
        "muted": ParagraphStyle(
            "muted", fontName=_font(), fontSize=8, leading=10,
            textColor=MUTED, italic=True,
        ),
        "price": ParagraphStyle(
            "price", fontName=_font(bold=True), fontSize=14, leading=18,
            textColor=ACCENT, alignment=TA_RIGHT,
        ),
    }


def _build_summary_table(items: list[EstimateItem]) -> Table:
    """시술 항목 표 — 시술명 / 부위 / 설명 / 가격."""
    rows = [["시술명", "부위", "설명", "가격 범위"]]
    for it in items:
        rows.append([
            f"{it.name_ko}\n({it.name_en})",
            it.region or "-",
            it.description or "-",
            it.price_range_str(),
        ])
    tbl = Table(rows, colWidths=[4*cm, 1.8*cm, 7.2*cm, 3.5*cm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), _font(bold=True)),
        ("FONTNAME", (0, 1), (-1, -1), _font()),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("FONTNAME", (0, 1), (0, -1), _font(bold=True)),
        ("TEXTCOLOR", (0, 1), (0, -1), NAVY),
        ("TEXTCOLOR", (-1, 1), (-1, -1), ACCENT),
    ]))
    return tbl


def _build_total_table(total_min: int, total_max: int) -> Table:
    rows = [
        ["합산 견적 (최소)", f"{total_min // 10000:,} 만원"],
        ["합산 견적 (최대)", f"{total_max // 10000:,} 만원"],
        ["평균 견적", f"{(total_min + total_max) // 20000:,} 만원"],
    ]
    tbl = Table(rows, colWidths=[12*cm, 4.5*cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), _font(bold=True)),
        ("FONTNAME", (1, 0), (1, -1), _font(bold=True)),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (0, -1), CHARCOAL),
        ("TEXTCOLOR", (1, 0), (1, -1), ACCENT),
        ("FONTSIZE", (0, 2), (-1, 2), 14),
        ("BACKGROUND", (0, 2), (-1, 2), ICE),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tbl


def _build_image_comparison(item: EstimateItem, max_width_cm: float = 7.5):
    """Before/After 이미지 한 쌍을 가로 비교 테이블로."""
    cells = []
    captions = []
    for path, label in [(item.before_path, "Before"), (item.after_path, "After")]:
        if path and Path(path).exists():
            img = RLImage(str(path), width=max_width_cm*cm, height=max_width_cm*cm)
            cells.append(img)
        else:
            cells.append(Paragraph(f"<i>(이미지 없음)</i>", _make_styles()["muted"]))
        captions.append(label)

    tbl = Table([cells, captions], colWidths=[max_width_cm*cm + 0.5*cm] * 2)
    tbl.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 1), (-1, 1), _font(bold=True)),
        ("TEXTCOLOR", (0, 1), (-1, 1), NAVY),
        ("FONTSIZE", (0, 1), (-1, 1), 10),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
    ]))
    return tbl


def generate_estimate_pdf(
    items: list[EstimateItem],
    output_path: str | Path,
    patient_name: str = "익명",
    consultation_date: Optional[date] = None,
    include_images: bool = True,
    clinic_name: str = "CV-Final 가상 클리닉",
) -> Path:
    """견적서 PDF 생성.

    구조:
    - 1페이지: 표지 + 시술 요약 표 + 합산 견적
    - 2페이지~: 시술별 Before/After 큰 이미지 + 가격/설명 (시술당 1페이지)

    Args:
        items: EstimateItem 리스트.
        output_path: 출력 PDF 경로.
        patient_name: 환자 이름 (표지에 표시).
        consultation_date: 상담일 (기본 오늘).
        include_images: True면 시술별 Before/After 페이지 포함.
        clinic_name: 클리닉 이름 (표지).

    Returns:
        생성된 PDF 경로 (Path).

    Raises:
        ValueError: items가 비어있을 때.
    """
    if not items:
        raise ValueError("최소 1개 이상의 EstimateItem 필요")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    consultation_date = consultation_date or date.today()
    styles = _make_styles()

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title=f"{patient_name}님 성형 견적서",
    )
    story = []

    # ─── 1페이지: 표지 ───
    story.append(Paragraph(f"성형 시뮬레이션 견적서", styles["title"]))
    story.append(Paragraph(
        f"{clinic_name} · {consultation_date.strftime('%Y년 %m월 %d일')} · "
        f"{patient_name}님",
        styles["sub"],
    ))
    story.append(Spacer(1, 0.5*cm))

    # ─── 1페이지: 시술 요약 표 ───
    story.append(Paragraph("1. 추천 시술 항목", styles["h1"]))
    story.append(_build_summary_table(items))
    story.append(Spacer(1, 0.4*cm))

    # ─── 1페이지: 합산 견적 ───
    total_min = sum(it.price_min for it in items)
    total_max = sum(it.price_max for it in items)
    story.append(Paragraph("2. 합산 견적", styles["h1"]))
    story.append(_build_total_table(total_min, total_max))

    # ─── 2페이지~: 시술별 Before/After (각 시술 1페이지) ───
    if include_images and any(it.before_path or it.after_path for it in items):
        for idx, it in enumerate(items, start=1):
            story.append(PageBreak())
            # 시술 헤더
            story.append(Paragraph(
                f"3-{idx}. {it.name_ko} <font color='#7B8FA1' size='10'>"
                f"· {it.name_en}</font>",
                styles["h1"],
            ))
            story.append(Paragraph(
                f"<b>부위</b>: {it.region or '-'} &nbsp;&nbsp;&nbsp;"
                f"<b>가격대</b>: <font color='#F96167'>{it.price_range_str()}</font>",
                styles["body"],
            ))
            if it.description:
                story.append(Paragraph(
                    f"<b>설명</b>: {it.description}", styles["body"],
                ))
            story.append(Spacer(1, 0.4*cm))

            # Before/After 큰 이미지
            story.append(_build_image_comparison(it, max_width_cm=8.0))

            # 안내 캡션
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(
                "※ After 이미지는 SC-FEGAN GAN 기반 AI 시뮬레이션 결과이며, "
                "실제 시술 결과와 다를 수 있습니다.",
                styles["muted"],
            ))

    # ─── 마지막 페이지: 면책 푸터 ───
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph(
        "※ 본 견적은 SC-FEGAN 기반 AI 시뮬레이션으로 생성된 참고용 자료입니다. "
        "실제 시술 결과 및 가격은 의료진 상담을 통해 결정됩니다.",
        styles["muted"],
    ))
    story.append(Paragraph(
        f"© {clinic_name} · CV Final Project 2026",
        styles["muted"],
    ))

    doc.build(story)
    return output_path
