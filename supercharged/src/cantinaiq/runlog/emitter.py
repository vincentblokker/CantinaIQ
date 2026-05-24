"""Context-manager emitter for stage run-logs."""

from __future__ import annotations

import os
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from cantinaiq.config.loader import snapshot_config
from cantinaiq.config.models import PipelineConfig
from cantinaiq.runlog.schema import StageRunLog


class RunLog:
    @staticmethod
    @contextmanager
    def stage(
        name: str,
        run_id: str,
        cfg: PipelineConfig,
        runs_dir: Path,
    ) -> Iterator[StageRunLog]:
        runs_dir = Path(runs_dir)
        stage_dir = runs_dir / run_id
        stage_dir.mkdir(parents=True, exist_ok=True)
        snapshot_ref = snapshot_config(cfg, cfg.paths.snapshots_dir)
        started = datetime.now(UTC)
        log = StageRunLog(
            stage=name,
            started_at=started,
            finished_at=started,
            config_hash=cfg.hash,
            config_snapshot_ref=str(snapshot_ref),
        )
        try:
            yield log
        except BaseException as exc:
            log.error = {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            log.finished_at = datetime.now(UTC)
            _atomic_write_log(log, stage_dir)
            raise
        log.finished_at = datetime.now(UTC)
        _atomic_write_log(log, stage_dir)


def _atomic_write_log(log: StageRunLog, stage_dir: Path) -> None:
    target = stage_dir / f"stage-{log.stage}.json"
    tmp = target.with_suffix(".tmp")
    tmp.write_text(log.model_dump_json(indent=2))
    os.replace(tmp, target)
