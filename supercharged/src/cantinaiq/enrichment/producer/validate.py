"""Post-hoc validation of producer extraction (spec §5.3).

Three warnings emitted to the run-log (not failures):
  1. distribution_overlap_warning — top-50 extracted producers vs the
     hand-curated known-top-50 list. Catches LLM/regex drift.
  2. multi_producer_per_wine_warning — same wine_name assigned different
     producers across rows; symptom of inconsistent disambiguation.
  3. coverage_warnings — overall + per-macro-region rate of
     enrichment_confidence in {High, Medium}; flags blind spots.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import polars as pl


def distribution_overlap_warning(
    enriched: pl.DataFrame,
    known_top50_path: Path,
    threshold: float = 0.6,
) -> dict[str, Any] | None:
    known: set[str] = set()
    with Path(known_top50_path).open() as f:
        for row in csv.DictReader(f):
            known.add(row["canonical_name"])
    if "producer_name" not in enriched.columns:
        return None
    top50 = (
        enriched.filter(pl.col("producer_name").is_not_null())
        .group_by("producer_name")
        .agg(pl.len().alias("n"))
        .sort("n", descending=True)
        .head(50)
    )
    extracted = set(top50["producer_name"].to_list())
    overlap = len(known & extracted) / max(len(known), 1)
    if overlap < threshold:
        return {
            "overlap": overlap,
            "threshold": threshold,
            "extracted_count": len(extracted),
        }
    return None


def multi_producer_per_wine_warning(enriched: pl.DataFrame) -> dict[str, Any] | None:
    if "wine_name_normalised" not in enriched.columns or "producer_name" not in enriched.columns:
        return None
    counts = (
        enriched.filter(pl.col("producer_name").is_not_null())
        .group_by("wine_name_normalised")
        .agg(pl.col("producer_name").n_unique().alias("u"))
        .filter(pl.col("u") > 1)
    )
    if counts.height == 0:
        return None
    samples = counts.head(5).to_dicts()
    return {"inconsistent_count": counts.height, "samples": samples}


def coverage_warnings(
    enriched: pl.DataFrame,
    target_overall: float = 0.80,
    target_per_region: float = 0.70,
) -> dict[str, Any]:
    total = enriched.height
    hi_med = enriched.filter(pl.col("enrichment_confidence").is_in(["High", "Medium"])).height
    overall = hi_med / total if total else 0.0
    per_region = (
        enriched.group_by("macro_region")
        .agg(
            pl.len().alias("n"),
            pl.col("enrichment_confidence").is_in(["High", "Medium"]).sum().alias("hi_med"),
        )
        .to_dicts()
    )
    regions_below = {
        r["macro_region"]: r["hi_med"] / r["n"] if r["n"] else 0.0
        for r in per_region
        if r["n"] > 0 and (r["hi_med"] / r["n"]) < target_per_region
    }
    return {
        "overall": overall,
        "overall_target": target_overall,
        "overall_below_target": overall < target_overall,
        "regions_below_target": regions_below,
    }
