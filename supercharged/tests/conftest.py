"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from cantinaiq.config.loader import config_from_dict
from cantinaiq.config.models import PipelineConfig


@pytest.fixture
def baseline_cfg(tmp_path) -> PipelineConfig:  # type: ignore[no-untyped-def]
    """A valid PipelineConfig pointing snapshots at a temp dir."""
    return config_from_dict(
        {
            "cleaning": {},
            "enrichment": {},
            "segments": {},
            "paths": {"snapshots_dir": str(tmp_path / "snapshots")},
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
