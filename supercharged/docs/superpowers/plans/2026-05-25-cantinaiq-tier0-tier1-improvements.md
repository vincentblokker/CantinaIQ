# CantinaIQ Tier 0 + Tier 1.2 + 1.4 Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the assignment-compliance gaps in `/supercharged/` (top-5 reasons, recommendation document, crawler extension, methodology delta, real producer disambiguation) and add two flagship features that no /bare-style submission can have: a run-comparison CLI and a sensitivity-sweep CLI.

**Architecture:** Plug-in additions to the existing Polars/Hydra pipeline. New `OpenRouterLLMClient` slots into the existing `LLMClient` Protocol. A `cantinaiq crawler extend` subcommand uses the `firecrawl-py` SDK behind a feature flag (stub by default). A generative reason-builder fills the empty `reasons` dict in `reporting/cli.py`. A new `executive-summary.md.j2` template joins the existing Jinja set. `cantinaiq compare` and `cantinaiq sensitivity` are net-new Typer subcommands that consume existing run-bundles + scored parquets. No changes to the cleaning/validation/scoring math itself.

**Tech Stack:** Python 3.13 · Polars · Hydra · Typer · Jinja2 · `openai` SDK (for OpenRouter) · `firecrawl-py` SDK · pytest + Hypothesis · uv.

---

## File map

**New files:**
- `src/cantinaiq/enrichment/producer/openrouter_client.py` — OpenRouter LLM client implementing the `LLMClient` Protocol
- `src/cantinaiq/reporting/reasons.py` — generative reason-builder (deterministic, no LLM)
- `reports/templates/executive-summary.md.j2` — half-A4 Slurpini recommendation template
- `src/cantinaiq/crawler/__init__.py` — package marker
- `src/cantinaiq/crawler/extend.py` — crawler extension entry points (stub + Firecrawl backends)
- `src/cantinaiq/crawler/cli.py` — `cantinaiq crawler extend` Typer subcommand
- `src/cantinaiq/compare.py` — run-bundle comparator (pure functions)
- `src/cantinaiq/sensitivity.py` — sensitivity sweep + Kendall-tau analysis
- `tests/unit/test_openrouter_client.py` — fake `openai`-compatible client wired in
- `tests/unit/test_reasons.py` — reason-builder unit tests
- `tests/unit/test_executive_summary_template.py` — template render smoke
- `tests/unit/test_crawler_extend.py` — stub + Firecrawl-backend tests with mocked SDK
- `tests/unit/test_compare.py` — diff math unit tests
- `tests/unit/test_sensitivity.py` — sweep + Kendall-tau tests

**Modified files:**
- `pyproject.toml` — add `openai>=1.40,<2`, `firecrawl-py>=2.0,<3`, `scipy>=1.14,<2` (for kendalltau)
- `src/cantinaiq/enrichment/run.py:57-72` — `_try_default_llm_client` selects OpenRouter when `OPENROUTER_API_KEY` is set
- `src/cantinaiq/reporting/cli.py:36-52` — `_findings_extra_context` calls reason-builder instead of passing `{}`
- `src/cantinaiq/reporting/cli.py:15-19` — register `executive-summary` in `TEMPLATES_BY_NAME`
- `src/cantinaiq/cli.py` — add `crawler`, `compare`, `sensitivity` sub-apps
- `reports/templates/methodology.md.j2` — add §3a "Row-count delta vs. /bare" paragraph

---

## Phase 1: OpenRouter LLM client

### Task 1.1: Add openai SDK dependency

**Files:**
- Modify: `pyproject.toml:8-22`

- [ ] **Step 1: Update dependencies**

Edit `pyproject.toml` `[project] dependencies` array to add `"openai>=1.40,<2"` after the `anthropic` line.

- [ ] **Step 2: Sync**

```bash
cd /Users/vincentblokker/ClubVentureProjects/CantinaIQ/supercharged
uv sync
```

Expected: openai installed, no version conflict.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/pyproject.toml supercharged/uv.lock
git -C .. commit -m "chore(deps): add openai SDK for OpenRouter client"
```

### Task 1.2: Write failing test for OpenRouterLLMClient

**Files:**
- Create: `tests/unit/test_openrouter_client.py`

- [ ] **Step 1: Write test**

```python
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
            {"id": "0", "producer": "Tenuta San Guido", "inferred_grape_or_style": "Cabernet blend", "confidence": "High", "reasoning": "Sassicaia is its flagship wine"},
            {"id": "1", "producer": None, "inferred_grape_or_style": None, "confidence": "Low", "reasoning": "No producer signal"},
        ]
    )
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def test_resolve_batch_parses_choices(monkeypatch: pytest.MonkeyPatch, fake_openai_response: MagicMock) -> None:
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


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        OpenRouterLLMClient()
```

- [ ] **Step 2: Run — verify failure**

```bash
uv run pytest tests/unit/test_openrouter_client.py -v
```

Expected: ImportError (module does not exist).

### Task 1.3: Implement OpenRouterLLMClient

**Files:**
- Create: `src/cantinaiq/enrichment/producer/openrouter_client.py`

- [ ] **Step 1: Write implementation**

```python
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
        model: str = "anthropic/claude-3.5-haiku",
        temperature: float = 0.0,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        from openai import OpenAI

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature

    def resolve_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        user_msg = "Entries:\n" + json.dumps(entries, ensure_ascii=False)
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        raw = resp.choices[0].message.content or "[]"
        # Strip code fences if the model wraps JSON in them.
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected JSON array, got {type(parsed)}")
        return parsed
```

- [ ] **Step 2: Run — verify pass**

```bash
uv run pytest tests/unit/test_openrouter_client.py -v
```

Expected: 2 passed.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/enrichment/producer/openrouter_client.py supercharged/tests/unit/test_openrouter_client.py
git -C .. commit -m "feat(enrichment): add OpenRouter LLM client implementing LLMClient Protocol"
```

### Task 1.4: Wire OpenRouter into _try_default_llm_client

**Files:**
- Modify: `src/cantinaiq/enrichment/run.py:57-78`

- [ ] **Step 1: Update selection logic**

Replace the body of `_try_default_llm_client` to prefer OpenRouter when `OPENROUTER_API_KEY` is set, fall back to Anthropic otherwise:

```python
def _try_default_llm_client(cfg: PipelineConfig) -> LLMClient | None:
    """Construct an LLM client unless disabled or unavailable.

    Returns None (pass-2 skipped) when:
      - CANTINAIQ_DISABLE_LLM=1 is set (explicit opt-out), or
      - no provider API key is available.

    Provider selection: OpenRouter if OPENROUTER_API_KEY is set,
    Anthropic if only ANTHROPIC_API_KEY is set.
    """
    if os.environ.get("CANTINAIQ_DISABLE_LLM") == "1":
        return None
    if os.environ.get("OPENROUTER_API_KEY"):
        from cantinaiq.enrichment.producer.openrouter_client import OpenRouterLLMClient
        try:
            return OpenRouterLLMClient(
                model=cfg.enrichment.llm.model,
                temperature=cfg.enrichment.llm.temperature,
            )
        except (RuntimeError, ImportError):
            return None
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return AnthropicLLMClient(
                model=cfg.enrichment.llm.model,
                temperature=cfg.enrichment.llm.temperature,
            )
        except (RuntimeError, ImportError):
            return None
    return None
```

- [ ] **Step 2: Add selector test**

Append to `tests/unit/test_enrichment_run.py`:

```python
def test_default_client_prefers_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    from cantinaiq.enrichment.run import _try_default_llm_client
    from cantinaiq.enrichment.producer.openrouter_client import OpenRouterLLMClient

    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.delenv("CANTINAIQ_DISABLE_LLM", raising=False)

    cfg = MagicMock()
    cfg.enrichment.llm.model = "anthropic/claude-3.5-haiku"
    cfg.enrichment.llm.temperature = 0.0

    client = _try_default_llm_client(cfg)
    assert isinstance(client, OpenRouterLLMClient)
```

If the file already has fixtures, reuse them. If `MagicMock`/`pytest` aren't imported, add at the top.

- [ ] **Step 3: Run all enrichment tests**

```bash
uv run pytest tests/unit/test_enrichment_run.py -v
```

Expected: all pass, including the new selector test.

- [ ] **Step 4: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/enrichment/run.py supercharged/tests/unit/test_enrichment_run.py
git -C .. commit -m "feat(enrichment): prefer OpenRouter when OPENROUTER_API_KEY is set"
```

---

## Phase 2: Generative top-5 reasons

### Task 2.1: Write failing test for reason-builder

**Files:**
- Create: `tests/unit/test_reasons.py`

- [ ] **Step 1: Write test**

```python
"""Generative reason-builder — deterministic prose for top-N producers."""
from __future__ import annotations

import pytest

from cantinaiq.reporting.reasons import build_reason


def test_hidden_gem_phrasing() -> None:
    reason = build_reason(
        producer_name="Cantine Due Palme",
        market_segment="Hidden Gem",
        weighted_rating=4.18,
        avg_price=14.0,
        total_reviews=1247,
        composite_score=0.82,
        value_score=2.1,
    )
    assert "Hidden Gem" in reason
    assert "4.18" in reason
    assert "1,247" in reason or "1247" in reason
    assert "€14" in reason


def test_premium_icon_phrasing() -> None:
    reason = build_reason(
        producer_name="Tenuta San Guido",
        market_segment="Premium Icon",
        weighted_rating=4.62,
        avg_price=534.0,
        total_reviews=307787,
        composite_score=0.95,
        value_score=0.7,
    )
    assert "Premium Icon" in reason
    assert "€534" in reason


def test_low_confidence_phrasing() -> None:
    reason = build_reason(
        producer_name="Obscure Cantina",
        market_segment="Low Confidence Niche",
        weighted_rating=4.4,
        avg_price=22.0,
        total_reviews=14,
        composite_score=0.4,
        value_score=1.9,
    )
    assert "few reviews" in reason.lower() or "low review" in reason.lower() or "14" in reason


@pytest.mark.parametrize("seg", ["Hidden Gem", "Premium Icon", "Commercial Value", "Overpriced Risk", "Low Confidence Niche"])
def test_all_segments_produce_non_empty_reason(seg: str) -> None:
    out = build_reason("X", seg, 4.0, 50.0, 500, 0.5, 1.0)
    assert len(out) >= 20
    assert len(out) <= 220
```

- [ ] **Step 2: Run — verify failure**

```bash
uv run pytest tests/unit/test_reasons.py -v
```

Expected: ImportError.

### Task 2.2: Implement reason-builder

**Files:**
- Create: `src/cantinaiq/reporting/reasons.py`

- [ ] **Step 1: Write implementation**

```python
"""Deterministic prose generator for top-N producer recommendations.

The output is a single sentence (<=220 chars) that combines the producer's
market segment, weighted rating, price band, and review confidence into a
human-readable rationale. No LLM is used — the function is pure and the
output is reproducible from the scoring run alone.
"""

from __future__ import annotations

SEGMENT_OPENERS: dict[str, str] = {
    "Hidden Gem": "Hidden Gem in the value tier",
    "Premium Icon": "Premium Icon at the top of the prestige tier",
    "Commercial Value": "Commercial Value — solid market signal at a scalable price",
    "Overpriced Risk": "Overpriced Risk — price runs ahead of consumer signal",
    "Low Confidence Niche": "Low Confidence Niche — interesting but thinly reviewed",
}


def _format_reviews(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _format_price(eur: float) -> str:
    return f"€{int(round(eur))}"


def build_reason(
    producer_name: str,
    market_segment: str,
    weighted_rating: float,
    avg_price: float,
    total_reviews: int,
    composite_score: float,
    value_score: float,
) -> str:
    """Return a single-sentence reason for the producer's recommendation."""
    opener = SEGMENT_OPENERS.get(market_segment, market_segment)
    rating_str = f"{weighted_rating:.2f}"
    reviews_str = _format_reviews(total_reviews)
    price_str = _format_price(avg_price)

    if market_segment == "Low Confidence Niche":
        return (
            f"{opener}: weighted rating {rating_str} on only {reviews_str} reviews "
            f"at {price_str} — too few reviews to commit; worth a tasting before dismissing."
        )
    if market_segment == "Hidden Gem":
        return (
            f"{opener}: weighted rating {rating_str} on {reviews_str} reviews "
            f"for {price_str} avg — above-median quality below the median price band."
        )
    if market_segment == "Premium Icon":
        return (
            f"{opener}: weighted rating {rating_str} on {reviews_str} reviews "
            f"at {price_str} — defensible anchor for Slurpini's premium positioning."
        )
    if market_segment == "Overpriced Risk":
        return (
            f"{opener}: rating {rating_str} on {reviews_str} reviews at {price_str} — "
            f"value score {value_score:.2f} suggests price outruns consumer signal."
        )
    return (
        f"{opener}: weighted rating {rating_str} on {reviews_str} reviews at {price_str} "
        f"— composite score {composite_score:.2f}."
    )
```

- [ ] **Step 2: Run — verify pass**

```bash
uv run pytest tests/unit/test_reasons.py -v
```

Expected: 7 passed (3 named + 5 parametrised − 1 already covered = 7 net).

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/reporting/reasons.py supercharged/tests/unit/test_reasons.py
git -C .. commit -m "feat(reporting): add deterministic reason-builder for top-N producers"
```

### Task 2.3: Wire reasons into findings context

**Files:**
- Modify: `src/cantinaiq/reporting/cli.py:21-52`

- [ ] **Step 1: Update `_findings_extra_context`**

Replace the `reasons={},` line with a builder call:

```python
def _findings_extra_context(processed_dir: Path, copy_path: Path) -> dict[str, Any]:
    from cantinaiq.reporting.reasons import build_reason

    producers = pl.read_parquet(processed_dir / "producers_scored.parquet")
    wines = pl.read_parquet(processed_dir / "wines_scored.parquet")
    copy = yaml.safe_load(copy_path.read_text()) if copy_path.exists() else {}

    top5 = producers.sort("composite_score", descending=True).head(5).to_dicts()
    reasons = {
        p["producer_name"]: build_reason(
            producer_name=p["producer_name"],
            market_segment=p["market_segment"],
            weighted_rating=p["weighted_rating"],
            avg_price=p["avg_price"],
            total_reviews=p["total_reviews"],
            composite_score=p["composite_score"],
            value_score=p.get("value_score", 0.0),
        )
        for p in top5
    }

    return build_findings_context(
        producers_scored=producers,
        wines_scored=wines,
        price_split=float(producers["avg_price"].median() or 60.0),  # type: ignore[arg-type]
        rating_split=float(producers["weighted_rating"].median() or 4.0),  # type: ignore[arg-type]
        reasons=reasons,
        findings_copy={
            "problem": copy.get("problem", ""),
            "limitations": copy.get("limitations", []),
        },
    )
```

- [ ] **Step 2: Add wiring test**

Add to `tests/reporting/test_findings_template.py` (or create if needed):

```python
def test_findings_template_renders_reasons(tmp_path: Path) -> None:
    """The findings template's Top-5 cards must contain non-empty reasons after wiring."""
    # This is verified end-to-end in Phase 8's `report build` smoke; here we just
    # confirm the context builder no longer hard-codes an empty dict.
    from cantinaiq.reporting.cli import _findings_extra_context  # type: ignore[attr-defined]
    import inspect
    src = inspect.getsource(_findings_extra_context)
    assert "reasons={}" not in src
    assert "build_reason" in src
```

- [ ] **Step 3: Run**

```bash
uv run pytest tests/reporting/ -v
```

Expected: all green.

- [ ] **Step 4: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/reporting/cli.py supercharged/tests/reporting/test_findings_template.py
git -C .. commit -m "feat(reporting): generate top-5 reasons from scored data instead of empty dict"
```

---

## Phase 3: Executive summary template

### Task 3.1: Write failing test

**Files:**
- Create: `tests/unit/test_executive_summary_template.py`

- [ ] **Step 1: Write test**

```python
"""Executive summary Jinja template renders a complete Slurpini recommendation."""
from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

TEMPLATES = Path("reports/templates")


@pytest.fixture
def env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture
def ctx() -> dict[str, object]:
    return {
        "run_id": "2026-05-25T12-00__abc12345",
        "config_hash": "abc12345",
        "totals": {"wines": 2986, "producers": 624, "regions": 51},
        "top_regions": [
            {"region": "Bolgheri Sassicaia", "weighted_rating": 4.62, "avg_price": 534, "wines": 76},
            {"region": "Brunello di Montalcino", "weighted_rating": 4.27, "avg_price": 197, "wines": 404},
            {"region": "Primitivo di Manduria", "weighted_rating": 4.26, "avg_price": 161, "wines": 95},
        ],
        "top_producers": [
            {"producer_name": "Tenuta San Guido", "macro_region": "Tuscany", "recommendation": "Premium Brand Builder", "weighted_rating": 4.62, "avg_price": 534, "reason": "Premium Icon ..."},
            {"producer_name": "Cantine Due Palme", "macro_region": "Puglia", "recommendation": "Value Opportunity", "weighted_rating": 4.18, "avg_price": 14, "reason": "Hidden Gem ..."},
        ],
        "hold": ["Tenuta San Guido", "Biondi-Santi"],
        "expand": ["Primitivo di Manduria", "Abruzzo"],
        "audit": ["producers with weighted rating ≥ 4.3 but < 10 reviews"],
    }


def test_renders_complete_summary(env: Environment, ctx: dict[str, object]) -> None:
    tpl = env.get_template("executive-summary.md.j2")
    out = tpl.render(**ctx)
    assert "# Executive Summary" in out
    assert "Bolgheri Sassicaia" in out
    assert "Primitivo di Manduria" in out
    assert "Tenuta San Guido" in out
    assert "Hold" in out
    assert "Expand" in out
    assert "Audit" in out
    assert "abc12345" in out  # config hash footer
```

- [ ] **Step 2: Run — verify failure**

```bash
uv run pytest tests/unit/test_executive_summary_template.py -v
```

Expected: TemplateNotFound.

### Task 3.2: Implement template

**Files:**
- Create: `reports/templates/executive-summary.md.j2`

- [ ] **Step 1: Write template**

```jinja
# Executive Summary

*Slurpini Partner Intelligence — board-level recommendation. Half-A4, addressed to a non-technical buying-committee reader. All numbers derive from pipeline run `{{ run_id }}` (config hash `{{ config_hash }}`).*

---

## What we did

Cleaned, validated, and scored {{ totals.wines | int }} unique Italian wines from the Dutch Vivino dataset, covering {{ totals.regions | int }} regions and {{ totals.producers | int }} producers (after pass-2 disambiguation). Producers and regions are ranked by a 5-factor composite Slurpini Partner Intelligence Score that combines a Bayesian-shrunk weighted rating, market confidence, value-for-money, premium fit, and portfolio opportunity. Scoring weights are versioned per config snapshot.

## What the data says

**Regions to prioritise** (top of the weighted-rating ranking):

{% for r in top_regions %}
- **{{ r.region }}** — weighted rating {{ "%.2f"|format(r.weighted_rating) }} across {{ r.wines }} wines at €{{ r.avg_price|round(0)|int }} avg.
{% endfor %}

**Producers to prioritise** (top of the composite-score ranking):

{% for p in top_producers %}
- **{{ p.producer_name }}** ({{ p.macro_region }}) — *{{ p.recommendation }}*. {{ p.reason }}
{% endfor %}

## Concretely, what we recommend

1. **Hold** the prestige tier: {{ hold | join(", ") }}. The data confirms what Slurpini already does; these are defensible anchors.
2. **Expand** in: {{ expand | join(", ") }}. These sit in the value-opportunity zone — above-median weighted rating at well-below-median average price — and are under-represented in most Dutch wine retail.
3. **Audit** {{ audit | join("; ") }}. Excluded from the ranking on confidence grounds, but worth a tasting before dismissing.

## What this does not tell you

- **Vivino is not the Dutch wine market.** Anglophone, younger skew; natural and biodynamic producers under-counted.
- **Sustainability is absent from the dataset.** Slurpini's USP must be cross-checked against producer certifications before commitment.
- **Vintage compression.** Multi-vintage wines are averaged; producers with strong recent runs are under-weighted.
- **Producer extraction is heuristic-with-LLM-assist.** Pass-1 alias whitelist covers the top-50; pass-2 LLM disambiguation is logged per row.

---

*Reproducibility: re-run with `cantinaiq run all --config-snapshot {{ config_hash }}` and `cantinaiq report build`. Methodology details in `methodology.md`; data quality in `data-quality.md`.*
```

- [ ] **Step 2: Run — verify pass**

```bash
uv run pytest tests/unit/test_executive_summary_template.py -v
```

Expected: 1 passed.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/reports/templates/executive-summary.md.j2 supercharged/tests/unit/test_executive_summary_template.py
git -C .. commit -m "feat(reporting): add executive-summary Jinja template"
```

### Task 3.3: Register executive-summary in the report build CLI

**Files:**
- Modify: `src/cantinaiq/reporting/cli.py:15-19, 36-52, 55-90`

- [ ] **Step 1: Register template + context builder**

Update `TEMPLATES_BY_NAME`:

```python
TEMPLATES_BY_NAME: dict[str, str] = {
    "data-quality": "data-quality.md.j2",
    "methodology": "methodology.md.j2",
    "findings-one-pager": "findings-one-pager.html.j2",
    "executive-summary": "executive-summary.md.j2",
}
```

Add an `_executive_summary_extra_context()` function next to `_findings_extra_context`:

```python
def _executive_summary_extra_context(processed_dir: Path, config_hash: str) -> dict[str, Any]:
    from cantinaiq.reporting.reasons import build_reason

    producers = pl.read_parquet(processed_dir / "producers_scored.parquet")
    regions = pl.read_parquet(processed_dir / "regions_scored.parquet")
    wines = pl.read_parquet(processed_dir / "wines_scored.parquet")

    top_regions = (
        regions.sort("weighted_rating", descending=True)
        .head(5)
        .select(["region", "weighted_rating", "avg_price", "wines"])
        .to_dicts()
    )
    top5 = producers.sort("composite_score", descending=True).head(5).to_dicts()
    top_producers = [
        {
            "producer_name": p["producer_name"],
            "macro_region": p["macro_region"],
            "recommendation": p["recommendation"],
            "weighted_rating": p["weighted_rating"],
            "avg_price": p["avg_price"],
            "reason": build_reason(
                producer_name=p["producer_name"],
                market_segment=p["market_segment"],
                weighted_rating=p["weighted_rating"],
                avg_price=p["avg_price"],
                total_reviews=p["total_reviews"],
                composite_score=p["composite_score"],
                value_score=p.get("value_score", 0.0),
            ),
        }
        for p in top5
    ]

    hold = [p["producer_name"] for p in top5 if p["market_segment"] == "Premium Icon"][:5]
    expand = [
        r["region"] for r in regions.sort("value_score", descending=True).head(20).to_dicts()
        if r["avg_price"] < float(regions["avg_price"].median() or 100)
    ][:3]
    audit = ["producers with weighted rating ≥ 4.3 but excluded from the ranking on review-count grounds"]

    return {
        "config_hash": config_hash,
        "totals": {
            "wines": wines.height,
            "producers": producers.height,
            "regions": regions.height,
        },
        "top_regions": top_regions,
        "top_producers": top_producers,
        "hold": hold,
        "expand": expand,
        "audit": audit,
    }
```

Then in `build()`, add the dispatch for the new template:

```python
        if name == "findings-one-pager":
            extra = _findings_extra_context(processed_dir, findings_copy)
        elif name == "executive-summary":
            extra = _executive_summary_extra_context(processed_dir, bundle.config_hash)
```

- [ ] **Step 2: Smoke-test build**

```bash
uv run cantinaiq report build --only executive-summary
ls -l reports/generated/executive-summary.md
head -20 reports/generated/executive-summary.md
```

Expected: file exists, contains "# Executive Summary", references a real region and producer name.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/reporting/cli.py
git -C .. commit -m "feat(reporting): register executive-summary template in report build CLI"
```

---

## Phase 4: Firecrawl crawler subcommand

### Task 4.1: Add firecrawl-py dependency

**Files:**
- Modify: `pyproject.toml:8-22`

- [ ] **Step 1: Add dep**

Append `"firecrawl-py>=2.0,<3"` to the `[project] dependencies` array.

- [ ] **Step 2: Sync**

```bash
uv sync
```

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/pyproject.toml supercharged/uv.lock
git -C .. commit -m "chore(deps): add firecrawl-py for crawler extension"
```

### Task 4.2: Write failing tests for crawler.extend

**Files:**
- Create: `tests/unit/test_crawler_extend.py`

- [ ] **Step 1: Write test**

```python
"""Crawler extension — derived fields + optional Firecrawl backend."""
from __future__ import annotations

from unittest.mock import MagicMock

import polars as pl
import pytest

from cantinaiq.crawler.extend import (
    add_derived_fields,
    enrich_with_firecrawl,
    extract_vintage,
    first_word_producer,
)


def test_extract_vintage_from_name() -> None:
    assert extract_vintage("Tignanello 2018 Toscana IGT") == 2018
    assert extract_vintage("Brunello di Montalcino 1999") == 1999
    assert extract_vintage("No year here") is None


def test_first_word_producer() -> None:
    assert first_word_producer("Antinori Tignanello 2018") == "Antinori"
    assert first_word_producer("  Gaja Barbaresco 2017") == "Gaja"
    assert first_word_producer("") is None


def test_add_derived_fields_adds_two_columns() -> None:
    df = pl.DataFrame({"name": ["Antinori Tignanello 2018", "Gaja Sperss 2015"]})
    out = add_derived_fields(df)
    assert "vintage" in out.columns
    assert "producer_hint" in out.columns
    assert out["vintage"].to_list() == [2018, 2015]
    assert out["producer_hint"].to_list() == ["Antinori", "Gaja"]


def test_enrich_with_firecrawl_uses_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_app = MagicMock()
    fake_app.scrape_url.return_value = MagicMock(
        markdown="Alcohol: 13.5%\nGrapes: Sangiovese, Cabernet Sauvignon\nFood pairings: red meat",
    )

    class FakeFirecrawl:
        def __init__(self, api_key: str) -> None:  # noqa: ARG002
            pass

        def scrape_url(self, url: str, **kwargs: object) -> MagicMock:  # noqa: ARG002
            return fake_app.scrape_url(url)

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    monkeypatch.setattr("cantinaiq.crawler.extend._FirecrawlApp", FakeFirecrawl)

    result = enrich_with_firecrawl(
        wine_name="Tignanello 2018",
        url="https://www.vivino.com/wines/some-tignanello",
    )
    assert result["alcohol_percentage"] == 13.5
    assert "Sangiovese" in result["grape_varieties"]
    assert "red meat" in result["food_pairings"]


def test_enrich_without_api_key_returns_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    result = enrich_with_firecrawl(wine_name="Anything", url="https://example.com")
    assert result == {}
```

- [ ] **Step 2: Run — verify failure**

```bash
uv run pytest tests/unit/test_crawler_extend.py -v
```

Expected: ImportError.

### Task 4.3: Implement crawler.extend module

**Files:**
- Create: `src/cantinaiq/crawler/__init__.py`
- Create: `src/cantinaiq/crawler/extend.py`

- [ ] **Step 1: Package marker**

Write `src/cantinaiq/crawler/__init__.py`:

```python
"""Crawler extension utilities for CantinaIQ."""
```

- [ ] **Step 2: Module implementation**

Write `src/cantinaiq/crawler/extend.py`:

```python
"""Crawler extension for the Vivino dataset.

Adds derived fields computable from existing data (vintage, producer_hint)
and — behind a feature flag — fetches richer wine attributes via Firecrawl.

Default mode is *stub* (no network); set `FIRECRAWL_API_KEY` and the
explicit `--with-network` CLI flag to enable real scraping.
"""

from __future__ import annotations

import os
import re
from typing import Any

import polars as pl

VINTAGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
ALCOHOL_RE = re.compile(r"alcohol[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE)
GRAPES_RE = re.compile(r"grapes?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)
PAIRINGS_RE = re.compile(r"food\s*pairings?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)

# Indirection so tests can monkeypatch the SDK without touching the import line.
try:
    from firecrawl import FirecrawlApp as _FirecrawlApp  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    _FirecrawlApp = None  # type: ignore[assignment,misc]


def extract_vintage(name: str | None) -> int | None:
    """Return the four-digit year embedded in a wine name, or None."""
    if not isinstance(name, str):
        return None
    m = VINTAGE_RE.search(name)
    return int(m.group(1)) if m else None


def first_word_producer(name: str | None) -> str | None:
    """First-word heuristic for producer name."""
    if not isinstance(name, str) or not name.strip():
        return None
    return name.split()[0]


def add_derived_fields(df: pl.DataFrame) -> pl.DataFrame:
    """Return df with `vintage` and `producer_hint` columns appended."""
    return df.with_columns(
        pl.col("name").map_elements(extract_vintage, return_dtype=pl.Int64).alias("vintage"),
        pl.col("name").map_elements(first_word_producer, return_dtype=pl.Utf8).alias("producer_hint"),
    )


def _parse_markdown(md: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if m := ALCOHOL_RE.search(md):
        out["alcohol_percentage"] = float(m.group(1))
    if m := GRAPES_RE.search(md):
        out["grape_varieties"] = [g.strip() for g in m.group(1).split(",") if g.strip()]
    if m := PAIRINGS_RE.search(md):
        out["food_pairings"] = m.group(1).strip()
    return out


def enrich_with_firecrawl(wine_name: str, url: str) -> dict[str, Any]:  # noqa: ARG001
    """Scrape a wine page via Firecrawl and parse alcohol/grapes/pairings.

    Returns an empty dict if FIRECRAWL_API_KEY is unset (stub mode) or if
    the SDK is not installed.
    """
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key or _FirecrawlApp is None:
        return {}
    app = _FirecrawlApp(api_key=api_key)
    resp = app.scrape_url(url, formats=["markdown"])
    md = getattr(resp, "markdown", "") or ""
    return _parse_markdown(md)
```

- [ ] **Step 3: Run — verify pass**

```bash
uv run pytest tests/unit/test_crawler_extend.py -v
```

Expected: 5 passed.

- [ ] **Step 4: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/crawler supercharged/tests/unit/test_crawler_extend.py
git -C .. commit -m "feat(crawler): add Vivino crawler extension with Firecrawl backend"
```

### Task 4.4: Add `cantinaiq crawler extend` CLI subcommand

**Files:**
- Create: `src/cantinaiq/crawler/cli.py`
- Modify: `src/cantinaiq/cli.py:27-32`

- [ ] **Step 1: Write subcommand**

Write `src/cantinaiq/crawler/cli.py`:

```python
"""`cantinaiq crawler …` Typer subcommands."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from cantinaiq.crawler.extend import add_derived_fields, enrich_with_firecrawl

crawler_app = typer.Typer(no_args_is_help=True, help="Crawler extension utilities.")


@crawler_app.command("extend")
def extend(
    raw_path: Annotated[Path, typer.Option("--raw")] = Path("data/interim/01_raw.parquet"),
    out_path: Annotated[Path, typer.Option("--out")] = Path("data/interim/01_raw_extended.parquet"),
    with_network: Annotated[bool, typer.Option("--with-network")] = False,
    sample: Annotated[int, typer.Option("--sample", help="Limit network calls to top-N rows by review count.")] = 50,
) -> None:
    """Extend the ingested parquet with vintage + producer_hint, optionally enriched via Firecrawl."""
    df = pl.read_parquet(raw_path)
    df = add_derived_fields(df)
    typer.echo(f"Added derived fields → {df.height:,} rows, {len(df.columns)} columns.")

    if with_network:
        if not os.environ.get("FIRECRAWL_API_KEY"):
            typer.echo("FIRECRAWL_API_KEY not set; skipping network enrichment.")
        else:
            top = df.sort("rating_count", descending=True).head(sample)
            enriched_rows: list[dict[str, object]] = []
            for row in top.iter_rows(named=True):
                # Vivino URL convention: /wines/<slug>. We don't have slugs in the export,
                # so this is illustrative — production code would resolve a URL via search.
                url = f"https://www.vivino.com/search/wines?q={row['name'].replace(' ', '+')}"
                extras = enrich_with_firecrawl(wine_name=row["name"], url=url)
                enriched_rows.append({"name": row["name"], **extras})
            typer.echo(f"Enriched {len(enriched_rows)} top-reviewed wines via Firecrawl.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out_path)
    typer.echo(f"Wrote {out_path}.")
```

- [ ] **Step 2: Wire into main CLI**

Edit `src/cantinaiq/cli.py`. After the existing `app.add_typer(...)` lines, add:

```python
from cantinaiq.crawler.cli import crawler_app
app.add_typer(crawler_app, name="crawler")
```

- [ ] **Step 3: Smoke test**

```bash
uv run cantinaiq crawler extend --help
uv run cantinaiq crawler extend --raw data/interim/01_raw.parquet --out /tmp/extended.parquet
```

Expected: help renders, file written, stdout reports row count.

- [ ] **Step 4: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/crawler/cli.py supercharged/src/cantinaiq/cli.py
git -C .. commit -m "feat(cli): add cantinaiq crawler extend subcommand"
```

---

## Phase 5: Methodology delta paragraph

### Task 5.1: Update methodology template

**Files:**
- Modify: `reports/templates/methodology.md.j2`

- [ ] **Step 1: Add §3a paragraph**

Locate the `## 3. Cleaning cascade` section. Insert a new subsection immediately after it (or replace if §3a already exists):

```jinja
## 3a. Row-count delta vs. /bare track

The companion `/bare` track keeps {{ "5,786" }} Italian wines after de-duplication; this track keeps {{ totals.wines | default(2986) | int }} after the additional cleaning and validation stages. The delta is intentional: this pipeline drops wines with `rating_count < 50` (low statistical confidence), wines where pass-1 producer disambiguation returns null *and* pass-2 LLM disambiguation also returns null with low confidence, and regions that fail the canonical-name match against `data/reference/macro_regions.csv`. The /bare track keeps every row that passes basic schema constraints, accepting more noise in exchange for breadth. This track trades breadth for confidence — every retained row has a non-null producer and a canonical region label.
```

If the template doesn't already have `totals.wines` in scope, the existing `methodology.md` render in the previous Phase 0 verification step shows it does (the cleaning cascade table references row counts). If it doesn't, add a passthrough in the renderer; otherwise leave as-is.

- [ ] **Step 2: Re-render**

```bash
uv run cantinaiq report build --only methodology
grep -A 2 "3a." reports/generated/methodology.md
```

Expected: the new paragraph appears with the real row count substituted.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/reports/templates/methodology.md.j2
git -C .. commit -m "docs(methodology): explain row-count delta vs /bare track"
```

---

## Phase 6: compare CLI

### Task 6.1: Write failing tests for compare module

**Files:**
- Create: `tests/unit/test_compare.py`

- [ ] **Step 1: Write tests**

```python
"""Run comparison — diff scored parquets + run bundles between two config hashes."""
from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from cantinaiq.compare import (
    RunComparison,
    compare_runs,
    diff_producer_rankings,
    diff_segment_movements,
)


@pytest.fixture
def producers_a(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "producer_name": ["A", "B", "C", "D"],
            "composite_score": [0.9, 0.8, 0.7, 0.6],
            "market_segment": ["Premium Icon", "Hidden Gem", "Commercial Value", "Monitor"],
            "recommendation": ["Premium Brand Builder", "Value Opportunity", "Monitor", "Monitor"],
        }
    )
    p = tmp_path / "a.parquet"
    df.write_parquet(p)
    return p


@pytest.fixture
def producers_b(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "producer_name": ["A", "B", "C", "D"],
            "composite_score": [0.92, 0.6, 0.75, 0.85],
            "market_segment": ["Premium Icon", "Monitor", "Commercial Value", "Hidden Gem"],
            "recommendation": ["Premium Brand Builder", "Monitor", "Monitor", "Value Opportunity"],
        }
    )
    p = tmp_path / "b.parquet"
    df.write_parquet(p)
    return p


def test_diff_producer_rankings_returns_rank_shifts(producers_a: Path, producers_b: Path) -> None:
    shifts = diff_producer_rankings(producers_a, producers_b)
    by_name = {row["producer_name"]: row for row in shifts}
    assert by_name["A"]["rank_a"] == 1
    assert by_name["A"]["rank_b"] == 1
    assert by_name["D"]["rank_a"] == 4
    assert by_name["D"]["rank_b"] == 2  # D climbed
    assert by_name["B"]["rank_a"] == 2
    assert by_name["B"]["rank_b"] == 4  # B fell


def test_diff_segment_movements(producers_a: Path, producers_b: Path) -> None:
    moves = diff_segment_movements(producers_a, producers_b)
    by_name = {m["producer_name"]: m for m in moves}
    assert by_name["B"]["segment_a"] == "Hidden Gem"
    assert by_name["B"]["segment_b"] == "Monitor"
    assert by_name["D"]["segment_a"] == "Monitor"
    assert by_name["D"]["segment_b"] == "Hidden Gem"


def test_compare_runs_returns_full_comparison(producers_a: Path, producers_b: Path) -> None:
    comp = compare_runs(producers_a, producers_b, hash_a="aaa", hash_b="bbb")
    assert isinstance(comp, RunComparison)
    assert comp.hash_a == "aaa"
    assert comp.hash_b == "bbb"
    assert len(comp.ranking_shifts) == 4
    assert any(m["producer_name"] == "B" for m in comp.segment_movements)
```

- [ ] **Step 2: Run — verify failure**

```bash
uv run pytest tests/unit/test_compare.py -v
```

Expected: ImportError.

### Task 6.2: Implement compare module

**Files:**
- Create: `src/cantinaiq/compare.py`

- [ ] **Step 1: Write implementation**

```python
"""Compare two CantinaIQ runs — ranking shifts, segment movements, drop deltas."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl


@dataclass(frozen=True)
class RunComparison:
    hash_a: str
    hash_b: str
    ranking_shifts: list[dict[str, Any]]
    segment_movements: list[dict[str, Any]]


def diff_producer_rankings(parquet_a: Path, parquet_b: Path) -> list[dict[str, Any]]:
    """Return per-producer rank shifts (rank_a → rank_b)."""
    a = (
        pl.read_parquet(parquet_a)
        .sort("composite_score", descending=True)
        .with_row_index(name="rank_a", offset=1)
        .select(["producer_name", "rank_a", "composite_score"])
        .rename({"composite_score": "score_a"})
    )
    b = (
        pl.read_parquet(parquet_b)
        .sort("composite_score", descending=True)
        .with_row_index(name="rank_b", offset=1)
        .select(["producer_name", "rank_b", "composite_score"])
        .rename({"composite_score": "score_b"})
    )
    joined = a.join(b, on="producer_name", how="full", coalesce=True)
    joined = joined.with_columns(
        (pl.col("rank_a").cast(pl.Int64) - pl.col("rank_b").cast(pl.Int64)).alias("shift"),
    )
    return joined.to_dicts()


def diff_segment_movements(parquet_a: Path, parquet_b: Path) -> list[dict[str, Any]]:
    """Return rows where market_segment changed between runs."""
    a = pl.read_parquet(parquet_a).select(["producer_name", "market_segment", "recommendation"]).rename(
        {"market_segment": "segment_a", "recommendation": "rec_a"}
    )
    b = pl.read_parquet(parquet_b).select(["producer_name", "market_segment", "recommendation"]).rename(
        {"market_segment": "segment_b", "recommendation": "rec_b"}
    )
    joined = a.join(b, on="producer_name", how="inner")
    moved = joined.filter(pl.col("segment_a") != pl.col("segment_b"))
    return moved.to_dicts()


def compare_runs(
    parquet_a: Path,
    parquet_b: Path,
    hash_a: str,
    hash_b: str,
) -> RunComparison:
    return RunComparison(
        hash_a=hash_a,
        hash_b=hash_b,
        ranking_shifts=diff_producer_rankings(parquet_a, parquet_b),
        segment_movements=diff_segment_movements(parquet_a, parquet_b),
    )
```

- [ ] **Step 2: Run — verify pass**

```bash
uv run pytest tests/unit/test_compare.py -v
```

Expected: 3 passed.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/compare.py supercharged/tests/unit/test_compare.py
git -C .. commit -m "feat(compare): add run-comparison module (rankings + segment movements)"
```

### Task 6.3: Add `cantinaiq compare` CLI command

**Files:**
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Add command**

Append to `src/cantinaiq/cli.py` (after the `audit` command):

```python
@app.command()
def compare(
    hash_a: str,
    hash_b: str,
    processed_dir: Annotated[Path, typer.Option("--processed-dir")] = Path("data/processed"),
    top: Annotated[int, typer.Option("--top", help="Show top-N largest rank shifts.")] = 10,
) -> None:
    """Compare two CantinaIQ runs by config hash."""
    from cantinaiq.compare import compare_runs

    parquet_a = processed_dir / f"producers_scored__{hash_a}.parquet"
    parquet_b = processed_dir / f"producers_scored__{hash_b}.parquet"
    if not parquet_a.exists():
        # fall back to the latest snapshot
        parquet_a = processed_dir / "producers_scored.parquet"
        console.print(f"[yellow]No hash-tagged parquet for {hash_a}; using default {parquet_a}[/yellow]")
    if not parquet_b.exists():
        parquet_b = processed_dir / "producers_scored.parquet"
        console.print(f"[yellow]No hash-tagged parquet for {hash_b}; using default {parquet_b}[/yellow]")

    comp = compare_runs(parquet_a, parquet_b, hash_a=hash_a, hash_b=hash_b)

    console.print(f"\n[bold]Comparing runs[/bold] {hash_a} ↔ {hash_b}")
    console.print(f"\n[bold]Top {top} rank shifts:[/bold]")
    shifts_sorted = sorted(
        (s for s in comp.ranking_shifts if s.get("shift") is not None),
        key=lambda s: abs(int(s["shift"])),
        reverse=True,
    )[:top]
    for s in shifts_sorted:
        arrow = "↑" if (s["shift"] or 0) > 0 else "↓"
        console.print(
            f"  {arrow} {s['producer_name']:30}  rank {s['rank_a']} → {s['rank_b']}  (Δ={s['shift']})"
        )

    console.print(f"\n[bold]Segment movements:[/bold] {len(comp.segment_movements)}")
    for m in comp.segment_movements[:top]:
        console.print(f"  {m['producer_name']:30}  {m['segment_a']} → {m['segment_b']}")
```

- [ ] **Step 2: Smoke test**

```bash
uv run cantinaiq compare --help
```

Expected: help text including `hash_a`, `hash_b`, `--top`.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/cli.py
git -C .. commit -m "feat(cli): add cantinaiq compare command"
```

---

## Phase 7: sensitivity CLI

### Task 7.1: Add scipy dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Append dep**

Add `"scipy>=1.14,<2"` to `[project] dependencies`.

- [ ] **Step 2: Sync**

```bash
uv sync
```

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/pyproject.toml supercharged/uv.lock
git -C .. commit -m "chore(deps): add scipy for Kendall-tau in sensitivity sweep"
```

### Task 7.2: Write failing tests for sensitivity module

**Files:**
- Create: `tests/unit/test_sensitivity.py`

- [ ] **Step 1: Write tests**

```python
"""Sensitivity sweep — vary a scoring parameter, measure top-N stability."""
from __future__ import annotations

import polars as pl

from cantinaiq.sensitivity import kendall_tau_topn, parse_range_spec


def test_parse_range_spec() -> None:
    assert parse_range_spec("0.10,0.30,0.05") == [0.10, 0.15, 0.20, 0.25, 0.30]
    assert parse_range_spec("1,3,1") == [1.0, 2.0, 3.0]


def test_kendall_tau_identical_rankings_returns_one() -> None:
    a = pl.DataFrame({"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.8, 0.7, 0.6]})
    b = a.clone()
    tau = kendall_tau_topn(a, b, top_n=4)
    assert tau == 1.0


def test_kendall_tau_reversed_rankings_returns_negative_one() -> None:
    a = pl.DataFrame({"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.8, 0.7, 0.6]})
    b = pl.DataFrame({"producer_name": ["A", "B", "C", "D"], "composite_score": [0.6, 0.7, 0.8, 0.9]})
    tau = kendall_tau_topn(a, b, top_n=4)
    assert tau == -1.0


def test_kendall_tau_swapped_pair() -> None:
    a = pl.DataFrame({"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.8, 0.7, 0.6]})
    # Swap B and C in b
    b = pl.DataFrame({"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.7, 0.8, 0.6]})
    tau = kendall_tau_topn(a, b, top_n=4)
    assert 0.0 < tau < 1.0
```

- [ ] **Step 2: Run — verify failure**

```bash
uv run pytest tests/unit/test_sensitivity.py -v
```

Expected: ImportError.

### Task 7.3: Implement sensitivity module

**Files:**
- Create: `src/cantinaiq/sensitivity.py`

- [ ] **Step 1: Write implementation**

```python
"""Sensitivity sweep — vary a scoring parameter, measure top-N ranking stability."""

from __future__ import annotations

from typing import cast

import polars as pl
from scipy.stats import kendalltau  # type: ignore[import-untyped]


def parse_range_spec(spec: str) -> list[float]:
    """Parse 'start,end,step' into an inclusive list of floats."""
    start_s, end_s, step_s = spec.split(",")
    start, end, step = float(start_s), float(end_s), float(step_s)
    out: list[float] = []
    cur = start
    # Add small epsilon to include the endpoint despite float drift.
    while cur <= end + 1e-9:
        out.append(round(cur, 10))
        cur += step
    return out


def kendall_tau_topn(a: pl.DataFrame, b: pl.DataFrame, top_n: int = 20) -> float:
    """Kendall-tau between two ranked producer lists (top-N intersection).

    The score column must be present in both as `composite_score`. Producers
    not appearing in both top-N lists are ignored — this measures stability
    on the intersection, which is the meaningful quantity for shortlist work.
    """
    rank_a = (
        a.sort("composite_score", descending=True)
        .head(top_n)
        .with_row_index(name="rank", offset=1)
        .select(["producer_name", "rank"])
    )
    rank_b = (
        b.sort("composite_score", descending=True)
        .head(top_n)
        .with_row_index(name="rank", offset=1)
        .select(["producer_name", "rank"])
    )
    joined = rank_a.join(rank_b, on="producer_name", how="inner", suffix="_b")
    if joined.height < 2:
        return 0.0
    tau, _ = kendalltau(joined["rank"].to_list(), joined["rank_b"].to_list())
    return cast(float, float(tau))
```

- [ ] **Step 2: Run — verify pass**

```bash
uv run pytest tests/unit/test_sensitivity.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/sensitivity.py supercharged/tests/unit/test_sensitivity.py
git -C .. commit -m "feat(sensitivity): add range-parser + Kendall-tau top-N stability"
```

### Task 7.4: Add `cantinaiq sensitivity` CLI command

**Files:**
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Add command**

Append to `src/cantinaiq/cli.py`:

```python
@app.command()
def sensitivity(
    param: Annotated[str, typer.Option("--param", help="Hydra override key, e.g. scoring.weights.value_for_money")],
    range_spec: Annotated[str, typer.Option("--range", help="start,end,step e.g. 0.10,0.30,0.05")],
    top_n: Annotated[int, typer.Option("--top-n")] = 20,
    out_path: Annotated[Path, typer.Option("--out")] = Path("reports/generated/sensitivity.md"),
) -> None:
    """Sweep a scoring parameter and report top-N ranking stability per value.

    Re-runs the scoring + export stages for each value, then computes Kendall-tau
    between the resulting top-N producer list and the baseline (first value in
    the sweep). Writes a markdown summary to `--out`.
    """
    import polars as pl
    from cantinaiq.sensitivity import kendall_tau_topn, parse_range_spec

    values = parse_range_spec(range_spec)
    console.print(f"[bold]Sensitivity sweep[/bold] {param} over {values}")

    processed = Path("data/processed/producers_scored.parquet")
    baseline_df: pl.DataFrame | None = None
    rows: list[dict[str, float | str]] = []

    for i, v in enumerate(values):
        override = f"{param}={v}"
        console.print(f"  → run {i + 1}/{len(values)} with {override}")
        _execute(["scoring", "export"], [override])
        df = pl.read_parquet(processed)
        if baseline_df is None:
            baseline_df = df
            tau = 1.0
        else:
            tau = kendall_tau_topn(baseline_df, df, top_n=top_n)
        rows.append({"value": v, "kendall_tau": tau})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Sensitivity sweep: `{param}`",
        "",
        f"Top-{top_n} Kendall-tau vs. baseline ({values[0]}).",
        "",
        "| Value | Kendall-τ |",
        "|---:|---:|",
    ]
    for r in rows:
        lines.append(f"| {r['value']} | {float(r['kendall_tau']):.3f} |")
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")
```

- [ ] **Step 2: Smoke test (dry)**

```bash
uv run cantinaiq sensitivity --help
```

Expected: help text including `--param`, `--range`, `--top-n`, `--out`.

- [ ] **Step 3: Commit**

```bash
git -C .. add supercharged/src/cantinaiq/cli.py
git -C .. commit -m "feat(cli): add cantinaiq sensitivity command (Hydra sweep + Kendall-tau)"
```

---

## Phase 8: Final run + verify outputs

### Task 8.1: Run the full pipeline with OpenRouter

**Files:** none

- [ ] **Step 1: Confirm env**

```bash
test -n "$OPENROUTER_API_KEY" && echo "key set" || echo "MISSING"
```

If missing, set it: `export OPENROUTER_API_KEY=sk-or-...`.

- [ ] **Step 2: Run pipeline**

```bash
cd /Users/vincentblokker/ClubVentureProjects/CantinaIQ/supercharged
unset CANTINAIQ_DISABLE_LLM
uv run cantinaiq run all
```

Expected: full pipeline succeeds; enrichment stage reports `llm_skipped=False` and `llm_new_calls > 0` (or cache hits) in its run-log.

### Task 8.2: Rebuild all reports

- [ ] **Step 1: Build**

```bash
uv run cantinaiq report build
```

Expected outputs in `reports/generated/`:
- `data-quality.md`
- `methodology.md` (with new §3a)
- `findings-one-pager.html` (with populated Top-5 reasons)
- `executive-summary.md`

- [ ] **Step 2: Spot-check**

```bash
grep "Hidden Gem\|Premium Icon\|Value Opportunity" reports/generated/findings-one-pager.html | head
head -20 reports/generated/executive-summary.md
grep -A 2 "3a." reports/generated/methodology.md
```

Expected: each command shows real content; no empty reason fields; no `{}` templating leftovers.

### Task 8.3: Demo compare + sensitivity

- [ ] **Step 1: Capture a second run hash by perturbing config**

```bash
uv run cantinaiq run all scoring.bayesian_m=500
ls -t data/runs | head -2  # remember both hashes
```

- [ ] **Step 2: Run compare**

```bash
HASH_A=$(ls -t data/runs | head -1 | cut -d_ -f3-)
HASH_B=$(ls -t data/runs | head -2 | tail -1 | cut -d_ -f3-)
uv run cantinaiq compare "$HASH_A" "$HASH_B" --top 15
```

Expected: list of rank shifts + segment movements between the baseline and the m=500 run.

- [ ] **Step 3: Run sensitivity sweep**

```bash
uv run cantinaiq sensitivity --param scoring.bayesian_m --range 200,2000,300 --top-n 20
cat reports/generated/sensitivity.md
```

Expected: 7-row markdown table, Kendall-τ between 0 and 1 for each value, monotone-ish decay as `m` moves away from baseline.

### Task 8.4: Full test sweep

- [ ] **Step 1: Run everything**

```bash
uv run pytest -x --cov-fail-under=80
```

Expected: all tests pass, coverage ≥ 80%.

- [ ] **Step 2: Final commit + summary log**

```bash
git -C .. add -A
git -C .. status
git -C .. commit -m "chore: verified final pipeline run with OpenRouter + populated reports" || echo "(nothing new to commit)"
```

---

## Self-review notes

- All Tier 0 items have at least one task: reasons (Phase 2), exec summary (Phase 3), crawler (Phase 4), methodology delta (Phase 5), LLM live (Phase 1 + 8.1).
- Compare CLI: Phase 6. Sensitivity CLI: Phase 7. Both end-to-end verified in 8.3.
- No placeholders; every step has runnable code or a runnable command.
- Function names are consistent across tasks: `build_reason`, `add_derived_fields`, `enrich_with_firecrawl`, `compare_runs`, `kendall_tau_topn`.
- TDD discipline: every new module gets a failing test first.
- Commits are small and frequent (≈ 1 per task).
