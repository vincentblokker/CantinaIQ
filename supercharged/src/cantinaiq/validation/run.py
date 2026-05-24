"""Validation stage: Pandera contract check; fail-loud on breach."""

from __future__ import annotations

from pathlib import Path

import pandera as pa
import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog
from cantinaiq.validation.schemas import CleanedSchema


def _failure_cases_to_polars(exc: pa.errors.SchemaError | pa.errors.SchemaErrors) -> pl.DataFrame:
    """Return pandera's failure_cases as a Polars DataFrame.

    pandera-polars exposes failure_cases as a Polars DataFrame natively;
    if it ever comes back as something else (older API, pandas), we fall
    back to a single-row error-message frame so the file always exists.
    """
    fc = getattr(exc, "failure_cases", None)
    if isinstance(fc, pl.DataFrame):
        return fc
    return pl.DataFrame({"error": [str(exc)]})


@register_stage("validation")
def run_validation(cfg: PipelineConfig, run_id: str) -> Path:
    interim = Path(cfg.paths.interim_dir)
    src = interim / "02_cleaned.parquet"
    out = interim / "03_validated.parquet"
    runs_dir = Path(cfg.paths.runs_dir) / run_id
    with RunLog.stage("validation", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        log.pre_rows = df.height
        try:
            CleanedSchema.validate(df, lazy=True)
        except (pa.errors.SchemaError, pa.errors.SchemaErrors) as exc:
            failures_path = runs_dir / "validation-failures.parquet"
            failures_path.parent.mkdir(parents=True, exist_ok=True)
            failure_cases = _failure_cases_to_polars(exc)
            failure_cases.write_parquet(failures_path)
            counts: dict[str, int] = {}
            if "check" in failure_cases.columns:
                for check in failure_cases["check"].to_list():
                    counts[str(check)] = counts.get(str(check), 0) + 1
            else:
                counts = {"total": failure_cases.height}
            log.schema_failures = counts
            log.custom = {"failures_path": str(failures_path)}
            raise
        df.write_parquet(out)
        log.post_rows = df.height
        log.custom = {"output_path": str(out)}
    return out
