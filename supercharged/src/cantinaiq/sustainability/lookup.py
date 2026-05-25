"""Sustainability-certification lookup via Firecrawl.

Strategy: query Firecrawl with the producer name + an Italian organic
directory (FederBio operator search), then parse the returned markdown
for unambiguous certification keywords. Demeter is checked via the
international Demeter producer directory.

This is a coarse, public-data signal — not a substitute for verifying
certificates with the producer directly. Hits should be treated as
"strong leads to verify", not as ground truth.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal

try:
    from firecrawl import FirecrawlApp as _FirecrawlApp  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    try:
        from firecrawl import Firecrawl as _FirecrawlApp  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover
        _FirecrawlApp = None  # type: ignore[assignment,misc]


Certification = Literal["FederBio", "Demeter", "Both"]

FEDERBIO_KEYWORDS = re.compile(
    r"federbio|operatore biologico|certificazione biologica|IT-BIO-", re.IGNORECASE
)
DEMETER_KEYWORDS = re.compile(r"demeter|biodinamic|biodynamic", re.IGNORECASE)


@dataclass(frozen=True)
class CertificationResult:
    producer: str
    certification: Certification | None
    source: str


def classify_certification(markdown: str, producer: str) -> Certification | None:
    """Return the certification hint from raw markdown that mentions `producer`."""
    if producer.lower() not in markdown.lower():
        return None
    has_federbio = bool(FEDERBIO_KEYWORDS.search(markdown))
    has_demeter = bool(DEMETER_KEYWORDS.search(markdown))
    if has_federbio and has_demeter:
        return "Both"
    if has_federbio:
        return "FederBio"
    if has_demeter:
        return "Demeter"
    return None


def _build_search_urls(producer: str) -> list[str]:
    name = producer.replace(" ", "+")
    return [
        f"https://www.federbio.it/operatori/?ricerca={name}",
        f"https://www.demeter.net/producers/?search={name}",
    ]


def _scrape_markdown(app: object, url: str) -> str:
    """Compatibility shim for firecrawl-py 2.x (`scrape_url`) and 3.x (`scrape`)."""
    if hasattr(app, "scrape"):  # 3.x
        resp = app.scrape(url, formats=["markdown"])  # type: ignore[attr-defined]
    else:  # 2.x
        resp = app.scrape_url(url, formats=["markdown"])  # type: ignore[attr-defined]
    return getattr(resp, "markdown", None) or ""


def lookup_sustainability(producer: str) -> CertificationResult:
    """Query directories and return a `CertificationResult` for `producer`."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key or _FirecrawlApp is None:
        return CertificationResult(producer=producer, certification=None, source="(stub)")
    app = _FirecrawlApp(api_key=api_key)
    for url in _build_search_urls(producer):
        try:
            md = _scrape_markdown(app, url)
            cert = classify_certification(md, producer)
            if cert is not None:
                return CertificationResult(
                    producer=producer, certification=cert, source=url
                )
        except Exception:  # noqa: BLE001 — best-effort lookup, skip failures
            continue
    return CertificationResult(producer=producer, certification=None, source="(no match)")
