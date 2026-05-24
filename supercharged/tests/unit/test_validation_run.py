from pathlib import Path
from typing import Any

import pandera as pa
import polars as pl
import pytest

from cantinaiq.config.loader import config_from_dict
from cantinaiq.config.models import PipelineConfig
from cantinaiq.validation.run import run_validation


@pytest.fixture
def cfg(tmp_path: Path) -> PipelineConfig:
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
                "source_excel": str(tmp_path / "missing.xlsx"),
            },
        }
    )


def _write_input(cfg: PipelineConfig, rows: list[dict[str, Any]]) -> None:
    interim = Path(cfg.paths.interim_dir)
    interim.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_parquet(interim / "02_cleaned.parquet")


def _valid_row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "wine_name": "Test 2020",
        "wine_name_normalised": "test 2020",
        "country": "Italy",
        "region": "Toscana",
        "rating": 4.2,
        "rating_count": 120,
        "price": 25.0,
        "vintage": 2020,
        "producer_hint": "Test",
        "source_sheet": "Italy",
        "run_config_hash": "a3f8e1c2",
    }
    row.update(overrides)
    return row


def test_validation_passes_for_valid_rows(cfg: PipelineConfig) -> None:
    _write_input(cfg, [_valid_row()])
    out = run_validation(cfg, run_id="2026-05-16T00-00__val01")
    assert out.exists()


def test_validation_fails_loud_for_bad_rating(cfg: PipelineConfig) -> None:
    _write_input(cfg, [_valid_row(), _valid_row(rating=5.4)])
    with pytest.raises((pa.errors.SchemaError, pa.errors.SchemaErrors)):
        run_validation(cfg, run_id="2026-05-16T00-00__val02")
    failures = Path(cfg.paths.runs_dir) / "2026-05-16T00-00__val02" / "validation-failures.parquet"
    assert failures.exists()


def test_validation_fails_loud_for_non_italy(cfg: PipelineConfig) -> None:
    _write_input(cfg, [_valid_row(country="France")])
    with pytest.raises((pa.errors.SchemaError, pa.errors.SchemaErrors)):
        run_validation(cfg, run_id="2026-05-16T00-00__val03")
