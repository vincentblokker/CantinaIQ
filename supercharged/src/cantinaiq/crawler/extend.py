"""Crawler extension for the Vivino dataset.

Adds derived fields computable from existing data (`vintage`, `producer_hint`)
and — behind a feature flag — fetches richer wine attributes via Firecrawl.

Default mode is *stub* (no network): `enrich_with_firecrawl()` returns an
empty dict unless `FIRECRAWL_API_KEY` is set AND the caller opts in. This
keeps the test-suite and offline runs deterministic.
"""

from __future__ import annotations

import os
import re
from typing import Any

import polars as pl

VINTAGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
ALCOHOL_RE = re.compile(r"alcohol[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE)
GRAPES_RE = re.compile(r"grapes?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)
PAIRINGS_RE = re.compile(r"food\s*pairings?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)

# Indirection so tests can monkeypatch the SDK without touching the import line.
try:
    from firecrawl import FirecrawlApp as _FirecrawlApp  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    try:
        from firecrawl import Firecrawl as _FirecrawlApp  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover
        _FirecrawlApp = None  # type: ignore[assignment,misc]


def extract_vintage(name: str | None) -> int | None:
    """Return the four-digit year embedded in a wine name, or None."""
    if not isinstance(name, str):
        return None
    m = VINTAGE_RE.search(name)
    return int(m.group(1)) if m else None


def first_word_producer(name: str | None) -> str | None:
    """First-word heuristic for producer name."""
    if not isinstance(name, str) or not name.strip():
        return None
    return name.split()[0]


def _name_column(df: pl.DataFrame) -> str:
    """Return the column that holds the wine name (handles both schemas)."""
    for cand in ("name", "wine_name"):
        if cand in df.columns:
            return cand
    raise KeyError(f"No name column found; expected one of: name, wine_name. Got: {df.columns}")


def add_derived_fields(df: pl.DataFrame) -> pl.DataFrame:
    """Return `df` with `vintage` and `producer_hint` columns appended."""
    col = _name_column(df)
    return df.with_columns(
        pl.col(col).map_elements(extract_vintage, return_dtype=pl.Int64).alias("vintage"),
        pl.col(col).map_elements(first_word_producer, return_dtype=pl.Utf8).alias("producer_hint"),
    )


def _parse_markdown(md: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if m := ALCOHOL_RE.search(md):
        out["alcohol_percentage"] = float(m.group(1))
    if m := GRAPES_RE.search(md):
        out["grape_varieties"] = [g.strip() for g in m.group(1).split(",") if g.strip()]
    if m := PAIRINGS_RE.search(md):
        out["food_pairings"] = m.group(1).strip()
    return out


def enrich_with_firecrawl(wine_name: str, url: str) -> dict[str, Any]:  # noqa: ARG001
    """Scrape a wine page via Firecrawl and parse alcohol/grapes/pairings.

    Returns an empty dict if `FIRECRAWL_API_KEY` is unset (stub mode) or if
    the SDK is not installed. Caller is responsible for any rate-limit /
    backoff / robots.txt logic.
    """
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key or _FirecrawlApp is None:
        return {}
    app = _FirecrawlApp(api_key=api_key)
    resp = app.scrape_url(url, formats=["markdown"])
    md = getattr(resp, "markdown", None) or (resp.get("markdown") if isinstance(resp, dict) else "") or ""
    return _parse_markdown(md)
