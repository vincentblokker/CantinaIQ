"""Ingestion stage: read Excel sheets into a single Parquet."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


@register_stage("ingestion")
def run_ingestion(cfg: PipelineConfig, run_id: str) -> Path:
    interim = Path(cfg.paths.interim_dir)
    interim.mkdir(parents=True, exist_ok=True)
    out = interim / "01_raw.parquet"
    with RunLog.stage("ingestion", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        sheets = pl.read_excel(cfg.paths.source_excel, sheet_id=0)
        if isinstance(sheets, dict):
            frames = []
            counts: dict[str, int] = {}
            for sheet_name, df in sheets.items():
                tagged = df.with_columns(pl.lit(sheet_name).alias("source_sheet"))
                counts[sheet_name] = tagged.height
                frames.append(tagged)
            combined = pl.concat(frames, how="diagonal_relaxed")
        else:
            combined = sheets.with_columns(pl.lit("default").alias("source_sheet"))
            counts = {"default": combined.height}
        combined = combined.with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        combined.write_parquet(out)
        log.pre_rows = 0
        log.post_rows = combined.height
        log.custom = {
            "sheets_read": list(counts.keys()),
            "rows_per_sheet": counts,
            "column_inventory": combined.columns,
            "output_path": str(out),
        }
    return out
