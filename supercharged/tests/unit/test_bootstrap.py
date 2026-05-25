"""Bootstrap rank stability — resample the wine dataset, re-aggregate to producers, measure CIs."""
from __future__ import annotations

import polars as pl

from cantinaiq.bootstrap import bootstrap_producer_rank_ci


def test_bootstrap_identical_data_gives_tight_ci() -> None:
    """When data is well-separated, top producers' rank CIs collapse."""
    wines = pl.DataFrame(
        {
            "producer_name": ["A"] * 100 + ["B"] * 100 + ["C"] * 100,
            "weighted_rating": [4.8] * 100 + [4.5] * 100 + [4.2] * 100,
            "rating_count": [5000] * 100 + [3000] * 100 + [1000] * 100,
            "price": [50.0] * 100 + [50.0] * 100 + [50.0] * 100,
        }
    )
    cis = bootstrap_producer_rank_ci(wines, n_bootstraps=50, top_n=3, seed=42)
    by_name = {c["producer_name"]: c for c in cis}
    assert by_name["A"]["rank_p50"] == 1
    assert by_name["A"]["rank_p95"] <= 2
    assert by_name["C"]["rank_p50"] == 3


def test_bootstrap_returns_top_n_only() -> None:
    wines = pl.DataFrame(
        {
            "producer_name": [chr(65 + i // 10) for i in range(60)],
            "weighted_rating": [4.0 + i / 100 for i in range(60)],
            "rating_count": [100] * 60,
            "price": [20.0] * 60,
        }
    )
    cis = bootstrap_producer_rank_ci(wines, n_bootstraps=30, top_n=5, seed=0)
    assert len(cis) == 5
    assert all("rank_p50" in c for c in cis)
    assert all("rank_p05" in c and "rank_p95" in c for c in cis)
