"""Selector for the default LLM client: OpenRouter > Anthropic > None."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from cantinaiq.enrichment.producer.openrouter_client import OpenRouterLLMClient
from cantinaiq.enrichment.producer.pass2_llm import AnthropicLLMClient
from cantinaiq.enrichment.run import _try_default_llm_client


def _cfg(model: str = "anthropic/claude-3.5-haiku", temperature: float = 0.0) -> SimpleNamespace:
    return SimpleNamespace(
        enrichment=SimpleNamespace(llm=SimpleNamespace(model=model, temperature=temperature))
    )


def test_disabled_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CANTINAIQ_DISABLE_LLM", "1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    assert _try_default_llm_client(_cfg()) is None  # type: ignore[arg-type]


def test_prefers_openrouter_when_both_keys_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CANTINAIQ_DISABLE_LLM", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    client = _try_default_llm_client(_cfg())  # type: ignore[arg-type]
    assert isinstance(client, OpenRouterLLMClient)


def test_falls_back_to_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CANTINAIQ_DISABLE_LLM", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    # Stub the Anthropic SDK so the constructor doesn't try a real connection.
    import cantinaiq.enrichment.producer.pass2_llm as p2

    fake_module = MagicMock()
    fake_module.Anthropic.return_value = MagicMock()
    monkeypatch.setattr(p2, "AnthropicLLMClient", AnthropicLLMClient)
    monkeypatch.setitem(__import__("sys").modules, "anthropic", fake_module)
    client = _try_default_llm_client(_cfg())  # type: ignore[arg-type]
    assert isinstance(client, AnthropicLLMClient)


def test_no_keys_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CANTINAIQ_DISABLE_LLM", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert _try_default_llm_client(_cfg()) is None  # type: ignore[arg-type]
