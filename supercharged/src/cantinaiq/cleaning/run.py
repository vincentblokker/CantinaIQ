"""Cleaning stage: normalisation, encoding fixes, dedupe, IT filter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from cantinaiq.cleaning.rules import (
    extract_vintage,
    fix_encoding,
    normalise_wine_name,
    parse_tuple_string,
)
from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


def _clean_country_region(value: str | None) -> str:
    return fix_encoding(parse_tuple_string(value or ""))


def _first_word(name: str | None) -> str | None:
    return name.split()[0] if name else None


@register_stage("cleaning")
def run_cleaning(cfg: PipelineConfig, run_id: str) -> Path:
    interim = Path(cfg.paths.interim_dir)
    src = interim / "01_raw.parquet"
    out = interim / "02_cleaned.parquet"
    with RunLog.stage("cleaning", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        log.pre_rows = df.height
        drops: dict[str, int] = {}
        samples: dict[str, list[dict[str, Any]]] = {}

        # 1. Parse tuple-strings + encoding fix on country/region.
        df = df.with_columns(
            [
                pl.col("country").map_elements(_clean_country_region, return_dtype=pl.String),
                pl.col("region").map_elements(_clean_country_region, return_dtype=pl.String),
            ]
        )

        # 2. Numeric coercion.
        df = df.with_columns(
            [
                pl.col("rating").cast(pl.Float64, strict=False),
                pl.col("rating_count").cast(pl.Int64, strict=False),
                pl.col("price").cast(pl.Float64, strict=False),
            ]
        )

        # 3. Drop rows missing required string fields (records drop reason).
        for col in ("country", "region", "wine_name"):
            before = df.height
            df = df.filter(pl.col(col).is_not_null() & (pl.col(col) != ""))
            removed = before - df.height
            if removed:
                drops[f"missing_{col}"] = drops.get(f"missing_{col}", 0) + removed

        # 3b. Drop rows that won't satisfy the validation contract (rating in [0,5],
        #     rating_count >= 1, price > 0). Validation remains as backstop —
        #     anything that slips through here will fail loud.
        before = df.height
        df = df.filter(
            pl.col("rating").is_not_null()
            & (pl.col("rating") >= 0)
            & (pl.col("rating") <= 5)
        )
        if (removed := before - df.height) > 0:
            drops["invalid_rating"] = removed
        before = df.height
        df = df.filter(pl.col("rating_count").is_not_null() & (pl.col("rating_count") >= 1))
        if (removed := before - df.height) > 0:
            drops["invalid_rating_count"] = removed
        before = df.height
        df = df.filter(pl.col("price").is_not_null() & (pl.col("price") > 0))
        if (removed := before - df.height) > 0:
            drops["invalid_price"] = removed

        # 4. Country titlecase + strip.
        df = df.with_columns(pl.col("country").str.strip_chars().str.to_titlecase())

        # 5. IT filter — must run *after* tuple-parse + titlecase.
        target = cfg.cleaning.italian_country_token
        before = df.height
        non_it_samples = (
            df.filter(pl.col("country") != target)
            .select(["wine_name", "country"])
            .head(3)
            .to_dicts()
        )
        df = df.filter(pl.col("country") == target)
        non_it = before - df.height
        if non_it:
            drops["non_italian"] = non_it
            samples["non_italian"] = non_it_samples

        # 6. Helper columns required for dedupe + downstream stages.
        df = df.with_columns(
            [
                pl.col("wine_name")
                .map_elements(normalise_wine_name, return_dtype=pl.String)
                .alias("wine_name_normalised"),
                pl.col("wine_name")
                .map_elements(_first_word, return_dtype=pl.String)
                .alias("producer_hint"),
                pl.col("wine_name")
                .map_elements(extract_vintage, return_dtype=pl.Int64)
                .alias("vintage"),
            ]
        )

        # 7. Dedupe on configured keys.
        before = df.height
        df = df.unique(subset=cfg.cleaning.dedup_keys, keep="first", maintain_order=True)
        collapsed = before - df.height
        if collapsed:
            drops["duplicate"] = collapsed

        # 8. Refresh run_config_hash (ingestion already stamped, but the
        #    cleaned shape is what downstream stages consume).
        df = df.with_columns(pl.lit(cfg.hash).alias("run_config_hash"))

        df.write_parquet(out)
        log.post_rows = df.height
        log.drops = drops
        log.drop_samples = samples
        log.custom = {
            "it_filter_kept": df.height,
            "output_path": str(out),
        }
    return out
