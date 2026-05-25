"""OpenRouter LLM client — implements the LLMClient Protocol via the openai SDK.

OpenRouter exposes an OpenAI-compatible Chat Completions endpoint at
https://openrouter.ai/api/v1, so we reuse the openai SDK rather than writing
a bespoke HTTP layer.
"""

from __future__ import annotations

import json
import os
from typing import Any

from cantinaiq.enrichment.producer.pass2_llm import SYSTEM_PROMPT


class OpenRouterLLMClient:
    """Real client. Only constructed on explicit opt-in via OPENROUTER_API_KEY."""

    def __init__(
        self,
        model: str | None = None,
        temperature: float = 0.0,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        from openai import OpenAI

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model or os.environ.get("OPENROUTER_MODEL") or "anthropic/claude-3.5-haiku"
        self.temperature = temperature
        referer = os.environ.get("OPENROUTER_REFERER")
        self._extra_headers: dict[str, str] = {"HTTP-Referer": referer} if referer else {}

    def resolve_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        user_msg = "Entries:\n" + json.dumps(entries, ensure_ascii=False)
        kwargs: dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        }
        if self._extra_headers:
            kwargs["extra_headers"] = self._extra_headers
        resp = self.client.chat.completions.create(**kwargs)
        raw = (resp.choices[0].message.content or "[]").strip()
        if raw.startswith("```"):
            raw = raw.strip("`").lstrip()
            if raw.lower().startswith("json"):
                raw = raw[4:].lstrip()
            if raw.endswith("```"):
                raw = raw[:-3].rstrip()
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected JSON array, got {type(parsed)}")
        return parsed
