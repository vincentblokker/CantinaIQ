from pathlib import Path

from cantinaiq.enrichment.producer.cache import LLMCache, cache_key


def test_cache_key_is_stable() -> None:
    a = cache_key("Tignanello 2019", "Toscana", "claude-haiku-4-5-20251001")
    b = cache_key("Tignanello 2019", "Toscana", "claude-haiku-4-5-20251001")
    assert a == b
    assert a != cache_key("Sassicaia 2018", "Toscana", "claude-haiku-4-5-20251001")


def test_cache_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "cache.parquet"
    cache = LLMCache(path=path, model_version="claude-haiku-4-5-20251001")
    cache.put(
        wine_name="Tignanello 2019",
        region="Toscana",
        producer="Marchesi Antinori",
        inferred_grape_or_style="Sangiovese blend",
        confidence="High",
        reasoning="Tignanello is Antinori's flagship",
    )
    cache.flush()
    cache2 = LLMCache(path=path, model_version="claude-haiku-4-5-20251001")
    hit = cache2.get("Tignanello 2019", "Toscana")
    assert hit is not None
    assert hit["producer"] == "Marchesi Antinori"


def test_cache_miss_on_model_version_change(tmp_path: Path) -> None:
    path = tmp_path / "cache.parquet"
    cache = LLMCache(path=path, model_version="model-a")
    cache.put("Wine X 2020", "Toscana", "Producer X", None, "High", "n/a")
    cache.flush()
    cache_b = LLMCache(path=path, model_version="model-b")
    assert cache_b.get("Wine X 2020", "Toscana") is None
