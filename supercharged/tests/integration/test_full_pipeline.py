import shutil
from pathlib import Path

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.config.models import PipelineConfig
from cantinaiq.enrichment.run import run_enrichment
from cantinaiq.export.run import run_export
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.scoring.run import run_scoring

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def cfg(
    tmp_path: Path, sample_xlsx: Path, llm_cache_fixture: Path, monkeypatch: pytest.MonkeyPatch
) -> PipelineConfig:
    monkeypatch.setenv("CANTINAIQ_DISABLE_LLM", "1")
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    for f in ("producer_aliases.csv", "macro_regions.csv", "known_producers_top50.csv"):
        shutil.copy(REPO / "data" / "reference" / f, ref / f)
    shutil.copy(llm_cache_fixture, ref / "llm_cache.parquet")
    return config_from_dict(
        {
            "cleaning": {},
            "segments": {},
            "enrichment": {
                "aliases_path": str(ref / "producer_aliases.csv"),
                "macro_regions_path": str(ref / "macro_regions.csv"),
                "known_top50_path": str(ref / "known_producers_top50.csv"),
                "llm": {"cache_path": str(ref / "llm_cache.parquet")},
            },
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
                "reference_dir": str(ref),
                "snapshots_dir": str(tmp_path / "config" / "snapshots"),
                "source_excel": str(sample_xlsx),
            },
        }
    )


def test_full_pipeline_end_to_end(cfg: PipelineConfig) -> None:
    run_id = "2026-05-16T00-00__e2e01"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    interim = Path(cfg.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    run_enrichment(cfg, run_id)
    run_scoring(cfg, run_id)
    outs = run_export(cfg, run_id)
    for p in outs.values():
        assert p.exists()
    # All 6 stage runlogs landed on disk.
    runs_dir = Path(cfg.paths.runs_dir) / run_id
    stage_logs = sorted(runs_dir.glob("stage-*.json"))
    expected_stages = {"ingestion", "cleaning", "enrichment", "scoring", "export"}
    actual_stages = {p.stem.replace("stage-", "") for p in stage_logs}
    assert expected_stages.issubset(actual_stages)
