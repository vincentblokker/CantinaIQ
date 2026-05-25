"""Deterministic prose generator for top-N producer recommendations.

The output is a single sentence (<=280 chars) that combines the producer's
market segment, weighted rating, price band, and review confidence into a
human-readable rationale. No LLM is used — the function is pure and the
output is reproducible from the scoring run alone.
"""

from __future__ import annotations

SEGMENT_OPENERS: dict[str, str] = {
    "Hidden Gem": "Hidden Gem in the value tier",
    "Premium Icon": "Premium Icon at the top of the prestige tier",
    "Commercial Value": "Commercial Value — solid market signal at a scalable price",
    "Overpriced Risk": "Overpriced Risk — price runs ahead of consumer signal",
    "Low Confidence Niche": "Low Confidence Niche — interesting but thinly reviewed",
}


def _format_reviews(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _format_price(eur: float) -> str:
    return f"€{int(round(eur))}"


def build_reason(
    producer_name: str,
    market_segment: str,
    weighted_rating: float,
    avg_price: float,
    total_reviews: int,
    composite_score: float,
    value_score: float,
) -> str:
    """Return a single-sentence reason for the producer's recommendation."""
    opener = SEGMENT_OPENERS.get(market_segment, market_segment)
    rating_str = f"{weighted_rating:.2f}"
    reviews_str = _format_reviews(total_reviews)
    price_str = _format_price(avg_price)

    if market_segment == "Low Confidence Niche":
        return (
            f"{opener}: weighted rating {rating_str} on only {reviews_str} reviews "
            f"at {price_str} — too few reviews to commit; worth a tasting before dismissing."
        )
    if market_segment == "Hidden Gem":
        return (
            f"{opener}: weighted rating {rating_str} on {reviews_str} reviews "
            f"for {price_str} avg — above-median quality below the median price band."
        )
    if market_segment == "Premium Icon":
        return (
            f"{opener}: weighted rating {rating_str} on {reviews_str} reviews "
            f"at {price_str} — defensible anchor for Slurpini's premium positioning."
        )
    if market_segment == "Overpriced Risk":
        return (
            f"{opener}: rating {rating_str} on {reviews_str} reviews at {price_str} — "
            f"value score {value_score:.2f} suggests price outruns consumer signal."
        )
    return (
        f"{opener}: weighted rating {rating_str} on {reviews_str} reviews at {price_str} "
        f"— composite score {composite_score:.2f}."
    )
