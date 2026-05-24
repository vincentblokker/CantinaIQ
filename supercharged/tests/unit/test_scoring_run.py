import shutil
from pathlib import Path

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.config.models import PipelineConfig
from cantinaiq.enrichment.run import run_enrichment
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.scoring.run import run_scoring
from cantinaiq.validation.schemas import (
    ScoredProducerSchema,
    ScoredRegionSchema,
    ScoredWineSchema,
)

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


def test_scoring_produces_three_outputs(cfg: PipelineConfig) -> None:
    run_id = "2026-05-16T00-00__sc01"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    interim = Path(cfg.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    run_enrichment(cfg, run_id)
    paths = run_scoring(cfg, run_id)
    wines = pl.read_parquet(paths["wines"])
    producers = pl.read_parquet(paths["producers"])
    regions = pl.read_parquet(paths["regions"])
    ScoredWineSchema.validate(wines, lazy=True)
    ScoredProducerSchema.validate(producers, lazy=True)
    ScoredRegionSchema.validate(regions, lazy=True)
    # composite_score must be in [0, 1] (normalised sub-scores · weights summing to 1).
    assert wines["composite_score"].max() <= 1.0
    assert wines["composite_score"].min() >= 0.0
    # m_strategy was 'manual' because bayesian_m=100 explicit.
    log_path = Path(cfg.paths.runs_dir) / run_id / "stage-scoring.json"
    import json

    log = json.loads(log_path.read_text())
    assert log["custom"]["m_used"] == 100
    assert log["custom"]["m_strategy"] == "manual"


def test_scoring_auto_median_when_m_none(cfg: PipelineConfig) -> None:
    """When bayesian_m is None, runner falls back to median(rating_count)."""
    # Rebuild cfg with bayesian_m=None
    raw = cfg.model_dump()
    raw["scoring"]["bayesian_m"] = None
    cfg2 = type(cfg)(**raw)
    run_id = "2026-05-16T00-00__sc02"
    run_ingestion(cfg2, run_id)
    run_cleaning(cfg2, run_id)
    interim = Path(cfg2.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    run_enrichment(cfg2, run_id)
    run_scoring(cfg2, run_id)
    import json

    log = json.loads(
        (Path(cfg2.paths.runs_dir) / run_id / "stage-scoring.json").read_text()
    )
    assert log["custom"]["m_strategy"] == "auto-median"
    assert log["custom"]["m_used"] >= 1
