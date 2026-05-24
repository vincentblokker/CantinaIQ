from pathlib import Path
from typing import Any

import polars as pl

from cantinaiq.enrichment.producer.validate import (
    coverage_warnings,
    distribution_overlap_warning,
    multi_producer_per_wine_warning,
)

KNOWN = Path("data/reference/known_producers_top50.csv")


def _df(rows: list[dict[str, Any]]) -> pl.DataFrame:
    return pl.DataFrame(rows)


def test_distribution_overlap_warning_below_threshold() -> None:
    df = _df(
        [
            {"producer_name": "UnknownA", "macro_region": "Toscana"},
            {"producer_name": "UnknownB", "macro_region": "Toscana"},
            {"producer_name": "UnknownC", "macro_region": "Toscana"},
        ]
    )
    warning = distribution_overlap_warning(df, known_top50_path=KNOWN, threshold=0.6)
    assert warning is not None
    assert warning["overlap"] < 0.6


def test_multi_producer_per_wine_warning() -> None:
    df = _df(
        [
            {"wine_name_normalised": "tignanello 2019", "producer_name": "Antinori"},
            {"wine_name_normalised": "tignanello 2019", "producer_name": "Marchesi Antinori"},
            {"wine_name_normalised": "sassicaia 2018", "producer_name": "Tenuta San Guido"},
        ]
    )
    w = multi_producer_per_wine_warning(df)
    assert w is not None
    assert w["inconsistent_count"] == 1


def test_coverage_warnings_below_target() -> None:
    df = _df(
        [
            {"enrichment_confidence": "High", "macro_region": "Toscana"},
            {"enrichment_confidence": "None", "macro_region": "Toscana"},
            {"enrichment_confidence": "None", "macro_region": "Toscana"},
            {"enrichment_confidence": "High", "macro_region": "Piemonte"},
        ]
    )
    warnings = coverage_warnings(df, target_overall=0.80, target_per_region=0.70)
    assert warnings["overall_below_target"] is True
    assert "Toscana" in warnings["regions_below_target"]
    assert "Piemonte" not in warnings["regions_below_target"]


def test_coverage_warnings_above_target() -> None:
    df = _df(
        [
            {"enrichment_confidence": "High", "macro_region": "Toscana"},
            {"enrichment_confidence": "Medium", "macro_region": "Toscana"},
            {"enrichment_confidence": "High", "macro_region": "Piemonte"},
            {"enrichment_confidence": "High", "macro_region": "Piemonte"},
        ]
    )
    warnings = coverage_warnings(df, target_overall=0.80, target_per_region=0.70)
    assert warnings["overall_below_target"] is False
    assert warnings["regions_below_target"] == {}
