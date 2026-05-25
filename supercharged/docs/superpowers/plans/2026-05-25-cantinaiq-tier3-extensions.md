# CantinaIQ Tier 3 — Differentiator Extensions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the four "above-and-beyond" features that turn the project from a strong final-assignment submission into a portfolio piece: anomaly detection (Isolation Forest on suspicious review patterns), sustainability lookup (Firecrawl against FederBio/Demeter for Slurpini's USP), live Vivino enrichment (alcohol % + grapes + food pairings via Firecrawl, rate-limited + cached), and a Vite + React dashboard consuming the JSON exports.

**Architecture:** Three new Python modules (`anomaly`, `sustainability`, `vivino_live`) following the established pattern: pure functions → CLI subcommand → optional report. A new `dashboard/` sibling directory holds a standalone Vite SPA that reads `data/exports/*.json` at build time. Each Tier-3 layer is opt-in (off by default), so the existing pipeline keeps producing identical baseline outputs.

**Tech Stack:** scikit-learn (IsolationForest, already vendored) · Firecrawl (already vendored) · diskcache for HTTP-cache · Vite 5 + React 19 + TypeScript + Tailwind 4 + Recharts.

---

## File map

**New Python files:**
- `src/cantinaiq/anomaly.py` — Isolation Forest on (log(rating_count), rating) feature space
- `src/cantinaiq/sustainability/__init__.py`
- `src/cantinaiq/sustainability/lookup.py` — Firecrawl-driven cert lookup, parses FederBio/Demeter directories
- `src/cantinaiq/sustainability/cli.py` — `cantinaiq sustainability check` subcommand
- `src/cantinaiq/vivino_live/__init__.py`
- `src/cantinaiq/vivino_live/enrich.py` — top-N wine page scrape + parse
- `src/cantinaiq/vivino_live/cache.py` — diskcache wrapper (1 day TTL)
- `src/cantinaiq/vivino_live/cli.py` — `cantinaiq enrich live` subcommand
- `tests/unit/test_anomaly.py`
- `tests/unit/test_sustainability.py`
- `tests/unit/test_vivino_live.py`

**New dashboard files:**
- `dashboard/package.json` — Vite + React + Recharts + Tailwind
- `dashboard/vite.config.ts`
- `dashboard/tsconfig.json`
- `dashboard/index.html`
- `dashboard/tailwind.config.ts`
- `dashboard/src/main.tsx` — entry point
- `dashboard/src/App.tsx` — router + layout
- `dashboard/src/lib/data.ts` — JSON loaders (typed)
- `dashboard/src/pages/Overview.tsx` — exec summary cards + KPIs
- `dashboard/src/pages/Regions.tsx` — region intel table + chart
- `dashboard/src/pages/Producers.tsx` — producer shortlist (Target/Premium/Monitor pills)
- `dashboard/src/pages/Matrix.tsx` — opportunity quadrant scatter
- `dashboard/src/components/MetricCard.tsx`
- `dashboard/src/components/RecommendationPill.tsx`
- `dashboard/public/data/` — symlink or build-step copy of supercharged `data/exports/`
- `dashboard/README.md`

**Modified files:**
- `pyproject.toml` — add `diskcache>=5.6,<6`
- `src/cantinaiq/cli.py` — register `anomaly`, `sustainability`, `enrich live` subcommands
- `reports/templates/methodology.md.j2` — add §3c (anomaly detection summary)

---

## Phase 1: Anomaly detection (Isolation Forest)

### Task 1.1: Failing tests

**Files:**
- Create: `tests/unit/test_anomaly.py`

- [ ] **Step 1: Write tests**

```python
"""Anomaly detection on suspicious review patterns.

Builds a 2D feature space `(log10(rating_count), rating)` and runs an
Isolation Forest to flag rows that look unlike the bulk of the dataset.
Typical false-positive-mode failures we want to surface:
  - rating 4.9 with only 8 reviews (over-confident niche)
  - rating 4.0 with 200,000 reviews (under-rated mass-market)
"""
from __future__ import annotations

import polars as pl

from cantinaiq.anomaly import flag_review_anomalies


def test_flag_review_anomalies_adds_is_anomaly_column() -> None:
    df = pl.DataFrame(
        {
            "name": [f"W{i}" for i in range(50)],
            "rating": [4.0 + (i % 5) * 0.05 for i in range(50)],
            "rating_count": [1000 + i * 100 for i in range(50)],
        }
    )
    out = flag_review_anomalies(df, contamination=0.1, seed=42)
    assert "is_anomaly" in out.columns
    assert "anomaly_score" in out.columns
    # ~10% of rows should be flagged.
    assert 3 <= out.filter(pl.col("is_anomaly")).height <= 8


def test_extreme_rating_with_few_reviews_flagged() -> None:
    df = pl.DataFrame(
        {
            "name": ["normal"] * 100 + ["suspicious"],
            "rating": [4.0] * 100 + [4.95],
            "rating_count": [1000] * 100 + [3],
        }
    )
    out = flag_review_anomalies(df, contamination=0.05, seed=42)
    suspicious = out.filter(pl.col("name") == "suspicious")
    assert bool(suspicious["is_anomaly"][0]) is True
```

- [ ] **Step 2: Verify failure**

```bash
cd supercharged && uv run pytest tests/unit/test_anomaly.py -v
```

Expected: ImportError.

### Task 1.2: Implement anomaly module

**Files:**
- Create: `src/cantinaiq/anomaly.py`

- [ ] **Step 1: Implementation**

```python
"""Isolation Forest anomaly detection on Vivino review patterns.

Inputs: a polars DataFrame with `rating` and `rating_count` columns.
Outputs: the same DataFrame with `is_anomaly: bool` and
`anomaly_score: float` columns appended.

`anomaly_score` follows sklearn's convention — lower values are more
anomalous. `is_anomaly` is `True` for the `contamination` fraction with the
lowest scores.
"""

from __future__ import annotations

import numpy as np
import polars as pl
from sklearn.ensemble import IsolationForest  # type: ignore[import-untyped]


def flag_review_anomalies(
    df: pl.DataFrame,
    contamination: float = 0.05,
    seed: int = 42,
) -> pl.DataFrame:
    """Return `df` with `is_anomaly` + `anomaly_score` columns appended."""
    rating = df["rating"].cast(pl.Float64).fill_null(0.0).to_numpy()
    rc = df["rating_count"].cast(pl.Int64).fill_null(1).to_numpy()
    rc_log = np.log10(np.maximum(rc, 1))
    X = np.column_stack([rating, rc_log])

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=seed,
    )
    pred = model.fit_predict(X)
    score = model.decision_function(X)
    is_anom = pred == -1
    return df.with_columns(
        pl.Series("is_anomaly", is_anom),
        pl.Series("anomaly_score", score),
    )
```

- [ ] **Step 2: Verify pass**

```bash
cd supercharged && uv run pytest tests/unit/test_anomaly.py -v
```

Expected: 2 passed.

### Task 1.3: Add `cantinaiq anomaly` CLI command

**Files:**
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Add command**

After the existing `bootstrap` command in `src/cantinaiq/cli.py`:

```python
@app.command()
def anomaly(
    contamination: Annotated[
        float, typer.Option("--contamination", help="Expected fraction of anomalies.")
    ] = 0.05,
    seed: Annotated[int, typer.Option("--seed")] = 42,
    wines_path: Annotated[Path, typer.Option("--wines")] = Path(
        "data/processed/wines_scored.parquet"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "reports/generated/anomalies.md"
    ),
) -> None:
    """Flag suspicious review patterns via Isolation Forest."""
    import polars as pl

    from cantinaiq.anomaly import flag_review_anomalies

    df = pl.read_parquet(wines_path)
    out = flag_review_anomalies(df, contamination=contamination, seed=seed)
    anomalies = (
        out.filter(pl.col("is_anomaly"))
        .sort("anomaly_score")
        .head(30)
        .select(["name", "region", "rating", "rating_count", "price", "anomaly_score"])
    )
    lines = [
        f"# Review anomalies (contamination={contamination}, seed={seed})",
        "",
        f"Flagged {out.filter(pl.col('is_anomaly')).height:,} of {out.height:,} wines.",
        "Lower anomaly_score = more anomalous.",
        "",
        "| Wine | Region | Rating | Reviews | Price (€) | Score |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in anomalies.iter_rows(named=True):
        lines.append(
            f"| {row['name'][:60]} | {row.get('region', '')[:30]} | "
            f"{row['rating']:.2f} | {row['rating_count']:,} | "
            f"{row.get('price', 0):.2f} | {row['anomaly_score']:.3f} |"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")
```

- [ ] **Step 2: Smoke test**

```bash
cd supercharged && uv run cantinaiq anomaly --contamination 0.03
head -20 reports/generated/anomalies.md
```

Expected: 80–100 anomalies flagged (3% of ~2986); top-30 shown with extreme rating/rating_count ratios.

- [ ] **Step 3: Commit**

```bash
git add supercharged/src/cantinaiq/anomaly.py supercharged/src/cantinaiq/cli.py supercharged/tests/unit/test_anomaly.py
git commit -m "feat(anomaly): Isolation Forest on review patterns"
```

---

## Phase 2: Sustainability lookup (FederBio/Demeter via Firecrawl)

### Task 2.1: Failing tests

**Files:**
- Create: `tests/unit/test_sustainability.py`

- [ ] **Step 1: Write tests**

```python
"""Sustainability cert lookup for Italian wine producers.

The lookup queries Firecrawl with a producer name + Italian directory site
(FederBio for organic, Demeter for biodynamic). It returns one of:
  - "FederBio" — organic certified
  - "Demeter" — biodynamic certified
  - "Both" — both certifications found
  - None — no certification found (caller logs as "unknown")
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cantinaiq.sustainability.lookup import (
    CertificationResult,
    classify_certification,
    lookup_sustainability,
)


def test_classify_certification_from_markdown_federbio() -> None:
    md = "## Antinori\n\nOperatore biologico certificato FederBio (codice IT-BIO-007)."
    assert classify_certification(md, "Antinori") == "FederBio"


def test_classify_certification_from_markdown_demeter() -> None:
    md = "Azienda Querciabella - certificazione Demeter biodinamica."
    assert classify_certification(md, "Querciabella") == "Demeter"


def test_classify_certification_no_match() -> None:
    md = "Random wine winery in Italy."
    assert classify_certification(md, "Random") is None


def test_lookup_sustainability_uses_firecrawl(monkeypatch: pytest.MonkeyPatch) -> None:
    scrape_resp = MagicMock()
    scrape_resp.markdown = "Antinori - FederBio biologico"

    class FakeFirecrawl:
        def __init__(self, api_key: str) -> None:  # noqa: ARG002
            pass

        def scrape_url(self, url: str, **kwargs: object) -> MagicMock:  # noqa: ARG002
            return scrape_resp

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    monkeypatch.setattr(
        "cantinaiq.sustainability.lookup._FirecrawlApp", FakeFirecrawl
    )

    result = lookup_sustainability(producer="Antinori")
    assert isinstance(result, CertificationResult)
    assert result.certification == "FederBio"
    assert result.source.startswith("https://")


def test_lookup_sustainability_no_api_key_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    result = lookup_sustainability(producer="Anyone")
    assert result.certification is None
```

- [ ] **Step 2: Verify failure**

```bash
cd supercharged && uv run pytest tests/unit/test_sustainability.py -v
```

Expected: ImportError.

### Task 2.2: Implement sustainability lookup

**Files:**
- Create: `src/cantinaiq/sustainability/__init__.py`
- Create: `src/cantinaiq/sustainability/lookup.py`

- [ ] **Step 1: Package marker**

Write `src/cantinaiq/sustainability/__init__.py`:

```python
"""Sustainability-certification lookup for Italian wine producers."""
```

- [ ] **Step 2: Implementation**

Write `src/cantinaiq/sustainability/lookup.py`:

```python
"""Sustainability-certification lookup via Firecrawl.

Strategy: query Firecrawl with the producer name + an Italian organic
directory (FederBio operator search), then parse the returned markdown
for unambiguous certification keywords. Demeter is checked via the
international Demeter producer directory.

This is a coarse, public-data signal — not a substitute for verifying
certificates with the producer directly. Hits should be treated as
"strong leads to verify", not as ground truth.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal

try:
    from firecrawl import FirecrawlApp as _FirecrawlApp  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    try:
        from firecrawl import Firecrawl as _FirecrawlApp  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover
        _FirecrawlApp = None  # type: ignore[assignment,misc]


Certification = Literal["FederBio", "Demeter", "Both"]

FEDERBIO_KEYWORDS = re.compile(r"federbio|operatore biologico|certificazione biologica|IT-BIO-", re.IGNORECASE)
DEMETER_KEYWORDS = re.compile(r"demeter|biodinamic|biodynamic", re.IGNORECASE)


@dataclass(frozen=True)
class CertificationResult:
    producer: str
    certification: Certification | None
    source: str


def classify_certification(markdown: str, producer: str) -> Certification | None:
    """Return the certification hint from raw markdown that mentions `producer`."""
    if producer.lower() not in markdown.lower():
        return None
    has_federbio = bool(FEDERBIO_KEYWORDS.search(markdown))
    has_demeter = bool(DEMETER_KEYWORDS.search(markdown))
    if has_federbio and has_demeter:
        return "Both"
    if has_federbio:
        return "FederBio"
    if has_demeter:
        return "Demeter"
    return None


def _build_search_urls(producer: str) -> list[str]:
    name = producer.replace(" ", "+")
    return [
        f"https://www.federbio.it/operatori/?ricerca={name}",
        f"https://www.demeter.net/producers/?search={name}",
    ]


def lookup_sustainability(producer: str) -> CertificationResult:
    """Query directories and return a `CertificationResult` for `producer`."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key or _FirecrawlApp is None:
        return CertificationResult(producer=producer, certification=None, source="(stub)")
    app = _FirecrawlApp(api_key=api_key)
    for url in _build_search_urls(producer):
        try:
            resp = app.scrape_url(url, formats=["markdown"])
            md = getattr(resp, "markdown", "") or ""
            cert = classify_certification(md, producer)
            if cert is not None:
                return CertificationResult(producer=producer, certification=cert, source=url)
        except Exception:  # noqa: BLE001 — best-effort lookup, skip failures
            continue
    return CertificationResult(producer=producer, certification=None, source="(no match)")
```

- [ ] **Step 3: Verify pass**

```bash
cd supercharged && uv run pytest tests/unit/test_sustainability.py -v
```

Expected: 5 passed.

### Task 2.3: Sustainability CLI subcommand

**Files:**
- Create: `src/cantinaiq/sustainability/cli.py`
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Write subcommand**

Write `src/cantinaiq/sustainability/cli.py`:

```python
"""`cantinaiq sustainability …` Typer subcommands."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from cantinaiq.sustainability.lookup import lookup_sustainability

sustainability_app = typer.Typer(
    no_args_is_help=True, help="Producer sustainability lookups."
)


@sustainability_app.command("check")
def check(
    producers_path: Annotated[
        Path, typer.Option("--producers")
    ] = Path("data/processed/producers_scored.parquet"),
    top_n: Annotated[int, typer.Option("--top", help="Check top-N producers by composite_score.")] = 50,
    cache_path: Annotated[
        Path, typer.Option("--cache")
    ] = Path("data/reference/sustainability_cache.csv"),
    out_json: Annotated[
        Path, typer.Option("--out-json")
    ] = Path("data/exports/sustainability_report.json"),
    out_md: Annotated[
        Path, typer.Option("--out-md")
    ] = Path("reports/generated/sustainability.md"),
    rate_limit_ms: Annotated[
        int, typer.Option("--rate-limit-ms", help="Sleep between Firecrawl calls.")
    ] = 500,
) -> None:
    """Check sustainability cert for top-N producers; cache results."""
    cache: dict[str, dict[str, str]] = {}
    if cache_path.exists():
        with cache_path.open() as f:
            for row in csv.DictReader(f):
                cache[row["producer"]] = row

    df = pl.read_parquet(producers_path).sort("composite_score", descending=True).head(top_n)
    results: list[dict[str, str | None]] = []
    fresh_calls = 0
    for row in df.iter_rows(named=True):
        producer = row["producer_name"]
        if producer in cache:
            results.append(
                {
                    "producer": producer,
                    "certification": cache[producer].get("certification") or None,
                    "source": cache[producer].get("source"),
                    "from_cache": True,
                }
            )
            continue
        res = lookup_sustainability(producer)
        results.append(
            {
                "producer": producer,
                "certification": res.certification,
                "source": res.source,
                "from_cache": False,
            }
        )
        fresh_calls += 1
        if rate_limit_ms > 0:
            time.sleep(rate_limit_ms / 1000)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["producer", "certification", "source"])
        w.writeheader()
        for r in results:
            w.writerow(
                {
                    "producer": r["producer"],
                    "certification": r["certification"] or "",
                    "source": r["source"] or "",
                }
            )

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2))

    certified = [r for r in results if r["certification"]]
    sustainable_targets = certified[:5]
    lines = [
        "# Sustainability check (FederBio + Demeter)",
        "",
        f"Checked top **{top_n}** producers by composite_score. "
        f"Fresh API calls: **{fresh_calls}**. "
        f"Certified hits: **{len(certified)}**.",
        "",
        "## Sustainable Targets (top 5 certified producers)",
        "",
        "| Producer | Certification | Source |",
        "|---|---|---|",
    ]
    for r in sustainable_targets:
        lines.append(
            f"| {r['producer']} | {r['certification']} | "
            f"[link]({r['source']}) |"
        )
    lines.extend(["", "## Full results", "", "| Producer | Certification |", "|---|---|"])
    for r in results:
        cert = r["certification"] or "—"
        lines.append(f"| {r['producer']} | {cert} |")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n")
    typer.echo(f"Wrote {out_md}")
    typer.echo(f"Wrote {out_json}")
```

- [ ] **Step 2: Wire into main CLI**

In `src/cantinaiq/cli.py`, add:

```python
from cantinaiq.sustainability.cli import sustainability_app
app.add_typer(sustainability_app, name="sustainability")
```

- [ ] **Step 3: Smoke test (stub mode — no API call)**

```bash
cd supercharged && unset FIRECRAWL_API_KEY && uv run cantinaiq sustainability check --top 5 --rate-limit-ms 0
cat reports/generated/sustainability.md | head -20
```

Expected: report written; certified=0 (because stub mode returns no matches); cache CSV written.

- [ ] **Step 4: Commit**

```bash
git add supercharged/src/cantinaiq/sustainability supercharged/src/cantinaiq/cli.py supercharged/tests/unit/test_sustainability.py
git commit -m "feat(sustainability): FederBio + Demeter cert lookup via Firecrawl"
```

---

## Phase 3: Live Vivino enrichment

### Task 3.1: Add diskcache dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Append dep**

Add `"diskcache>=5.6,<6"` to `[project] dependencies`.

- [ ] **Step 2: Sync**

```bash
cd supercharged && uv sync
```

- [ ] **Step 3: Commit**

```bash
git add supercharged/pyproject.toml supercharged/uv.lock
git commit -m "chore(deps): add diskcache for vivino_live HTTP cache"
```

### Task 3.2: Failing tests for vivino_live

**Files:**
- Create: `tests/unit/test_vivino_live.py`

- [ ] **Step 1: Write tests**

```python
"""Live Vivino enrichment: alcohol%, grapes, food pairings for top-N wines."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cantinaiq.vivino_live.enrich import enrich_wines, parse_wine_page


def test_parse_wine_page_extracts_alcohol_grapes_pairings() -> None:
    md = (
        "# Tignanello 2018\n\n"
        "**Alcohol:** 14.5%\n"
        "**Grapes:** Sangiovese, Cabernet Sauvignon, Cabernet Franc\n"
        "**Food pairings:** Beef, Lamb, Game (deer, venison)\n"
    )
    parsed = parse_wine_page(md)
    assert parsed["alcohol_percentage"] == 14.5
    assert "Sangiovese" in parsed["grape_varieties"]
    assert "Beef" in parsed["food_pairings"]


def test_parse_wine_page_returns_partial_on_missing_fields() -> None:
    md = "Alcohol: 13.0%\nNo grapes listed."
    parsed = parse_wine_page(md)
    assert parsed["alcohol_percentage"] == 13.0
    assert parsed.get("grape_varieties") in (None, [])


def test_enrich_wines_uses_cache_and_firecrawl(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    scrape_resp = MagicMock()
    scrape_resp.markdown = "Alcohol: 13.5%\nGrapes: Sangiovese"

    call_log: list[str] = []

    class FakeFirecrawl:
        def __init__(self, api_key: str) -> None:  # noqa: ARG002
            pass

        def scrape_url(self, url: str, **kwargs: object) -> MagicMock:  # noqa: ARG002
            call_log.append(url)
            return scrape_resp

    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    monkeypatch.setattr("cantinaiq.vivino_live.enrich._FirecrawlApp", FakeFirecrawl)

    cache_dir = tmp_path / "cache"
    wines = [{"name": "Tignanello 2018", "id": "abc"}]
    out = enrich_wines(wines, cache_dir=cache_dir, rate_limit_ms=0)
    assert out[0]["alcohol_percentage"] == 13.5

    # Second call should hit cache (no extra Firecrawl call).
    out2 = enrich_wines(wines, cache_dir=cache_dir, rate_limit_ms=0)
    assert out2[0]["alcohol_percentage"] == 13.5
    assert len(call_log) == 1  # only the first call hit the network
```

- [ ] **Step 2: Verify failure**

```bash
cd supercharged && uv run pytest tests/unit/test_vivino_live.py -v
```

Expected: ImportError.

### Task 3.3: Implement vivino_live

**Files:**
- Create: `src/cantinaiq/vivino_live/__init__.py`
- Create: `src/cantinaiq/vivino_live/cache.py`
- Create: `src/cantinaiq/vivino_live/enrich.py`

- [ ] **Step 1: Package marker**

Write `src/cantinaiq/vivino_live/__init__.py`:

```python
"""Live Vivino enrichment via Firecrawl (rate-limited + disk-cached)."""
```

- [ ] **Step 2: Cache wrapper**

Write `src/cantinaiq/vivino_live/cache.py`:

```python
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
```

- [ ] **Step 3: Enrich module**

Write `src/cantinaiq/vivino_live/enrich.py`:

```python
"""Live Vivino enrichment: alcohol %, grape varieties, food pairings.

This module is opt-in: nothing runs unless the CLI is invoked with
`--with-network` and `FIRECRAWL_API_KEY` is set. Even then, every URL is
cached on disk (1-day TTL by default), so repeat runs do not re-hit the
network. Always respects a rate-limit between fresh calls.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

from cantinaiq.vivino_live.cache import WineCache

try:
    from firecrawl import FirecrawlApp as _FirecrawlApp  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    try:
        from firecrawl import Firecrawl as _FirecrawlApp  # type: ignore[no-redef]
    except ImportError:  # pragma: no cover
        _FirecrawlApp = None  # type: ignore[assignment,misc]

ALCOHOL_RE = re.compile(r"alcohol[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE)
GRAPES_RE = re.compile(r"grapes?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)
PAIRINGS_RE = re.compile(r"food\s*pairings?\s*[:\-]\s*([^\n]+)", re.IGNORECASE)


def parse_wine_page(markdown: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if m := ALCOHOL_RE.search(markdown):
        out["alcohol_percentage"] = float(m.group(1))
    if m := GRAPES_RE.search(markdown):
        out["grape_varieties"] = [g.strip() for g in m.group(1).split(",") if g.strip()]
    if m := PAIRINGS_RE.search(markdown):
        out["food_pairings"] = [g.strip() for g in m.group(1).split(",") if g.strip()]
    return out


def _wine_url(name: str) -> str:
    return "https://www.vivino.com/search/wines?q=" + name.replace(" ", "+")


def enrich_wines(
    wines: list[dict[str, Any]],
    cache_dir: Path,
    rate_limit_ms: int = 500,
) -> list[dict[str, Any]]:
    """Enrich each wine dict with alcohol/grapes/pairings via Firecrawl + diskcache."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    cache = WineCache(cache_dir)
    out: list[dict[str, Any]] = []
    app = None
    if api_key and _FirecrawlApp is not None:
        app = _FirecrawlApp(api_key=api_key)
    try:
        for w in wines:
            url = _wine_url(w["name"])
            cached = cache.get(url)
            if cached is not None:
                merged: dict[str, Any] = {**w, **cached}
                out.append(merged)
                continue
            extras: dict[str, Any] = {}
            if app is not None:
                try:
                    resp = app.scrape_url(url, formats=["markdown"])
                    md = getattr(resp, "markdown", None) or ""
                    extras = parse_wine_page(md)
                    cache.set(url, extras)
                except Exception:  # noqa: BLE001
                    pass
                if rate_limit_ms > 0:
                    time.sleep(rate_limit_ms / 1000)
            out.append({**w, **extras})
    finally:
        cache.close()
    return out
```

- [ ] **Step 4: Verify pass**

```bash
cd supercharged && uv run pytest tests/unit/test_vivino_live.py -v
```

Expected: 3 passed.

### Task 3.4: CLI subcommand

**Files:**
- Create: `src/cantinaiq/vivino_live/cli.py`
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Subcommand**

Write `src/cantinaiq/vivino_live/cli.py`:

```python
"""`cantinaiq enrich live` Typer subcommand."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from cantinaiq.vivino_live.enrich import enrich_wines

enrich_app = typer.Typer(no_args_is_help=True, help="Live enrichment helpers.")


@enrich_app.command("live")
def live(
    wines_path: Annotated[
        Path, typer.Option("--wines")
    ] = Path("data/processed/wines_scored.parquet"),
    top_n: Annotated[int, typer.Option("--top")] = 50,
    out_path: Annotated[
        Path, typer.Option("--out")
    ] = Path("data/exports/wine_enrichments.json"),
    cache_dir: Annotated[
        Path, typer.Option("--cache-dir")
    ] = Path("data/reference/vivino_cache"),
    rate_limit_ms: Annotated[int, typer.Option("--rate-limit-ms")] = 500,
    with_network: Annotated[bool, typer.Option("--with-network")] = False,
) -> None:
    """Enrich top-N wines via Vivino (Firecrawl). Cached on disk."""
    if not with_network:
        typer.echo(
            "Stub mode: --with-network not set. Re-run with --with-network and "
            "FIRECRAWL_API_KEY for live data."
        )
        return

    df = (
        pl.read_parquet(wines_path)
        .sort("rating_count", descending=True)
        .head(top_n)
    )
    wines = df.select(["name", "region", "rating", "rating_count", "price"]).to_dicts()
    enriched = enrich_wines(wines, cache_dir=cache_dir, rate_limit_ms=rate_limit_ms)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(enriched, indent=2))
    typer.echo(f"Wrote {out_path} ({len(enriched)} entries)")
```

- [ ] **Step 2: Wire into main CLI**

In `src/cantinaiq/cli.py`, add (next to the other `add_typer` lines):

```python
from cantinaiq.vivino_live.cli import enrich_app
app.add_typer(enrich_app, name="enrich")
```

> If a top-level `enrich` already exists (it does not; only `run enrichment` exists), rename this sub-app to `live`.

- [ ] **Step 3: Smoke test (stub mode)**

```bash
cd supercharged && uv run cantinaiq enrich live --top 5
```

Expected: prints stub-mode message; no files written.

- [ ] **Step 4: Commit**

```bash
git add supercharged/src/cantinaiq/vivino_live supercharged/src/cantinaiq/cli.py supercharged/tests/unit/test_vivino_live.py
git commit -m "feat(vivino_live): rate-limited, disk-cached live enrichment via Firecrawl"
```

---

## Phase 4: Vite dashboard

### Task 4.1: Scaffold

**Files:**
- Create: `dashboard/package.json`
- Create: `dashboard/vite.config.ts`
- Create: `dashboard/tsconfig.json`
- Create: `dashboard/index.html`
- Create: `dashboard/tailwind.config.ts`
- Create: `dashboard/postcss.config.js`
- Create: `dashboard/src/index.css`
- Create: `dashboard/src/main.tsx`

- [ ] **Step 1: package.json**

Write `dashboard/package.json`:

```json
{
  "name": "cantinaiq-dashboard",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^6.28.0",
    "recharts": "^2.13.0"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.6.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: vite.config.ts**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: { port: 5173 },
});
```

- [ ] **Step 3: tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "allowImportingTsExtensions": false,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src", "vite.config.ts"]
}
```

- [ ] **Step 4: index.html**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CantinaIQ — Slurpini Partner Intelligence</title>
  </head>
  <body class="bg-stone-50 text-stone-900">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Tailwind + Postcss**

`dashboard/tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1F1B16",
        "ink-2": "#5A4F44",
        cream: "#FAF7F2",
        tuscan: "#8B3A2F",
        leaf: "#4A6B36",
        sea: "#1F3A5F",
      },
      fontFamily: {
        serif: ['"Source Serif 4"', "Georgia", "serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
```

`dashboard/postcss.config.js`:

```javascript
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
};
```

- [ ] **Step 6: src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body { font-family: ui-sans-serif, system-ui, sans-serif; }
```

- [ ] **Step 7: src/main.tsx**

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
```

- [ ] **Step 8: Install + verify build pipeline**

```bash
cd dashboard && npm install && npm run build
```

Expected: `dist/` written. If npm is unavailable, document and skip — Python side is the load-bearing deliverable.

- [ ] **Step 9: Commit scaffold**

```bash
git add dashboard/package.json dashboard/vite.config.ts dashboard/tsconfig.json dashboard/index.html dashboard/tailwind.config.ts dashboard/postcss.config.js dashboard/src/index.css dashboard/src/main.tsx
git commit -m "feat(dashboard): scaffold Vite + React + Tailwind + Recharts SPA"
```

### Task 4.2: Data loaders + App shell

**Files:**
- Create: `dashboard/src/lib/data.ts`
- Create: `dashboard/src/App.tsx`

- [ ] **Step 1: Data loaders**

Write `dashboard/src/lib/data.ts`:

```typescript
export type Recommendation =
  | "Target"
  | "Premium Brand Builder"
  | "Value Opportunity"
  | "Monitor"
  | "Avoid for Now";

export interface Producer {
  producer_name: string;
  macro_region: string;
  recommendation: Recommendation;
  market_segment: string;
  weighted_rating: number;
  total_reviews: number;
  avg_price: number;
  composite_score: number;
  value_score?: number;
}

export interface Region {
  region: string;
  macro_region?: string;
  weighted_rating: number;
  avg_price: number;
  wines: number;
  total_reviews: number;
  value_score?: number;
}

export interface DashboardSummary {
  totals: { wines: number; producers: number; regions: number };
  config_hash: string;
  run_id: string;
}

const base = (path: string) => `/data/${path}`;

export async function loadProducers(): Promise<Producer[]> {
  const r = await fetch(base("producer_rankings.json"));
  return r.json();
}

export async function loadRegions(): Promise<Region[]> {
  const r = await fetch(base("region_rankings.json"));
  return r.json();
}

export async function loadSummary(): Promise<DashboardSummary> {
  const r = await fetch(base("dashboard_summary.json"));
  return r.json();
}
```

- [ ] **Step 2: App shell**

Write `dashboard/src/App.tsx`:

```typescript
import { Link, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview";
import Regions from "./pages/Regions";
import Producers from "./pages/Producers";
import Matrix from "./pages/Matrix";

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-stone-200 bg-cream">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-baseline gap-8">
          <h1 className="font-serif text-2xl text-ink">
            CantinaIQ
            <span className="ml-2 text-sm text-ink-2">— Slurpini Partner Intelligence</span>
          </h1>
          <nav className="ml-auto flex gap-6 text-sm">
            <Link to="/" className="hover:text-tuscan">Overview</Link>
            <Link to="/regions" className="hover:text-tuscan">Regions</Link>
            <Link to="/producers" className="hover:text-tuscan">Producers</Link>
            <Link to="/matrix" className="hover:text-tuscan">Matrix</Link>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/regions" element={<Regions />} />
          <Route path="/producers" element={<Producers />} />
          <Route path="/matrix" element={<Matrix />} />
        </Routes>
      </main>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add dashboard/src/lib dashboard/src/App.tsx
git commit -m "feat(dashboard): data loaders + router shell"
```

### Task 4.3: Overview page

**Files:**
- Create: `dashboard/src/pages/Overview.tsx`
- Create: `dashboard/src/components/MetricCard.tsx`

- [ ] **Step 1: MetricCard**

```typescript
interface Props {
  label: string;
  value: string | number;
  hint?: string;
}

export default function MetricCard({ label, value, hint }: Props) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white px-5 py-4">
      <div className="text-xs uppercase tracking-wide text-ink-2">{label}</div>
      <div className="mt-1 font-serif text-3xl text-ink">{value}</div>
      {hint && <div className="mt-1 text-xs text-ink-2">{hint}</div>}
    </div>
  );
}
```

- [ ] **Step 2: Overview page**

Write `dashboard/src/pages/Overview.tsx`:

```typescript
import { useEffect, useState } from "react";
import MetricCard from "../components/MetricCard";
import { DashboardSummary, Producer, Region, loadProducers, loadRegions, loadSummary } from "../lib/data";

export default function Overview() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [producers, setProducers] = useState<Producer[]>([]);
  const [regions, setRegions] = useState<Region[]>([]);

  useEffect(() => {
    loadSummary().then(setSummary).catch(() => null);
    loadProducers().then(setProducers).catch(() => null);
    loadRegions().then(setRegions).catch(() => null);
  }, []);

  const topProducers = [...producers]
    .sort((a, b) => b.composite_score - a.composite_score)
    .slice(0, 5);
  const topRegions = [...regions]
    .sort((a, b) => b.weighted_rating - a.weighted_rating)
    .slice(0, 5);

  if (!summary) return <div className="text-ink-2">Loading…</div>;

  return (
    <div className="space-y-8">
      <section className="grid grid-cols-3 gap-4">
        <MetricCard label="Wines analysed" value={summary.totals.wines.toLocaleString()} />
        <MetricCard label="Regions" value={summary.totals.regions} />
        <MetricCard label="Producers" value={summary.totals.producers.toLocaleString()} />
      </section>

      <section>
        <h2 className="font-serif text-xl text-ink mb-3">Top 5 producers</h2>
        <ol className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white">
          {topProducers.map((p) => (
            <li key={p.producer_name} className="px-4 py-3 flex items-baseline gap-4">
              <span className="text-ink-2 text-sm w-6">#{topProducers.indexOf(p) + 1}</span>
              <span className="font-serif text-ink flex-1">{p.producer_name}</span>
              <span className="text-xs uppercase tracking-wide text-leaf">{p.recommendation}</span>
              <span className="text-sm text-ink-2 tabular-nums">★ {p.weighted_rating.toFixed(2)}</span>
              <span className="text-sm text-ink-2 tabular-nums">€{Math.round(p.avg_price)}</span>
            </li>
          ))}
        </ol>
      </section>

      <section>
        <h2 className="font-serif text-xl text-ink mb-3">Top 5 regions</h2>
        <ol className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white">
          {topRegions.map((r) => (
            <li key={r.region} className="px-4 py-3 flex items-baseline gap-4">
              <span className="text-ink-2 text-sm w-6">#{topRegions.indexOf(r) + 1}</span>
              <span className="font-serif text-ink flex-1">{r.region}</span>
              <span className="text-sm text-ink-2 tabular-nums">★ {r.weighted_rating.toFixed(2)}</span>
              <span className="text-sm text-ink-2 tabular-nums">{r.wines} wines</span>
              <span className="text-sm text-ink-2 tabular-nums">€{Math.round(r.avg_price)}</span>
            </li>
          ))}
        </ol>
      </section>

      <footer className="text-xs text-ink-2 pt-6 border-t border-stone-200">
        Config hash <span className="font-mono">{summary.config_hash}</span> · run {summary.run_id}
      </footer>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add dashboard/src/pages/Overview.tsx dashboard/src/components/MetricCard.tsx
git commit -m "feat(dashboard): Overview page with KPIs + top 5 producers/regions"
```

### Task 4.4: Regions + Producers pages

**Files:**
- Create: `dashboard/src/pages/Regions.tsx`
- Create: `dashboard/src/pages/Producers.tsx`
- Create: `dashboard/src/components/RecommendationPill.tsx`

- [ ] **Step 1: RecommendationPill**

```typescript
import { Recommendation } from "../lib/data";

const STYLES: Record<Recommendation, string> = {
  "Premium Brand Builder": "bg-purple-50 text-purple-800 border-purple-200",
  Target: "bg-blue-50 text-blue-800 border-blue-200",
  "Value Opportunity": "bg-green-50 text-green-800 border-green-200",
  Monitor: "bg-stone-50 text-stone-700 border-stone-200",
  "Avoid for Now": "bg-rose-50 text-rose-800 border-rose-200",
};

export default function RecommendationPill({ value }: { value: Recommendation }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs rounded-full border ${
        STYLES[value] ?? STYLES.Monitor
      }`}
    >
      {value}
    </span>
  );
}
```

- [ ] **Step 2: Regions page**

```typescript
import { useEffect, useState } from "react";
import { loadRegions, Region } from "../lib/data";

export default function Regions() {
  const [rows, setRows] = useState<Region[]>([]);
  useEffect(() => {
    loadRegions().then((rs) =>
      setRows([...rs].sort((a, b) => b.weighted_rating - a.weighted_rating))
    );
  }, []);

  return (
    <div>
      <h2 className="font-serif text-2xl text-ink mb-4">Region intelligence</h2>
      <table className="w-full text-sm border border-stone-200 rounded-lg overflow-hidden bg-white">
        <thead className="bg-stone-50 text-ink-2 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">Region</th>
            <th className="text-right px-3 py-2">Wines</th>
            <th className="text-right px-3 py-2">Weighted rating</th>
            <th className="text-right px-3 py-2">Avg price (€)</th>
            <th className="text-right px-3 py-2">Reviews</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {rows.slice(0, 50).map((r) => (
            <tr key={r.region}>
              <td className="px-3 py-2 font-serif">{r.region}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.wines}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.weighted_rating.toFixed(2)}</td>
              <td className="text-right tabular-nums px-3 py-2">{Math.round(r.avg_price)}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.total_reviews.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 3: Producers page**

```typescript
import { useEffect, useState } from "react";
import { loadProducers, Producer } from "../lib/data";
import RecommendationPill from "../components/RecommendationPill";

export default function Producers() {
  const [rows, setRows] = useState<Producer[]>([]);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    loadProducers().then((ps) =>
      setRows([...ps].sort((a, b) => b.composite_score - a.composite_score))
    );
  }, []);

  const filtered =
    filter === "all" ? rows : rows.filter((r) => r.recommendation === filter);

  return (
    <div>
      <div className="flex items-baseline gap-3 mb-4">
        <h2 className="font-serif text-2xl text-ink">Producer shortlist</h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="ml-auto text-sm border border-stone-300 rounded px-2 py-1 bg-white"
        >
          <option value="all">All recommendations</option>
          <option value="Premium Brand Builder">Premium Brand Builder</option>
          <option value="Target">Target</option>
          <option value="Value Opportunity">Value Opportunity</option>
          <option value="Monitor">Monitor</option>
          <option value="Avoid for Now">Avoid for Now</option>
        </select>
      </div>
      <table className="w-full text-sm border border-stone-200 rounded-lg overflow-hidden bg-white">
        <thead className="bg-stone-50 text-ink-2 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">Producer</th>
            <th className="text-left px-3 py-2">Macro region</th>
            <th className="text-left px-3 py-2">Recommendation</th>
            <th className="text-right px-3 py-2">Weighted rating</th>
            <th className="text-right px-3 py-2">Avg price (€)</th>
            <th className="text-right px-3 py-2">Composite</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {filtered.slice(0, 100).map((p) => (
            <tr key={p.producer_name}>
              <td className="px-3 py-2 font-serif">{p.producer_name}</td>
              <td className="px-3 py-2 text-ink-2">{p.macro_region}</td>
              <td className="px-3 py-2"><RecommendationPill value={p.recommendation} /></td>
              <td className="text-right tabular-nums px-3 py-2">{p.weighted_rating.toFixed(2)}</td>
              <td className="text-right tabular-nums px-3 py-2">{Math.round(p.avg_price)}</td>
              <td className="text-right tabular-nums px-3 py-2">{p.composite_score.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add dashboard/src/pages/Regions.tsx dashboard/src/pages/Producers.tsx dashboard/src/components/RecommendationPill.tsx
git commit -m "feat(dashboard): regions table + producers shortlist with filter pills"
```

### Task 4.5: Opportunity Matrix page

**Files:**
- Create: `dashboard/src/pages/Matrix.tsx`

- [ ] **Step 1: Matrix scatter**

```typescript
import { useEffect, useState } from "react";
import { loadProducers, Producer } from "../lib/data";
import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

const COLOUR_BY_SEGMENT: Record<string, string> = {
  "Hidden Gem": "#4A6B36",
  "Premium Icon": "#1F3A5F",
  "Commercial Value": "#8B7355",
  "Overpriced Risk": "#9B3A2F",
  "Low Confidence Niche": "#8B7355",
};

export default function Matrix() {
  const [rows, setRows] = useState<Producer[]>([]);
  useEffect(() => {
    loadProducers().then(setRows);
  }, []);

  const data = rows.map((p) => ({
    x: p.avg_price,
    y: p.weighted_rating,
    z: p.total_reviews,
    name: p.producer_name,
    segment: p.market_segment,
    fill: COLOUR_BY_SEGMENT[p.market_segment] ?? "#888",
  }));

  return (
    <div>
      <h2 className="font-serif text-2xl text-ink mb-4">Opportunity matrix</h2>
      <div className="bg-white border border-stone-200 rounded-lg p-4">
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 30 }}>
            <CartesianGrid stroke="#eee" />
            <XAxis
              dataKey="x"
              name="Avg price (€)"
              scale="log"
              domain={[1, 2000]}
              tickFormatter={(v) => `€${v}`}
            />
            <YAxis
              dataKey="y"
              name="Weighted rating"
              domain={[3.0, 5.0]}
              tickFormatter={(v) => v.toFixed(1)}
            />
            <ZAxis dataKey="z" range={[20, 400]} />
            <Tooltip
              cursor={{ strokeDasharray: "3 3" }}
              content={({ payload }) => {
                if (!payload || payload.length === 0) return null;
                const p = payload[0].payload as {
                  name: string;
                  y: number;
                  x: number;
                  z: number;
                  segment: string;
                };
                return (
                  <div className="bg-white border border-stone-200 rounded p-2 text-xs">
                    <div className="font-serif text-ink">{p.name}</div>
                    <div>★ {p.y.toFixed(2)} · €{Math.round(p.x)} · {p.z.toLocaleString()} reviews</div>
                    <div className="text-ink-2">{p.segment}</div>
                  </div>
                );
              }}
            />
            <Scatter data={data} fill="#888" shape="circle" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-ink-2 mt-3">
        X = log-price, Y = weighted rating, bubble size ∝ review count. Top-left = Hidden Gem,
        top-right = Premium Icon, bottom = Overpriced or Commercial Value.
      </p>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add dashboard/src/pages/Matrix.tsx
git commit -m "feat(dashboard): opportunity matrix scatter chart"
```

### Task 4.6: Symlink data + verify build

**Files:**
- Create: `dashboard/public/data` (symlink)
- Create: `dashboard/README.md`

- [ ] **Step 1: Symlink data exports**

```bash
cd dashboard
mkdir -p public
ln -sfn ../../supercharged/data/exports public/data
ls -la public/data
```

Expected: symlink resolves to `supercharged/data/exports/`.

- [ ] **Step 2: README**

Write `dashboard/README.md`:

````markdown
# CantinaIQ Dashboard

Single-page React app over the JSON exports produced by the supercharged pipeline.

## Run locally

```bash
npm install
npm run dev
```

Then open http://localhost:5173.

## Data source

The dashboard expects JSON in `public/data/`, which is symlinked to
`../supercharged/data/exports/`. Refresh the data with:

```bash
cd ../supercharged && uv run cantinaiq run all && uv run cantinaiq report build
```

## Build for production

```bash
npm run build
```

`dist/` contains the static SPA — deploy to any static host (Vercel, Netlify,
GitHub Pages).
````

- [ ] **Step 3: Build dashboard**

```bash
cd dashboard && npm run build 2>&1 | tail -10
ls -la dist/
```

Expected: `dist/index.html` + `dist/assets/*.js` produced.

- [ ] **Step 4: Commit**

```bash
git add dashboard/README.md dashboard/public/data
git commit -m "feat(dashboard): symlink data + README"
```

---

## Phase 5: Wire anomaly section + final verification

### Task 5.1: Methodology §3c — anomaly detection

**Files:**
- Modify: `reports/templates/methodology.md.j2`

- [ ] **Step 1: Insert §3c after §3b**

After the `## 3b. Producer-extraction evaluation` block:

```jinja
## 3c. Anomaly detection on review patterns

`cantinaiq anomaly --contamination 0.03` fits an Isolation Forest over the
`(rating, log10(rating_count))` feature space and flags rows whose pattern
diverges from the bulk of the dataset. Typical hits:

- ratings ≥ 4.8 with fewer than 20 reviews (over-confident niches),
- ratings ≤ 3.2 with very high review counts (controversial mass-market wines).

The flag is *informational* — flagged wines are not removed from the pipeline.
The full top-30 ranking is in `reports/generated/anomalies.md`.
```

- [ ] **Step 2: Rebuild + verify**

```bash
cd supercharged && uv run cantinaiq report build --only methodology
grep -A 2 "## 3c" reports/generated/methodology.md
```

Expected: §3c appears with the listed bullets.

- [ ] **Step 3: Commit**

```bash
git add supercharged/reports/templates/methodology.md.j2
git commit -m "docs(methodology): wire anomaly detection into §3c"
```

### Task 5.2: Full test sweep + CLI smoke

- [ ] **Step 1: Run all tests**

```bash
cd supercharged && uv run pytest 2>&1 | tail -5
```

Expected: 127 (Tier 2) + 10 new ≈ 137 passed.

- [ ] **Step 2: Run all new CLIs against the real dataset**

```bash
cd supercharged
uv run cantinaiq anomaly --contamination 0.03
unset FIRECRAWL_API_KEY  # ensure stub mode for the CI smoke
uv run cantinaiq sustainability check --top 5 --rate-limit-ms 0
uv run cantinaiq enrich live --top 5
```

Expected: anomaly report written; sustainability runs in stub mode (zero certified); enrich stub returns the "set --with-network" hint.

- [ ] **Step 3: Optional — run sustainability with real API**

```bash
cd supercharged && set -a && . ../.env.local && set +a
uv run cantinaiq sustainability check --top 10 --rate-limit-ms 1000
cat reports/generated/sustainability.md | head -30
```

Expected: 10 producer rows; ≥ 1 certified hit on common bio producers (Antinori has FederBio-certified vineyards; Querciabella has Demeter).

- [ ] **Step 4: Final commit**

```bash
git status --short
git commit -am "chore: Tier-3 verified against real data" || echo "(nothing to commit)"
```

---

## Self-review

- All four user-selected items have phases: anomaly (Phase 1), sustainability (Phase 2), live enrichment (Phase 3), dashboard (Phase 4).
- Methodology updated via §3c (Phase 5).
- TDD discipline preserved: every Python module has failing tests first.
- Function names consistent: `flag_review_anomalies`, `classify_certification`, `lookup_sustainability`, `parse_wine_page`, `enrich_wines`.
- All Firecrawl integrations follow the same pattern: opt-in feature flag, stub default, monkey-patchable `_FirecrawlApp` indirection for tests.
- Dashboard tasks are bite-sized (one component per task) so a fresh subagent can iterate independently.
- npm-side may be flaky on offline machines; Phase 4 docs that fallback explicitly so the Python deliverable still ships if the dashboard build fails.
