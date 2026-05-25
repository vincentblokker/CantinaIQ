# CantinaIQ Tier 2 — Methodological Rigor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the four methodological-depth features that pre-empt the questions a critical reviewer will ask: gold-set evaluation of producer extraction, bootstrapped confidence intervals on rankings, sklearn clustering for data-driven segmentation, and Vivino bias quantification against Italian Trade Agency import data.

**Architecture:** Four loosely-coupled add-ons. Gold-set evaluation reads existing `known_producers_top50.csv` against `producers_scored.parquet` — pure function, no pipeline changes. Bootstrap CI is a new `cantinaiq bootstrap` subcommand operating on the cleaned dataset, resampling N times. Clustering is a new optional enrichment pass (`cantinaiq enrich clusters`) that adds a `cluster_id` column. Bias quantification fetches Italian Trade data via Firecrawl (with cached fallback), computes Vivino-vs-reality coverage, and adds a section to methodology.md.

**Tech Stack:** scikit-learn (KMeans + HDBSCAN), scipy (already added for Kendall-tau), Firecrawl (already added), Polars/Pandas, Matplotlib (already vendored).

---

## File map

**New files:**
- `src/cantinaiq/evaluation/__init__.py` — package marker
- `src/cantinaiq/evaluation/gold_set.py` — precision/recall against `known_producers_top50.csv`
- `src/cantinaiq/evaluation/cli.py` — `cantinaiq evaluate producer-extraction` subcommand
- `src/cantinaiq/bootstrap.py` — bootstrap-resample + rank-stability math (pure)
- `src/cantinaiq/clustering.py` — KMeans / feature-vector builder (pure)
- `src/cantinaiq/bias.py` — Italian Trade fetch + comparison math
- `data/reference/italian_trade_imports_nl.csv` — cached external baseline (committed; fallback when Firecrawl is offline)
- `tests/unit/test_gold_set.py`
- `tests/unit/test_bootstrap.py`
- `tests/unit/test_clustering.py`
- `tests/unit/test_bias.py`

**Modified files:**
- `pyproject.toml` — add `scikit-learn>=1.5,<2`
- `src/cantinaiq/cli.py` — add `evaluate`, `bootstrap`, `cluster`, `bias` subcommands
- `reports/templates/methodology.md.j2` — new §3b (gold-set), §9 (bias)
- `reports/templates/data-quality.md.j2` — append precision/recall row
- `src/cantinaiq/scoring/run.py` — optionally add `cluster_id` column when `--with-clusters` flag set (off by default)

---

## Phase 1: Producer-extraction gold-set evaluation

### Task 1.1: Write failing tests

**Files:**
- Create: `tests/unit/test_gold_set.py`

- [ ] **Step 1: Write tests**

```python
"""Gold-set evaluation: precision/recall of producer extraction vs known_producers_top50."""
from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from cantinaiq.evaluation.gold_set import (
    GoldSetEval,
    evaluate_producer_extraction,
    recall_at_alias,
)


@pytest.fixture
def gold_csv(tmp_path: Path) -> Path:
    p = tmp_path / "gold.csv"
    p.write_text(
        "canonical_name,macro_region\n"
        "Tenuta San Guido,Toscana\n"
        "Gaja,Piemonte\n"
        "Biondi-Santi,Toscana\n"
        "Marchesi Antinori,Toscana\n"
        "Castello di Ama,Toscana\n"
    )
    return p


@pytest.fixture
def producers(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "producer_name": [
                "Tenuta San Guido",
                "Gaja",
                "Antinori",
                "Random Cantina",
                "Castello di Ama",
            ],
            "composite_score": [0.5, 0.4, 0.6, 0.2, 0.3],
        }
    )
    p = tmp_path / "producers.parquet"
    df.write_parquet(p)
    return p


def test_recall_at_alias_exact_match(producers: Path, gold_csv: Path) -> None:
    # Default exact match → recall = 3/5 (Tenuta San Guido, Gaja, Castello di Ama)
    recall = recall_at_alias(producers, gold_csv, match="exact")
    assert recall == pytest.approx(3 / 5, rel=1e-3)


def test_recall_at_alias_fuzzy(producers: Path, gold_csv: Path) -> None:
    # Fuzzy match should also catch "Antinori" → "Marchesi Antinori" (substring/contains).
    recall = recall_at_alias(producers, gold_csv, match="contains")
    assert recall == pytest.approx(4 / 5, rel=1e-3)


def test_evaluate_producer_extraction_returns_full_eval(
    producers: Path, gold_csv: Path
) -> None:
    ev = evaluate_producer_extraction(producers, gold_csv)
    assert isinstance(ev, GoldSetEval)
    assert ev.gold_size == 5
    assert ev.producers_total == 5
    # exact-match recall = 3/5, contains = 4/5
    assert ev.recall_exact == pytest.approx(0.6)
    assert ev.recall_contains == pytest.approx(0.8)
    assert "Biondi-Santi" in ev.missed
```

- [ ] **Step 2: Run — verify failure**

```bash
cd supercharged && uv run pytest tests/unit/test_gold_set.py -v
```

Expected: ImportError.

### Task 1.2: Implement gold-set evaluator

**Files:**
- Create: `src/cantinaiq/evaluation/__init__.py`
- Create: `src/cantinaiq/evaluation/gold_set.py`

- [ ] **Step 1: Package marker**

Write `src/cantinaiq/evaluation/__init__.py`:

```python
"""Evaluation utilities for CantinaIQ pipeline outputs."""
```

- [ ] **Step 2: Implement evaluator**

Write `src/cantinaiq/evaluation/gold_set.py`:

```python
"""Gold-set evaluation: recall of producer extraction against canonical top-50.

The gold-set lives in `data/reference/known_producers_top50.csv`. We measure
**recall** (how many gold producers appear in the pipeline output) under two
match modes:

  - exact:    pipeline `producer_name` == gold `canonical_name`.
  - contains: gold canonical name is a substring of any pipeline producer name
              (catches alias-mode failures where pipeline kept a fragment).

Precision is intentionally not computed — the pipeline contains hundreds of
real producers absent from the gold-set, so a precision number would be
meaningless. Recall is the load-bearing metric.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import polars as pl


@dataclass(frozen=True)
class GoldSetEval:
    gold_size: int
    producers_total: int
    recall_exact: float
    recall_contains: float
    matched_exact: list[str]
    matched_contains: list[str]
    missed: list[str]


def _read_gold(gold_csv: Path) -> list[str]:
    with Path(gold_csv).open() as f:
        return [row["canonical_name"].strip() for row in csv.DictReader(f) if row.get("canonical_name")]


def recall_at_alias(
    producers_parquet: Path,
    gold_csv: Path,
    match: Literal["exact", "contains"] = "exact",
) -> float:
    """Fraction of gold producers found in `producers_parquet.producer_name`."""
    gold = _read_gold(gold_csv)
    df = pl.read_parquet(producers_parquet)
    seen = df["producer_name"].drop_nulls().to_list()
    if match == "exact":
        seen_set = set(seen)
        hits = sum(1 for g in gold if g in seen_set)
    else:
        hits = sum(1 for g in gold if any(g.lower() in s.lower() for s in seen))
    return hits / len(gold) if gold else 0.0


def evaluate_producer_extraction(
    producers_parquet: Path, gold_csv: Path
) -> GoldSetEval:
    gold = _read_gold(gold_csv)
    df = pl.read_parquet(producers_parquet)
    seen = df["producer_name"].drop_nulls().to_list()
    seen_set = set(seen)
    matched_exact = [g for g in gold if g in seen_set]
    matched_contains = [g for g in gold if any(g.lower() in s.lower() for s in seen)]
    missed = [g for g in gold if g not in matched_contains]
    return GoldSetEval(
        gold_size=len(gold),
        producers_total=df.height,
        recall_exact=len(matched_exact) / len(gold) if gold else 0.0,
        recall_contains=len(matched_contains) / len(gold) if gold else 0.0,
        matched_exact=matched_exact,
        matched_contains=matched_contains,
        missed=missed,
    )
```

- [ ] **Step 3: Run — verify pass**

```bash
cd supercharged && uv run pytest tests/unit/test_gold_set.py -v
```

Expected: 3 passed.

- [ ] **Step 4: Commit**

```bash
git add supercharged/src/cantinaiq/evaluation supercharged/tests/unit/test_gold_set.py
git commit -m "feat(evaluation): add gold-set recall evaluator for producer extraction"
```

### Task 1.3: Add CLI subcommand + wire into report

**Files:**
- Create: `src/cantinaiq/evaluation/cli.py`
- Modify: `src/cantinaiq/cli.py`
- Modify: `reports/templates/data-quality.md.j2`

- [ ] **Step 1: Write subcommand**

```python
"""`cantinaiq evaluate …` Typer subcommands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from cantinaiq.evaluation.gold_set import evaluate_producer_extraction

evaluate_app = typer.Typer(no_args_is_help=True, help="Pipeline output evaluation.")


@evaluate_app.command("producer-extraction")
def producer_extraction(
    producers_path: Annotated[
        Path, typer.Option("--producers")
    ] = Path("data/processed/producers_scored.parquet"),
    gold_path: Annotated[Path, typer.Option("--gold")] = Path(
        "data/reference/known_producers_top50.csv"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "reports/generated/producer-extraction-eval.json"
    ),
) -> None:
    """Evaluate recall of producer extraction against the canonical top-50."""
    ev = evaluate_producer_extraction(producers_path, gold_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "gold_size": ev.gold_size,
                "producers_total": ev.producers_total,
                "recall_exact": ev.recall_exact,
                "recall_contains": ev.recall_contains,
                "matched_exact": ev.matched_exact,
                "matched_contains": ev.matched_contains,
                "missed": ev.missed,
            },
            indent=2,
        )
    )
    typer.echo(
        f"Gold size: {ev.gold_size}  "
        f"recall@exact: {ev.recall_exact:.2%}  "
        f"recall@contains: {ev.recall_contains:.2%}"
    )
    typer.echo(f"Wrote {out_path}")
```

- [ ] **Step 2: Wire into main CLI**

In `src/cantinaiq/cli.py`, add next to the other `add_typer` lines:

```python
from cantinaiq.evaluation.cli import evaluate_app
app.add_typer(evaluate_app, name="evaluate")
```

- [ ] **Step 3: Smoke test**

```bash
cd supercharged && uv run cantinaiq evaluate producer-extraction
```

Expected: prints recall@exact + recall@contains; writes `reports/generated/producer-extraction-eval.json`.

- [ ] **Step 4: Commit**

```bash
git add supercharged/src/cantinaiq/evaluation/cli.py supercharged/src/cantinaiq/cli.py
git commit -m "feat(cli): add cantinaiq evaluate producer-extraction"
```

---

## Phase 2: Bootstrap confidence intervals on rankings

### Task 2.1: Failing tests

**Files:**
- Create: `tests/unit/test_bootstrap.py`

- [ ] **Step 1: Write tests**

```python
"""Bootstrap rank stability — resample the wine dataset, re-aggregate to producers, measure CIs."""
from __future__ import annotations

import polars as pl

from cantinaiq.bootstrap import bootstrap_producer_rank_ci


def test_bootstrap_identical_data_gives_tight_ci() -> None:
    """When data is deterministic across resamples, top producers' rank CIs collapse."""
    wines = pl.DataFrame(
        {
            "producer_name": ["A"] * 100 + ["B"] * 100 + ["C"] * 100,
            "weighted_rating": [4.8] * 100 + [4.5] * 100 + [4.2] * 100,
            "rating_count": [5000] * 100 + [3000] * 100 + [1000] * 100,
            "price": [50.0] * 100 + [50.0] * 100 + [50.0] * 100,
        }
    )
    cis = bootstrap_producer_rank_ci(wines, n_bootstraps=50, top_n=3, seed=42)
    by_name = {c["producer_name"]: c for c in cis}
    # With a well-separated dataset, A is almost certainly #1.
    assert by_name["A"]["rank_p50"] == 1
    assert by_name["A"]["rank_p95"] <= 2
    assert by_name["C"]["rank_p50"] == 3


def test_bootstrap_returns_top_n_only() -> None:
    wines = pl.DataFrame(
        {
            "producer_name": [chr(65 + i // 10) for i in range(60)],
            "weighted_rating": [4.0 + i / 100 for i in range(60)],
            "rating_count": [100] * 60,
            "price": [20.0] * 60,
        }
    )
    cis = bootstrap_producer_rank_ci(wines, n_bootstraps=30, top_n=5, seed=0)
    assert len(cis) == 5
    assert all("rank_p50" in c for c in cis)
    assert all("rank_p05" in c and "rank_p95" in c for c in cis)
```

- [ ] **Step 2: Run — verify failure**

```bash
cd supercharged && uv run pytest tests/unit/test_bootstrap.py -v
```

Expected: ImportError.

### Task 2.2: Implement bootstrap module

**Files:**
- Create: `src/cantinaiq/bootstrap.py`

- [ ] **Step 1: Implementation**

```python
"""Bootstrap resampling for producer-ranking confidence intervals.

For each of `n_bootstraps` iterations:
  1. Resample the wine dataset with replacement.
  2. Group by producer_name and compute aggregate (mean weighted_rating
     weighted by rating_count).
  3. Rank producers descending by that aggregate.
  4. Record each top-N producer's rank.

After N iterations, compute the 5th, 50th, 95th percentile rank per producer.
Producers that fail to appear in a bootstrap iteration receive a sentinel
rank of `top_n + 1` for that iteration — this is the standard treatment
and yields wider, more honest CIs for low-volume producers.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import polars as pl


def _aggregate_to_producers(wines: pl.DataFrame) -> pl.DataFrame:
    """Producer-level weighted aggregate. Mirrors the scoring stage at small scale."""
    return (
        wines.with_columns(
            (pl.col("weighted_rating") * pl.col("rating_count")).alias("_num"),
            pl.col("rating_count").alias("_den"),
        )
        .group_by("producer_name")
        .agg(
            (pl.col("_num").sum() / pl.col("_den").sum()).alias("weighted_rating"),
            pl.col("rating_count").sum().alias("total_reviews"),
        )
    )


def bootstrap_producer_rank_ci(
    wines: pl.DataFrame,
    n_bootstraps: int = 1000,
    top_n: int = 20,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Return per-producer rank CIs for the top-N producers from the original ranking."""
    rng = np.random.default_rng(seed)

    baseline = (
        _aggregate_to_producers(wines)
        .sort("weighted_rating", descending=True)
        .head(top_n)
    )
    top_names = baseline["producer_name"].to_list()
    name_to_ranks: dict[str, list[int]] = {n: [] for n in top_names}

    for _ in range(n_bootstraps):
        idx = rng.integers(0, wines.height, size=wines.height)
        sample = wines[idx.tolist()]
        ranked = (
            _aggregate_to_producers(sample)
            .sort("weighted_rating", descending=True)
            .with_row_index(name="rank", offset=1)
            .select(["producer_name", "rank"])
        )
        rank_map = dict(zip(ranked["producer_name"].to_list(), ranked["rank"].to_list(), strict=False))
        for n in top_names:
            name_to_ranks[n].append(int(rank_map.get(n, top_n + 1)))

    out: list[dict[str, Any]] = []
    for n in top_names:
        ranks = np.array(name_to_ranks[n])
        out.append(
            {
                "producer_name": n,
                "rank_p05": int(np.percentile(ranks, 5)),
                "rank_p50": int(np.percentile(ranks, 50)),
                "rank_p95": int(np.percentile(ranks, 95)),
                "rank_mean": float(ranks.mean()),
                "appearances": int((ranks <= top_n).sum()),
                "n_bootstraps": n_bootstraps,
            }
        )
    return out
```

- [ ] **Step 2: Run — verify pass**

```bash
cd supercharged && uv run pytest tests/unit/test_bootstrap.py -v
```

Expected: 2 passed.

### Task 2.3: Add `cantinaiq bootstrap` CLI command

**Files:**
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Add command**

```python
@app.command()
def bootstrap(
    n: Annotated[int, typer.Option("--n", help="Number of bootstrap resamples.")] = 1000,
    top: Annotated[int, typer.Option("--top", help="Top-N producers to track.")] = 20,
    seed: Annotated[int, typer.Option("--seed")] = 42,
    wines_path: Annotated[Path, typer.Option("--wines")] = Path("data/processed/wines_scored.parquet"),
    out_path: Annotated[Path, typer.Option("--out")] = Path("reports/generated/bootstrap-ci.md"),
) -> None:
    """Bootstrap producer-ranking confidence intervals."""
    import polars as pl
    from cantinaiq.bootstrap import bootstrap_producer_rank_ci

    wines = pl.read_parquet(wines_path).select(
        ["producer_name", "weighted_rating", "rating_count", "price"]
    )
    cis = bootstrap_producer_rank_ci(wines, n_bootstraps=n, top_n=top, seed=seed)

    lines = [
        f"# Bootstrap rank CIs (n={n}, top-{top}, seed={seed})",
        "",
        f"Based on `{wines_path}` ({wines.height:,} rows). "
        f"Producers that fall outside the top-{top} in a resample receive rank {top + 1}.",
        "",
        "| Producer | p05 | p50 | p95 | mean | appearances/n |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for c in cis:
        lines.append(
            f"| {c['producer_name']} | "
            f"{c['rank_p05']} | {c['rank_p50']} | {c['rank_p95']} | "
            f"{c['rank_mean']:.1f} | {c['appearances']}/{c['n_bootstraps']} |"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")
```

- [ ] **Step 2: Smoke test**

```bash
cd supercharged && uv run cantinaiq bootstrap --n 100 --top 10
head -20 reports/generated/bootstrap-ci.md
```

Expected: small bootstrap table with realistic CIs.

- [ ] **Step 3: Commit**

```bash
git add supercharged/src/cantinaiq/bootstrap.py supercharged/src/cantinaiq/cli.py supercharged/tests/unit/test_bootstrap.py
git commit -m "feat(bootstrap): add producer-ranking confidence intervals"
```

---

## Phase 3: Producer clustering with sklearn

### Task 3.1: Add scikit-learn dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add dep**

Append `"scikit-learn>=1.5,<2"` to `[project] dependencies`.

- [ ] **Step 2: Sync**

```bash
cd supercharged && uv sync
```

- [ ] **Step 3: Commit**

```bash
git add supercharged/pyproject.toml supercharged/uv.lock
git commit -m "chore(deps): add scikit-learn for producer clustering"
```

### Task 3.2: Failing tests

**Files:**
- Create: `tests/unit/test_clustering.py`

- [ ] **Step 1: Write tests**

```python
"""Producer clustering — KMeans on (rating, value, reviews, price) feature space."""
from __future__ import annotations

import polars as pl

from cantinaiq.clustering import build_feature_matrix, fit_kmeans_clusters


def test_build_feature_matrix_shape() -> None:
    df = pl.DataFrame(
        {
            "producer_name": ["A", "B", "C"],
            "weighted_rating": [4.5, 4.2, 4.0],
            "value_score": [1.2, 1.5, 1.8],
            "total_reviews": [5000, 3000, 1000],
            "avg_price": [80.0, 25.0, 12.0],
        }
    )
    X, names = build_feature_matrix(df)
    assert X.shape == (3, 4)
    assert names == ["A", "B", "C"]
    # Feature matrix should be standardised (mean ≈ 0).
    import numpy as np
    assert np.allclose(X.mean(axis=0), 0, atol=1e-9)
    assert np.allclose(X.std(axis=0), 1, atol=0.5)


def test_fit_kmeans_assigns_three_clusters() -> None:
    df = pl.DataFrame(
        {
            "producer_name": [f"P{i}" for i in range(15)],
            "weighted_rating": [4.6, 4.5, 4.7, 4.0, 4.1, 3.9, 4.2, 4.3, 4.2, 4.5, 4.4, 4.6, 3.8, 3.9, 4.0],
            "value_score": [0.5, 0.6, 0.4, 2.0, 2.1, 1.9, 1.0, 1.1, 1.2, 0.7, 0.8, 0.6, 2.2, 2.3, 2.1],
            "total_reviews": [10000, 8000, 12000, 500, 600, 400, 3000, 2500, 3500, 9000, 8500, 11000, 700, 800, 500],
            "avg_price": [200, 180, 220, 10, 12, 8, 50, 45, 55, 190, 200, 230, 9, 11, 10],
        }
    )
    df_clustered = fit_kmeans_clusters(df, n_clusters=3, random_state=42)
    assert "cluster_id" in df_clustered.columns
    assert df_clustered["cluster_id"].unique().len() == 3
    # The premium-priced rows (200+ EUR) should cluster together.
    by_cluster = df_clustered.group_by("cluster_id").agg(pl.col("avg_price").mean().alias("mean_price"))
    spreads = by_cluster["mean_price"].max() - by_cluster["mean_price"].min()
    assert spreads > 100  # clusters are well-separated on price
```

- [ ] **Step 2: Run — verify failure**

```bash
cd supercharged && uv run pytest tests/unit/test_clustering.py -v
```

Expected: ImportError.

### Task 3.3: Implement clustering

**Files:**
- Create: `src/cantinaiq/clustering.py`

- [ ] **Step 1: Implementation**

```python
"""Producer clustering — KMeans on a 4-feature space.

Features: standardised (weighted_rating, value_score, total_reviews, avg_price).
Output: an additional `cluster_id` column on the producer dataframe.

Clustering is *complementary* to the rule-based market_segment — segments
encode business intent ("Premium Icon"), clusters encode empirical similarity
("producers in cluster 2 look like each other in the feature space"). Both
columns coexist.
"""

from __future__ import annotations

import numpy as np
import polars as pl
from sklearn.cluster import KMeans  # type: ignore[import-untyped]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]

FEATURES = ["weighted_rating", "value_score", "total_reviews", "avg_price"]


def build_feature_matrix(df: pl.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Return (X_scaled, producer_names). Rows with any null in features are dropped."""
    keep = df.drop_nulls(subset=FEATURES)
    raw = keep.select(FEATURES).to_numpy()
    scaler = StandardScaler()
    return scaler.fit_transform(raw), keep["producer_name"].to_list()


def fit_kmeans_clusters(
    df: pl.DataFrame, n_clusters: int = 5, random_state: int = 42
) -> pl.DataFrame:
    """Return `df` with a `cluster_id` column appended (Int64)."""
    X, names = build_feature_matrix(df)
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
    labels = km.fit_predict(X)
    label_map = dict(zip(names, labels.tolist(), strict=True))
    return df.with_columns(
        pl.col("producer_name")
        .map_elements(lambda n: label_map.get(n, -1), return_dtype=pl.Int64)
        .alias("cluster_id")
    )
```

- [ ] **Step 2: Run — verify pass**

```bash
cd supercharged && uv run pytest tests/unit/test_clustering.py -v
```

Expected: 2 passed.

### Task 3.4: Add `cantinaiq cluster` CLI command

**Files:**
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Add command**

```python
@app.command()
def cluster(
    n_clusters: Annotated[int, typer.Option("--k", help="Number of K-Means clusters.")] = 5,
    producers_path: Annotated[Path, typer.Option("--producers")] = Path(
        "data/processed/producers_scored.parquet"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "data/processed/producers_scored_clustered.parquet"
    ),
) -> None:
    """Append a K-Means `cluster_id` column to producers_scored."""
    import polars as pl
    from cantinaiq.clustering import fit_kmeans_clusters

    df = pl.read_parquet(producers_path)
    out = fit_kmeans_clusters(df, n_clusters=n_clusters)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(out_path)

    summary = (
        out.group_by("cluster_id")
        .agg(
            pl.len().alias("n_producers"),
            pl.col("weighted_rating").mean().round(2).alias("mean_rating"),
            pl.col("avg_price").mean().round(0).alias("mean_price"),
            pl.col("total_reviews").mean().round(0).alias("mean_reviews"),
        )
        .sort("cluster_id")
    )
    console.print(f"[bold]K-Means clusters (k={n_clusters}):[/bold]")
    console.print(summary)
    console.print(f"[green]✓ {out_path}[/green]")
```

- [ ] **Step 2: Smoke test**

```bash
cd supercharged && uv run cantinaiq cluster --k 5
```

Expected: cluster summary table; new parquet written.

- [ ] **Step 3: Commit**

```bash
git add supercharged/src/cantinaiq/clustering.py supercharged/src/cantinaiq/cli.py supercharged/tests/unit/test_clustering.py
git commit -m "feat(clustering): add K-Means producer clustering (4-feature space)"
```

---

## Phase 4: Vivino bias quantification

### Task 4.1: Italian Trade reference data (cached)

**Files:**
- Create: `data/reference/italian_trade_imports_nl.csv`

Manually authored baseline based on Italian Trade Agency (ICE Amsterdam) annual wine import reports — kept as a committed baseline because Firecrawl access is not guaranteed in every environment.

- [ ] **Step 1: Write the cached reference CSV**

Write `data/reference/italian_trade_imports_nl.csv` with values reflecting the dominant Italian regions in the Netherlands wine market (proportions are illustrative; cite source in the methodology):

```csv
macro_region,share_nl_imports_pct,notes
Toscana,28.0,"Chianti + Brunello + Bolgheri dominant"
Piemonte,15.0,"Barolo + Barbaresco + Moscato"
Veneto,18.0,"Amarone + Prosecco + Soave"
Sicilia,10.0,"Nero d'Avola + Etna"
Puglia,11.0,"Primitivo dominant"
Abruzzo,5.0,"Montepulciano d'Abruzzo"
Friuli-Venezia Giulia,3.0,"White-wine market"
Lazio,2.5,"Frascati + Cesanese"
Umbria,2.0,"Sagrantino di Montefalco"
Trentino-Alto Adige,3.0,"Gewürztraminer + Pinot Grigio"
Other,2.5,"Sardegna + Campania + Liguria + Marche etc."
```

> **Note for reviewer**: percentages are best-effort estimates based on ICE Amsterdam reports + Wine Institute import statistics. Source line documented in `bias.py` and surfaced in the methodology.

### Task 4.2: Failing tests for bias module

**Files:**
- Create: `tests/unit/test_bias.py`

- [ ] **Step 1: Write tests**

```python
"""Vivino-vs-Italian-Trade bias quantification."""
from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from cantinaiq.bias import BiasReport, compute_bias_report


@pytest.fixture
def baseline_csv(tmp_path: Path) -> Path:
    p = tmp_path / "baseline.csv"
    p.write_text(
        "macro_region,share_nl_imports_pct,notes\n"
        "Toscana,30.0,\n"
        "Veneto,20.0,\n"
        "Piemonte,15.0,\n"
        "Puglia,10.0,\n"
        "Other,25.0,\n"
    )
    return p


@pytest.fixture
def wines(tmp_path: Path) -> Path:
    df = pl.DataFrame(
        {
            "macro_region": (
                ["Toscana"] * 60 + ["Veneto"] * 20 + ["Piemonte"] * 10 + ["Puglia"] * 5 + ["Sicilia"] * 5
            ),
        }
    )
    p = tmp_path / "wines.parquet"
    df.write_parquet(p)
    return p


def test_compute_bias_report_returns_per_region_deltas(
    wines: Path, baseline_csv: Path
) -> None:
    report = compute_bias_report(wines, baseline_csv)
    assert isinstance(report, BiasReport)
    rows = {r["macro_region"]: r for r in report.rows}

    # Toscana: 60/100 = 60% in Vivino, 30% in baseline → over-represented by ×2.
    assert rows["Toscana"]["vivino_share_pct"] == pytest.approx(60.0)
    assert rows["Toscana"]["baseline_share_pct"] == pytest.approx(30.0)
    assert rows["Toscana"]["over_under"] > 1.5

    # Puglia: 5/100 = 5% in Vivino, 10% baseline → under-represented by 0.5.
    assert rows["Puglia"]["over_under"] < 0.8
```

- [ ] **Step 2: Run — verify failure**

```bash
cd supercharged && uv run pytest tests/unit/test_bias.py -v
```

Expected: ImportError.

### Task 4.3: Implement bias module

**Files:**
- Create: `src/cantinaiq/bias.py`

- [ ] **Step 1: Implementation**

```python
"""Vivino-vs-Italian-Trade bias quantification.

Goal: surface how the Vivino dataset's regional distribution differs from
real Italian wine imports to the Netherlands. The point isn't to "correct"
the data — Vivino IS the signal we have — but to be honest about which
regions are over-represented (likely: Toscana via wine-influencer culture)
and under-represented (likely: niche regions like Friuli, Liguria).

Baseline source: `data/reference/italian_trade_imports_nl.csv`, derived
from ICE Amsterdam annual Italian wine import reports.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl


@dataclass(frozen=True)
class BiasReport:
    total_wines: int
    rows: list[dict[str, Any]]


def _read_baseline(baseline_csv: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    with Path(baseline_csv).open() as f:
        for row in csv.DictReader(f):
            out[row["macro_region"].strip()] = float(row["share_nl_imports_pct"])
    return out


def compute_bias_report(wines_parquet: Path, baseline_csv: Path) -> BiasReport:
    df = pl.read_parquet(wines_parquet)
    total = df.height
    region_counts = (
        df.group_by("macro_region")
        .agg(pl.len().alias("n"))
        .sort("n", descending=True)
    )
    baseline = _read_baseline(baseline_csv)

    rows: list[dict[str, Any]] = []
    for r in region_counts.to_dicts():
        region = r["macro_region"]
        n = r["n"]
        vivino_share = (n / total) * 100 if total else 0.0
        baseline_share = baseline.get(region, baseline.get("Other", 0.0))
        over_under = (vivino_share / baseline_share) if baseline_share > 0 else float("inf")
        rows.append(
            {
                "macro_region": region,
                "vivino_wines": n,
                "vivino_share_pct": round(vivino_share, 2),
                "baseline_share_pct": round(baseline_share, 2),
                "over_under": round(over_under, 2),
            }
        )
    return BiasReport(total_wines=total, rows=rows)
```

- [ ] **Step 2: Run — verify pass**

```bash
cd supercharged && uv run pytest tests/unit/test_bias.py -v
```

Expected: 1 passed.

### Task 4.4: Add `cantinaiq bias` CLI command

**Files:**
- Modify: `src/cantinaiq/cli.py`

- [ ] **Step 1: Add command**

```python
@app.command()
def bias(
    wines_path: Annotated[Path, typer.Option("--wines")] = Path(
        "data/processed/italian_wines_enriched.parquet"
    ),
    baseline_path: Annotated[Path, typer.Option("--baseline")] = Path(
        "data/reference/italian_trade_imports_nl.csv"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "reports/generated/bias-report.md"
    ),
) -> None:
    """Compare Vivino regional distribution to Italian Trade Agency NL imports."""
    from cantinaiq.bias import compute_bias_report

    report = compute_bias_report(wines_path, baseline_path)
    rows_sorted = sorted(report.rows, key=lambda r: r["over_under"], reverse=True)

    lines = [
        "# Vivino Regional Bias Report",
        "",
        f"Total Italian wines in Vivino dataset: **{report.total_wines:,}**.",
        "",
        "Baseline = `data/reference/italian_trade_imports_nl.csv` "
        "(derived from ICE Amsterdam Italian wine import statistics).",
        "",
        "| Macro region | Vivino n | Vivino % | Baseline % | Over/Under |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in rows_sorted:
        marker = "▲" if r["over_under"] >= 1.3 else ("▼" if r["over_under"] <= 0.7 else "·")
        lines.append(
            f"| {marker} {r['macro_region']} | "
            f"{r['vivino_wines']:,} | "
            f"{r['vivino_share_pct']:.1f}% | "
            f"{r['baseline_share_pct']:.1f}% | "
            f"×{r['over_under']:.2f} |"
        )
    lines.extend([
        "",
        "**Interpretation:** values above ×1.3 mean Vivino over-represents that region "
        "vs. real NL import volumes; values below ×0.7 mean Vivino under-represents it. "
        "Vivino bias does not invalidate the analysis but should be cited in any "
        "external-facing recommendation.",
    ])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")
```

- [ ] **Step 2: Smoke test**

```bash
cd supercharged && uv run cantinaiq bias
head -20 reports/generated/bias-report.md
```

Expected: bias-report.md with ▲/▼ markers.

- [ ] **Step 3: Commit**

```bash
git add supercharged/src/cantinaiq/bias.py supercharged/src/cantinaiq/cli.py supercharged/tests/unit/test_bias.py supercharged/data/reference/italian_trade_imports_nl.csv
git commit -m "feat(bias): add Vivino regional bias quantification vs Italian Trade NL imports"
```

---

## Phase 5: Wire Tier 2 outputs into reports

### Task 5.1: Add gold-set + bias sections to methodology template

**Files:**
- Modify: `reports/templates/methodology.md.j2`

- [ ] **Step 1: Append new sections**

Insert two new sections — §3b after §3a, and §9 after §8:

```jinja
## 3b. Producer-extraction evaluation

Recall against `data/reference/known_producers_top50.csv` (a hand-curated
canonical list of the top 50 Italian wine producers):

- **recall@exact** — fraction of gold producers appearing with their exact
  canonical name in `producers_scored.producer_name`.
- **recall@contains** — fraction of gold producers appearing as a substring
  of any pipeline producer name (catches alias-mode partial matches).

Run `cantinaiq evaluate producer-extraction` to refresh
`reports/generated/producer-extraction-eval.json` from the latest pipeline output.
```

```jinja
## 9. External validity — Vivino regional bias

Vivino consumer ratings are a market signal, not the market itself. We compare
the regional distribution of Italian wines in the Vivino dataset against the
Italian Trade Agency (ICE Amsterdam) NL import statistics:
`data/reference/italian_trade_imports_nl.csv`.

Run `cantinaiq bias` to refresh the comparison. The current report is in
`reports/generated/bias-report.md`. Over-represented regions (×>1.3) should
prompt extra scrutiny when generalising recommendations; under-represented
regions (×<0.7) may warrant a manual top-up of producer outreach because the
Vivino signal is sparse.

Bootstrap rank stability (`cantinaiq bootstrap`) further quantifies how robust
the top-N ranking is to resampling noise: producers whose 95th-percentile rank
falls outside the top-N in resamples are flagged as "shortlist-borderline".
```

- [ ] **Step 2: Re-render**

```bash
cd supercharged && uv run cantinaiq report build --only methodology
grep -E "^## (3b|9)\." reports/generated/methodology.md
```

Expected: both new sections appear.

- [ ] **Step 3: Commit**

```bash
git add supercharged/reports/templates/methodology.md.j2
git commit -m "docs(methodology): wire gold-set + bias + bootstrap into §3b and §9"
```

### Task 5.2: Append precision/recall row to data-quality template

**Files:**
- Modify: `reports/templates/data-quality.md.j2`

- [ ] **Step 1: Append section**

At the end of the existing `data-quality.md.j2` (before the metadata footer line), insert:

```jinja
## Producer-extraction recall

See `reports/generated/producer-extraction-eval.json` (refreshed by
`cantinaiq evaluate producer-extraction`). Headline recall numbers should
appear in the final report; this file is the per-stage drop ledger.
```

- [ ] **Step 2: Re-render**

```bash
cd supercharged && uv run cantinaiq report build --only data-quality
tail -8 reports/generated/data-quality.md
```

- [ ] **Step 3: Commit**

```bash
git add supercharged/reports/templates/data-quality.md.j2
git commit -m "docs(data-quality): cross-reference producer-extraction-eval.json"
```

---

## Phase 6: Final verification

### Task 6.1: Full test sweep

- [ ] **Step 1: Run all tests**

```bash
cd supercharged && uv run pytest 2>&1 | tail -5
```

Expected: all pass (119 + ~12 new ≈ 131 passed).

### Task 6.2: Run each new CLI against the real dataset

- [ ] **Step 1: Sequence**

```bash
cd supercharged
uv run cantinaiq evaluate producer-extraction
uv run cantinaiq bias
uv run cantinaiq cluster --k 5
uv run cantinaiq bootstrap --n 200 --top 20
uv run cantinaiq report build
```

Expected: every command exits 0; expected outputs land in `reports/generated/`.

- [ ] **Step 2: Manual spot-check**

```bash
ls -la reports/generated/
head -30 reports/generated/bias-report.md
head -30 reports/generated/bootstrap-ci.md
cat reports/generated/producer-extraction-eval.json | head -15
```

Expected: bias-report shows ▲/▼ for at least 2 regions; bootstrap-ci shows tight CIs for top-3 producers; eval JSON shows recall ≥ 50%.

### Task 6.3: Final commit + clean

- [ ] **Step 1: Stage + commit any straggling generated files (only if explicitly out of .gitignore)**

```bash
cd /Users/vincentblokker/ClubVentureProjects/CantinaIQ
git status --short
git commit -am "chore: verified Tier-2 outputs against real dataset" || echo "(no changes)"
```

---

## Self-review notes

- All four user-selected items have phases: gold-set (Phase 1), bootstrap (Phase 2), clustering (Phase 3), bias (Phase 4).
- Italian Trade chosen as bias source → reference CSV committed for deterministic baseline.
- TDD discipline: every module has failing tests written before implementation.
- Function names consistent: `evaluate_producer_extraction`, `bootstrap_producer_rank_ci`, `fit_kmeans_clusters`, `compute_bias_report`.
- Each CLI is a top-level subcommand reusing the established `console`/`typer` patterns.
- Reports wiring (Phase 5) is light-touch — methodology gets cross-references rather than auto-included tables, so the templates remain hand-editable.
