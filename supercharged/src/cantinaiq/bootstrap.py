"""Bootstrap resampling for producer-ranking confidence intervals.

For each of `n_bootstraps` iterations:
  1. Resample the wine dataset with replacement.
  2. Group by producer_name and compute aggregate (mean weighted_rating
     weighted by rating_count).
  3. Rank producers descending by that aggregate.
  4. Record each top-N producer's rank.

After N iterations, compute the 5th, 50th, 95th percentile rank per producer.
Producers that fail to appear in a bootstrap iteration receive a sentinel
rank of `top_n + 1` for that iteration — this is the standard treatment
and yields wider, more honest CIs for low-volume producers.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import polars as pl


def _aggregate_to_producers(wines: pl.DataFrame) -> pl.DataFrame:
    """Producer-level weighted aggregate. Mirrors the scoring stage at small scale."""
    return (
        wines.with_columns(
            (pl.col("weighted_rating") * pl.col("rating_count")).alias("_num"),
            pl.col("rating_count").alias("_den"),
        )
        .group_by("producer_name")
        .agg(
            (pl.col("_num").sum() / pl.col("_den").sum()).alias("weighted_rating"),
            pl.col("rating_count").sum().alias("total_reviews"),
        )
    )


def bootstrap_producer_rank_ci(
    wines: pl.DataFrame,
    n_bootstraps: int = 1000,
    top_n: int = 20,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Return per-producer rank CIs for the top-N producers from the baseline ranking."""
    rng = np.random.default_rng(seed)

    baseline = (
        _aggregate_to_producers(wines)
        .sort("weighted_rating", descending=True)
        .head(top_n)
    )
    top_names = baseline["producer_name"].to_list()
    name_to_ranks: dict[str, list[int]] = {n: [] for n in top_names}

    for _ in range(n_bootstraps):
        idx = rng.integers(0, wines.height, size=wines.height)
        sample = wines[idx.tolist()]
        ranked = (
            _aggregate_to_producers(sample)
            .sort("weighted_rating", descending=True)
            .with_row_index(name="rank", offset=1)
            .select(["producer_name", "rank"])
        )
        rank_map = dict(
            zip(ranked["producer_name"].to_list(), ranked["rank"].to_list(), strict=False)
        )
        for n in top_names:
            name_to_ranks[n].append(int(rank_map.get(n, top_n + 1)))

    out: list[dict[str, Any]] = []
    for n in top_names:
        ranks = np.array(name_to_ranks[n])
        out.append(
            {
                "producer_name": n,
                "rank_p05": int(np.percentile(ranks, 5)),
                "rank_p50": int(np.percentile(ranks, 50)),
                "rank_p95": int(np.percentile(ranks, 95)),
                "rank_mean": float(ranks.mean()),
                "appearances": int((ranks <= top_n).sum()),
                "n_bootstraps": n_bootstraps,
            }
        )
    return out
