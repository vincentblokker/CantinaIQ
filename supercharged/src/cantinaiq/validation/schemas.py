"""Pandera schemas — used both in the validation stage and in the test suite."""

from __future__ import annotations

import pandera.polars as pa
from pandera.typing.polars import Series


class CleanedSchema(pa.DataFrameModel):
    wine_name: Series[str] = pa.Field(nullable=False, str_length={"min_value": 1})
    wine_name_normalised: Series[str] = pa.Field(nullable=False, str_length={"min_value": 1})
    country: Series[str] = pa.Field(isin=["Italy"])
    region: Series[str] = pa.Field(nullable=False, str_length={"min_value": 1})
    rating: Series[float] = pa.Field(ge=0, le=5)
    rating_count: Series[int] = pa.Field(ge=1)
    price: Series[float] = pa.Field(gt=0)
    vintage: Series[int] = pa.Field(ge=1900, le=2100, nullable=True)
    producer_hint: Series[str] = pa.Field(nullable=True)
    source_sheet: Series[str] = pa.Field(nullable=False)
    run_config_hash: Series[str] = pa.Field(str_length=8)

    class Config:
        strict = True
        coerce = False


class EnrichedSchema(CleanedSchema):
    producer_name: Series[str] = pa.Field(nullable=True)
    macro_region: Series[str] = pa.Field(nullable=False)
    price_segment: Series[str] = pa.Field(
        isin=["Entry", "Accessible Premium", "Premium", "Prestige"]
    )
    confidence_segment: Series[str] = pa.Field(
        isin=["Low Confidence", "Emerging Signal", "Reliable Signal", "Strong Market Signal"]
    )
    enrichment_confidence: Series[str] = pa.Field(isin=["High", "Medium", "Low", "None"])
    inferred_grape_or_style: Series[str] = pa.Field(nullable=True)


class ScoredWineSchema(EnrichedSchema):
    weighted_rating: Series[float] = pa.Field(ge=0, le=5)
    value_score: Series[float] = pa.Field(gt=0)
    composite_score: Series[float] = pa.Field(ge=0, le=1)
    market_segment: Series[str] = pa.Field(
        isin=[
            "Premium Icon",
            "Hidden Gem",
            "Commercial Value",
            "Low Confidence Niche",
            "Overpriced Risk",
        ]
    )


class ScoredProducerSchema(pa.DataFrameModel):
    producer_name: Series[str] = pa.Field(nullable=False)
    macro_region: Series[str] = pa.Field(nullable=False)
    wines_in_dataset: Series[int] = pa.Field(ge=1)
    total_reviews: Series[int] = pa.Field(ge=1)
    avg_price: Series[float] = pa.Field(gt=0)
    weighted_rating: Series[float] = pa.Field(ge=0, le=5)
    value_score: Series[float] = pa.Field(gt=0)
    composite_score: Series[float] = pa.Field(ge=0, le=1)
    market_segment: Series[str] = pa.Field(
        isin=[
            "Premium Icon",
            "Hidden Gem",
            "Commercial Value",
            "Low Confidence Niche",
            "Overpriced Risk",
        ]
    )
    recommendation: Series[str] = pa.Field(
        isin=["Target", "Monitor", "Premium Brand Builder", "Value Opportunity", "Avoid for Now"]
    )
    run_config_hash: Series[str] = pa.Field(str_length=8)

    class Config:
        strict = True
        coerce = False


class ScoredRegionSchema(pa.DataFrameModel):
    region: Series[str] = pa.Field(nullable=False)
    macro_region: Series[str] = pa.Field(nullable=False)
    wines_in_dataset: Series[int] = pa.Field(ge=1)
    total_reviews: Series[int] = pa.Field(ge=1)
    avg_price: Series[float] = pa.Field(gt=0)
    weighted_rating: Series[float] = pa.Field(ge=0, le=5)
    value_score: Series[float] = pa.Field(gt=0)
    low_sample_region: Series[bool]
    run_config_hash: Series[str] = pa.Field(str_length=8)

    class Config:
        strict = True
        coerce = False
