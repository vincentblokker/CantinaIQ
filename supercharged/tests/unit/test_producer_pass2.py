import shutil
from pathlib import Path
from typing import Any

from cantinaiq.enrichment.producer.cache import LLMCache
from cantinaiq.enrichment.producer.pass2_llm import Pass2Resolver


class _RecordingClient:
    def __init__(self) -> None:
        self.calls = 0

    def resolve_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.calls += 1
        return [
            {
                "id": e["id"],
                "producer": "MockProducer",
                "inferred_grape_or_style": None,
                "confidence": "Medium",
                "reasoning": "mocked",
            }
            for e in entries
        ]


def test_pass2_uses_cache_when_available(tmp_path: Path, llm_cache_fixture: Path) -> None:
    cache_path = tmp_path / "cache.parquet"
    shutil.copy(llm_cache_fixture, cache_path)
    client = _RecordingClient()
    resolver = Pass2Resolver(
        cache=LLMCache(path=cache_path, model_version="claude-haiku-4-5-20251001"),
        client=client,
        batch_size=50,
    )
    candidates = resolver.resolve(
        [
            {"id": 1, "wine_name": "Tignanello 2019", "region": "Toscana"},
            {"id": 2, "wine_name": "Sassicaia 2018", "region": "Toscana"},
        ]
    )
    assert client.calls == 0  # all served from cache
    assert candidates[1].name == "Marchesi Antinori"
    assert candidates[2].name == "Tenuta San Guido"


def test_pass2_calls_client_for_misses_then_caches(tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.parquet"
    client = _RecordingClient()
    cache = LLMCache(path=cache_path, model_version="claude-haiku-4-5-20251001")
    resolver = Pass2Resolver(cache=cache, client=client, batch_size=50)
    candidates = resolver.resolve(
        [
            {"id": 1, "wine_name": "Unknown Wine 2020", "region": "Toscana"},
        ]
    )
    assert client.calls == 1
    assert candidates[1].name == "MockProducer"
    # Re-resolve must be cache-hit only — no new API calls.
    client2 = _RecordingClient()
    resolver2 = Pass2Resolver(
        cache=LLMCache(path=cache_path, model_version="claude-haiku-4-5-20251001"),
        client=client2,
        batch_size=50,
    )
    resolver2.resolve([{"id": 1, "wine_name": "Unknown Wine 2020", "region": "Toscana"}])
    assert client2.calls == 0
