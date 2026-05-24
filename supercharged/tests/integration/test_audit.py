from pathlib import Path

import pytest
from typer.testing import CliRunner

from cantinaiq.cli import app
from cantinaiq.config.loader import config_from_dict, snapshot_config

runner = CliRunner()


def test_audit_lists_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    cfg = config_from_dict(
        {
            "cleaning": {},
            "enrichment": {},
            "segments": {},
            "paths": {"snapshots_dir": str(tmp_path / "config" / "snapshots")},
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
    snapshot_config(cfg, Path(cfg.paths.snapshots_dir))
    res = runner.invoke(app, ["audit", cfg.hash])
    assert res.exit_code == 0, res.stdout
    assert cfg.hash in res.stdout


def test_audit_missing_hash_exits_nonzero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["audit", "deadbeef"])
    assert res.exit_code == 1
    assert "No snapshot" in res.stdout
