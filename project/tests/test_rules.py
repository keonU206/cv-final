"""recommender.rules 단위 테스트.

외부 의존(mediapipe/opencv) 없이 dict와 yaml만 사용해서 추천 로직을 검증.
"""
from pathlib import Path

import pytest

from project.recommender.rules import (
    Recommendation,
    load_procedures,
    recommend,
)

PROCS_YAML = Path(__file__).parents[1] / "recommender" / "procedures.yaml"


def test_load_procedures():
    procs = load_procedures(PROCS_YAML)
    assert len(procs) == 3
    ids = {p["id"] for p in procs}
    assert ids == {"nose_tip", "double_eyelid", "jaw_v_line"}
    for p in procs:
        assert "mask_landmarks" in p and len(p["mask_landmarks"]) >= 3
        assert "trigger" in p
        assert p["price_krw_min"] < p["price_krw_max"]


def test_recommend_triggers_when_thresholds_crossed():
    procs = load_procedures(PROCS_YAML)
    ratios = {
        "nose_tip_droop": 0.05,
        "eyelid_height_ratio": 0.10,
        "jaw_angle_deg": 125.0,
    }
    recs = recommend(ratios, procs)
    assert len(recs) == 3
    assert all(isinstance(r, Recommendation) for r in recs)
    assert all(0.0 <= r.confidence <= 1.0 for r in recs)
    assert recs == sorted(recs, key=lambda r: -r.confidence)


def test_recommend_skips_when_thresholds_not_met():
    procs = load_procedures(PROCS_YAML)
    ratios = {
        "nose_tip_droop": -0.1,
        "eyelid_height_ratio": 0.5,
        "jaw_angle_deg": 90.0,
    }
    recs = recommend(ratios, procs)
    assert len(recs) == 0


def test_recommend_partial_triggers():
    procs = load_procedures(PROCS_YAML)
    ratios = {
        "nose_tip_droop": 0.05,
        "eyelid_height_ratio": 0.5,
        "jaw_angle_deg": 90.0,
    }
    recs = recommend(ratios, procs)
    assert len(recs) == 1
    assert recs[0].id == "nose_tip"


def test_recommend_handles_missing_metric():
    procs = load_procedures(PROCS_YAML)
    ratios = {"nose_tip_droop": 0.05}
    recs = recommend(ratios, procs)
    assert len(recs) == 1
    assert recs[0].id == "nose_tip"
