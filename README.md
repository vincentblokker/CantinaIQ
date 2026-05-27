# CantinaIQ

![CantinaIQ — Slurpini Partner Intelligence Engine](assets/hero.png)

**Slurpini Partner Intelligence Engine** — final assignment for the ADA Applied AI Bootcamp.

> *Which Italian wine producers should Slurpini prioritise for partnership, with what confidence, at what price band, with what defensible methodology?*

[![tests](https://img.shields.io/badge/tests-137%20passing-brightgreen)](supercharged/tests) [![python](https://img.shields.io/badge/python-3.13-blue)](supercharged/pyproject.toml) [![dashboard](https://img.shields.io/badge/dashboard-Vite%20%2B%20React-purple)](dashboard)

The brief was answered **twice** on purpose. The delta between the two tracks *is* the argument.

```text
/bare           ← the assignment as briefed: one notebook, pandas, EDA, recommendation
/supercharged   ← a reproducible data product: Polars + DuckDB + Pandera contracts +
                  Bayesian scoring + property tests + run logs + Jinja templates +
                  Firecrawl + Isolation Forest + Bootstrap CIs + Vivino bias analysis
/dashboard      ← Vite + React + Tailwind + Recharts SPA over the JSON exports
```

**Start here:** [FOR_REVIEWERS.md](FOR_REVIEWERS.md) — how to read this submission depending on whether you have 5 minutes, 30 minutes, or an hour.

**Quick links:** [Strategy brief PDF](CantinaIQ-in-Practice.pdf) · [Live dashboard](https://cantinaiq.clubventure.nl/) · [Rubric map](https://cantinaiq.clubventure.nl/for-evaluators) · [3-min walkthrough video](https://cantinaiq.clubventure.nl/downloads/walkthrough.mp4)

---

## Quick start

```bash
make setup    # install Python + Node deps (one-time)
make demo     # full pipeline + reports + dashboard build (~30 s)
make serve-dashboard   # then open http://localhost:5175
```

`make` from the repo root. No further setup needed beyond a Python 3.13 + Node 22 install.

---

## What this answers

ADA's brief: **(i)** extend the Vivino crawler, **(ii)** EDA on the export, **(iii)** an evidence-based recommendation for Slurpini.

- `/bare` ships that minimum in ~30 seconds of notebook runtime: one notebook, pandas, a half-page recommendation. Outputs are baked in — no need to run anything to read it.
- `/supercharged` treats the same business question as a reproducible data product. The output is not a recommendation — it's an *engine* that produces a recommendation whose every claim traces back to a config-hashed run log.

Both tracks converge on the same directional findings (Bolgheri Sassicaia + Brunello at the top by weighted rating; Primitivo di Manduria + Abruzzo as value plays). They differ in **how defensibly** the recommendation is reached.

---

## The contrast at a glance

| | `/bare` | `/supercharged` |
|---|---|---|
| Lines of code | ~150 | ~3,500 |
| Producer extraction | First-word heuristic | Alias whitelist → LLM disambiguation (OpenRouter) → gold-set evaluated (88 % exact recall, 96 % contains) |
| Rating aggregation | Bayesian shrinkage | Same, but `m` configurable, with sensitivity sweep + Kendall-τ stability |
| Scoring | Single weighted rating | 5-factor composite (rating · confidence · value · premium fit · opportunity) versioned per config snapshot |
| Validation | `if rating > 5: drop` | Pandera schema contracts; failures saved to parquet |
| Tests | None | 137 — unit, integration, property-based (Hypothesis), schema |
| Reproducibility | "Run all cells" | Deterministic CLI; `run_config_hash` stamps; `cantinaiq audit <hash>` |
| Bias discussion | 4 bullets | Quantified vs. Italian Trade Agency NL imports; Puglia ×0.61, Abruzzo ×0.52 under-represented |
| Anomaly handling | — | Isolation Forest flags 90/2,986 wines (extreme rating/review ratios) |
| Reporting | One markdown file | 8 generated artefacts — exec summary, methodology, data quality, findings one-pager (HTML), bias report, bootstrap CIs, anomalies, sustainability |
| Sustainability lookup | — | Live FederBio + Demeter check via Firecrawl |
| Dashboard | None | Vite + React + Tailwind + Recharts SPA — 4 pages, 762-bubble opportunity matrix |

---

## Repo layout

```text
.
├── README.md                  ← you are here
├── FOR_REVIEWERS.md           ← how to read this submission (start here)
├── Makefile                   ← `make demo`, `make test`, `make serve-dashboard`
├── bare/                      ← brief-compliant minimum (one notebook + crawler + recommendation)
├── supercharged/              ← the data product
│   ├── PRD.md
│   ├── README.md              ← stack + commands
│   ├── src/cantinaiq/         ← pipeline (ingestion → cleaning → validation → enrichment → scoring → export) + 14 CLI subcommands
│   ├── tests/                 ← 137 tests (unit/integration/properties/schema/reporting)
│   ├── config/                ← Hydra YAML + per-run config snapshots
│   ├── data/                  ← raw, interim, processed, exports, runs/<id>/, reference
│   ├── reports/
│   │   ├── templates/         ← Jinja templates (methodology, findings, exec summary, …)
│   │   └── generated/         ← rendered reports (regenerated by `cantinaiq report build`)
│   └── docs/superpowers/      ← spec + 4 implementation plans, one per development tier
├── dashboard/                 ← Vite + React + Tailwind + Recharts SPA
│   ├── src/{pages,components,lib}
│   └── public/data            ← symlink → supercharged/data/exports
└── CLAUDE.md                  ← guidance for AI coding agents working in this repo
```

---

## How the supercharged pipeline runs

```text
Vivino-export.xlsx  (409 777 rows × 16 sheets)
    │
    ▼ ingestion
01_raw.parquet
    │
    ▼ cleaning  (encoding fixes, tuple unwrap, country filter, dedupe)
02_cleaned.parquet                   ← 2 986 rows
    │
    ▼ validation  (Pandera contracts; failures → validation-failures.parquet)
03_validated.parquet
    │
    ▼ enrichment  (alias whitelist → LLM disambiguation → macro-region + segments)
italian_wines_enriched.parquet
    │
    ▼ scoring  (Bayesian weighted rating + 5-factor composite + segments + recommendations)
{wines,producers,regions}_scored.parquet
    │
    ▼ export
data/exports/*.json  ──► consumed by the dashboard
data/runs/<id>/stage-*.json  ←  per-stage run log, JSON
reports/generated/*.{md,html}  ←  rendered from templates + run-log
```

Every stage is a pure function of `(input parquet, config) → (output parquet, run-log JSON)`. No hidden state, no side-effects outside `data/`.

---

## Tech stack

**Python pipeline:** Polars · DuckDB · Pandera · Hydra · Pydantic · Typer · Jinja2 · scikit-learn · scipy · OpenAI SDK (OpenRouter) · Firecrawl · pytest + Hypothesis · uv · ruff · mypy.

**Dashboard:** Vite · React 19 · TypeScript · Tailwind 3 · Recharts · React Router.

---

## Reproducibility

Every output Parquet carries a `run_config_hash`. The config that produced any report is snapshotted at `supercharged/config/snapshots/<hash>.yaml`. Re-running with

```bash
cd supercharged && uv run cantinaiq run all --config-snapshot <hash>
```

reproduces the same outputs byte-for-byte (modulo timestamp metadata in run logs).

---

## Deploying updates to the live site

The site at https://cantinaiq.clubventure.nl/ is a static deploy — no
backend, no database. The dashboard fetches JSON files baked into the
build at compile time. Updating the live site is two targets in the
Makefile:

```bash
make deploy       # package current build → push to live (no pipeline re-run)
make redeploy     # pipeline + reports + dashboard + deploy (full chain)
```

**`make deploy`** is for changes that touch only the dashboard SPA
(React code, copy edits, assets). It runs `vite build`, tars `dist/`,
scps the tarball to the server, creates a timestamped backup of the
current site, then extracts the new build over the webroot.

**`make redeploy`** is for changes that touch the data — most often
editing `supercharged/data/raw/Vivino-export.xlsx` or a pipeline config.
It chains `pipeline → reports → dashboard → deploy` so a single
command re-runs the full pipeline, regenerates the JSON exports the
dashboard consumes, rebuilds the SPA, and ships the result.

Both targets back up the previous live site to
`/tmp/cantinaiq-site-backup-<timestamp>.tar.gz` on the server before
extracting. Rollback in one command:

```bash
ssh clubventure 'tar -xzf /tmp/cantinaiq-site-backup-<STAMP>.tar.gz -C /opt/apps/react-cantinaiq/site'
```

The SSH host and webroot are configurable via Make variables:

```bash
make deploy SSH_HOST=other-host SSH_PATH=/var/www/other-site
```

Defaults: `SSH_HOST=clubventure`, `SSH_PATH=/opt/apps/react-cantinaiq/site` — both match
the `~/.ssh/config` entry and the bind-mount target of the nginx:alpine
container that serves the site on the Hetzner box. Traefik handles
HTTPS via Let's Encrypt; range requests for the `walkthrough.mp4` work
out of the box (nginx serves byte-ranges by default), so the embedded
HTML5 video player on `/for-evaluators` supports seeking.

---

## Roadmap

Beyond the submission, the architecture is shaped to make the next
few features tractable rather than aspirational. Listed roughly by
ROI per hour of work.

### 1 · `/admin` — upload a new Vivino export, run the pipeline, redeploy

Today the data refresh is `make redeploy` from a laptop with the repo
checked out. The next step is a small admin route on the dashboard
itself:

- **`/admin` route** behind basic auth (or a magic-link), hidden from
  the public navigation.
- **Drag-and-drop upload** for a new `Vivino-export.xlsx`. File goes
  to a server-side staging directory.
- **Run button** triggers the supercharged pipeline against the
  uploaded file in a background job.
- **Live log stream** during the run (Server-Sent Events from the
  job runner). On success, the new JSON exports replace the live
  ones atomically and the dashboard re-renders without a browser
  reload — the JSON fetch hooks already exist.
- **Run history** with diffs against the previous run — which
  producers moved into / out of the top 20, what the bias delta is,
  whether the bootstrap stability dropped.

**The architectural cost.** This breaks the current "fully static"
property of the live site. A small backend service (FastAPI + a
Redis/RQ job queue, or just a Python script behind a reverse-proxied
endpoint) needs to run alongside the nginx static server. The pipeline
itself stays unchanged — it already produces deterministic outputs
from `(input parquet, config) → output JSON`. The new service is
thin: file-upload, invoke `uv run cantinaiq run all`, atomically
swap the JSON exports, push a status update.

**Estimated effort.** 1-2 days of focused work. The longest sub-task
is auth (deciding on the right approach for a single-tenant tool
hosted on a shared box).

### 2 · Scheduled re-runs against a fresh Vivino crawl

Today the Vivino export is a static file. The bare-track crawler is
already in `bare/crawler-extension.py`. A `cron` (or systemd timer)
on the Hetzner box, running monthly, could re-crawl, run the
pipeline, and redeploy automatically — turning the dashboard into a
living signal rather than a snapshot. This stacks on top of item 1
(the admin route would then expose the schedule + last-run status).

### 3 · Per-evaluator share links

When this submission gets reused as a portfolio piece, individual
share links per evaluator (with their name baked into the cover,
their own usage analytics, optional expiry) would replace the
generic `/for-evaluators` URL. Cheap to add — it's a Vite route
with a URL param.

### 4 · Producer outreach hand-off

The strategy brief recommends a shortlist of producers. The next
useful artefact is an export per recommended producer with the
evidence pre-bundled — recent ratings, value-segment placement,
bias-adjusted ranking, sustainability findings. A button on
`/producers/<slug>` that generates the PDF dossier on demand.
Would lean on the existing Jinja templates in `supercharged/reports/templates/`.

### 5 · Paid data sources — where the budget unlocks real depth

Today's pipeline uses two paid APIs sparingly (OpenRouter for LLM
disambiguation, Firecrawl for sustainability lookups). With a
modest monthly budget the depth of the recommendation can step up
significantly. Listed by what each unlocks per euro:

- **Vivino official API** *(if access is granted — currently
  partnership-only)*. Replaces the static Excel crawler with live
  region/producer/wine data, vintage-level reviews, taste
  descriptors. Eliminates the "data is from a snapshot" caveat.
  Highest impact if available.

- **Italian Trade Agency (ICE Amsterdam) import data** *(paid
  subscription)*. The bias report compares Vivino's regional
  distribution against ICE NL import volumes — currently using a
  one-time export. A live feed would let the dashboard quantify
  drift over time and flag emerging regions before Vivino's user
  base catches up.

- **Wine-Searcher API** *(tiered pricing, ~€100-300/mo)*. Real-time
  price benchmarking across the Dutch + EU market. Replaces the
  single-snapshot price in the Excel with a price corridor + recent
  movement. Lets the value-for-money composite reflect what
  partners actually charge today, not what Vivino recorded months ago.

- **FederBio Pro / Demeter direct database access** *(paid tier)*.
  Today's Firecrawl sustainability check scrapes public pages,
  which is brittle and rate-limited. Direct DB access via the paid
  tiers would verify certifications authoritatively, including
  expiry dates, and unlock the "sustainability segment" filter that
  the strategy brief alludes to but cannot ship reliably yet.

- **Premium LLM tier (GPT-5 or Claude Opus 4.7 direct)** for
  producer disambiguation. Today's LLM pass runs on OpenRouter's
  cheaper tiers, hitting 88% exact recall against the gold set. A
  premium tier would close most of the remaining 12% — the hard
  cases (multi-vintage variants, sub-brand naming) — at roughly
  €0.50 per full pipeline run. Marginal cost, meaningful gain.

- **Google Maps Places + Geocoding APIs** *(pay-per-call)*. The
  current macro-region grouping is a hand-curated lookup. With the
  Places API, sub-region polygons + altitude + grape-suitability
  overlays could power a real map on `/regions` instead of the
  current chart. The producer modals could surface nearby horeca
  density — useful context for Slurpini's distribution decisions.

**Order-of-magnitude budget:** ~€200-500/month covers items 3-6
above (Wine-Searcher, FederBio/Demeter, premium LLM, Google Maps).
Item 1 (Vivino) is partnership-gated, not money-gated. Item 2
(ICE) is in the same range but requires a separate B2B contract.

The pipeline architecture absorbs these without restructuring —
each is a new stage (`enrichment_wine_searcher`, `enrichment_geo`)
that reads parquet, writes parquet, ships a config-hashed run log.
The cost surface stays auditable: every API call is logged to
`data/runs/<run-id>/api-calls.json` for cost reconciliation against
the provider's billing.

---

## Author

Vincent Blokker — [vincentblokker@gmail.com](mailto:vincentblokker@gmail.com)
