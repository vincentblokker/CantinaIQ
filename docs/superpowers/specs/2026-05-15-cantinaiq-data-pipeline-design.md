# CantinaIQ Sub-Project A — Data Pipeline Design

**Status:** Approved, ready for implementation planning
**Date:** 2026-05-15
**Author:** Vincent Blokker (with Claude as design partner)
**Audience:** Vincent (primary), ADA staff / HBO/academic examiners (secondary)
**Supersedes:** —

---

## 0. Why this spec exists

CantinaIQ is built as an argument-by-demonstration to the Amsterdam Data Academy (ADA) that their Applied AI Bootcamp final assignment sits below HBO/academic level. The project deliberately over-delivers against the original brief (which asks for *crawler-extension + EDA + recommendation*). The artefact's *quality* makes the argument; the spec does not editorialise about ADA.

This spec describes **sub-project A**, the data-pipeline fundament. The full project decomposes into:

| Sub-project | Scope |
|---|---|
| **A** *(this spec)* | Data pipeline: ingestion → cleaning → validation → enrichment → scoring → export, plus instrumented reporting. |
| B | Crawler extension (Python, follows ADA brief literally). |
| C | Statistical rigour: bootstrap/Wilson CIs, sensitivity analysis, bias quantification, clustering validation. |
| D | Next.js decision-support dashboard (5 pages). |
| E | Academic reporting (methodology, limitations, executive summary, critique). |

A is the bottleneck — B/C/D/E all consume A's outputs. A's exports (`data/exports/*.json`) are a stable contract for downstream sub-projects.

---

## 1. Design decisions (resolved)

The six decisions made during brainstorming:

| # | Decision | Choice |
|---|---|---|
| 1 | Scope boundary A vs C (statistical depth in A) | **Moderate** — point estimates + Bayesian shrinkage with full reproducibility metadata + DQ report. CIs/sensitivity/bias go to C. |
| 2 | Engineering stack | **Polars + DuckDB + Pandera + uv + Pytest**, Python 3.13. |
| 3 | Producer extraction | **Two-pass: rule-based (regex + alias whitelist) + LLM-disambiguation with persistent cache.** |
| 4 | DQ reporting strategy | **Instrumented pipeline + Jinja2 templates.** Each stage emits a run-log JSON; reports render from the log so numbers never drift from code. |
| 5 | Orchestration + testing | **Typer CLI + Hydra config composition; Pytest + Hypothesis property-tests + Pandera schema-tests.** |
| 6 | Config management | **Pydantic schema (type-validated tunables) + Hydra orchestration (CLI overrides, multirun for C).** |

---

## 2. Architecture

Sub-project A is a locally-runnable Python package that turns `Upload/Vivino-export.xlsx` into (i) validated/enriched/scored Parquet datasets, (ii) JSON exports for downstream consumers (sub-projects C/D), and (iii) Markdown data-quality / methodology reports rendered from instrumented run-logs.

### 2.1 Repository topology

```
config/                              # Hydra YAMLs + Pydantic schemas
src/cantinaiq/
  cli.py                             # Typer entrypoint
  config/                            # Pydantic models + Hydra loader
  ingestion/                         # Excel → raw Parquet (all sheets, no filter)
  cleaning/                          # normalisation, dedupe, IT filter
  validation/                        # Pandera schemas, fail-loud on contract breaches
  enrichment/                        # producer (rule+LLM), macro-region, segments
  scoring/                           # weighted_rating, value_score, composite
  export/                            # producer/region/wine-shortlist JSONs
  reporting/                         # run-log → markdown via Jinja2
  runlog/                            # instrumentation helpers (used by all stages)
data/
  raw/                               # source files (Vivino-export.xlsx)
  interim/                           # per-stage Parquets
  processed/                         # final cleaned + enriched + scored
  exports/                           # JSON for downstream
  runs/<run_id>/                     # run-logs per stage (JSON)
  reference/                         # producer_aliases.csv, macro_regions.csv, llm_cache.parquet
reports/
  templates/                         # Jinja2 .md.j2
  generated/                         # rendered output (gitignored except cover artefacts)
tests/
  fixtures/vivino_sample.xlsx        # 50-row hand-picked sample
  unit/   schemas/   properties/   integration/   reporting/
```

### 2.2 Stack

- **Python 3.13** (`.python-version`).
- **Polars 1.x** — dataframes, lazy API where it helps readability.
- **DuckDB 1.x** — SQL layer for aggregation/JSON-export queries on intermediate Parquets.
- **Pandera 0.20+** with Polars support — schema validation, dual-used in production and tests.
- **Hydra 1.3+** — config composition, CLI overrides, multirun (for sub-project C).
- **Pydantic 2.x** — type-validated config schema with cross-field invariants.
- **Typer 0.12+** — CLI surface (`cantinaiq run …`, `cantinaiq report …`, `cantinaiq audit …`).
- **Pytest + Hypothesis** — unit, schema, property, and integration tests.
- **Jinja2** — Markdown template rendering with run-log injection.
- **Matplotlib** — deterministic static charts (PNG/SVG), fingerprinted by config hash.
- **uv** — dependency management, lockfile, Python toolchain.
- **Ruff + mypy** — linting and type checking in CI.

### 2.3 Foundational principle

**Every stage is a pure function of `(input parquet, config) → (output parquet, run-log JSON)`.** No hidden state, no side-effects outside `data/`. Each stage is individually testable; the full pipeline is deterministically replayable.

---

## 3. Data flow

| Stage | Input | Transform | Output | Run-log keys |
|---|---|---|---|---|
| **ingestion** | `data/raw/Vivino-export.xlsx` | Read all sheets via `polars.read_excel`, add `source_sheet` column, concat. No filter, no cleaning. | `data/interim/01_raw.parquet` | `sheets_read`, `rows_per_sheet`, `total_rows`, `column_inventory` |
| **cleaning** | `01_raw.parquet` | Tuple-string parsing, encoding fix, numeric coercion, country/region trim+title-case, wine-name normalisation, dedupe on `(wine_name_normalised, producer_hint, vintage)`. **IT filter: keep only `country == "Italy"` *after* cleaning; `source_sheet` is metadata only.** | `data/interim/02_cleaned.parquet` | `drops_per_reason`, `drop_samples`, `pre_rows`, `post_rows`, `dedup_collisions`, `it_filter_kept` |
| **validation** | `02_cleaned.parquet` | Pandera schema: rating ∈ [0,5], rating_count ≥ 1, price > 0, country/region non-empty. *Fail-loud:* exit non-zero on schema failure; write `validation-failures.parquet`. | `data/interim/03_validated.parquet` | `schema_name`, `failures_per_rule`, `samples` |
| **enrichment** | `03_validated.parquet` + `data/reference/{producer_aliases.csv, macro_regions.csv, llm_cache.parquet}` | Three sub-passes: (a) macro-region lookup, (b) price/confidence segment from config thresholds, (c) producer extraction (pass-1 rules + pass-2 LLM with cache). | `data/processed/italian_wines_enriched.parquet` | `enrichment_coverage`, `producer_pass1_match_rate`, `llm_cache_hits`, `llm_new_calls`, `aliases_used` |
| **scoring** | `italian_wines_enriched.parquet` | Bayesian weighted rating per wine with `m` from config (auto-median fallback if absent); aggregate to producer/region (review-count-weighted); composite Slurpini Partner Intelligence Score; market_segment via config rules. | `wines_scored.parquet`, `producers_scored.parquet`, `regions_scored.parquet` | `global_mean_rating`, `m_used`, `m_strategy` (manual/auto-median), `weights_used`, `score_distribution_summary` |
| **export** | three `*_scored.parquet` | Format JSON contracts: `producer_rankings`, `region_rankings`, `wine_shortlist`, `dashboard_summary`. | `data/exports/*.json` | `records_per_export` |
| **reporting** | `data/runs/<run_id>/*.json` + templates | Render `data-quality.md`, inject `{{ run.* }}` placeholders in `methodology.md`. | `reports/generated/*.md` | n/a |

### 3.1 Stage independence

Stages read only their own input Parquet, not earlier ones. After a config change, `cantinaiq run all --from scoring` re-runs only what's affected. This is essential for sub-project C's sensitivity sweeps.

### 3.2 Edge-case handling

- **No-producer wines:** `producer_name = null`, `enrichment_confidence = "None"`. Kept in wine-shortlist; excluded from producer aggregation.
- **Low-sample regions:** regions with < 3 wines after cleaning are scored but flagged `low_sample_region = true` in the export. Downstream decides visibility.
- **Config-hash trace:** every output Parquet carries a `run_config_hash` column. Every output file is traceable to the exact config that produced it.

---

## 4. Configuration & reproducibility

### 4.1 Hydra composition

```
config/
  pipeline.yaml                      # main entry
  cleaning/default.yaml
  enrichment/{default.yaml, aliases.yaml, llm.yaml}
  scoring/
    default.yaml
    weights/{baseline.yaml, rating-heavy.yaml, value-heavy.yaml}
  segments/default.yaml
  paths/default.yaml
  snapshots/<hash>.yaml              # auto-archived configs (append-only)
```

### 4.2 Pydantic schema (excerpt)

```python
class ScoringWeights(BaseModel):
    weighted_rating: float = Field(ge=0, le=1)
    market_confidence: float = Field(ge=0, le=1)
    value_for_money: float = Field(ge=0, le=1)
    premium_fit: float = Field(ge=0, le=1)
    portfolio_opportunity: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def sum_to_one(self):
        s = sum(self.model_dump().values())
        if not 0.999 <= s <= 1.001:
            raise ValueError(f"Scoring weights must sum to 1.0, got {s:.4f}")
        return self

class PipelineConfig(BaseModel):
    cleaning: CleaningConfig
    enrichment: EnrichmentConfig
    scoring: ScoringConfig
    segments: SegmentsConfig
    paths: PathsConfig

    @cached_property
    def hash(self) -> str:
        payload = json.dumps(self.model_dump(), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:8]
```

Every business assumption is in YAML, validated by Pydantic on load, and reachable via `cfg.scoring.weights.value_for_money`.

**Hydra ↔ Pydantic integration:** Hydra produces an `OmegaConf` DictConfig. The CLI entrypoint converts it to a plain dict (`OmegaConf.to_container(cfg, resolve=True)`) and then constructs `PipelineConfig(**d)`. Validation (`sum_to_one`, bounds, types) happens in Pydantic's `__init__`, so an invalid config aborts before any stage runs. We do *not* use `hydra-zen` or `pydantic-omegaconf` — keeping the bridge as a single explicit conversion call avoids hidden coupling.

### 4.3 CLI surface

```bash
cantinaiq run cleaning                                # one stage
cantinaiq run all                                     # full pipeline
cantinaiq run all --from scoring                      # resume from stage
cantinaiq run scoring scoring.weights.value_for_money=0.30 \
                      scoring.weights.weighted_rating=0.30
cantinaiq run scoring scoring/weights=value-heavy     # swap config group
cantinaiq run scoring --multirun \
  scoring/weights=baseline,rating-heavy,value-heavy \
  scoring.bayesian_m=50,100,250                       # for sub-project C
cantinaiq run all --config-snapshot a3f8e1            # reproduce historical run
cantinaiq status                                      # last run summary
cantinaiq audit <config-hash>                         # list outputs, commits, deltas
cantinaiq report build [--run <id>|--latest]
cantinaiq cache invalidate --where region=Toscana     # producer LLM cache
```

### 4.4 Reproducibility contract

1. **Deterministic:** Polars operations use explicit sort keys; LLM-cache lookups are content-hashed; cache versioning prevents drift on model upgrades.
2. **Versioned configs:** Every distinct config hash is snapshotted to `config/snapshots/<hash>.yaml` (append-only, git-committed). Full audit trail.
3. **Auditable:** `cantinaiq audit <hash>` cross-references outputs, commits, and current-vs-snapshot deltas.
4. **Pinned environment:** `uv.lock` committed, `pyproject.toml` pins major versions, Python pinned via `.python-version`.

### 4.5 Bayesian `m` strategy

`m` (shrinkage threshold) is configurable but has an automatic default: `m = median(rating_count)` over the cleaned Italian dataset. The pipeline computes it in the scoring stage and records both the value and the strategy (`manual` or `auto-median`) in the run-log. *We chose `m` from the data, not from intuition* — defensible to an examiner.

---

## 5. Producer extraction

The only stage with significant inferential uncertainty; treated as a *modelling* decision, not data cleaning.

### 5.1 Pass 1 — deterministic (`pass1_rules.py`)

Input: `wine_name`, `region`. Output: `ProducerCandidate(name, confidence, method)`.

In order:

1. **Alias whitelist** (`data/reference/producer_aliases.csv`, columns `pattern, canonical_name, match_type`) — first match wins, `confidence = "High"`, `method = "alias:<canonical>"`. Seed entries: Castello di Ama, Tenuta San Guido, Marchesi Antinori, Fattoria Le Pupille, Gaja, Biondi-Santi, Frescobaldi, Casanova di Neri, etc.
2. **Italian honorific prefixes** — whitelist of titles that precede a producer name: `Marchese, Marchesi, Tenuta, Fattoria, Castello, Azienda Agricola, Cantina, Podere, Villa, Conte, Barone, Antica, Antichi, Vigneti, Cascina`. If `wine_name` starts with one → take first 2-3 tokens. `confidence = "Medium"`, `method = "honorific-prefix"`.
3. **First-token heuristic** — fall back to first token *unless* it matches a wine-style blacklist (`Brunello, Chianti, Barolo, Barbaresco, Amarone, Prosecco, Rosso, Bianco, Bolgheri, Etna, …`). `confidence = "Low"`, `method = "first-token"`.
4. **No match** → `confidence = "None"`, candidate for pass 2.

### 5.2 Pass 2 — LLM disambiguation (`pass2_llm.py`)

Triggered for `confidence ∈ {"Low", "None"}` or flagged-ambiguous rows (≥5 tokens before vintage, multiple honorifics, pass-1 result outside known-producer distribution).

- **Model:** `claude-haiku-4-5-20251001` (fast, cheap, sufficient for structured extraction). Temperature 0. JSON-mode output. Prompt-caching enabled on the system prompt (constant across batches).
- **Batching:** 50 rows per call.
- **Prompt:** see spec sketch in §5.2.1 below.
- **Cache:** `data/reference/llm_cache.parquet` keyed on `sha256(wine_name + "|" + region + "|" + model_version)`. Hit policy: same key + same `model_version` → skip API. Mismatch on `model_version` flags for opt-in re-call.

#### 5.2.1 Prompt template

```
You are extracting Italian wine producer names from raw Vivino wine entries.

For each entry, return JSON with:
  - producer: the canonical producer/winery name. Use full Italian honorific
    where standard ("Tenuta San Guido", not "San Guido"). If you are not
    confident the wine name actually contains a producer, return null.
  - inferred_grape_or_style: e.g. "Sangiovese", "Nebbiolo", "Sangiovese-
    dominant blend", or null if uncertain.
  - confidence: "High" | "Medium" | "Low".
  - reasoning: ≤15 words.

Rules:
  - Producer ≠ appellation. "Brunello di Montalcino" is an appellation; the
    producer is whoever made it.
  - Producer ≠ wine name. "Sassicaia" is a wine; the producer is "Tenuta San
    Guido".
  - If no producer signal, return null with confidence "Low".

Entries: [ { "id": N, "wine_name": "...", "region": "..." }, ... ]

Return: JSON array of { id, producer, inferred_grape_or_style, confidence, reasoning }.
```

### 5.3 Post-hoc validation (`validate.py`)

Three warnings emitted to the run-log (not failures):

1. **Distribution check** — top-50 producers by wine count compared against a hand-curated `known_producers_top50.csv`. < 60% overlap → warning. This is the *anchor* against LLM drift.
2. **Multi-producer-per-wine check** — same `wine_name` assigned different producers → `producer_extraction_inconsistency` warning with sample rows.
3. **Coverage report** — `% rows with confidence ∈ {High, Medium}` per macro-region. Targets: ≥80% overall, ≥70% per macro-region. Misses are surfaced in `data-quality.md`.

---

## 6. Data-quality reporting

### 6.1 Three-layer structure

```
src/cantinaiq/runlog/                   # emitter + schema + loader
src/cantinaiq/reporting/                # CLI, context builder, renderer, charts
reports/templates/{*.md.j2, _macros.j2} # Jinja2 sources
reports/generated/                      # rendered output + figures/
```

### 6.2 Run-log schema (Pydantic)

```python
class StageRunLog(BaseModel):
    stage: str
    started_at: datetime
    finished_at: datetime
    pre_rows: int
    post_rows: int
    drops: dict[str, int]
    drop_samples: dict[str, list[dict]]
    schema_failures: dict[str, int] | None
    custom: dict[str, Any]
    config_hash: str
    config_snapshot_ref: str

class RunBundle(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: datetime
    stages: dict[str, StageRunLog]
    pipeline_config: dict[str, Any]
    cli_args: list[str]
    git_sha: str | None
    python_version: str
    package_version: str
```

### 6.3 Emitter pattern

```python
with RunLog.stage("cleaning", run_id, cfg) as log:
    log.pre_rows = raw.height
    cleaned, drops = apply_cleaning_rules(raw, cfg.cleaning)
    log.post_rows = cleaned.height
    log.drops = drops.counts
    log.drop_samples = drops.samples
    log.custom["it_filter_kept"] = cleaned.filter(...).height
    cleaned.with_columns(pl.lit(cfg.hash).alias("run_config_hash")).write_parquet(out)
```

The context manager atomic-writes `data/runs/<run_id>/stage-<name>.json`, catches exceptions (logs traceback + non-zero exit), and appends to `data/runs/<run_id>/manifest.json` on success with output-path + checksum.

### 6.4 Drop-cascade table (illustrative)

| Stage | Pre-rows | Post-rows | Removed | % | Top reason |
|---|---:|---:|---:|---:|---|
| ingestion | — | 47,291 | — | — | — |
| cleaning → encoding/parsing | 47,291 | 47,180 | 111 | 0.23% | unparseable price |
| cleaning → IT filter | 47,180 | 11,932 | 35,248 | 74.71% | non-Italian country (cleaned) |
| cleaning → dedupe | 11,932 | 9,847 | 2,085 | 17.47% | duplicate (name, producer-hint, vintage) |
| validation → schema | 9,847 | 9,841 | 6 | 0.06% | rating > 5 (data error) |
| enrichment → producer-coverage | 9,841 | 9,841 | 0 | 0.00% | pass-through; 87% confidence ≥ Medium |
| scoring → low-review-floor | 9,841 | 9,693 | 148 | 1.50% | rating_count < scoring.min_reviews_floor |

Numbers are placeholders; generated 100% from `RunBundle`.

### 6.5 Charts (static, deterministic)

Matplotlib only (no Plotly). PNG + SVG. Filenames fingerprint config-hash. Generated:

1. **Drop-cascade waterfall**
2. **Rating distribution histogram — pre vs post Bayesian shrinkage**
3. **Confidence-segment coverage per macro-region** (stacked bar)
4. **Producer-extraction confidence mix** (donut: High / Medium / Low / None)
5. **m-sensitivity sweep** *(optional; only if run used `--multirun`)* — top-10 producer shuffle vs `m`

### 6.6 Templates

`methodology.md.j2` is ~80% editorial prose + ~20% `{{ run.* }}` injection. Example excerpt:

```
After parsing, encoding-fix, dedupe and the country filter, we retain
{{ run.stages.cleaning.post_rows | thousands }} Italian wines —
a {{ ((run.stages.ingestion.post_rows - run.stages.cleaning.post_rows) / run.stages.ingestion.post_rows * 100) | round(1) }}%
reduction.
{{ figure("drop-waterfall") }}
```

Argument under editorial control; numbers under code control. They cannot drift.

### 6.7 CLI

```bash
cantinaiq report build                                 # latest run
cantinaiq report build --run 2026-05-15T14-22__a3f8e1
cantinaiq report build --only data-quality
cantinaiq report serve                                 # local HTTP for previewing
```

### 6.8 Markdown-only

No HTML reports. Reasons: markdown diffs in PRs, GitHub renders out-of-the-box, `pandoc methodology.md -o methodology.pdf` for print. HTML adds visual polish at the cost of review-loop speed; not worth it.

---

## 7. Testing

### 7.1 Layout

```
tests/
  conftest.py
  fixtures/
    vivino_sample.xlsx                  # 50 rows, hand-curated
    vivino_sample_dirty.xlsx            # extra dirt for cleaning tests
    expected_outputs/{cleaned,enriched,scored_producers}.parquet
    producer_aliases_test.csv
    llm_cache_fixture.parquet           # so tests make zero API calls
  unit/
    test_ingestion.py
    test_cleaning.py
    test_validation.py
    test_enrichment_producer_pass1.py
    test_enrichment_producer_pass2.py   # mocked LLM via cache-hit
    test_enrichment_macro_region.py
    test_enrichment_segments.py
    test_scoring.py
    test_export.py
  schemas/
    test_pandera_schemas.py
  properties/
    test_bayesian_properties.py
    test_scoring_properties.py
  integration/
    test_full_pipeline.py
    test_config_hash_stability.py
    test_multirun_isolation.py
  reporting/
    test_report_renders.py
    test_drop_cascade_table.py
```

### 7.2 The 50-row fixture

Hand-curated to hit every dirty pattern at least twice:

- 3 tuple-string country rows
- 2 encoding-corruption rows
- 4 duplicates
- 5 non-Italian (must be filtered)
- 3 missing-price, 3 zero-rating-count, 2 rating > 5
- 5 whitelist-matchable producers (Castello di Ama, Tenuta San Guido, Marchesi Antinori, Gaja, Biondi-Santi)
- 5 pass-1 misses, pass-2 cache-hits (Tignanello, Sassicaia, Solaia, …)
- 3 truly ambiguous (no producer token)
- 5 macro-regions (Toscana, Piemonte, Veneto, Sicilia, Puglia)
- 10 with varying `rating_count` (5, 50, 500, 5000, 50000) for Bayesian tests

### 7.3 Pandera schemas — dual-use

```python
import pandera.polars as pa

class CleanedSchema(pa.DataFrameModel):
    wine_name: str = pa.Field(nullable=False, str_length={"min_value": 1})
    country: str = pa.Field(isin=["Italy"])
    region: str = pa.Field(nullable=False, str_length={"min_value": 1})
    rating: float = pa.Field(ge=0, le=5)
    rating_count: int = pa.Field(ge=1)
    price: float = pa.Field(gt=0)
    source_sheet: str = pa.Field(nullable=False)
    run_config_hash: str = pa.Field(str_length=8)

    class Config:
        strict = True
        coerce = False

class EnrichedSchema(CleanedSchema):
    producer_name: str | None = pa.Field(nullable=True)
    macro_region: str = pa.Field(nullable=False)
    price_segment: str = pa.Field(isin=["Entry", "Accessible Premium", "Premium", "Prestige"])
    confidence_segment: str = pa.Field(isin=["Low Confidence", "Emerging Signal", "Reliable Signal", "Strong Market Signal"])
    enrichment_confidence: str = pa.Field(isin=["High", "Medium", "Low", "None"])
    inferred_grape_or_style: str | None = pa.Field(nullable=True)

class ScoredWineSchema(EnrichedSchema):
    weighted_rating: float = pa.Field(ge=0, le=5)
    value_score: float = pa.Field(gt=0)
    composite_score: float = pa.Field(ge=0, le=1)
    market_segment: str = pa.Field(isin=["Premium Icon", "Hidden Gem", "Commercial Value", "Low Confidence Niche", "Overpriced Risk"])
```

Used twice: in production validation (fail-loud) and in `tests/schemas/`.

### 7.4 Hypothesis property tests

Bayesian properties (`test_bayesian_properties.py`):

```python
@given(rating=st.floats(0, 5), rating_count=st.integers(1, 100_000),
       m=st.integers(1, 10_000), global_mean=st.floats(3.0, 4.5))
def test_weighted_rating_is_convex_combination(rating, rating_count, m, global_mean):
    wr = bayesian_weighted_rating(rating, rating_count, m, global_mean)
    lo, hi = min(rating, global_mean), max(rating, global_mean)
    assert lo - 1e-9 <= wr <= hi + 1e-9

@given(...)
def test_high_volume_approaches_rating(...):
    """As rating_count → ∞, weighted_rating → rating."""

@given(...)
def test_high_m_approaches_global_mean(...):
    """As m → ∞, weighted_rating → global_mean."""
```

Value-score properties (`test_scoring_properties.py`):

- Monotone decreasing in price (ceteris paribus).
- Monotone increasing in weighted_rating (ceteris paribus).

### 7.5 Integration tests

- `test_full_pipeline.py` — full pipeline on sample fixture; golden-file comparison. `UPDATE_GOLDENS=1` env var regenerates (rare, conscious schema changes only).
- `test_config_hash_stability.py` — 100× load same config, hash is stable. Catches implicit dict-ordering bugs.
- `test_multirun_isolation.py` — Hydra `--multirun` across 3 weight configs; assert run-dirs separate and outputs differ.

### 7.6 Coverage + mutation testing

- Coverage target: **≥85%** on `src/cantinaiq/` via `pytest-cov`. CI fails below.
- **Mutation testing** (opt-in `make test-mutation`): `mutmut` on `src/cantinaiq/scoring/`. Not in CI (slow). Available for an examiner to run.

### 7.7 CI

```yaml
# .github/workflows/ci.yml
- uv sync --frozen
- uv run ruff check .
- uv run ruff format --check .
- uv run mypy src/
- uv run pytest --cov=src/cantinaiq --cov-report=term --cov-fail-under=85
```

PR coverage delta posted as a comment.

---

## 8. Out of scope (for this sub-project)

| Goes to | Items |
|---|---|
| **C** | Bootstrap/Wilson CIs on rankings; weight sensitivity (Hydra multirun + report); `m` sensitivity; top-N stability analysis; Vivino-NL bias quantification (CBS/Wijninfo/KVNW comparison); clustering as validation of segmentation; pass-1/pass-2 Cohen's kappa. |
| **B** | Crawler extension (year, alcohol %, food pairings, sustainability claims, producer URL); rate-limiting; retry logic; new scrape vs. reuse Excel; persistence as `vivino_extended_<ts>.parquet`. A's ingestion is currently hard-bound to `Upload/Vivino-export.xlsx`; introducing an alternative-source switch is explicitly deferred and would require an additive change to `config/paths/default.yaml` plus `src/cantinaiq/ingestion/`. |
| **D** | Next.js + Tailwind + shadcn/ui + Recharts/Tremor; reads `data/exports/*.json` (A's contract); filtering, drill-down, producer dossiers, print styles, deployment. |
| **E** | Editorial content of methodology / limitations / executive-summary / final-report; literature references; external-validity discussion; `docs/why-this-bar.md`; PDF publication; presentation deck. |

**Never (current scope):**

- Sustainability as a scoring factor (no source data; would create fake precision). Reserved as a `null`-defaulted enriched field for future hook-in.
- Live Vivino data, CDC, real-time updates.
- Producer CRM integration, outreach automation.
- Multi-tenant / multi-importer (config-driven so it *would* mostly work, but not designed for).
- i18n / localisation. Code and docs English; Dutch only in personal notes.
- Auth / secret manager. `.env` via `python-dotenv` for `ANTHROPIC_API_KEY`, in `.gitignore`.

### 8.1 Scope-creep rules

1. If a requirement of A "naturally" leads to C/B/D/E work → stop, flag here, capture in a follow-up spec.
2. If something in §8 turns out to be necessary to ship A → stop, move the boundary explicitly with a rationale, then implement.

---

## 9. Visual deliverables (Claude Design prompts)

Two prompts to use against `claude.ai/design`. Outputs are previews of sub-project D, useful as ADA-facing artefacts well before D is implemented.

### 9.1 Prompt 1 — full dashboard

```
You are designing a professional decision-support dashboard for a real business
case in the premium Italian wine import industry. This is not a marketing site
and not a consumer wine app — it's an internal analytics product used by a wine
importer's commercial team to decide which Italian producers and regions to
prioritise for partnership outreach. The reviewers are HBO/academic
data-science examiners, not consumers; visual restraint and information density
matter more than playfulness.

PRODUCT
Name: CantinaIQ — Slurpini Partner Intelligence Engine
Tagline: "Evidence-based partner selection for Italian wine importers"
Stack target: Next.js 15 + Tailwind + shadcn/ui + Recharts + Tremor
Audience: commercial buyers, partnership managers, and academic examiners

BRAND POSITION
Sober, premium, Italian without cliché. Think the visual register of Linear,
Vercel, or Stripe Dashboard — not Vivino, not a wine subscription app. No grape
illustrations, no wine glass icons, no Tuscan landscape photos. Italian
character comes from typography (a humanist serif for display, a precise
geometric sans for UI) and a restrained palette inspired by terra rossa,
travertine, ink, and aged paper — never from emojis or stock imagery.

PALETTE (target)
- Background: warm off-white #FBF8F3 (paper)
- Surface: pure white with 8% terracotta tint
- Ink primary: #1A1714 (near-black with brown undertone)
- Accent (data positive / Hidden Gem): #6B8E4E (sage/olive)
- Accent (data attention / Overpriced Risk): #9B3A2F (terra rossa, restrained)
- Accent (data premium / Premium Icon): #1F3A5F (ink-blue)
- Neutral data: #8B7355 (umber)
- Gridlines/dividers: warm gray #E8E0D5

TYPOGRAPHY
- Display/H1-H2: GT Sectra, Tiempos, or Source Serif 4 (humanist serif)
- UI body / data: Inter or IBM Plex Sans (geometric, sharp tabular figures)
- Tabular numerals everywhere in tables (so digits align)

PAGES (5)

1. EXECUTIVE OVERVIEW (home)
   - Top: 4 KPI tiles — "Italian wines analysed" (e.g. 8,247), "Regions
     covered" (e.g. 142), "Producers shortlisted" (e.g. 86), "Avg. weighted
     rating" (e.g. 4.12 / 5)
   - Mid-left: bar chart "Top 5 Recommended Regions" by weighted rating
   - Mid-right: horizontal bar "Top 10 Producer Opportunities"
   - Bottom: a single editorial paragraph — "Strategic insight" — written like
     a McKinsey one-pager bullet, not a tweet
   - Footer: "Last pipeline run: 2026-05-15 14:22 · config hash a3f8e1 · 8,247
     wines · methodology"

2. REGION INTELLIGENCE
   - A sortable table: Region | Macro-region | Wines | Avg. weighted rating |
     Avg. price (€) | Value score | Market segment
   - Filters: macro-region multiselect, price segment chips (Entry / Accessible
     Premium / Premium / Prestige), confidence segment chips
   - Right side: a small map of Italy with regions tinted by weighted rating
     (choropleth, no labels on tint legend — just the four segment colours)

3. PRODUCER SHORTLIST
   - Dense ranked table: # | Producer | Region | Wines in dataset | Reviews
     (total) | Weighted rating | Avg. price | Segment | Recommendation
   - Recommendation column shows a pill: Target / Monitor / Premium Brand
     Builder / Value Opportunity / Avoid for Now (each pill colour-coded)
   - Click a row → side panel with the producer's wines, score breakdown
     (component contributions: rating 35%, confidence 20%, value 20%, premium
     fit 15%, opportunity 10%), and an "Open producer dossier" link

4. OPPORTUNITY MATRIX
   - The hero visual: a scatter plot, x = avg. price (€, log scale), y =
     weighted rating, bubble size = total reviews. Four quadrants labelled
     Hidden Gems (low price, high rating), Premium Icons (high price, high
     rating), Budget Risk (low price, low rating), Overpriced Risk (high
     price, low rating). Each bubble is a producer; hover shows producer +
     headline number. Sustainability-flagged producers (future enrichment)
     have a thin sage outline.
   - Sidebar: explanatory legend, plus three "Spotlight" cards picked from the
     Hidden Gems quadrant.

5. METHODOLOGY
   - Editorial layout, narrow column, serif body.
   - Sections: Research question · Dataset · Cleaning cascade (with row-count
     waterfall chart showing 47,291 → 8,247) · Validation rules · Bayesian
     weighted rating (with the formula rendered in LaTeX) · Scoring weights
     (table) · Segmentation logic · Limitations · Reproducibility (config
     hash, run timestamp).

DATA REALISM (use these names so it looks credible)
- Regions: Toscana, Piemonte, Veneto, Sicilia, Puglia, Campania, Friuli-Venezia
  Giulia, Lombardia, Trentino-Alto Adige
- Producers: Marchesi Antinori, Tenuta San Guido, Gaja, Biondi-Santi, Fontodi,
  Castello di Ama, Allegrini, Planeta, Mastroberardino, Vietti, Bruno Giacosa,
  Frescobaldi, Argiolas, COS
- Sample appellations: Brunello di Montalcino, Chianti Classico Gran Selezione,
  Barolo, Barbaresco, Amarone della Valpolicella, Etna Rosso, Bolgheri
  Superiore, Taurasi
- Plausible price ranges: €18 – €280
- Plausible weighted ratings: 3.7 – 4.6

INTERACTION DETAILS
- Density default: comfortable, with a "compact" toggle in the top bar.
- Empty states: an editorial sentence, no illustrations.
- Loading states: skeleton blocks matching the final layout, no spinners.
- Dark mode: the same warm paper palette, inverted intelligently (not pure
  black — use #1A1714 on #FBF8F3, and #FBF8F3 on #1A1714).
- All charts have a methodology footnote (small italic serif) — "Weighted
  rating via Bayesian shrinkage, m = ___" — so a reviewer never has to ask
  what they're looking at.

DO NOT
- Do not add stock photography or hero images.
- Do not put wine glass / grape / map-pin icons in the chrome.
- Do not use rounded-3xl playful corners — keep radii subtle (≤8px).
- Do not put marketing copy ("the smartest way to..."). Every word is
  data-product copy.

OUTPUT
Five fully-designed page screens, plus a component-system page showing
typography, palette, button/pill states, table styles, and chart styles.
```

### 9.2 Prompt 2 — executive one-pager

```
Design a single-page executive infographic titled "CantinaIQ — Slurpini Partner
Intelligence Engine: Findings & Recommendations". A4 portrait. Same brand
register as the dashboard above (sober, premium Italian, Linear/Vercel
aesthetic, humanist serif display + geometric sans body, terra rossa / sage /
ink-blue accents on warm paper).

The page must communicate, top-to-bottom:
1. One-sentence problem statement (Slurpini's partner selection challenge).
2. Approach in three steps — pictograms or numbered tiles: "Clean & validate
   8,247 Italian wines" / "Score with Bayesian-shrunk rating + 5-factor
   composite" / "Segment producers into 5 opportunity classes".
3. The opportunity matrix (small but legible) as the centrepiece visual.
4. A horizontal "top 5 producer recommendations" strip with: producer name,
   region, recommendation pill, weighted rating, headline reason in ≤12 words.
5. Bottom: limitations (three short bullets) and methodology footer (formula,
   config hash, run date).

The page must be printable, defendable in a board room, and survive a 30-second
read. No stock imagery, no clichés, no decorative wine references.
```

---

## 10. Open questions

None blocking. Things to revisit during implementation:

- Exact alias-whitelist seed (~200 entries) — first 50 hand-curated from real `wine_name` top-frequencies in the dataset; iterate after pass-1 coverage measurement.
- Exact macro-region lookup table — start from PRD §12.4 examples, expand as `region` values surface in cleaning.
- Whether `min_reviews_floor` (the optional drop in scoring) is on by default — current intent: off; flagged as configurable in `scoring/default.yaml`.

---

## 11. Acceptance criteria

A is considered "done" when:

1. `uv run cantinaiq run all` on a clean checkout produces `data/exports/*.json` and `reports/generated/{data-quality,methodology}.md` deterministically.
2. `uv run pytest` passes with ≥85% coverage on `src/cantinaiq/`.
3. The drop-cascade table in `data-quality.md` is generated 100% from `RunBundle` (no hand-typed numbers).
4. `cantinaiq audit <hash>` returns a non-empty audit for at least one prior run.
5. Pandera schemas pass on every committed-shape Parquet output (`02_cleaned`, `03_validated`, `italian_wines_enriched`, `wines_scored`, `producers_scored`, `regions_scored`). Schemas for the producer/region aggregates are defined as subclasses or separate models — not yet enumerated in §7.3; finalise during implementation.
6. The hand-curated `known_producers_top50.csv` overlap warning fires correctly on a deliberately-broken LLM-cache fixture (i.e., the alarm works).
7. A reviewer running `git log` sees that the design doc, all source files, the lockfile, and at least one `config/snapshots/<hash>.yaml` are committed.

---

## 12. Hand-off

After user review and approval of this spec, the next step is to invoke `superpowers:writing-plans` to produce an implementation plan that decomposes A into independently-executable tasks (likely organised by stage, with the runlog/reporting/config infrastructure as an early foundation).
