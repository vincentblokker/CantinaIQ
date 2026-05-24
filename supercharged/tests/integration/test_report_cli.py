import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cantinaiq.cli import app
from cantinaiq.config.loader import config_from_dict
from cantinaiq.runlog import RunLog

REPO = Path(__file__).resolve().parents[2]
runner = CliRunner()


def _make_run(tmp_path: Path) -> str:
    cfg = config_from_dict(
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
    run_id = "2026-05-16T00-00__rep01"
    with RunLog.stage("ingestion", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        log.pre_rows = 0
        log.post_rows = 100
    with RunLog.stage("cleaning", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        log.pre_rows = 100
        log.post_rows = 80
        log.drops = {"non_italian": 20}
    return run_id


def test_report_build_latest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    templates_src = REPO / "reports" / "templates" / "data-quality.md.j2"
    target = tmp_path / "reports" / "templates" / "data-quality.md.j2"
    target.parent.mkdir(parents=True)
    shutil.copy(templates_src, target)
    _make_run(tmp_path)
    res = runner.invoke(app, ["report", "build", "--only", "data-quality"])
    assert res.exit_code == 0, res.stdout
    out_md = tmp_path / "reports" / "generated" / "data-quality.md"
    assert out_md.exists()
    text = out_md.read_text()
    assert "non_italian" in text
    assert "2026-05-16T00-00__rep01" in text
