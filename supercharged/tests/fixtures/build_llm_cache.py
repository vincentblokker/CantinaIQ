"""Pre-populate the LLM cache for the 5 fixture wines that pass-1 misses,
so tests never call the API."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

MODEL = "claude-haiku-4-5-20251001"
HERE = Path(__file__).parent

# (wine_name, region, producer, grape, confidence, reasoning)
SEEDS: list[tuple[str, str, str, str, str, str]] = [
    (
        "Tignanello 2019",
        "Toscana",
        "Marchesi Antinori",
        "Sangiovese-Cabernet blend",
        "High",
        "Tignanello is Antinori's flagship Super Tuscan",
    ),
    (
        "Sassicaia 2018",
        "Toscana",
        "Tenuta San Guido",
        "Cabernet Sauvignon-Cabernet Franc",
        "High",
        "Sassicaia is produced exclusively by Tenuta San Guido",
    ),
    (
        "Solaia 2017",
        "Toscana",
        "Marchesi Antinori",
        "Cabernet Sauvignon-Sangiovese",
        "High",
        "Solaia is Antinori's iconic Cabernet-dominant Super Tuscan",
    ),
    (
        "Ornellaia 2018",
        "Toscana",
        "Tenuta dell'Ornellaia",
        "Bordeaux blend",
        "High",
        "Ornellaia is the eponymous wine of Tenuta dell'Ornellaia",
    ),
    (
        "Masseto 2017",
        "Toscana",
        "Tenuta Masseto",
        "Merlot",
        "High",
        "Masseto is a 100% Merlot from Tenuta Masseto",
    ),
]


def cache_key(wine: str, region: str) -> str:
    return hashlib.sha256(f"{wine}|{region}|{MODEL}".encode()).hexdigest()


def main() -> None:
    now = datetime.now(UTC)
    rows = []
    for wine, region, producer, grape, conf, reason in SEEDS:
        rows.append(
            {
                "cache_key": cache_key(wine, region),
                "wine_name": wine,
                "region": region,
                "producer": producer,
                "inferred_grape_or_style": grape,
                "confidence": conf,
                "reasoning": reason,
                "model_version": MODEL,
                "created_at": now,
            }
        )
    out = HERE / "llm_cache.parquet"
    pl.DataFrame(rows).write_parquet(out)
    print(f"wrote {out} with {len(rows)} cached entries")


if __name__ == "__main__":
    main()
