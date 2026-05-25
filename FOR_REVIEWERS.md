# For reviewers — how to read this submission

<img src="assets/detail.png" alt="" width="320" align="right" style="margin-left: 1em;" />

*Vincent Blokker · ADA Applied AI Bootcamp Final Assignment · the Slurpini wine case.*

This repo contains **two parallel deliverables** for the same business problem. The split is intentional: it lets you check two boxes — compliance with the brief, *and* a separate demonstration of what's possible beyond it.

---

## 5-minute read

```text
1.  bare/recommendation.md          ← half-A4 Slurpini recommendation
2.  bare/notebooks/slurpini-...     ← the notebook (outputs baked in)
3.  bare/crawler-extension.py       ← the crawler ask, deliverable (i)
```

Everything ADA's brief literally asks for sits in `/bare`. It runs in ~30 seconds and answers the three deliverables explicitly:

| Brief requirement | Lives in |
|---|---|
| (i) Crawler extension | [bare/crawler-extension.py](bare/crawler-extension.py) |
| (ii) EDA + analysis | [bare/notebooks/slurpini-analysis.ipynb](bare/notebooks/slurpini-analysis.ipynb) |
| (iii) Written recommendation | [bare/recommendation.md](bare/recommendation.md) |

If you only have five minutes, stop here. `/bare` is the answer to the assignment.

---

## 30-minute read — what `/supercharged` adds

`/supercharged` answers the same business question (*which Italian producers should Slurpini prioritise?*) as a reproducible data product instead of a one-off analysis. The artefact's quality is the argument — there's no editorialising inside the code.

**Run it yourself**: `make demo` from the repo root. ~30 seconds, no setup beyond `make setup` once. Outputs land in `supercharged/reports/generated/` and `dashboard/dist/`.

**What's in there:**

| What | Where | Why |
|---|---|---|
| Executive summary (board-level) | [supercharged/reports/generated/executive-summary.md](supercharged/reports/generated/executive-summary.md) | The written recommendation, but generated from the run-log so the numbers cannot drift from the code. |
| Methodology (13 sections) | [supercharged/reports/generated/methodology.md](supercharged/reports/generated/methodology.md) | Bayesian shrinkage formula, /bare-delta explanation, producer-extraction recall, anomaly detection, clustering, Vivino bias quantification, reproducibility. |
| Data quality | [supercharged/reports/generated/data-quality.md](supercharged/reports/generated/data-quality.md) | Drop-cascade ledger per pipeline stage. |
| Findings one-pager (HTML) | [supercharged/reports/generated/findings-one-pager.html](supercharged/reports/generated/findings-one-pager.html) | Single-print A4 for executives. |
| Bias quantification | [supercharged/reports/generated/bias-report.md](supercharged/reports/generated/bias-report.md) | Vivino vs. Italian Trade Agency NL imports. Reveals: Puglia ×0.61, Abruzzo ×0.52, Campania ×0.55 under-represented. |
| Bootstrap rank CIs | [supercharged/reports/generated/bootstrap-ci.md](supercharged/reports/generated/bootstrap-ci.md) | 200 resamples: Tenuta Masseto in top-10 in 195/200 (97.5 %). |
| Sensitivity sweep | [supercharged/reports/generated/sensitivity.md](supercharged/reports/generated/sensitivity.md) | Kendall-τ stability of top-20 vs. `bayesian_m` parameter. |
| Anomaly detection | [supercharged/reports/generated/anomalies.md](supercharged/reports/generated/anomalies.md) | Isolation Forest, 90/2986 flagged. |
| Gold-set evaluation | [supercharged/reports/generated/producer-extraction-eval.json](supercharged/reports/generated/producer-extraction-eval.json) | Recall against known top-50: **88 % exact, 96 % contains**. |
| Sustainability lookup | [supercharged/reports/generated/sustainability.md](supercharged/reports/generated/sustainability.md) | FederBio + Demeter cert lookup via Firecrawl (3/5 known biodynamic producers detected). |
| Dashboard SPA | [dashboard/](dashboard/) | `make serve-dashboard` then http://localhost:5175 — 4 pages, 762 producers in opportunity matrix. |

**What's in the code:**

- 137 tests pass (`make test`) — unit, integration, property-based (Hypothesis), schema (Pandera), Jinja template smoke.
- 14 CLI subcommands: `run · audit · status · compare · sensitivity · bootstrap · cluster · bias · anomaly · evaluate · sustainability · enrich-live · crawler · report`.
- Every output Parquet stamped with a config-hash; `cantinaiq audit <hash>` reproduces it.
- Deterministic pipeline: pure functions, run-log JSON per stage, configurable via Hydra + Pydantic-validated YAML snapshots.

---

## Hour-long deep dive — the design docs

For the full design intent, read in order:

1. [supercharged/PRD.md](supercharged/PRD.md) — what the product is and why.
2. [supercharged/docs/superpowers/specs/2026-05-15-cantinaiq-data-pipeline-design.md](supercharged/docs/superpowers/specs/2026-05-15-cantinaiq-data-pipeline-design.md) — the original technical spec.
3. [supercharged/docs/superpowers/plans/](supercharged/docs/superpowers/plans/) — four implementation plans, one per development tier. Each was written before the code, then executed task-by-task.

---

## Why two tracks?

ADA's brief asks for **(i)** a crawler extension, **(ii)** EDA, **(iii)** a written recommendation. That's the minimum. `/bare` ships that minimum honestly — pandas, one notebook, a half-page recommendation. The first-word producer heuristic is deliberately wrong (and the limitation is surfaced in the recommendation) so the contrast with `/supercharged` is the value proposition.

`/supercharged` answers the same business question if treated at HBO/academic level: a reproducible data product with explicit research question, schema contracts at every stage boundary, property-based tests on the scoring math, deterministic run logs, Vivino bias quantification against external import statistics, and a Next-style dashboard.

The delta between the two **is** the argument.

---

## Author

Vincent Blokker — [vincentblokker@gmail.com](mailto:vincentblokker@gmail.com)
