"""project.report.pdf_generator 단위 테스트.

reportlab + Windows 한글 폰트 sanity check.
"""
from pathlib import Path

import pytest

reportlab = pytest.importorskip("reportlab")

from project.report.pdf_generator import (
    EstimateItem,
    build_estimate,
    generate_estimate_pdf,
    load_procedure_catalog,
)


def test_load_procedure_catalog_returns_dict():
    catalog = load_procedure_catalog()
    assert isinstance(catalog, dict)
    assert "nose_tip" in catalog
    assert "double_eyelid" in catalog


def test_build_estimate_single():
    items = build_estimate(["nose_tip"])
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, EstimateItem)
    assert item.procedure_id == "nose_tip"
    assert item.price_min > 0
    assert item.price_max >= item.price_min
    assert item.name_ko  # 한글 이름 존재


def test_build_estimate_multiple():
    items = build_estimate(["nose_tip", "double_eyelid", "jaw_v_line"])
    assert len(items) == 3


def test_build_estimate_unknown_raises():
    with pytest.raises(ValueError):
        build_estimate(["ghost_procedure_xyz"])


def test_estimate_item_price_helpers():
    item = EstimateItem(
        procedure_id="t", name_ko="t", name_en="t",
        price_min=1_000_000, price_max=3_000_000,
    )
    assert item.price_avg == 2_000_000
    assert "100" in item.price_range_str()
    assert "300" in item.price_range_str()
    assert "만원" in item.price_range_str()


def test_generate_pdf_minimal(tmp_path):
    """이미지 없이 최소 PDF 생성."""
    items = build_estimate(["nose_tip"])
    out = tmp_path / "test.pdf"
    result = generate_estimate_pdf(
        items, out, patient_name="테스트환자",
        include_images=False,
    )
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 1000  # 최소 1KB는 되어야 함


def test_generate_pdf_multiple_items(tmp_path):
    items = build_estimate(["nose_tip", "double_eyelid"])
    out = tmp_path / "multi.pdf"
    generate_estimate_pdf(items, out, include_images=False)
    assert out.exists()


def test_generate_pdf_empty_raises(tmp_path):
    with pytest.raises(ValueError):
        generate_estimate_pdf([], tmp_path / "empty.pdf")


def test_generate_pdf_with_dummy_images(tmp_path):
    """가짜 이미지 파일을 만들어서 image 포함 PDF 생성."""
    import numpy as np
    import cv2

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    before = img_dir / "before.jpg"
    after = img_dir / "after.jpg"
    arr = np.full((200, 200, 3), [200, 180, 160], dtype=np.uint8)
    cv2.imwrite(str(before), arr)
    cv2.imwrite(str(after), arr)

    items = build_estimate(
        ["nose_tip"],
        before_paths={"nose_tip": before},
        after_paths={"nose_tip": after},
    )
    out = tmp_path / "with_images.pdf"
    generate_estimate_pdf(items, out, include_images=True)
    assert out.exists()
    assert out.stat().st_size > 5000  # 이미지 포함 → 더 큼
