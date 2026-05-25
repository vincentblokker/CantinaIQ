"""Pydantic config schema for the CantinaIQ pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ScoringWeights(BaseModel):
    weighted_rating: float = Field(ge=0, le=1)
    market_confidence: float = Field(ge=0, le=1)
    value_for_money: float = Field(ge=0, le=1)
    premium_fit: float = Field(ge=0, le=1)
    portfolio_opportunity: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _sum_to_one(self) -> ScoringWeights:
        s = (
            self.weighted_rating
            + self.market_confidence
            + self.value_for_money
            + self.premium_fit
            + self.portfolio_opportunity
        )
        if not 0.999 <= s <= 1.001:
            raise ValueError(f"Scoring weights must sum to 1.0, got {s:.4f}")
        return self


class ScoringConfig(BaseModel):
    bayesian_m: int | None = Field(
        default=None, gt=0, description="Shrinkage threshold; None = auto-median"
    )
    min_reviews_floor: int = Field(default=0, ge=0)
    weights: ScoringWeights
    composite_formula_version: Literal["v1"] = "v1"


class PriceSegments(BaseModel):
    entry_max: float = 15.0
    accessible_premium_max: float = 30.0
    premium_max: float = 75.0


class ConfidenceSegments(BaseModel):
    low_max: int = 50
    emerging_max: int = 250
    reliable_max: int = 1000


class MarketSegmentRules(BaseModel):
    hidden_gem_min_rating: float = 4.2
    premium_icon_min_rating: float = 4.3
    premium_icon_min_price: float = 75.0
    overpriced_max_rating: float = 4.0
    overpriced_min_price: float = 75.0
    low_confidence_review_max: int = 50


class RecommendationThresholds(BaseModel):
    """Composite-score thresholds that upgrade a producer beyond `Monitor`.

    Tuned to the observed composite-score distribution: with v1 weights the
    composite saturates near 0.4, so the original 0.55-0.65 thresholds left
    every producer flagged `Monitor`. Defaults are roughly the 70th percentile
    within each segment.
    """

    premium_brand_builder_min_composite: float = 0.30
    target_min_composite: float = 0.30
    value_opportunity_min_composite: float = 0.30


class SegmentsConfig(BaseModel):
    prices: PriceSegments = Field(default_factory=PriceSegments)
    confidence: ConfidenceSegments = Field(default_factory=ConfidenceSegments)
    market: MarketSegmentRules = Field(default_factory=MarketSegmentRules)
    recommendations: RecommendationThresholds = Field(
        default_factory=RecommendationThresholds
    )


class CleaningConfig(BaseModel):
    italian_country_token: str = "Italy"
    dedup_keys: list[str] = Field(
        default_factory=lambda: ["wine_name_normalised", "producer_hint", "vintage"]
    )


class LLMConfig(BaseModel):
    model: str = "claude-haiku-4-5-20251001"
    temperature: float = 0.0
    batch_size: int = 50
    max_retries: int = 3
    cache_path: Path = Path("data/reference/llm_cache.parquet")


class EnrichmentConfig(BaseModel):
    aliases_path: Path = Path("data/reference/producer_aliases.csv")
    macro_regions_path: Path = Path("data/reference/macro_regions.csv")
    known_top50_path: Path = Path("data/reference/known_producers_top50.csv")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    coverage_target_overall: float = 0.80
    coverage_target_per_region: float = 0.70


class PathsConfig(BaseModel):
    raw_dir: Path = Path("data/raw")
    interim_dir: Path = Path("data/interim")
    processed_dir: Path = Path("data/processed")
    exports_dir: Path = Path("data/exports")
    runs_dir: Path = Path("data/runs")
    reference_dir: Path = Path("data/reference")
    snapshots_dir: Path = Path("config/snapshots")
    source_excel: Path = Path("data/raw/Vivino-export.xlsx")


class PipelineConfig(BaseModel):
    cleaning: CleaningConfig
    enrichment: EnrichmentConfig
    scoring: ScoringConfig
    segments: SegmentsConfig
    paths: PathsConfig

    @property
    def hash(self) -> str:
        import hashlib
        import json

        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, default=str).encode()
        return hashlib.sha256(payload).hexdigest()[:8]
