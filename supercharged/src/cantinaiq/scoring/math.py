"""Pure scoring functions — no Polars I/O. Targets of Hypothesis property tests."""

from __future__ import annotations

import math


def bayesian_weighted_rating(rating: float, rating_count: int, m: int, global_mean: float) -> float:
    """Shrink an observed rating toward `global_mean` in proportion to how few
    reviews back it. Convex combination of (rating, global_mean) with weight
    `n / (n + m)` on the observed rating."""
    if rating_count < 1:
        raise ValueError(f"rating_count must be >= 1, got {rating_count}")
    n = rating_count
    return (n / (n + m)) * rating + (m / (n + m)) * global_mean


def value_score(weighted_rating: float, price: float) -> float:
    """Quality-per-euro proxy: weighted_rating / log(price + 1).

    Monotone decreasing in price, monotone increasing in weighted_rating.
    """
    if price <= 0:
        raise ValueError(f"price must be > 0, got {price}")
    return weighted_rating / math.log(price + 1)


def composite_score(
    weighted_rating_norm: float,
    market_confidence_norm: float,
    value_norm: float,
    premium_fit_norm: float,
    portfolio_opportunity_norm: float,
    weights: tuple[float, float, float, float, float],
) -> float:
    """Weighted linear combination of five normalised [0, 1] sub-scores."""
    w1, w2, w3, w4, w5 = weights
    return (
        weighted_rating_norm * w1
        + market_confidence_norm * w2
        + value_norm * w3
        + premium_fit_norm * w4
        + portfolio_opportunity_norm * w5
    )
