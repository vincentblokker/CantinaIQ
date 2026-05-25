"""OpenRouter LLM client — OpenAI-SDK-compatible chat completion against OpenRouter."""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from cantinaiq.enrichment.producer.openrouter_client import OpenRouterLLMClient


@pytest.fixture
def fake_openai_response() -> MagicMock:
    msg = MagicMock()
    msg.content = json.dumps(
        [
            {
                "id": "0",
                "producer": "Tenuta San Guido",
                "inferred_grape_or_style": "Cabernet blend",
                "confidence": "High",
                "reasoning": "Sassicaia is its flagship wine",
            },
            {
                "id": "1",
                "producer": None,
                "inferred_grape_or_style": None,
                "confidence": "Low",
                "reasoning": "No producer signal",
            },
        ]
    )
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def test_resolve_batch_parses_choices(
    monkeypatch: pytest.MonkeyPatch, fake_openai_response: MagicMock
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    client = OpenRouterLLMClient(model="anthropic/claude-3.5-haiku")
    fake_chat = MagicMock()
    fake_chat.completions.create.return_value = fake_openai_response
    client.client.chat = fake_chat  # type: ignore[assignment]

    entries: list[dict[str, Any]] = [
        {"id": "0", "name": "Sassicaia 2018", "region": "Bolgheri Sassicaia"},
        {"id": "1", "name": "Unknown Bottle", "region": "Veneto"},
    ]
    out = client.resolve_batch(entries)

    assert len(out) == 2
    assert out[0]["producer"] == "Tenuta San Guido"
    assert out[1]["producer"] is None
    fake_chat.completions.create.assert_called_once()
    call_kwargs = fake_chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "anthropic/claude-3.5-haiku"
    assert call_kwargs["temperature"] == 0.0


def test_strips_code_fences(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    client = OpenRouterLLMClient()
    msg = MagicMock()
    msg.content = '```json\n[{"id": "0", "producer": "Gaja", "confidence": "High"}]\n```'
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    fake_chat = MagicMock()
    fake_chat.completions.create.return_value = resp
    client.client.chat = fake_chat  # type: ignore[assignment]

    out = client.resolve_batch([{"id": "0", "name": "Gaja Barbaresco", "region": "Piedmont"}])
    assert out[0]["producer"] == "Gaja"


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        OpenRouterLLMClient()
