"""Gold-set evaluation: precision/recall of producer extraction vs known_producers_top50."""
from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from cantinaiq.evaluation.gold_set import (
    GoldSetEval,
    evaluate_producer_extraction,
    recall_at_alias,
)


@pytest.fixture
def gold_csv(tmp_path: Path) -> Path:
    p = tmp_path / "gold.csv"
    p.write_text(
        "canonical_name,macro_region\n"
        "Tenuta San Guido,Toscana\n"
        "Gaja,Piemonte\n"
        "Biondi-Santi,Toscana\n"
        "Marchesi Antinori,Toscana\n"
        "Castello di Ama,Toscana\n"
    )
    return p


@pytest.fixture
def producers(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "producer_name": [
                "Tenuta San Guido",
                "Gaja",
                "Antinori",
                "Random Cantina",
                "Castello di Ama",
            ],
            "composite_score": [0.5, 0.4, 0.6, 0.2, 0.3],
        }
    )
    p = tmp_path / "producers.parquet"
    df.write_parquet(p)
    return p


def test_recall_at_alias_exact_match(producers: Path, gold_csv: Path) -> None:
    recall = recall_at_alias(producers, gold_csv, match="exact")
    assert recall == pytest.approx(3 / 5, rel=1e-3)


def test_recall_at_alias_fuzzy(producers: Path, gold_csv: Path) -> None:
    recall = recall_at_alias(producers, gold_csv, match="contains")
    assert recall == pytest.approx(4 / 5, rel=1e-3)


def test_evaluate_producer_extraction_returns_full_eval(
    producers: Path, gold_csv: Path
) -> None:
    ev = evaluate_producer_extraction(producers, gold_csv)
    assert isinstance(ev, GoldSetEval)
    assert ev.gold_size == 5
    assert ev.producers_total == 5
    assert ev.recall_exact == pytest.approx(0.6)
    assert ev.recall_contains == pytest.approx(0.8)
    assert "Biondi-Santi" in ev.missed
