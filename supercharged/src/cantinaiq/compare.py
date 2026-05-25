"""Compare two CantinaIQ runs — ranking shifts, segment movements."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl


@dataclass(frozen=True)
class RunComparison:
    hash_a: str
    hash_b: str
    ranking_shifts: list[dict[str, Any]]
    segment_movements: list[dict[str, Any]]


def diff_producer_rankings(parquet_a: Path, parquet_b: Path) -> list[dict[str, Any]]:
    """Return per-producer rank shifts (rank_a → rank_b) as a list of dicts."""
    a = (
        pl.read_parquet(parquet_a)
        .sort("composite_score", descending=True)
        .with_row_index(name="rank_a", offset=1)
        .select(["producer_name", "rank_a", "composite_score"])
        .rename({"composite_score": "score_a"})
    )
    b = (
        pl.read_parquet(parquet_b)
        .sort("composite_score", descending=True)
        .with_row_index(name="rank_b", offset=1)
        .select(["producer_name", "rank_b", "composite_score"])
        .rename({"composite_score": "score_b"})
    )
    joined = a.join(b, on="producer_name", how="full", coalesce=True)
    joined = joined.with_columns(
        (pl.col("rank_a").cast(pl.Int64) - pl.col("rank_b").cast(pl.Int64)).alias("shift"),
    )
    return joined.to_dicts()


def diff_segment_movements(parquet_a: Path, parquet_b: Path) -> list[dict[str, Any]]:
    """Return rows where market_segment changed between runs."""
    a = (
        pl.read_parquet(parquet_a)
        .select(["producer_name", "market_segment", "recommendation"])
        .rename({"market_segment": "segment_a", "recommendation": "rec_a"})
    )
    b = (
        pl.read_parquet(parquet_b)
        .select(["producer_name", "market_segment", "recommendation"])
        .rename({"market_segment": "segment_b", "recommendation": "rec_b"})
    )
    joined = a.join(b, on="producer_name", how="inner")
    moved = joined.filter(pl.col("segment_a") != pl.col("segment_b"))
    return moved.to_dicts()


def compare_runs(
    parquet_a: Path,
    parquet_b: Path,
    hash_a: str,
    hash_b: str,
) -> RunComparison:
    return RunComparison(
        hash_a=hash_a,
        hash_b=hash_b,
        ranking_shifts=diff_producer_rankings(parquet_a, parquet_b),
        segment_movements=diff_segment_movements(parquet_a, parquet_b),
    )
