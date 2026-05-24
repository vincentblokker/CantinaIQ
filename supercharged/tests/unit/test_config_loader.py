from pathlib import Path
from typing import Any

import pytest
from omegaconf import OmegaConf

from cantinaiq.config.loader import (
    config_from_dict,
    config_from_omegaconf,
    snapshot_config,
)
from cantinaiq.config.models import PipelineConfig


@pytest.fixture
def baseline_dict() -> dict[str, Any]:
    return {
        "cleaning": {},
        "enrichment": {},
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
        "segments": {},
        "paths": {},
    }


def test_config_from_dict_constructs(baseline_dict: dict[str, Any]) -> None:
    cfg = config_from_dict(baseline_dict)
    assert isinstance(cfg, PipelineConfig)
    assert cfg.scoring.bayesian_m == 100


def test_config_from_omegaconf_resolves(baseline_dict: dict[str, Any]) -> None:
    oc = OmegaConf.create(baseline_dict)
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.weights.weighted_rating == 0.35


def test_config_hash_is_stable(baseline_dict: dict[str, Any]) -> None:
    cfg_a = config_from_dict(baseline_dict)
    cfg_b = config_from_dict(baseline_dict)
    assert cfg_a.hash == cfg_b.hash
    assert len(cfg_a.hash) == 8


def test_config_hash_changes_with_weight(baseline_dict: dict[str, Any]) -> None:
    cfg_a = config_from_dict(baseline_dict)
    baseline_dict["scoring"]["weights"]["weighted_rating"] = 0.40
    baseline_dict["scoring"]["weights"]["portfolio_opportunity"] = 0.05
    cfg_b = config_from_dict(baseline_dict)
    assert cfg_a.hash != cfg_b.hash


def test_snapshot_writes_yaml(tmp_path: Path, baseline_dict: dict[str, Any]) -> None:
    cfg = config_from_dict(baseline_dict)
    snapshot_dir = tmp_path / "snapshots"
    path = snapshot_config(cfg, snapshot_dir)
    assert path.exists()
    assert path.name == f"{cfg.hash}.yaml"
    # Idempotency: second call returns same path without overwriting.
    path2 = snapshot_config(cfg, snapshot_dir)
    assert path == path2
