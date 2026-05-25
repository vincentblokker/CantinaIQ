"""Generative reason-builder — deterministic prose for top-N producers."""
from __future__ import annotations

import pytest

from cantinaiq.reporting.reasons import build_reason


def test_hidden_gem_phrasing() -> None:
    reason = build_reason(
        producer_name="Cantine Due Palme",
        market_segment="Hidden Gem",
        weighted_rating=4.18,
        avg_price=14.0,
        total_reviews=1247,
        composite_score=0.82,
        value_score=2.1,
    )
    assert "Hidden Gem" in reason
    assert "4.18" in reason
    assert "1.247" in reason or "1247" in reason
    assert "€14" in reason


def test_premium_icon_phrasing() -> None:
    reason = build_reason(
        producer_name="Tenuta San Guido",
        market_segment="Premium Icon",
        weighted_rating=4.62,
        avg_price=534.0,
        total_reviews=307787,
        composite_score=0.95,
        value_score=0.7,
    )
    assert "Premium Icon" in reason
    assert "€534" in reason


def test_low_confidence_phrasing() -> None:
    reason = build_reason(
        producer_name="Obscure Cantina",
        market_segment="Low Confidence Niche",
        weighted_rating=4.4,
        avg_price=22.0,
        total_reviews=14,
        composite_score=0.4,
        value_score=1.9,
    )
    lowered = reason.lower()
    assert "few reviews" in lowered or "low review" in lowered or "too few" in lowered


@pytest.mark.parametrize(
    "seg",
    [
        "Hidden Gem",
        "Premium Icon",
        "Commercial Value",
        "Overpriced Risk",
        "Low Confidence Niche",
    ],
)
def test_all_segments_produce_non_empty_reason(seg: str) -> None:
    out = build_reason("X", seg, 4.0, 50.0, 500, 0.5, 1.0)
    assert len(out) >= 20
    assert len(out) <= 280
