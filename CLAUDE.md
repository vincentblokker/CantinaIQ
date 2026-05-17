# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Status

This repo holds **two parallel deliverables** for the ADA Applied AI Bootcamp Final Assignment (the Slurpini wine case). The split is deliberate — see the root `README.md` for the framing. Do not collapse them into one.

```
bare/             ← minimum-viable answer to ADA's brief.
                    Complete and runnable. One pandas notebook + crawler-extension
                    script + half-page recommendation. ~150 LOC total. Outputs
                    baked into the .ipynb.

supercharged/     ← HBO/academic-grade answer to the same business question.
                    Fully specified (design + plan), implementation pending.
                    Polars + DuckDB + Pandera + Pydantic-validated Hydra configs +
                    Hypothesis property tests + instrumented run-logging +
                    Jinja2-templated reports + Next.js dashboard (planned).
                    See supercharged/docs/superpowers/ for spec + plan.

data/             ← does NOT exist at repo root. Each track owns its own
                    bare/data/raw/ and supercharged/data/raw/ so each is
                    independently runnable.
```

## Audience and framing

The supercharged track exists to demonstrate that the ADA bootcamp's bar sits below HBO/academic level. The artefact's quality is the argument; do not editorialise about ADA inside the code or docs. Let the work speak.

The bare track exists to defuse the "you didn't do the assignment" counter-argument. It must remain *minimum-viable* — do not over-engineer it. If you find yourself adding sensitivity analysis or schema contracts to `/bare/`, stop: that work belongs in `/supercharged/`.

The contrast between the two is the value proposition. Maintain it.

## Working in `/bare/`

- Single source of truth: `bare/notebooks/slurpini-analysis.ipynb`.
- Stack: pandas + matplotlib + openpyxl. No Polars, no Pydantic, no Hydra.
- Producer extraction: first-word heuristic (deliberately imperfect; the imperfection is the contrast point).
- Re-run via `cd bare && jupyter notebook notebooks/slurpini-analysis.ipynb` and run all cells, or:
  `python crawler-extension.py` for the extension script alone.
- The data lives at `bare/data/raw/Vivino-export.xlsx`. Notebook paths are relative (`../data/raw/...`).
- Headline numbers from the real data:
  - 409,758 raw rows across 16 sheets
  - 5,786 unique Italian wines after dedupe + validation
  - 179 distinct regions, 564 producer fragments (first-word heuristic)

## Working in `/supercharged/`

- Pre-implementation. The full design is in `supercharged/docs/superpowers/specs/2026-05-15-cantinaiq-data-pipeline-design.md`. The implementation plan with bite-sized TDD tasks is in `supercharged/docs/superpowers/plans/2026-05-15-cantinaiq-data-pipeline.md`.
- Read those two files before touching anything under `supercharged/`. Do not invent new structure or commands not in the spec.
- Target stack: Polars 1.x · DuckDB 1.x · Pandera 0.20+ · Hydra 1.3+ · Pydantic 2.x · Typer · Jinja2 · Matplotlib · uv · Ruff · mypy · Pytest + Hypothesis.
- Architecture principle (do not violate): every stage is a pure function of `(input parquet, config) → (output parquet, run-log JSON)`. No hidden state, no side-effects outside `data/`.
- Data lives at `supercharged/data/raw/Vivino-export.xlsx`. When the pipeline is built, intermediate parquets land in `supercharged/data/{interim,processed,exports}/` and run-logs in `supercharged/data/runs/<run-id>/`.

## Critical domain rules (apply across both tracks)

1. **Bayesian weighted rating, not raw average.** A 4.8/12-reviews wine must not outrank a 4.4/5000-reviews wine. Both tracks use `(n/(n+m))·rating + (m/(n+m))·global_mean` with `m` derived from the data (bare uses median, supercharged makes it configurable with explicit `m_strategy`).
2. **Filter to Italian wines on the cleaned `country` field, not on sheet name.** The Excel sheet split is noise: every sheet contains wines from many countries.
3. **Mojibake on diacritics is Mac-Roman ↔ UTF-8.** `Itali√´` → `Italië` via `s.encode('mac_roman').decode('utf-8')`. Latin-1 will NOT work.
4. **Tuple-encoded strings** in country/region: `"('Italië',)"` → unwrap via regex `^\(\s*'([^']*)'\s*,\s*\)$`.
5. **Producer extraction is heuristic.** In bare: first-word. In supercharged: alias whitelist + LLM disambiguation. Never present inferred fields as ground truth.
6. **Sustainability is not in the dataset.** Do not use it as a scoring factor in either track.

## Data shape, post-cleaning

After the (track-specific) cleaning steps both tracks converge on ~5,786 rows with columns:

| Column | Type | Notes |
|---|---|---|
| `name` | str | Original wine name, includes vintage suffix |
| `country` | str | `Italië` after mojibake fix |
| `region` | str | Mix of macro-region, appellation, and sub-region |
| `rating` | float | 0.0 – 5.0 |
| `rating_count` | int | ≥ 1 after validation |
| `price` | float | EUR, > 0 after validation |
| `source_sheet` | str | Metadata only — not a country filter |

Supercharged track adds `wine_name_normalised`, `vintage`, `producer_hint`, `producer_name` (post-extraction), `macro_region`, `price_segment`, `confidence_segment`, `enrichment_confidence`, `inferred_grape_or_style`, then `weighted_rating`, `value_score`, `composite_score`, `market_segment`, `run_config_hash`.

## Commands

`/bare`:
```bash
cd bare
pip install -r requirements.txt
jupyter notebook notebooks/slurpini-analysis.ipynb       # interactive
python crawler-extension.py                              # standalone
```

`/supercharged` (planned — pipeline not yet implemented):
```bash
cd supercharged
uv sync
uv run cantinaiq run all                                 # full pipeline
uv run cantinaiq report build                            # render reports
uv run pytest --cov-fail-under=85
```

When asked to "run the supercharged pipeline" before its code is implemented, point at the plan and propose the first phase to scaffold.
