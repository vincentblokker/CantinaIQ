import json
from pathlib import Path

import pytest

from cantinaiq.config.models import PipelineConfig
from cantinaiq.runlog import RunLog


def test_stage_writes_log_on_success(tmp_path: Path, baseline_cfg: PipelineConfig) -> None:
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__test01"
    with RunLog.stage("cleaning", run_id, baseline_cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 100
        log.post_rows = 80
        log.drops = {"non_italian": 20}
    target = runs_dir / run_id / "stage-cleaning.json"
    assert target.exists()
    payload = json.loads(target.read_text())
    assert payload["post_rows"] == 80
    assert payload["drops"]["non_italian"] == 20
    assert payload["error"] is None


def test_stage_writes_log_on_failure(tmp_path: Path, baseline_cfg: PipelineConfig) -> None:
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__test02"
    with (
        pytest.raises(RuntimeError),
        RunLog.stage("cleaning", run_id, baseline_cfg, runs_dir=runs_dir) as log,
    ):
        log.pre_rows = 100
        raise RuntimeError("boom")
    target = runs_dir / run_id / "stage-cleaning.json"
    assert target.exists()
    payload = json.loads(target.read_text())
    assert payload["error"]["type"] == "RuntimeError"
    assert "boom" in payload["error"]["message"]


def test_atomic_write(tmp_path: Path, baseline_cfg: PipelineConfig) -> None:
    """Stage log writes to a temp file then renames — no partial files left behind."""
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__test03"
    with RunLog.stage("ingestion", run_id, baseline_cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 5
        log.post_rows = 5
    stage_dir = runs_dir / run_id
    leftovers = [p for p in stage_dir.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []
