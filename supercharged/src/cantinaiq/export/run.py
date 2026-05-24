"""Export stage: JSON contracts for downstream consumers."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


@register_stage("export")
def run_export(cfg: PipelineConfig, run_id: str) -> dict[str, Path]:
    processed = Path(cfg.paths.processed_dir)
    exports = Path(cfg.paths.exports_dir)
    exports.mkdir(parents=True, exist_ok=True)
    wines = pl.read_parquet(processed / "wines_scored.parquet")
    producers = pl.read_parquet(processed / "producers_scored.parquet")
    regions = pl.read_parquet(processed / "regions_scored.parquet")

    out: dict[str, Path] = {}
    with RunLog.stage("export", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        log.pre_rows = wines.height

        prod_rank = producers.sort("composite_score", descending=True).to_dicts()
        out["producer_rankings"] = exports / "producer_rankings.json"
        out["producer_rankings"].write_text(json.dumps(prod_rank, indent=2, default=str))

        reg_rank = regions.sort("weighted_rating", descending=True).to_dicts()
        out["region_rankings"] = exports / "region_rankings.json"
        out["region_rankings"].write_text(json.dumps(reg_rank, indent=2, default=str))

        shortlist = wines.sort("composite_score", descending=True).head(100).to_dicts()
        out["wine_shortlist"] = exports / "wine_shortlist.json"
        out["wine_shortlist"].write_text(json.dumps(shortlist, indent=2, default=str))

        summary = {
            "run_id": run_id,
            "config_hash": cfg.hash,
            "wines_total": wines.height,
            "producers_total": producers.height,
            "regions_total": regions.height,
            "avg_weighted_rating": float(wines["weighted_rating"].mean() or 0),  # type: ignore[arg-type]
            "avg_price": float(wines["price"].mean() or 0),  # type: ignore[arg-type]
            "top_regions": (
                regions.sort("weighted_rating", descending=True)
                .head(5)
                .select(["region", "macro_region", "weighted_rating", "avg_price"])
                .to_dicts()
            ),
            "top_producers": (
                producers.sort("composite_score", descending=True)
                .head(10)
                .select(
                    [
                        "producer_name",
                        "macro_region",
                        "weighted_rating",
                        "composite_score",
                        "recommendation",
                    ]
                )
                .to_dicts()
            ),
        }
        out["dashboard_summary"] = exports / "dashboard_summary.json"
        out["dashboard_summary"].write_text(json.dumps(summary, indent=2, default=str))

        log.post_rows = wines.height
        log.custom = {
            "records_per_export": {
                k: (len(json.loads(p.read_text())) if k != "dashboard_summary" else 1)
                for k, p in out.items()
            },
            "outputs": {k: str(v) for k, v in out.items()},
        }
    return out
