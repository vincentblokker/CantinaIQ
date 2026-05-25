"""Anomaly detection on suspicious review patterns."""
from __future__ import annotations

import polars as pl

from cantinaiq.anomaly import flag_review_anomalies


def test_flag_review_anomalies_adds_is_anomaly_column() -> None:
    df = pl.DataFrame(
        {
            "name": [f"W{i}" for i in range(50)],
            "rating": [4.0 + (i % 5) * 0.05 for i in range(50)],
            "rating_count": [1000 + i * 100 for i in range(50)],
        }
    )
    out = flag_review_anomalies(df, contamination=0.1, seed=42)
    assert "is_anomaly" in out.columns
    assert "anomaly_score" in out.columns
    flagged = out.filter(pl.col("is_anomaly")).height
    assert 3 <= flagged <= 8


def test_extreme_rating_with_few_reviews_flagged() -> None:
    df = pl.DataFrame(
        {
            "name": ["normal"] * 100 + ["suspicious"],
            "rating": [4.0] * 100 + [4.95],
            "rating_count": [1000] * 100 + [3],
        }
    )
    out = flag_review_anomalies(df, contamination=0.05, seed=42)
    suspicious = out.filter(pl.col("name") == "suspicious")
    assert bool(suspicious["is_anomaly"][0]) is True
