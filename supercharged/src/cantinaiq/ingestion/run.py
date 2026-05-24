"""Ingestion stage: read Excel sheets into a single Parquet.

The real Vivino-export.xlsx encodes every row as a single CSV-text cell
(columns name,country,region,rating,rating_count,price comma-joined into
one string). The 50-row test fixture uses proper separate columns. This
ingester detects the format and normalises both into the same schema.
"""

from __future__ import annotations

import io
from pathlib import Path

import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog

CANONICAL_COLUMNS = ["wine_name", "country", "region", "rating", "rating_count", "price"]


def _is_csv_text_format(df: pl.DataFrame) -> bool:
    """Detect the 'one CSV string per row' format: a single data column whose
    name contains commas (the joined header line)."""
    data_cols = [c for c in df.columns if c != "source_sheet"]
    return len(data_cols) == 1 and "," in data_cols[0]


def _expand_csv_text(df: pl.DataFrame, sheet_name: str) -> pl.DataFrame:
    """Parse single-column CSV-text rows into a proper 6-column frame."""
    text_col = next(c for c in df.columns if c != "source_sheet")
    csv_text = "\n".join(s for s in df[text_col].to_list() if s)
    if not csv_text.strip():
        return pl.DataFrame(schema={c: pl.String for c in CANONICAL_COLUMNS})
    parsed = pl.read_csv(
        io.BytesIO(csv_text.encode()),
        has_header=False,
        new_columns=CANONICAL_COLUMNS,
        infer_schema_length=0,  # all-string; cleaning stage handles coercion
        truncate_ragged_lines=True,
    )
    return parsed.with_columns(pl.lit(sheet_name).alias("source_sheet"))


def _normalise(df: pl.DataFrame, sheet_name: str) -> pl.DataFrame:
    """Bring a sheet into the canonical wine_name/country/region/... schema."""
    if _is_csv_text_format(df):
        return _expand_csv_text(df, sheet_name)
    # Already in column-form. Map "name" → "wine_name" for downstream consistency.
    if "name" in df.columns and "wine_name" not in df.columns:
        df = df.rename({"name": "wine_name"})
    return df.with_columns(pl.lit(sheet_name).alias("source_sheet"))


@register_stage("ingestion")
def run_ingestion(cfg: PipelineConfig, run_id: str) -> Path:
    interim = Path(cfg.paths.interim_dir)
    interim.mkdir(parents=True, exist_ok=True)
    out = interim / "01_raw.parquet"
    with RunLog.stage("ingestion", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        sheets = pl.read_excel(cfg.paths.source_excel, sheet_id=0)
        if isinstance(sheets, dict):
            frames: list[pl.DataFrame] = []
            counts: dict[str, int] = {}
            for sheet_name, df in sheets.items():
                tagged = df.with_columns(pl.lit(sheet_name).alias("source_sheet"))
                normalised = _normalise(tagged, sheet_name)
                counts[sheet_name] = normalised.height
                frames.append(normalised)
            combined = pl.concat(frames, how="diagonal_relaxed")
        else:
            tagged = sheets.with_columns(pl.lit("default").alias("source_sheet"))
            combined = _normalise(tagged, "default")
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
