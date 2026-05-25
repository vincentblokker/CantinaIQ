"""Live Vivino enrichment: alcohol%, grapes, food pairings for top-N wines."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cantinaiq.vivino_live.enrich import enrich_wines, parse_wine_page


def test_parse_wine_page_extracts_alcohol_grapes_pairings() -> None:
    md = (
        "# Tignanello 2018\n\n"
        "**Alcohol:** 14.5%\n"
        "**Grapes:** Sangiovese, Cabernet Sauvignon, Cabernet Franc\n"
        "**Food pairings:** Beef, Lamb, Game\n"
    )
    parsed = parse_wine_page(md)
    assert parsed["alcohol_percentage"] == 14.5
    assert "Sangiovese" in parsed["grape_varieties"]
    assert "Beef" in parsed["food_pairings"]


def test_parse_wine_page_returns_partial_on_missing_fields() -> None:
    md = "Alcohol: 13.0%\nNo grapes listed."
    parsed = parse_wine_page(md)
    assert parsed["alcohol_percentage"] == 13.0
    assert parsed.get("grape_varieties") in (None, [])


def test_enrich_wines_uses_cache_and_firecrawl(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    scrape_resp = MagicMock()
    scrape_resp.markdown = "Alcohol: 13.5%\nGrapes: Sangiovese"

    call_log: list[str] = []

    class FakeFirecrawl:
        def __init__(self, api_key: str) -> None:  # noqa: ARG002
            pass

        def scrape(self, url: str, **kwargs: object) -> MagicMock:  # noqa: ARG002
            call_log.append(url)
            return scrape_resp

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    monkeypatch.setattr("cantinaiq.vivino_live.enrich._FirecrawlApp", FakeFirecrawl)

    cache_dir = tmp_path / "cache"
    wines = [{"name": "Tignanello 2018", "id": "abc"}]
    out = enrich_wines(wines, cache_dir=cache_dir, rate_limit_ms=0)
    assert out[0]["alcohol_percentage"] == 13.5

    out2 = enrich_wines(wines, cache_dir=cache_dir, rate_limit_ms=0)
    assert out2[0]["alcohol_percentage"] == 13.5
    assert len(call_log) == 1  # cache hit on second call
