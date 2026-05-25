"""Thin diskcache wrapper used by the enrichment loop.

One-day TTL by default. The cache key is the wine URL (or a deterministic
identifier the caller supplies). The cache lives at the path provided so
test runs can pin it to a tmp_path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import diskcache  # type: ignore[import-untyped]


class WineCache:
    def __init__(self, cache_dir: Path, ttl_seconds: int = 86400) -> None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = diskcache.Cache(str(cache_dir))
        self._ttl = ttl_seconds

    def get(self, key: str) -> Any | None:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache.set(key, value, expire=self._ttl)

    def close(self) -> None:
        self._cache.close()
