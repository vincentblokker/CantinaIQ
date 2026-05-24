import json
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


def test_export_produces_four_json(cfg: PipelineConfig) -> None:
    run_id = "2026-05-16T00-00__exp01"
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
    out = run_export(cfg, run_id)
    expected = {"producer_rankings", "region_rankings", "wine_shortlist", "dashboard_summary"}
    assert set(out) == expected
    for name, path in out.items():
        assert path.exists(), name
        payload = json.loads(path.read_text())
        assert isinstance(payload, list | dict)
    # dashboard_summary must include the run-provenance fields.
    summary = json.loads(out["dashboard_summary"].read_text())
    assert summary["run_id"] == run_id
    assert summary["config_hash"] == cfg.hash
    assert len(summary["top_regions"]) <= 5
    assert len(summary["top_producers"]) <= 10
