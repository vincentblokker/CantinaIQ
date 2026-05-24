"""Enrichment stage: macro-region, price/confidence segments, producer extraction."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import polars as pl

from cantinaiq.config.models import PipelineConfig, SegmentsConfig
from cantinaiq.enrichment.producer.cache import LLMCache
from cantinaiq.enrichment.producer.models import ProducerCandidate
from cantinaiq.enrichment.producer.pass1_rules import Pass1Extractor
from cantinaiq.enrichment.producer.pass2_llm import (
    AnthropicLLMClient,
    LLMClient,
    Pass2Resolver,
)
from cantinaiq.enrichment.producer.validate import (
    coverage_warnings,
    distribution_overlap_warning,
    multi_producer_per_wine_warning,
)
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


def _load_macro_regions(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with Path(path).open() as f:
        for row in csv.DictReader(f):
            mapping[row["region"].strip().lower()] = row["macro_region"].strip()
    return mapping


def _price_segment(price: float, seg: SegmentsConfig) -> str:
    if price <= seg.prices.entry_max:
        return "Entry"
    if price <= seg.prices.accessible_premium_max:
        return "Accessible Premium"
    if price <= seg.prices.premium_max:
        return "Premium"
    return "Prestige"


def _confidence_segment(count: int, seg: SegmentsConfig) -> str:
    if count < seg.confidence.low_max:
        return "Low Confidence"
    if count < seg.confidence.emerging_max:
        return "Emerging Signal"
    if count < seg.confidence.reliable_max:
        return "Reliable Signal"
    return "Strong Market Signal"


def _try_default_llm_client(cfg: PipelineConfig) -> LLMClient | None:
    """Construct an AnthropicLLMClient unless disabled or unavailable.

    Returns None instead of raising when:
      - CANTINAIQ_DISABLE_LLM=1 is set (explicit opt-out), or
      - ANTHROPIC_API_KEY is missing (test/CI environments).

    The runner falls back to pass-1 results in either case — no implicit
    API spend, no test-environment surprises.
    """
    if os.environ.get("CANTINAIQ_DISABLE_LLM") == "1":
        return None
    try:
        return AnthropicLLMClient(
            model=cfg.enrichment.llm.model,
            temperature=cfg.enrichment.llm.temperature,
        )
    except RuntimeError:
        return None


@register_stage("enrichment")
def run_enrichment(
    cfg: PipelineConfig,
    run_id: str,
    llm_client: LLMClient | None = None,
) -> Path:
    interim = Path(cfg.paths.interim_dir)
    processed = Path(cfg.paths.processed_dir)
    processed.mkdir(parents=True, exist_ok=True)
    out = processed / "italian_wines_enriched.parquet"
    src = interim / "03_validated.parquet"

    with RunLog.stage("enrichment", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        log.pre_rows = df.height

        # 1. Macro-region lookup (passthrough region when unmapped).
        macro_map = _load_macro_regions(cfg.enrichment.macro_regions_path)
        df = df.with_columns(
            pl.col("region")
            .map_elements(
                lambda r: macro_map.get((r or "").strip().lower(), r or "Unknown"),
                return_dtype=pl.String,
            )
            .alias("macro_region")
        )

        # 2. Price + confidence segments from configured thresholds.
        seg = cfg.segments
        df = df.with_columns(
            [
                pl.col("price")
                .map_elements(lambda p: _price_segment(p, seg), return_dtype=pl.String)
                .alias("price_segment"),
                pl.col("rating_count")
                .map_elements(lambda c: _confidence_segment(c, seg), return_dtype=pl.String)
                .alias("confidence_segment"),
            ]
        )

        # 3. Pass-1 deterministic producer extraction.
        p1 = Pass1Extractor(aliases_path=cfg.enrichment.aliases_path)
        rows = df.select(["wine_name", "region"]).to_dicts()
        pass1_results: list[ProducerCandidate] = [
            p1.extract(r["wine_name"], r.get("region")) for r in rows
        ]

        # 4. Pass-2 LLM disambiguation for rows pass-1 couldn't resolve.
        candidates_for_p2 = [
            {"id": i, "wine_name": rows[i]["wine_name"], "region": rows[i]["region"]}
            for i, c in enumerate(pass1_results)
            if c.confidence in ("Low", "None")
        ]
        pass2_results: dict[int, ProducerCandidate] = {}
        llm_skipped = False
        llm_new_calls = 0
        if candidates_for_p2:
            client = llm_client if llm_client is not None else _try_default_llm_client(cfg)
            if client is None:
                llm_skipped = True
            else:
                cache = LLMCache(
                    path=cfg.enrichment.llm.cache_path,
                    model_version=cfg.enrichment.llm.model,
                )
                resolver = Pass2Resolver(
                    cache=cache,
                    client=client,
                    batch_size=cfg.enrichment.llm.batch_size,
                )
                pass2_results = resolver.resolve(candidates_for_p2)
                llm_new_calls = resolver.fresh_calls

        merged: list[ProducerCandidate] = [
            pass2_results.get(i, c) for i, c in enumerate(pass1_results)
        ]

        producer_df = pl.DataFrame(
            {
                "producer_name": [c.name for c in merged],
                "enrichment_confidence": [c.confidence for c in merged],
                "inferred_grape_or_style": [c.inferred_grape_or_style for c in merged],
            },
            schema={
                "producer_name": pl.String,
                "enrichment_confidence": pl.String,
                "inferred_grape_or_style": pl.String,
            },
        )
        df = pl.concat([df, producer_df], how="horizontal")

        # 5. Coverage reporting (overall + per macro-region).
        total = df.height
        coverage = df.filter(pl.col("enrichment_confidence").is_in(["High", "Medium"])).height
        per_region = (
            df.group_by("macro_region")
            .agg(
                pl.len().alias("n"),
                pl.col("enrichment_confidence").is_in(["High", "Medium"]).sum().alias("hi_med"),
            )
            .to_dicts()
        )

        # 6. Post-hoc validation warnings (spec §5.3) — never failures.
        warnings_payload = {
            "coverage": coverage_warnings(
                df,
                target_overall=cfg.enrichment.coverage_target_overall,
                target_per_region=cfg.enrichment.coverage_target_per_region,
            ),
            "distribution": distribution_overlap_warning(df, cfg.enrichment.known_top50_path),
            "multi_producer": multi_producer_per_wine_warning(df),
        }

        df.write_parquet(out)
        log.post_rows = df.height
        log.custom = {
            "enrichment_coverage_overall": coverage / total if total else 0.0,
            "enrichment_coverage_per_macro_region": {
                r["macro_region"]: (r["hi_med"] / r["n"] if r["n"] else 0.0) for r in per_region
            },
            "pass1_resolved": sum(1 for c in pass1_results if c.confidence in ("High", "Medium")),
            "pass2_invoked_count": len(candidates_for_p2),
            "llm_new_calls": llm_new_calls,
            "llm_skipped": llm_skipped,
            "warnings": warnings_payload,
            "output_path": str(out),
        }
    return out
