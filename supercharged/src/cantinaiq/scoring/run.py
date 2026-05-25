"""Scoring stage: weighted rating, value score, composite, segmentation, aggregations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from cantinaiq.config.models import PipelineConfig, SegmentsConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog
from cantinaiq.scoring.math import bayesian_weighted_rating, composite_score, value_score


def _market_segment(row: dict[str, Any], seg: SegmentsConfig) -> str:
    r = row["weighted_rating"]
    p = row["price"]
    n = row["rating_count"]
    if n < seg.market.low_confidence_review_max:
        return "Low Confidence Niche"
    if r >= seg.market.premium_icon_min_rating and p >= seg.market.premium_icon_min_price:
        return "Premium Icon"
    if r >= seg.market.hidden_gem_min_rating and p < seg.market.premium_icon_min_price:
        return "Hidden Gem"
    if r <= seg.market.overpriced_max_rating and p >= seg.market.overpriced_min_price:
        return "Overpriced Risk"
    return "Commercial Value"


def _recommend(market_segment: str, composite: float, seg: SegmentsConfig) -> str:
    t = seg.recommendations
    if market_segment == "Premium Icon" and composite >= t.premium_brand_builder_min_composite:
        return "Premium Brand Builder"
    if market_segment == "Hidden Gem" and composite >= t.target_min_composite:
        return "Target"
    if market_segment == "Commercial Value" and composite >= t.value_opportunity_min_composite:
        return "Value Opportunity"
    if market_segment == "Overpriced Risk":
        return "Avoid for Now"
    return "Monitor"


@register_stage("scoring")
def run_scoring(cfg: PipelineConfig, run_id: str) -> dict[str, Path]:
    processed = Path(cfg.paths.processed_dir)
    processed.mkdir(parents=True, exist_ok=True)
    src = processed / "italian_wines_enriched.parquet"
    out_wines = processed / "wines_scored.parquet"
    out_producers = processed / "producers_scored.parquet"
    out_regions = processed / "regions_scored.parquet"

    with RunLog.stage("scoring", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        log.pre_rows = df.height

        # Optional drop floor on review count.
        if cfg.scoring.min_reviews_floor > 0:
            before = df.height
            df = df.filter(pl.col("rating_count") >= cfg.scoring.min_reviews_floor)
            log.drops["min_reviews_floor"] = before - df.height

        global_mean = float(df["rating"].mean() or 4.0)  # type: ignore[arg-type]
        if cfg.scoring.bayesian_m is not None:
            m_used = cfg.scoring.bayesian_m
            m_strategy = "manual"
        else:
            m_used = int(df["rating_count"].median() or 100)  # type: ignore[arg-type]
            m_strategy = "auto-median"

        df = df.with_columns(
            pl.struct(["rating", "rating_count"])
            .map_elements(
                lambda s: bayesian_weighted_rating(
                    rating=s["rating"],
                    rating_count=s["rating_count"],
                    m=m_used,
                    global_mean=global_mean,
                ),
                return_dtype=pl.Float64,
            )
            .alias("weighted_rating")
        )
        df = df.with_columns(
            pl.struct(["weighted_rating", "price"])
            .map_elements(
                lambda s: value_score(s["weighted_rating"], s["price"]),
                return_dtype=pl.Float64,
            )
            .alias("value_score")
        )

        # Min-max normalisation per column (constant column → 0.5).
        def _norm(col: str) -> pl.Expr:
            raw_min = df[col].min()
            raw_max = df[col].max()
            if raw_max is None or raw_min is None or raw_max == raw_min:
                return pl.lit(0.5)
            min_v = float(raw_min)  # type: ignore[arg-type]
            max_v = float(raw_max)  # type: ignore[arg-type]
            return (pl.col(col) - min_v) / (max_v - min_v)

        weights = (
            cfg.scoring.weights.weighted_rating,
            cfg.scoring.weights.market_confidence,
            cfg.scoring.weights.value_for_money,
            cfg.scoring.weights.premium_fit,
            cfg.scoring.weights.portfolio_opportunity,
        )

        df = df.with_columns(
            [
                _norm("weighted_rating").alias("_wr_n"),
                _norm("rating_count").alias("_mc_n"),
                _norm("value_score").alias("_v_n"),
                _norm("price").alias("_pf_n"),
                _norm("rating_count").alias("_po_n"),
            ]
        )
        df = df.with_columns(
            pl.struct(["_wr_n", "_mc_n", "_v_n", "_pf_n", "_po_n"])
            .map_elements(
                lambda s: composite_score(
                    s["_wr_n"],
                    s["_mc_n"],
                    s["_v_n"],
                    s["_pf_n"],
                    s["_po_n"],
                    weights=weights,
                ),
                return_dtype=pl.Float64,
            )
            .alias("composite_score")
        ).drop(["_wr_n", "_mc_n", "_v_n", "_pf_n", "_po_n"])

        df = df.with_columns(
            pl.struct(["weighted_rating", "price", "rating_count"])
            .map_elements(
                lambda s: _market_segment(s, cfg.segments),
                return_dtype=pl.String,
            )
            .alias("market_segment")
        )

        df = df.with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        df.write_parquet(out_wines)

        # Producer aggregation — review-count-weighted weighted_rating.
        prods = (
            df.filter(pl.col("producer_name").is_not_null())
            .group_by("producer_name")
            .agg(
                pl.col("macro_region").mode().first().alias("macro_region"),
                pl.len().cast(pl.Int64).alias("wines_in_dataset"),
                pl.col("rating_count").sum().alias("total_reviews"),
                pl.col("price").mean().alias("avg_price"),
                (pl.col("weighted_rating") * pl.col("rating_count")).sum().alias("_num"),
                pl.col("rating_count").sum().alias("_den"),
                pl.col("value_score").mean().alias("value_score"),
                pl.col("composite_score").mean().alias("composite_score"),
                pl.col("market_segment").mode().first().alias("market_segment"),
            )
            .with_columns((pl.col("_num") / pl.col("_den")).alias("weighted_rating"))
            .drop(["_num", "_den"])
        )
        seg_cfg = cfg.segments
        prods = prods.with_columns(
            pl.struct(["market_segment", "composite_score"])
            .map_elements(
                lambda s, _seg=seg_cfg: _recommend(
                    s["market_segment"], s["composite_score"], _seg
                ),
                return_dtype=pl.String,
            )
            .alias("recommendation")
        ).with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        prods.write_parquet(out_producers)

        # Region aggregation — same review-count weighting.
        regs = (
            df.group_by("region")
            .agg(
                pl.col("macro_region").mode().first().alias("macro_region"),
                pl.len().cast(pl.Int64).alias("wines_in_dataset"),
                pl.col("rating_count").sum().alias("total_reviews"),
                pl.col("price").mean().alias("avg_price"),
                (pl.col("weighted_rating") * pl.col("rating_count")).sum().alias("_num"),
                pl.col("rating_count").sum().alias("_den"),
                pl.col("value_score").mean().alias("value_score"),
            )
            .with_columns(
                [
                    (pl.col("_num") / pl.col("_den")).alias("weighted_rating"),
                    (pl.col("wines_in_dataset") < 3).alias("low_sample_region"),
                ]
            )
            .drop(["_num", "_den"])
            .with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        )
        regs.write_parquet(out_regions)

        log.post_rows = df.height
        log.custom = {
            "global_mean_rating": global_mean,
            "m_used": m_used,
            "m_strategy": m_strategy,
            "weights_used": dict(
                zip(
                    (
                        "weighted_rating",
                        "market_confidence",
                        "value_for_money",
                        "premium_fit",
                        "portfolio_opportunity",
                    ),
                    weights,
                    strict=True,
                )
            ),
            "score_distribution_summary": {
                "composite_p25": float(df["composite_score"].quantile(0.25) or 0),
                "composite_p50": float(df["composite_score"].quantile(0.50) or 0),
                "composite_p75": float(df["composite_score"].quantile(0.75) or 0),
            },
            "outputs": {
                "wines": str(out_wines),
                "producers": str(out_producers),
                "regions": str(out_regions),
            },
        }
    return {"wines": out_wines, "producers": out_producers, "regions": out_regions}
