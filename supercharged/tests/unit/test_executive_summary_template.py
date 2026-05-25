"""Executive summary Jinja template renders a complete Slurpini recommendation."""
from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

TEMPLATES = Path(__file__).resolve().parents[2] / "reports" / "templates"


@pytest.fixture
def env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture
def ctx() -> dict[str, object]:
    return {
        "run_id": "2026-05-25T12-00__abc12345",
        "config_hash": "abc12345",
        "totals": {"wines": 2986, "producers": 624, "regions": 51},
        "top_regions": [
            {
                "region": "Bolgheri Sassicaia",
                "weighted_rating": 4.62,
                "avg_price": 534,
                "wines": 76,
            },
            {
                "region": "Brunello di Montalcino",
                "weighted_rating": 4.27,
                "avg_price": 197,
                "wines": 404,
            },
            {
                "region": "Primitivo di Manduria",
                "weighted_rating": 4.26,
                "avg_price": 161,
                "wines": 95,
            },
        ],
        "top_producers": [
            {
                "producer_name": "Tenuta San Guido",
                "macro_region": "Tuscany",
                "recommendation": "Premium Brand Builder",
                "weighted_rating": 4.62,
                "avg_price": 534,
                "reason": "Premium Icon at the top of the prestige tier — defensible anchor.",
            },
            {
                "producer_name": "Cantine Due Palme",
                "macro_region": "Puglia",
                "recommendation": "Value Opportunity",
                "weighted_rating": 4.18,
                "avg_price": 14,
                "reason": "Hidden Gem in the value tier — above-median quality below median price.",
            },
        ],
        "hold": ["Tenuta San Guido", "Biondi-Santi"],
        "expand": ["Primitivo di Manduria", "Abruzzo"],
        "audit": ["producers with weighted rating ≥ 4.3 but < 10 reviews"],
    }


def test_renders_complete_summary(env: Environment, ctx: dict[str, object]) -> None:
    tpl = env.get_template("executive-summary.md.j2")
    out = tpl.render(**ctx)
    assert "# Executive Summary" in out
    assert "Bolgheri Sassicaia" in out
    assert "Primitivo di Manduria" in out
    assert "Tenuta San Guido" in out
    assert "Hold" in out
    assert "Expand" in out
    assert "Audit" in out
    assert "abc12345" in out
