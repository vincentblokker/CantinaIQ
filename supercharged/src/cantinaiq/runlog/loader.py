"""Load a run directory into a RunBundle."""

from __future__ import annotations

import platform
from pathlib import Path

from cantinaiq import __version__
from cantinaiq.runlog.schema import RunBundle, StageRunLog


def load_run_bundle(run_id: str, runs_dir: Path) -> RunBundle:
    run_dir = Path(runs_dir) / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    stages: dict[str, StageRunLog] = {}
    for stage_file in sorted(run_dir.glob("stage-*.json")):
        log = StageRunLog.model_validate_json(stage_file.read_text())
        stages[log.stage] = log
    if not stages:
        raise FileNotFoundError(f"No stage logs in {run_dir}")
    earliest = min(s.started_at for s in stages.values())
    latest = max(s.finished_at for s in stages.values())
    return RunBundle(
        run_id=run_id,
        started_at=earliest,
        finished_at=latest,
        stages=stages,
        pipeline_config={},
        cli_args=[],
        git_sha=None,
        python_version=platform.python_version(),
        package_version=__version__,
    )


def load_latest_run_id(runs_dir: Path) -> str:
    runs_dir = Path(runs_dir)
    if not runs_dir.exists():
        raise FileNotFoundError(f"Runs dir not found: {runs_dir}")
    candidates = [p for p in runs_dir.iterdir() if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No runs in {runs_dir}")
    return sorted(candidates, key=lambda p: p.name)[-1].name
