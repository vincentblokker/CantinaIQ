"""Vivino-vs-Italian-Trade bias quantification."""
from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from cantinaiq.bias import BiasReport, compute_bias_report


@pytest.fixture
def baseline_csv(tmp_path: Path) -> Path:
    p = tmp_path / "baseline.csv"
    p.write_text(
        "macro_region,share_nl_imports_pct,notes\n"
        "Toscana,30.0,\n"
        "Veneto,20.0,\n"
        "Piemonte,15.0,\n"
        "Puglia,10.0,\n"
        "Other,25.0,\n"
    )
    return p


@pytest.fixture
def wines(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "macro_region": (
                ["Toscana"] * 60
                + ["Veneto"] * 20
                + ["Piemonte"] * 10
                + ["Puglia"] * 5
                + ["Sicilia"] * 5
            ),
        }
    )
    p = tmp_path / "wines.parquet"
    df.write_parquet(p)
    return p


def test_compute_bias_report_returns_per_region_deltas(
    wines: Path, baseline_csv: Path
) -> None:
    report = compute_bias_report(wines, baseline_csv)
    assert isinstance(report, BiasReport)
    rows = {r["macro_region"]: r for r in report.rows}

    assert rows["Toscana"]["vivino_share_pct"] == pytest.approx(60.0)
    assert rows["Toscana"]["baseline_share_pct"] == pytest.approx(30.0)
    assert rows["Toscana"]["over_under"] > 1.5

    assert rows["Puglia"]["over_under"] < 0.8
