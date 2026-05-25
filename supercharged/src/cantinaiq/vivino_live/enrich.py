"""Live Vivino enrichment: alcohol %, grape varieties, food pairings.

This module is opt-in: nothing runs unless the CLI is invoked with
`--with-network` and `FIRECRAWL_API_KEY` is set. Even then, every URL is
cached on disk (1-day TTL by default), so repeat runs do not re-hit the
network. Always respects a rate-limit between fresh calls.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

from cantinaiq.vivino_live.cache import WineCache

try:
    from firecrawl import Firecrawl as _FirecrawlApp  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    try:
        from firecrawl import FirecrawlApp as _FirecrawlApp  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover
        _FirecrawlApp = None  # type: ignore[assignment,misc]

ALCOHOL_RE = re.compile(r"alcohol[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE)
GRAPES_RE = re.compile(r"grapes?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)
PAIRINGS_RE = re.compile(r"food\s*pairings?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)


def _clean_token(s: str) -> str:
    """Strip whitespace and leading markdown bold/list noise."""
    return re.sub(r"^[\s*_\-]+|[\s*_]+$", "", s)


def parse_wine_page(markdown: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if m := ALCOHOL_RE.search(markdown):
        out["alcohol_percentage"] = float(m.group(1))
    if m := GRAPES_RE.search(markdown):
        items = [_clean_token(g) for g in m.group(1).split(",")]
        out["grape_varieties"] = [g for g in items if g]
    if m := PAIRINGS_RE.search(markdown):
        items = [_clean_token(g) for g in m.group(1).split(",")]
        out["food_pairings"] = [g for g in items if g]
    return out


def _wine_url(name: str) -> str:
    return "https://www.vivino.com/search/wines?q=" + name.replace(" ", "+")


def _scrape_markdown(app: object, url: str) -> str:
    """Compatibility shim for firecrawl-py 2.x (`scrape_url`) and 3.x (`scrape`)."""
    if hasattr(app, "scrape"):
        resp = app.scrape(url, formats=["markdown"])  # type: ignore[attr-defined]
    else:
        resp = app.scrape_url(url, formats=["markdown"])  # type: ignore[attr-defined]
    return getattr(resp, "markdown", None) or ""


def enrich_wines(
    wines: list[dict[str, Any]],
    cache_dir: Path,
    rate_limit_ms: int = 500,
) -> list[dict[str, Any]]:
    """Enrich each wine dict with alcohol/grapes/pairings via Firecrawl + diskcache."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    cache = WineCache(cache_dir)
    out: list[dict[str, Any]] = []
    app = None
    if api_key and _FirecrawlApp is not None:
        app = _FirecrawlApp(api_key=api_key)
    try:
        for w in wines:
            url = _wine_url(w["name"])
            cached = cache.get(url)
            if cached is not None:
                out.append({**w, **cached})
                continue
            extras: dict[str, Any] = {}
            if app is not None:
                try:
                    md = _scrape_markdown(app, url)
                    extras = parse_wine_page(md)
                    cache.set(url, extras)
                except Exception:  # noqa: BLE001
                    pass
                if rate_limit_ms > 0:
                    time.sleep(rate_limit_ms / 1000)
            out.append({**w, **extras})
    finally:
        cache.close()
    return out
