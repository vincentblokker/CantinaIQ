# DEMO — 3-minute walkthrough script

A storyboard you can read aloud while screen-recording (Loom / QuickTime).
Total runtime ≈ 3 minutes if you don't pause.

**Before you start:**
- Have `make demo` already finished (so reports + dashboard are ready).
- Run `make serve-dashboard` in a terminal before recording — keeps the dev server warm.
- Recommended window layout: 1) browser pointed at http://localhost:5175, 2) VS Code on the repo root, 3) Terminal in the repo root.

---

## Scene 1 — Two tracks (0:00 – 0:25)

**On screen:** root `README.md` in VS Code, or just the repo directory tree.

> "ADA's final assignment is the Slurpini wine case — pick Italian wine producers using Vivino data. I answered it twice. `/bare` is the brief, literally: one pandas notebook, a half-page recommendation, and a crawler extension — what the assignment asks for in about thirty seconds of runtime. `/supercharged` answers the same business question as a reproducible data product instead of a one-off analysis. The delta between the two is the argument."

**Highlight:** the three top-level folders (`bare/`, `supercharged/`, `dashboard/`).

---

## Scene 2 — `/bare` ships the assignment (0:25 – 0:50)

**On screen:** open `bare/recommendation.md` in VS Code. Scroll through.

> "Half-A4, written for a non-technical buying-committee reader. Recommends to hold the prestige tier — Tenuta San Guido, Antinori, Gaja — and expand in Puglia and Abruzzo. Every claim traces to a CSV in `bare/output/`. Limitations are explicit: first-word producer extraction is wrong, Vivino isn't the Dutch wine market, sustainability isn't in the dataset. That's the assignment — done."

**Optional cut to:** `bare/crawler-extension.py` (deliverable (i) is there), `bare/notebooks/slurpini-analysis.ipynb` (deliverable (ii) with outputs baked in).

---

## Scene 3 — `/supercharged` runs end-to-end (0:50 – 1:25)

**On screen:** terminal.

```bash
make demo
```

> "`make demo` runs the full supercharged pipeline against the same Vivino export. Six stages — ingestion, cleaning, validation, enrichment, scoring, export. Each one is a pure function of (input parquet, config) → (output parquet, run-log JSON). Every output is config-hash stamped. Re-running with the same hash reproduces the same bytes."

**While it runs (~30 s):** show `supercharged/data/runs/<id>/` filling with per-stage JSON logs. Open one quickly to show pre/post rows + drop reasons.

> "Two thousand nine hundred eighty-six Italian wines after cleaning, down from four hundred ten thousand raw rows. Pass-2 LLM disambiguation against OpenRouter resolves seven hundred sixty-two distinct producers."

---

## Scene 4 — The reports (1:25 – 1:55)

**On screen:** `supercharged/reports/generated/` in VS Code. Open three files in tabs.

> "Eight generated reports. The executive summary is a Jinja template fed from the run log — numbers cannot drift from the code. Methodology has thirteen sections including a delta paragraph explaining why supercharged keeps two thousand nine hundred eighty-six wines and bare keeps five thousand seven hundred eighty-six. Findings one-pager is a printable A4 HTML."

**Quick reads:**
- `executive-summary.md` — top-5 producers, hold/expand/audit.
- `bias-report.md` — Vivino vs. ICE NL imports. Puglia, Abruzzo, Campania under-represented — surface this honestly, don't bury it.
- `bootstrap-ci.md` — Tenuta Masseto in top-10 in 195 of 200 resamples. Terre di San Vincenzo's p95 is 412 — that's a noise pick, not a real top-5.

---

## Scene 5 — The dashboard (1:55 – 2:30)

**On screen:** http://localhost:5175 (Overview page).

> "Same data, different surface. Vite + React + Tailwind + Recharts. Three KPIs, top-5 producers with recommendation pills, top-5 regions."

**Click through:**
- `/regions` — show the table.
- `/producers` — open the dropdown, filter on "Premium Brand Builder" (3 hits), then "Value Opportunity" (25 hits).
- `/matrix` — the scatter. Hover over a top-right blue bubble: "Tenuta Masseto, weighted rating 4.30, €1567, four thousand six hundred reviews".

> "Seven hundred sixty-two producers in one chart. Log-price on X, weighted rating on Y, bubble size proportional to review count, colour by market segment. Top-right is Premium Icon, top-left is Hidden Gem, bottom-right is Overpriced Risk."

---

## Scene 6 — What makes this defensible (2:30 – 2:55)

**On screen:** terminal.

```bash
make test
```

> "One hundred thirty-seven tests pass. Unit, integration, property-based — Hypothesis fuzzes the Bayesian scoring math, Pandera enforces schemas at every stage boundary."

```bash
ls supercharged/src/cantinaiq/
```

> "Fourteen CLI subcommands. The interesting ones beyond `run`: `compare` diffs two runs, `sensitivity` sweeps a parameter, `bootstrap` does rank CIs, `bias` quantifies Vivino against external import data, `cluster` does sklearn KMeans, `evaluate` measures producer-extraction recall against a gold set, `sustainability` checks FederBio and Demeter via Firecrawl."

---

## Scene 7 — Close (2:55 – 3:00)

**On screen:** `FOR_REVIEWERS.md`.

> "FOR_REVIEWERS.md tells you where to look depending on how much time you have. Five minutes — bare. Thirty minutes — supercharged. An hour — the design docs. Make demo runs everything in thirty seconds. Vincent Blokker, ADA Applied AI Bootcamp final assignment."

---

## Soundbites / one-liners you can drop

- *"The brief was answered twice on purpose. The delta is the argument."*
- *"Every output is config-hash stamped. Same hash, same bytes."*
- *"Pandera contracts at every stage boundary — fail loud, not silent."*
- *"Vivino's bias is quantified, not hand-waved away."*
- *"Tenuta Masseto in top-10 in one hundred ninety-five of two hundred resamples."*
- *"Numbers in templated reports cannot drift from the code."*

---

## Setup recap

```bash
make setup              # one-time
make demo               # full pipeline + reports + dashboard build  (~30 s)
make serve-dashboard    # http://localhost:5175
```

Optional environment for the LLM + Firecrawl passes:

```bash
export OPENROUTER_API_KEY=sk-or-...      # enables pass-2 producer disambiguation
export FIRECRAWL_API_KEY=fc-...          # enables sustainability + live enrichment
```
