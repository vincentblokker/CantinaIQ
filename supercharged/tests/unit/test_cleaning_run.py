from pathlib import Path

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.config.models import PipelineConfig
from cantinaiq.ingestion.run import run_ingestion


@pytest.fixture
def cfg(tmp_path: Path, sample_xlsx: Path) -> PipelineConfig:
    return config_from_dict(
        {
            "cleaning": {},
            "enrichment": {},
            "segments": {},
            "scoring": {
                "bayesian_m": 100,
                "weights": {
                    "weighted_rating": 0.35,
                    "market_confidence": 0.20,
                    "value_for_money": 0.20,
                    "premium_fit": 0.15,
                    "portfolio_opportunity": 0.10,
                },
            },
            "paths": {
                "raw_dir": str(tmp_path / "data" / "raw"),
                "interim_dir": str(tmp_path / "data" / "interim"),
                "processed_dir": str(tmp_path / "data" / "processed"),
                "exports_dir": str(tmp_path / "data" / "exports"),
                "runs_dir": str(tmp_path / "data" / "runs"),
                "reference_dir": str(tmp_path / "data" / "reference"),
                "snapshots_dir": str(tmp_path / "config" / "snapshots"),
                "source_excel": str(sample_xlsx),
            },
        }
    )


def test_cleaning_filters_non_italian_and_dedupes(cfg: PipelineConfig) -> None:
    run_id = "2026-05-16T00-00__clean01"
    run_ingestion(cfg, run_id)
    out = run_cleaning(cfg, run_id)
    df = pl.read_parquet(out)
    # Every surviving row is Italy.
    assert df["country"].unique().to_list() == ["Italy"]
    # Tuple-string and IT-filter combine to leave only Italian rows.
    # 50 rows total: 5 non-Italian filtered, 2 duplicate-collapses,
    # surviving rows have the helper columns added.
    assert df.height < 45
    assert {"wine_name_normalised", "vintage", "producer_hint", "source_sheet"}.issubset(
        set(df.columns)
    )
    # The 3 tuple-encoded "('Italy',)" rows survived as proper Italy.
    assert df.filter(pl.col("wine_name").str.contains("Dirty Tuple")).height == 3
    # Duplicates collapsed: each of the 2 dup-pairs becomes 1 row.
    assert df.filter(pl.col("wine_name").str.contains("Frescobaldi Nipozzano")).height == 1
    assert df.filter(pl.col("wine_name").str.contains("Bruno Giacosa")).height == 1


def test_cleaning_writes_runlog(cfg: PipelineConfig) -> None:
    run_id = "2026-05-16T00-00__clean02"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    log = Path(cfg.paths.runs_dir) / run_id / "stage-cleaning.json"
    assert log.exists()
