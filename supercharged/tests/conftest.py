"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from cantinaiq.config.loader import config_from_dict
from cantinaiq.config.models import PipelineConfig

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_xlsx() -> Path:
    """Path to the hand-curated 50-row Vivino sample fixture."""
    return FIXTURES / "vivino_sample.xlsx"


@pytest.fixture
def llm_cache_fixture() -> Path:
    """Path to the pre-populated LLM cache parquet for the 5 ambiguous fixture wines."""
    return FIXTURES / "llm_cache.parquet"


@pytest.fixture
def baseline_cfg_dict() -> dict[str, Any]:
    """Plain-dict baseline config (useful for OmegaConf-style construction)."""
    return {
        "cleaning": {},
        "enrichment": {},
        "segments": {},
        "paths": {},
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
    }


@pytest.fixture
def baseline_cfg(tmp_path: Path) -> PipelineConfig:
    """A valid PipelineConfig with all paths pointed at a temp directory.

    Snapshots, runs, interim, processed, exports — all rerouted under tmp_path
    so tests never touch the real repo data tree.
    """
    return config_from_dict(
        {
            "cleaning": {},
            "enrichment": {},
            "segments": {},
            "paths": {
                "raw_dir": str(tmp_path / "raw"),
                "interim_dir": str(tmp_path / "interim"),
                "processed_dir": str(tmp_path / "processed"),
                "exports_dir": str(tmp_path / "exports"),
                "runs_dir": str(tmp_path / "runs"),
                "reference_dir": str(tmp_path / "reference"),
                "snapshots_dir": str(tmp_path / "snapshots"),
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
        }
    )
