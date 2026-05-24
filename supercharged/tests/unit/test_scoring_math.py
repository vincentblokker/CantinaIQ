import math

import pytest

from cantinaiq.scoring.math import bayesian_weighted_rating, composite_score, value_score


def test_bayesian_at_zero_reviews_raises() -> None:
    with pytest.raises(ValueError):
        bayesian_weighted_rating(rating=4.5, rating_count=0, m=100, global_mean=4.0)


def test_bayesian_high_volume_dominates() -> None:
    wr = bayesian_weighted_rating(rating=4.5, rating_count=10_000, m=100, global_mean=4.0)
    assert math.isclose(wr, 4.4950495049504955, rel_tol=1e-9)


def test_bayesian_low_volume_shrinks_to_mean() -> None:
    # 1 review, large m → answer ≈ global_mean
    wr = bayesian_weighted_rating(rating=4.9, rating_count=1, m=10_000, global_mean=4.0)
    assert abs(wr - 4.0) < 0.001


def test_value_score_formula() -> None:
    vs = value_score(weighted_rating=4.0, price=10.0)
    assert math.isclose(vs, 4.0 / math.log(11), rel_tol=1e-9)


def test_value_score_rejects_zero_price() -> None:
    with pytest.raises(ValueError):
        value_score(weighted_rating=4.0, price=0)


def test_composite_score_baseline() -> None:
    s = composite_score(
        weighted_rating_norm=0.85,
        market_confidence_norm=0.50,
        value_norm=0.70,
        premium_fit_norm=0.60,
        portfolio_opportunity_norm=0.40,
        weights=(0.35, 0.20, 0.20, 0.15, 0.10),
    )
    # 0.85*.35 + 0.50*.20 + 0.70*.20 + 0.60*.15 + 0.40*.10
    # = 0.2975 + 0.10 + 0.14 + 0.09 + 0.04 = 0.6675
    assert math.isclose(s, 0.6675, rel_tol=1e-9)
