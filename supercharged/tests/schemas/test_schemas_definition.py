from typing import Any

import polars as pl
import pytest
from pandera.errors import SchemaError, SchemaErrors

from cantinaiq.validation.schemas import (
    CleanedSchema,
    EnrichedSchema,
    ScoredProducerSchema,
    ScoredRegionSchema,
    ScoredWineSchema,
)


def _valid_cleaned_row() -> dict[str, Any]:
    return {
        "wine_name": "Test 2020",
        "wine_name_normalised": "test 2020",
        "country": "Italy",
        "region": "Toscana",
        "rating": 4.2,
        "rating_count": 120,
        "price": 25.0,
        "vintage": 2020,
        "producer_hint": "Test",
        "source_sheet": "Italy",
        "run_config_hash": "a3f8e1c2",
    }


def test_cleaned_schema_accepts_valid_row() -> None:
    df = pl.DataFrame([_valid_cleaned_row()])
    CleanedSchema.validate(df, lazy=True)


def test_cleaned_schema_rejects_non_italy() -> None:
    bad = _valid_cleaned_row() | {"country": "France"}
    df = pl.DataFrame([bad])
    with pytest.raises((SchemaError, SchemaErrors)):
        CleanedSchema.validate(df, lazy=True)


def test_cleaned_schema_rejects_rating_above_five() -> None:
    bad = _valid_cleaned_row() | {"rating": 5.4}
    df = pl.DataFrame([bad])
    with pytest.raises((SchemaError, SchemaErrors)):
        CleanedSchema.validate(df, lazy=True)


def test_enriched_schema_accepts_valid_row() -> None:
    row = _valid_cleaned_row() | {
        "producer_name": "Test",
        "macro_region": "Toscana",
        "price_segment": "Accessible Premium",
        "confidence_segment": "Emerging Signal",
        "enrichment_confidence": "High",
        "inferred_grape_or_style": "Sangiovese",
    }
    df = pl.DataFrame([row])
    EnrichedSchema.validate(df, lazy=True)


def test_scored_wine_schema_accepts_valid_row() -> None:
    row = _valid_cleaned_row() | {
        "producer_name": "Test",
        "macro_region": "Toscana",
        "price_segment": "Accessible Premium",
        "confidence_segment": "Emerging Signal",
        "enrichment_confidence": "High",
        "inferred_grape_or_style": "Sangiovese",
        "weighted_rating": 4.15,
        "value_score": 1.27,
        "composite_score": 0.68,
        "market_segment": "Commercial Value",
    }
    df = pl.DataFrame([row])
    ScoredWineSchema.validate(df, lazy=True)


def test_scored_producer_schema_smoke() -> None:
    df = pl.DataFrame(
        [
            {
                "producer_name": "Test",
                "macro_region": "Toscana",
                "wines_in_dataset": 4,
                "total_reviews": 1200,
                "avg_price": 32.5,
                "weighted_rating": 4.2,
                "value_score": 1.3,
                "composite_score": 0.71,
                "market_segment": "Hidden Gem",
                "recommendation": "Target",
                "run_config_hash": "a3f8e1c2",
            }
        ]
    )
    ScoredProducerSchema.validate(df, lazy=True)


def test_scored_region_schema_smoke() -> None:
    df = pl.DataFrame(
        [
            {
                "region": "Toscana",
                "macro_region": "Toscana",
                "wines_in_dataset": 250,
                "total_reviews": 32000,
                "avg_price": 48.0,
                "weighted_rating": 4.15,
                "value_score": 1.21,
                "low_sample_region": False,
                "run_config_hash": "a3f8e1c2",
            }
        ]
    )
    ScoredRegionSchema.validate(df, lazy=True)
