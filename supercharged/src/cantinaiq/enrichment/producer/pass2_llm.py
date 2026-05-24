"""Pass-2 LLM disambiguation with persistent cache."""

from __future__ import annotations

import json
import os
from typing import Any, Protocol

from cantinaiq.enrichment.producer.cache import LLMCache
from cantinaiq.enrichment.producer.models import ProducerCandidate

SYSTEM_PROMPT = """You are extracting Italian wine producer names from raw Vivino wine entries.

For each entry, return JSON with:
  - producer: the canonical producer/winery name. Use full Italian honorific
    where standard ("Tenuta San Guido", not "San Guido"). If you are not
    confident the wine name actually contains a producer, return null.
  - inferred_grape_or_style: e.g. "Sangiovese", "Nebbiolo", "Sangiovese-
    dominant blend", or null if uncertain.
  - confidence: "High" | "Medium" | "Low".
  - reasoning: <=15 words.

Rules:
  - Producer != appellation. "Brunello di Montalcino" is an appellation.
  - Producer != wine name. "Sassicaia" is a wine; the producer is "Tenuta San Guido".
  - If no producer signal, return null with confidence "Low".

Return: JSON array of { id, producer, inferred_grape_or_style, confidence, reasoning }."""


class LLMClient(Protocol):
    def resolve_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]: ...


class AnthropicLLMClient:
    """Real client. Only constructed on explicit opt-in; never auto-instantiated."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001", temperature: float = 0.0):
        from anthropic import Anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def resolve_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        user_msg = "Entries:\n" + json.dumps(entries, ensure_ascii=False)
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=self.temperature,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(f"Unexpected LLM output (no JSON array): {text[:200]!r}")
        parsed: list[dict[str, Any]] = json.loads(text[start : end + 1])
        return parsed


class Pass2Resolver:
    def __init__(self, cache: LLMCache, client: LLMClient, batch_size: int = 50):
        self.cache = cache
        self.client = client
        self.batch_size = batch_size
        self.fresh_calls = 0  # incremented per LLM batch call (not per entry)

    def resolve(self, entries: list[dict[str, Any]]) -> dict[int, ProducerCandidate]:
        out: dict[int, ProducerCandidate] = {}
        misses: list[dict[str, Any]] = []
        for e in entries:
            hit = self.cache.get(e["wine_name"], e["region"])
            if hit is not None:
                out[e["id"]] = ProducerCandidate(
                    name=hit["producer"],
                    confidence=hit["confidence"],
                    method=f"llm-cache:{hit['confidence']}",
                    inferred_grape_or_style=hit.get("inferred_grape_or_style"),
                )
            else:
                misses.append(e)
        for i in range(0, len(misses), self.batch_size):
            batch = misses[i : i + self.batch_size]
            results = self.client.resolve_batch(batch)
            self.fresh_calls += 1
            for entry, res in zip(batch, results, strict=False):
                self.cache.put(
                    wine_name=entry["wine_name"],
                    region=entry["region"],
                    producer=res.get("producer"),
                    inferred_grape_or_style=res.get("inferred_grape_or_style"),
                    confidence=res.get("confidence", "Low"),
                    reasoning=res.get("reasoning", ""),
                )
                out[entry["id"]] = ProducerCandidate(
                    name=res.get("producer"),
                    confidence=res.get("confidence", "Low"),
                    method=f"llm-fresh:{res.get('confidence', 'Low')}",
                    inferred_grape_or_style=res.get("inferred_grape_or_style"),
                )
        self.cache.flush()
        return out
