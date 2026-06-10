"""룰베이스 추천 엔진.

procedures.yaml의 trigger 임계값과 ratios dict를 비교해 추천 리스트를 생성한다.
"""
from __future__ import annotations

import operator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_OPS = {
    "gt": operator.gt,
    "ge": operator.ge,
    "lt": operator.lt,
    "le": operator.le,
    "eq": operator.eq,
}


@dataclass
class Recommendation:
    """추천 결과 1건."""

    id: str
    name_ko: str
    region: str
    confidence: float  # 0.0 ~ 1.0
    price_krw_min: int
    price_krw_max: int
    reasoning: str
    procedure: dict[str, Any]  # 원본 procedure dict (mask_landmarks 등 사용)


def load_procedures(yaml_path: str | Path) -> list[dict[str, Any]]:
    """procedures.yaml을 로드."""
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"procedures.yaml not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("procedures.yaml은 시술 리스트여야 합니다.")
    return data


def _compute_confidence(value: float, threshold: float, op_name: str) -> float:
    """임계값을 얼마나 넘었는지에 비례한 신뢰도 (0 ~ 1)."""
    if op_name in ("gt", "ge"):
        delta = value - threshold
    else:
        delta = threshold - value
    if delta <= 0:
        return 0.0
    norm = abs(threshold) + 1e-3
    return float(min(1.0, delta / norm))


def recommend(
    ratios: dict[str, float],
    procedures: list[dict[str, Any]],
) -> list[Recommendation]:
    """ratios를 기반으로 시술 추천 리스트를 신뢰도 내림차순으로 반환."""
    out: list[Recommendation] = []
    for p in procedures:
        trig = p["trigger"]
        metric_name = trig["metric"]
        op_name = trig["op"]
        threshold = float(trig["threshold"])

        if metric_name not in ratios:
            continue

        value = float(ratios[metric_name])
        op_fn = _OPS[op_name]
        if not op_fn(value, threshold):
            continue

        confidence = _compute_confidence(value, threshold, op_name)
        reasoning = (
            f"{metric_name}={value:.3f} "
            f"({op_name} {threshold}) → {p['description']}"
        )
        out.append(
            Recommendation(
                id=p["id"],
                name_ko=p["name_ko"],
                region=p["region"],
                confidence=confidence,
                price_krw_min=int(p["price_krw_min"]),
                price_krw_max=int(p["price_krw_max"]),
                reasoning=reasoning,
                procedure=p,
            )
        )

    out.sort(key=lambda r: -r.confidence)
    return out
