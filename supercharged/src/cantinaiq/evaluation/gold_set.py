"""Gold-set evaluation: recall of producer extraction against canonical top-50.

The gold-set lives in `data/reference/known_producers_top50.csv`. We measure
**recall** (how many gold producers appear in the pipeline output) under two
match modes:

  - exact:    pipeline `producer_name` == gold `canonical_name`.
  - contains: gold canonical name is a substring of any pipeline producer name
              (catches alias-mode failures where pipeline kept a fragment).

Precision is intentionally not computed — the pipeline contains hundreds of
real producers absent from the gold-set, so a precision number would be
meaningless. Recall is the load-bearing metric.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import polars as pl


@dataclass(frozen=True)
class GoldSetEval:
    gold_size: int
    producers_total: int
    recall_exact: float
    recall_contains: float
    matched_exact: list[str]
    matched_contains: list[str]
    missed: list[str]


def _read_gold(gold_csv: Path) -> list[str]:
    with Path(gold_csv).open() as f:
        return [
            row["canonical_name"].strip()
            for row in csv.DictReader(f)
            if row.get("canonical_name")
        ]


def _bidirectional_match(gold_name: str, seen: list[str]) -> bool:
    """Return True if `gold_name` matches any seen producer in either direction.

    Catches alias-mode partials in both directions:
      - pipeline kept full name: "Tenuta San Guido" → gold "Tenuta San Guido" ✓
      - pipeline kept fragment: "Antinori" → gold "Marchesi Antinori" ✓
      - pipeline expanded: "Tenuta Gaja" → gold "Gaja" ✓
    """
    g = gold_name.lower()
    for s in seen:
        sl = s.lower()
        if g in sl or sl in g:
            return True
    return False


def recall_at_alias(
    producers_parquet: Path,
    gold_csv: Path,
    match: Literal["exact", "contains"] = "exact",
) -> float:
    """Fraction of gold producers found in `producers_parquet.producer_name`."""
    gold = _read_gold(gold_csv)
    df = pl.read_parquet(producers_parquet)
    seen = df["producer_name"].drop_nulls().to_list()
    if match == "exact":
        seen_set = set(seen)
        hits = sum(1 for g in gold if g in seen_set)
    else:
        hits = sum(1 for g in gold if _bidirectional_match(g, seen))
    return hits / len(gold) if gold else 0.0


def evaluate_producer_extraction(
    producers_parquet: Path, gold_csv: Path
) -> GoldSetEval:
    gold = _read_gold(gold_csv)
    df = pl.read_parquet(producers_parquet)
    seen = df["producer_name"].drop_nulls().to_list()
    seen_set = set(seen)
    matched_exact = [g for g in gold if g in seen_set]
    matched_contains = [g for g in gold if _bidirectional_match(g, seen)]
    missed = [g for g in gold if g not in matched_contains]
    return GoldSetEval(
        gold_size=len(gold),
        producers_total=df.height,
        recall_exact=len(matched_exact) / len(gold) if gold else 0.0,
        recall_contains=len(matched_contains) / len(gold) if gold else 0.0,
        matched_exact=matched_exact,
        matched_contains=matched_contains,
        missed=missed,
    )
