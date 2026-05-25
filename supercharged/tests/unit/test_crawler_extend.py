"""Crawler extension — derived fields + optional Firecrawl backend."""
from __future__ import annotations

from unittest.mock import MagicMock

import polars as pl
import pytest

from cantinaiq.crawler.extend import (
    add_derived_fields,
    enrich_with_firecrawl,
    extract_vintage,
    first_word_producer,
)


def test_extract_vintage_from_name() -> None:
    assert extract_vintage("Tignanello 2018 Toscana IGT") == 2018
    assert extract_vintage("Brunello di Montalcino 1999") == 1999
    assert extract_vintage("No year here") is None
    assert extract_vintage(None) is None


def test_first_word_producer() -> None:
    assert first_word_producer("Antinori Tignanello 2018") == "Antinori"
    assert first_word_producer("  Gaja Barbaresco 2017") == "Gaja"
    assert first_word_producer("") is None
    assert first_word_producer(None) is None


def test_add_derived_fields_adds_two_columns() -> None:
    df = pl.DataFrame({"name": ["Antinori Tignanello 2018", "Gaja Sperss 2015"]})
    out = add_derived_fields(df)
    assert "vintage" in out.columns
    assert "producer_hint" in out.columns
    assert out["vintage"].to_list() == [2018, 2015]
    assert out["producer_hint"].to_list() == ["Antinori", "Gaja"]


def test_enrich_with_firecrawl_uses_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    scrape_resp = MagicMock()
    scrape_resp.markdown = (
        "Alcohol: 13.5%\nGrapes: Sangiovese, Cabernet Sauvignon\nFood pairings: red meat"
    )

    class FakeFirecrawl:
        last_url: str | None = None

        def __init__(self, api_key: str) -> None:  # noqa: ARG002
            pass

        def scrape_url(self, url: str, **kwargs: object) -> MagicMock:  # noqa: ARG002
            FakeFirecrawl.last_url = url
            return scrape_resp

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    monkeypatch.setattr("cantinaiq.crawler.extend._FirecrawlApp", FakeFirecrawl)

    result = enrich_with_firecrawl(
        wine_name="Tignanello 2018",
        url="https://www.vivino.com/wines/some-tignanello",
    )
    assert result["alcohol_percentage"] == 13.5
    assert "Sangiovese" in result["grape_varieties"]
    assert "red meat" in result["food_pairings"]
    assert FakeFirecrawl.last_url == "https://www.vivino.com/wines/some-tignanello"


def test_enrich_without_api_key_returns_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    result = enrich_with_firecrawl(wine_name="Anything", url="https://example.com")
    assert result == {}
