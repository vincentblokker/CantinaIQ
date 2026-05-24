from pathlib import Path

import pytest

from cantinaiq.config.models import PipelineConfig
from cantinaiq.runlog import RunLog, load_run_bundle
from cantinaiq.runlog.loader import load_latest_run_id


def test_load_run_bundle_with_two_stages(tmp_path: Path, baseline_cfg: PipelineConfig) -> None:
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__abc123"
    with RunLog.stage("ingestion", run_id, baseline_cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 0
        log.post_rows = 100
    with RunLog.stage("cleaning", run_id, baseline_cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 100
        log.post_rows = 80
        log.drops = {"non_italian": 20}
    bundle = load_run_bundle(run_id, runs_dir=runs_dir)
    assert set(bundle.stages.keys()) == {"ingestion", "cleaning"}
    assert bundle.stages["cleaning"].drops["non_italian"] == 20


def test_load_run_bundle_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_run_bundle("does-not-exist", runs_dir=tmp_path)


def test_load_latest_run_id(tmp_path: Path, baseline_cfg: PipelineConfig) -> None:
    runs_dir = tmp_path / "runs"
    for run_id in ("2026-05-14T00-00__aaa", "2026-05-15T00-00__bbb"):
        with RunLog.stage("ingestion", run_id, baseline_cfg, runs_dir=runs_dir) as log:
            log.post_rows = 1
    latest = load_latest_run_id(runs_dir)
    assert latest == "2026-05-15T00-00__bbb"
