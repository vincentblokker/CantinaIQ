import pytest
from pydantic import ValidationError

from cantinaiq.config.models import (
    CleaningConfig,
    ConfidenceSegments,
    EnrichmentConfig,
    PathsConfig,
    PipelineConfig,
    PriceSegments,
    ScoringConfig,
    ScoringWeights,
    SegmentsConfig,
)


def _valid_weights() -> ScoringWeights:
    return ScoringWeights(
        weighted_rating=0.35,
        market_confidence=0.20,
        value_for_money=0.20,
        premium_fit=0.15,
        portfolio_opportunity=0.10,
    )


def test_scoring_weights_must_sum_to_one() -> None:
    with pytest.raises(ValidationError) as exc:
        ScoringWeights(
            weighted_rating=0.5,
            market_confidence=0.2,
            value_for_money=0.2,
            premium_fit=0.2,
            portfolio_opportunity=0.2,
        )
    assert "sum to 1.0" in str(exc.value)


def test_scoring_weights_valid_baseline() -> None:
    w = _valid_weights()
    assert w.weighted_rating == 0.35


def test_scoring_config_requires_positive_m() -> None:
    with pytest.raises(ValidationError):
        ScoringConfig(bayesian_m=0, weights=_valid_weights())


def test_price_segments_ordering() -> None:
    seg = PriceSegments(entry_max=15, accessible_premium_max=30, premium_max=75)
    assert seg.entry_max < seg.accessible_premium_max < seg.premium_max


def test_confidence_segments_defaults() -> None:
    cs = ConfidenceSegments()
    assert cs.low_max < cs.emerging_max < cs.reliable_max


def test_pipeline_config_constructs() -> None:
    cfg = PipelineConfig(
        cleaning=CleaningConfig(),
        enrichment=EnrichmentConfig(),
        scoring=ScoringConfig(bayesian_m=100, weights=_valid_weights()),
        segments=SegmentsConfig(),
        paths=PathsConfig(),
    )
    assert cfg.scoring.bayesian_m == 100
