import shutil
from pathlib import Path

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.config.models import PipelineConfig
from cantinaiq.enrichment.run import run_enrichment
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.validation.schemas import EnrichedSchema

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def cfg(
    tmp_path: Path, sample_xlsx: Path, llm_cache_fixture: Path, monkeypatch: pytest.MonkeyPatch
) -> PipelineConfig:
    """Build a hermetic cfg pointing at copied reference data + tmp paths."""
    monkeypatch.setenv("CANTINAIQ_DISABLE_LLM", "1")  # never call real Anthropic API
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    shutil.copy(REPO / "data" / "reference" / "producer_aliases.csv", ref / "producer_aliases.csv")
    shutil.copy(REPO / "data" / "reference" / "macro_regions.csv", ref / "macro_regions.csv")
    shutil.copy(
        REPO / "data" / "reference" / "known_producers_top50.csv",
        ref / "known_producers_top50.csv",
    )
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


def test_enrichment_full_path(cfg: PipelineConfig) -> None:
    run_id = "2026-05-16T00-00__enr01"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    # The fixture deliberately includes rows that fail validation (rating>5, etc.);
    # filter those out manually to test enrichment in isolation.
    interim = Path(cfg.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    out = run_enrichment(cfg, run_id)
    df = pl.read_parquet(out)
    # All rows get a price_segment + confidence_segment + macro_region.
    assert df["price_segment"].null_count() == 0
    assert df["confidence_segment"].null_count() == 0
    assert df["macro_region"].null_count() == 0
    # Producer extraction coverage: most fixture rows resolve via alias whitelist.
    high_or_med = df.filter(pl.col("enrichment_confidence").is_in(["High", "Medium"])).height
    assert high_or_med >= df.height * 0.5
    # Pandera schema validation passes on the enriched shape.
    EnrichedSchema.validate(df, lazy=True)
