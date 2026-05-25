"""Sustainability cert lookup for Italian wine producers."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cantinaiq.sustainability.lookup import (
    CertificationResult,
    classify_certification,
    lookup_sustainability,
)


def test_classify_certification_from_markdown_federbio() -> None:
    md = "## Antinori\n\nOperatore biologico certificato FederBio (codice IT-BIO-007)."
    assert classify_certification(md, "Antinori") == "FederBio"


def test_classify_certification_from_markdown_demeter() -> None:
    md = "Azienda Querciabella - certificazione Demeter biodinamica."
    assert classify_certification(md, "Querciabella") == "Demeter"


def test_classify_certification_no_match() -> None:
    md = "Random wine winery in Italy."
    assert classify_certification(md, "Random") is None


def test_lookup_sustainability_uses_firecrawl(monkeypatch: pytest.MonkeyPatch) -> None:
    scrape_resp = MagicMock()
    scrape_resp.markdown = "Antinori - FederBio biologico"

    class FakeFirecrawl:
        def __init__(self, api_key: str) -> None:  # noqa: ARG002
            pass

        def scrape_url(self, url: str, **kwargs: object) -> MagicMock:  # noqa: ARG002
            return scrape_resp

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    monkeypatch.setattr(
        "cantinaiq.sustainability.lookup._FirecrawlApp", FakeFirecrawl
    )

    result = lookup_sustainability(producer="Antinori")
    assert isinstance(result, CertificationResult)
    assert result.certification == "FederBio"
    assert result.source.startswith("https://")


def test_lookup_sustainability_no_api_key_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    result = lookup_sustainability(producer="Anyone")
    assert result.certification is None
