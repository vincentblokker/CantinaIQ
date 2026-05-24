"""Persistent Parquet-backed LLM-call cache."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl


def cache_key(wine_name: str, region: str, model_version: str) -> str:
    payload = f"{wine_name}|{region}|{model_version}".encode()
    return hashlib.sha256(payload).hexdigest()


class LLMCache:
    def __init__(self, path: Path, model_version: str):
        self.path = Path(path)
        self.model_version = model_version
        self._new_rows: list[dict[str, Any]] = []
        if self.path.exists():
            self._loaded: pl.DataFrame = pl.read_parquet(self.path)
        else:
            self._loaded = pl.DataFrame(
                schema={
                    "cache_key": pl.String,
                    "wine_name": pl.String,
                    "region": pl.String,
                    "producer": pl.String,
                    "inferred_grape_or_style": pl.String,
                    "confidence": pl.String,
                    "reasoning": pl.String,
                    "model_version": pl.String,
                    "created_at": pl.Datetime("us", "UTC"),
                }
            )

    def get(self, wine_name: str, region: str) -> dict[str, Any] | None:
        key = cache_key(wine_name, region, self.model_version)
        hits = self._loaded.filter(
            (pl.col("cache_key") == key) & (pl.col("model_version") == self.model_version)
        )
        if hits.height == 0:
            return None
        return hits.head(1).to_dicts()[0]

    def put(
        self,
        wine_name: str,
        region: str,
        producer: str | None,
        inferred_grape_or_style: str | None,
        confidence: str,
        reasoning: str,
    ) -> None:
        self._new_rows.append(
            {
                "cache_key": cache_key(wine_name, region, self.model_version),
                "wine_name": wine_name,
                "region": region,
                "producer": producer,
                "inferred_grape_or_style": inferred_grape_or_style,
                "confidence": confidence,
                "reasoning": reasoning,
                "model_version": self.model_version,
                "created_at": datetime.now(UTC),
            }
        )

    def flush(self) -> None:
        if not self._new_rows:
            return
        new_df = pl.DataFrame(self._new_rows)
        combined = pl.concat([self._loaded, new_df], how="diagonal_relaxed")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        combined.write_parquet(self.path)
        self._loaded = combined
        self._new_rows.clear()
