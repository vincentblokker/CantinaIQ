"""Vivino crawler extension — bare deliverable.

The original crawler (see ../data/raw/Pyton-script.docx) collected:
    name, country, region, rating, rating_count, price

This script demonstrates extending that output with two additional fields
useful for partner selection:

    vintage         — extracted from the wine name (regex)
    producer_hint   — first-word heuristic (imperfect; see recommendation.md)

A real network-scraping extension would also fetch:
    alcohol_percentage   — from the Vivino product page
    grape_varieties      — from the Vivino product page
    food_pairings        — from the Vivino product page
    sustainability_claim — from the producer's website (where listed)

We stub those as `fetch_vivino_extras()` rather than running it, because:
1. Vivino's terms of service prohibit unauthorised scraping at volume.
2. The assignment's focus is on analysis, not scraping.
3. The demonstrative pattern (function signature + return shape) is enough
   to show how the existing pipeline would be extended.

Run:
    python crawler-extension.py
Produces:
    output/wines_extended.csv
"""

from __future__ import annotations

import io
import re
import warnings
from pathlib import Path
from typing import TypedDict

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw" / "Vivino-export.xlsx"
OUT_DIR = ROOT / "output"
OUT_FILE = OUT_DIR / "wines_extended.csv"

VINTAGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
TUPLE_RE = re.compile(r"^\(\s*'([^']*)'\s*,\s*\)$")


class VivinoExtras(TypedDict, total=False):
    alcohol_percentage: float | None
    grape_varieties: list[str]
    food_pairings: list[str]
    sustainability_claim: str | None


# ---------------------------------------------------------------------------
# Real extension: fields derivable from data we already have
# ---------------------------------------------------------------------------

def extract_vintage(name: str) -> int | None:
    """Return the four-digit year embedded in a wine name, or None."""
    if not isinstance(name, str):
        return None
    match = VINTAGE_RE.search(name)
    return int(match.group(1)) if match else None


def first_word_producer(name: str) -> str | None:
    """First-word heuristic for producer name. Imperfect — see recommendation.md."""
    if not isinstance(name, str) or not name.strip():
        return None
    return name.split()[0]


# ---------------------------------------------------------------------------
# Stubbed extension: fields that would require network scraping
# ---------------------------------------------------------------------------

def fetch_vivino_extras(wine_name: str) -> VivinoExtras:  # noqa: ARG001
    """Placeholder. In a production extension this would:

    1. Search Vivino for the wine and resolve a stable product ID.
    2. Fetch the product page.
    3. Parse alcohol_percentage, grape_varieties, food_pairings.
    4. Optionally follow producer URLs to extract sustainability claims.

    Returns an empty dict here so the rest of the pipeline keeps working
    without network access.
    """
    return {}


# ---------------------------------------------------------------------------
# Shared cleaning utilities (same as the notebook)
# ---------------------------------------------------------------------------

def unwrap_tuple(value: str) -> str:
    if not isinstance(value, str):
        return value
    match = TUPLE_RE.match(value.strip())
    return match.group(1) if match else value.strip()


def fix_mojibake(value: str) -> str:
    if not isinstance(value, str):
        return value
    try:
        return value.encode("mac_roman").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def load_raw(path: Path) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    frames = []
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None, skiprows=1)
        if raw.empty:
            continue
        csv_text = "\n".join(raw[0].dropna().astype(str).tolist())
        df = pd.read_csv(
            io.StringIO(csv_text),
            names=["name", "country", "region", "rating", "rating_count", "price"],
            on_bad_lines="skip",
            engine="python",
        )
        df["source_sheet"] = sheet
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    print(f"Reading {RAW}")
    wines = load_raw(RAW)
    print(f"  raw rows: {len(wines):,}")

    wines["country"] = wines["country"].apply(unwrap_tuple).apply(fix_mojibake)
    wines["region"] = wines["region"].apply(unwrap_tuple).apply(fix_mojibake)
    wines["rating"] = pd.to_numeric(wines["rating"], errors="coerce")
    wines["rating_count"] = pd.to_numeric(wines["rating_count"], errors="coerce")
    wines["price"] = pd.to_numeric(wines["price"], errors="coerce")

    italian = wines[wines["country"] == "Italië"].copy()
    italian = italian.drop_duplicates(subset=["name", "rating", "price"])
    italian = italian.dropna(subset=["rating", "price", "rating_count"])
    italian = italian[
        (italian["rating_count"] > 0)
        & (italian["price"] > 0)
        & (italian["rating"].between(0, 5))
    ]
    print(f"  italian, deduped, validated: {len(italian):,}")

    italian["vintage"] = italian["name"].apply(extract_vintage)
    italian["producer_hint"] = italian["name"].apply(first_word_producer)

    extras_sample = [fetch_vivino_extras(n) for n in italian["name"].head(5)]
    print(f"  fetch_vivino_extras() stub returned: {extras_sample}")

    OUT_DIR.mkdir(exist_ok=True)
    italian.to_csv(OUT_FILE, index=False)
    print(f"Wrote {OUT_FILE}  ({len(italian):,} rows, {italian.shape[1]} columns)")
    print(f"Columns: {list(italian.columns)}")


if __name__ == "__main__":
    main()
