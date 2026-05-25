# /supercharged — Slurpini Partner Intelligence Engine

A reproducible data product that turns a raw Vivino export into a ranked,
defensible shortlist of Italian wine producers for Slurpini.

This is the *above-and-beyond* track of the [CantinaIQ submission](../README.md).
The *minimum-viable* track lives in [`/bare`](../bare/). The [root
README](../README.md) and [FOR_REVIEWERS.md](../FOR_REVIEWERS.md) explain why
both exist.

The full product spec is [`PRD.md`](PRD.md) (1 000+ lines). This file is the
developer-facing entrypoint.

---

## Quickstart

```bash
# from the repo root
make setup
make demo
```

Or directly:

```bash
cd supercharged
uv sync
uv run cantinaiq run all          # full pipeline (~5 s on 410 k rows)
uv run cantinaiq report build     # render markdown + HTML reports
uv run cantinaiq status           # latest run summary
uv run pytest                     # 137 tests
```

For the LLM-disambiguation pass on ambiguous producers, set `OPENROUTER_API_KEY`
in your environment. Without it the pipeline falls back to pass-1 (alias
whitelist + first-token heuristic).

For sustainability + live-Vivino enrichment, set `FIRECRAWL_API_KEY`.

---

## What this answers

> *Which Italian wine producers should Slurpini prioritise for collaboration,
> based on Dutch consumer preference, market confidence, price positioning,
> and value for money?*

The output is not a list of highly rated wines. It is a repeatable framework
that produces a ranked shortlist where every claim traces back to a
config-hashed run log.

---

## Pipeline

```text
Vivino-export.xlsx (409 777 rows × 16 sheets)
    │
    ▼ ingestion   ──► 01_raw.parquet
    ▼ cleaning    ──► 02_cleaned.parquet  (2 986 rows after Italian filter + dedupe)
    ▼ validation  ──► 03_validated.parquet  (Pandera contracts)
    ▼ enrichment  ──► italian_wines_enriched.parquet  (producer + macro_region + segments)
    ▼ scoring     ──► {wines, producers, regions}_scored.parquet  (5-factor composite)
    ▼ export      ──► data/exports/*.json  (consumed by /dashboard)
```

Every stage is a pure function of `(input parquet, config) → (output parquet,
run-log JSON)`. No hidden state.

---

## CLI

```text
cantinaiq run all                              # full pipeline
cantinaiq run <stage>                          # run a single stage
cantinaiq run all --from enrichment            # resume from a stage
cantinaiq report build                         # render all reports
cantinaiq report build --only methodology      # render one
cantinaiq audit <config-hash>                  # show snapshot + matching runs
cantinaiq status                               # latest run summary

# Tier 1 — analysis on top of a run
cantinaiq compare <hash-a> <hash-b>            # rank shifts + segment movements
cantinaiq sensitivity --param X --range a,b,s  # Kendall-τ over a parameter

# Tier 2 — methodological rigour
cantinaiq evaluate producer-extraction         # recall vs known top-50
cantinaiq bias                                 # Vivino vs ICE NL import baseline
cantinaiq cluster --k 5                        # KMeans over the producer feature space
cantinaiq bootstrap --n 1000 --top 20          # producer-ranking confidence intervals

# Tier 3 — differentiator extensions
cantinaiq anomaly --contamination 0.03         # Isolation Forest on review patterns
cantinaiq sustainability check --top 50        # FederBio + Demeter cert lookup
cantinaiq enrich-live live --with-network      # live Vivino enrichment (top-50)
cantinaiq crawler extend                       # crawler extension (deliverable (i) here too)
```

---

## Scoring

The **Slurpini Partner Intelligence Score** is a weighted linear combination
of five normalised [0, 1] components:

| Component | Weight | Captures |
|---|---:|---|
| Weighted rating | 35 % | Bayesian-shrunk consumer quality signal |
| Market confidence | 20 % | Review-volume reliability |
| Value for money | 20 % | Quality-per-euro |
| Premium fit | 15 % | Alignment with Slurpini's premium positioning |
| Portfolio opportunity | 10 % | Strategic gap fill |

Bayesian weighted rating:

```text
WR = (n / (n + m)) · r + (m / (n + m)) · r̄
```

`n` = reviews per row, `m` = shrinkage threshold (configurable; default
auto-median), `r̄` = global Italian-dataset mean rating.

Producers are classified into market segments (Hidden Gem · Premium Icon ·
Commercial Value · Overpriced Risk · Low Confidence Niche) and given a
recommendation (Premium Brand Builder · Target · Value Opportunity · Monitor
· Avoid for Now) based on segment + composite score. Thresholds live in
`config/segments/default.yaml`.

---

## Tests

```bash
uv run pytest                # 137 tests
uv run pytest -m slow        # excluded by default; long bootstrap/sensitivity tests
uv run pytest -m llm         # LLM cache-hit tests (require pre-built cache)
```

Coverage: unit · integration · property-based (Hypothesis on scoring math) ·
Pandera schema · Jinja template smoke.

---

## Reports

Generated artefacts live in `reports/generated/`:

| File | Content |
|---|---|
| [executive-summary.md](reports/generated/executive-summary.md) | Board-level Slurpini recommendation. |
| [methodology.md](reports/generated/methodology.md) | 13-section explanation: Bayesian shrinkage, gold-set recall, anomaly detection, clustering, Vivino bias, reproducibility. |
| [data-quality.md](reports/generated/data-quality.md) | Drop-cascade ledger per stage. |
| [findings-one-pager.html](reports/generated/findings-one-pager.html) | Print-ready A4 executive one-pager. |
| [bias-report.md](reports/generated/bias-report.md) | Vivino vs ICE Amsterdam regional import shares. |
| [bootstrap-ci.md](reports/generated/bootstrap-ci.md) | Producer-ranking 5/50/95-th percentile CIs. |
| [sensitivity.md](reports/generated/sensitivity.md) | Top-20 stability vs scoring parameter sweep. |
| [anomalies.md](reports/generated/anomalies.md) | Isolation Forest hits. |
| [producer-extraction-eval.json](reports/generated/producer-extraction-eval.json) | Recall vs known top-50: 88 % exact / 96 % contains. |
| [sustainability.md](reports/generated/sustainability.md) | FederBio + Demeter cert lookup results. |

Numbers in templated reports come from the run-log — they **cannot** drift
from the code.

---

## Reproducibility

Every output Parquet carries `run_config_hash`. Snapshots live in
`config/snapshots/`. To reproduce a run:

```bash
uv run cantinaiq run all --config-snapshot <hash>
uv run cantinaiq audit <hash>
```

---

## Tech stack

Polars · DuckDB · Pandera · Hydra · Pydantic · Typer · Jinja2 · scikit-learn ·
scipy · OpenAI SDK (OpenRouter) · Firecrawl · diskcache · pytest + Hypothesis ·
uv · ruff · mypy.

---

## Plans

Implementation history lives in `docs/superpowers/plans/`. Each plan was
written before its code, reviewed, then executed task-by-task.

1. [2026-05-25 Tier 0 + Tier 1 improvements](docs/superpowers/plans/2026-05-25-cantinaiq-tier0-tier1-improvements.md) — OpenRouter, generative reasons, executive summary, Firecrawl crawler, methodology delta, compare CLI, sensitivity CLI.
2. [2026-05-25 Tier 2 rigour](docs/superpowers/plans/2026-05-25-cantinaiq-tier2-rigor.md) — gold-set evaluation, bootstrap CIs, KMeans clustering, Vivino bias quantification.
3. [2026-05-25 Tier 3 extensions](docs/superpowers/plans/2026-05-25-cantinaiq-tier3-extensions.md) — anomaly detection, sustainability lookup, live Vivino enrichment, dashboard.
4. [2026-05-15 original spec](docs/superpowers/specs/2026-05-15-cantinaiq-data-pipeline-design.md) — the master design doc.
