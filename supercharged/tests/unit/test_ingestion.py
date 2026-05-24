from pathlib import Path

import polars as pl
import pytest

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


def test_ingestion_reads_all_sheets(cfg: PipelineConfig) -> None:
    out = run_ingestion(cfg, run_id="2026-05-16T00-00__test01")
    assert out.exists()
    df = pl.read_parquet(out)
    assert df.height == 50
    assert "source_sheet" in df.columns
    assert set(df["source_sheet"].unique()) == {
        "Italy",
        "France",
        "Spain",
        "Argentina",
        "Portugal",
        "USA",
    }
    assert df["run_config_hash"].unique().to_list() == [cfg.hash]
