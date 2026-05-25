"""Run comparison — diff scored parquets between two config hashes."""
from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from cantinaiq.compare import (
    RunComparison,
    compare_runs,
    diff_producer_rankings,
    diff_segment_movements,
)


@pytest.fixture
def producers_a(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "producer_name": ["A", "B", "C", "D"],
            "composite_score": [0.9, 0.8, 0.7, 0.6],
            "market_segment": [
                "Premium Icon",
                "Hidden Gem",
                "Commercial Value",
                "Low Confidence Niche",
            ],
            "recommendation": [
                "Premium Brand Builder",
                "Value Opportunity",
                "Monitor",
                "Monitor",
            ],
        }
    )
    p = tmp_path / "a.parquet"
    df.write_parquet(p)
    return p


@pytest.fixture
def producers_b(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "producer_name": ["A", "B", "C", "D"],
            "composite_score": [0.92, 0.6, 0.75, 0.85],
            "market_segment": [
                "Premium Icon",
                "Low Confidence Niche",
                "Commercial Value",
                "Hidden Gem",
            ],
            "recommendation": [
                "Premium Brand Builder",
                "Monitor",
                "Monitor",
                "Value Opportunity",
            ],
        }
    )
    p = tmp_path / "b.parquet"
    df.write_parquet(p)
    return p


def test_diff_producer_rankings_returns_rank_shifts(
    producers_a: Path, producers_b: Path
) -> None:
    shifts = diff_producer_rankings(producers_a, producers_b)
    by_name = {row["producer_name"]: row for row in shifts}
    assert by_name["A"]["rank_a"] == 1
    assert by_name["A"]["rank_b"] == 1
    assert by_name["D"]["rank_a"] == 4
    assert by_name["D"]["rank_b"] == 2  # D climbed
    assert by_name["B"]["rank_a"] == 2
    assert by_name["B"]["rank_b"] == 4  # B fell


def test_diff_segment_movements(producers_a: Path, producers_b: Path) -> None:
    moves = diff_segment_movements(producers_a, producers_b)
    by_name = {m["producer_name"]: m for m in moves}
    assert by_name["B"]["segment_a"] == "Hidden Gem"
    assert by_name["B"]["segment_b"] == "Low Confidence Niche"
    assert by_name["D"]["segment_a"] == "Low Confidence Niche"
    assert by_name["D"]["segment_b"] == "Hidden Gem"


def test_compare_runs_returns_full_comparison(producers_a: Path, producers_b: Path) -> None:
    comp = compare_runs(producers_a, producers_b, hash_a="aaa", hash_b="bbb")
    assert isinstance(comp, RunComparison)
    assert comp.hash_a == "aaa"
    assert comp.hash_b == "bbb"
    assert len(comp.ranking_shifts) == 4
    assert any(m["producer_name"] == "B" for m in comp.segment_movements)
