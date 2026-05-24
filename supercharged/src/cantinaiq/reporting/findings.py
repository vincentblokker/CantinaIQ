"""Context-builder for the findings-one-pager template."""

from __future__ import annotations

import math
from typing import Any

import polars as pl

PILL_BY_RECOMMENDATION: dict[str, dict[str, str]] = {
    "Premium Brand Builder": {
        "stroke": "#5B3A8C",
        "fill": "rgba(91,58,140,0.10)",
        "dot": "#5B3A8C",
        "abbr": "Brand Builder",
    },
    "Target": {
        "stroke": "#1F3A5F",
        "fill": "rgba(31,58,95,0.10)",
        "dot": "#1F3A5F",
        "abbr": "Target",
    },
    "Value Opportunity": {
        "stroke": "#4A6B36",
        "fill": "rgba(107,142,78,0.14)",
        "dot": "#6B8E4E",
        "abbr": "Value Opp.",
    },
    "Monitor": {
        "stroke": "#6B6258",
        "fill": "rgba(107,98,88,0.08)",
        "dot": "#6B6258",
        "abbr": "Monitor",
    },
    "Avoid for Now": {
        "stroke": "#7B2A22",
        "fill": "rgba(155,58,47,0.10)",
        "dot": "#9B3A2F",
        "abbr": "Avoid",
    },
}

SEGMENT_FILL: dict[str, str] = {
    "Hidden Gem": "#6B8E4E",
    "Premium Icon": "#1F3A5F",
    "Commercial Value": "#8B7355",
    "Overpriced Risk": "#9B3A2F",
    "Low Confidence Niche": "#8B7355",
}


def _project_x(price: float) -> float:
    return 60.0 + (math.log10(max(price, 1.0)) - 1.0) / (math.log10(320.0) - 1.0) * 500.0


def _project_y(rating: float) -> float:
    return 280.0 - (rating - 3.0) / (4.7 - 3.0) * 260.0


def _bubble_radius(reviews: int) -> float:
    # area ∝ reviews; r ∝ sqrt(reviews); calibrated so 5000 reviews → r ≈ 13
    return min(max(math.sqrt(max(reviews, 1)) * 0.18, 3.0), 14.0)


def build_findings_context(
    producers_scored: pl.DataFrame,
    wines_scored: pl.DataFrame,
    price_split: float,
    rating_split: float,
    reasons: dict[str, str],
    findings_copy: dict[str, Any],
) -> dict[str, Any]:
    top5 = producers_scored.sort("composite_score", descending=True).head(5).to_dicts()
    top_producers: list[dict[str, Any]] = []
    for i, p in enumerate(top5, start=1):
        pill = PILL_BY_RECOMMENDATION.get(p["recommendation"], PILL_BY_RECOMMENDATION["Monitor"])
        top_producers.append(
            {
                "rank": i,
                "producer_name": p["producer_name"],
                "region_label": p["macro_region"],
                "recommendation": pill["abbr"],
                "weighted_rating": p["weighted_rating"],
                "avg_price": p["avg_price"],
                "reason": reasons.get(p["producer_name"], ""),
                "pill_stroke": pill["stroke"],
                "pill_fill": pill["fill"],
                "pill_dot": pill["dot"],
            }
        )

    bubbles: list[dict[str, Any]] = []
    for row in producers_scored.to_dicts():
        fill = SEGMENT_FILL.get(row["market_segment"], "#8B7355")
        bubbles.append(
            {
                "cx": _project_x(row["avg_price"]),
                "cy": _project_y(row["weighted_rating"]),
                "r": _bubble_radius(row["total_reviews"]),
                "fill": fill,
                "stroke_color": fill,
                "stroke_width": 0.6,
            }
        )

    callouts: list[dict[str, Any]] = []
    for p in top5[:3]:
        cx = _project_x(p["avg_price"])
        cy = _project_y(p["weighted_rating"])
        callouts.append(
            {
                "label": p["producer_name"],
                "x": cx + 8,
                "y": cy - 16,
                "line_x1": cx,
                "line_y1": cy,
                "line_x2": cx + 6,
                "line_y2": cy - 14,
            }
        )

    return {
        "top_producers": top_producers,
        "matrix": {
            "split": {"price_eur": price_split, "rating": rating_split},
            "bubbles": bubbles,
            "callouts": callouts,
            "totals": {"producers": producers_scored.height, "wines": wines_scored.height},
        },
        "findings": findings_copy,
    }
