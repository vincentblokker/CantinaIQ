# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Status

This is a **spec-driven, pre-implementation** project. The repo currently contains only:

- `README.md` — full product description and recommended structure
- `PRD.md` — detailed product requirements, scoring model, and pipeline spec
- `Upload/Vivino-export.xlsx` — raw input dataset (4.1 MB Excel, multi-sheet, Dutch Vivino crawler output)
- `Upload/Pyton-script.docx` — reference for how the data was originally scraped (reference only, not the project focus)

There is **no source code, no pipeline, no dashboard, and no dependency manifest yet**. When asked to "build" or "run" something, treat the README and PRD as the design document and scaffold from there. Do not invent additional commands or files that the spec does not call for.

## Project Domain

**CantinaIQ / Slurpini Partner Intelligence Engine** — turns a raw Vivino export into a cleaned, scored, segmented dataset that helps Slurpini (a Dutch importer of Italian wines) prioritise Italian producers and regions for partnership outreach.

The dataset is treated as a **consumer-preference signal**, not as a measure of objective wine quality. This framing matters: low-review wines with high ratings must not be ranked above high-review wines with slightly lower ratings.

## Architecture (target, per spec)

The pipeline is a linear, reproducible flow. Each stage reads from the previous stage's output:

```
Excel (Upload/Vivino-export.xlsx)
  → ingestion       (combine sheets, raw dataframe)
  → cleaning        (normalise country/region, numeric coercion, dedupe, filter to Italian)
  → validation      (Pandera/Great Expectations rules — see PRD §10)
  → enrichment      (producer_name, macro_region, price_segment, confidence_segment,
                     market_segment, inferred_grape_or_style, enrichment_confidence)
  → scoring         (Slurpini Partner Intelligence Score — 5 weighted components)
  → export          (parquet + JSON for dashboard)
  → Next.js dashboard (5 pages: Executive, Region, Producer, Opportunity Matrix, Methodology)
```

Target tech stack from the spec: **Polars + DuckDB + Parquet** for data, **Pandera/Great Expectations** for validation, **Next.js + Tailwind + shadcn/ui + Recharts/Tremor** for the dashboard. Pandas is acceptable as a simpler fallback but the spec prefers Polars.

Target directory layout (from README §6 / PRD §20) — create these under the repo root when scaffolding:

```
data/{raw,interim,processed,exports}/
src/{ingestion,cleaning,validation,enrichment,scoring,export}/
notebooks/   dashboard/   reports/   docs/
```

The raw input lives in `Upload/` today; either move it to `data/raw/` or have the ingestion layer read from `Upload/` directly. Confirm with the user before moving the source file.

## Critical Domain Rules (do not violate)

These rules come from PRD §10, §12.4, §13 and are easy to get wrong:

1. **Bayesian weighted rating, not raw average.** A 4.8/12-reviews wine must not outrank a 4.4/5000-reviews wine. Use `(n/(n+m))·rating + (m/(n+m))·global_mean`, where `m` is a minimum-review threshold tuned to the cleaned Italian dataset.
2. **Filter to Italian wines only** for the main recommendation model. The dataset has mixed-country contamination across sheets.
3. **Producer extraction is heuristic.** Mark with `enrichment_confidence` (High/Medium/Low). Never present inferred fields as ground truth.
4. **Sustainability is not in the data.** Do not use it as a scoring factor. It is a future-enhancement field only.
5. **Scoring weights are business assumptions** (35/20/20/15/10 in PRD §13) and must remain adjustable — don't hard-code them deep in calculation logic.
6. **Confidence segmentation thresholds** (PRD §12.4): <50 / 50–250 / 250–1,000 / >1,000 reviews → Low / Emerging / Reliable / Strong Market Signal.

## Commands

No build/test/lint commands exist yet. When the pipeline is built, the spec proposes (README §16) — these are placeholders to validate with the user before committing to them:

```bash
# Python pipeline (proposed)
uv sync                                          # or: pip install -r requirements.txt
python -m src.ingestion.load_data
python -m src.cleaning.clean_data
python -m src.validation.validate_data
python -m src.enrichment.enrich_data
python -m src.scoring.score_wines
python -m src.export.export_dashboard_data

# Dashboard (proposed)
cd dashboard && npm install && npm run dev
```

When asked to "run the pipeline" before any code exists, surface that nothing is implemented yet and propose the first stage to scaffold.

## Working With the Raw Data

Known quality issues already catalogued in PRD §10 — expect and handle them upfront rather than discovering them mid-pipeline:

- Tuple-like string values from the crawler (e.g. `"('Italy',)"`)
- Encoding issues in country names
- Mixed-country data across sheets (sheet name is not a reliable country filter)
- Region names mixing macro-regions, appellations, and local areas
- Missing/zero prices and ratings
- Duplicate wine records

The dataset is ~4 MB Excel. Read it once into Parquet under `data/interim/` and work from Parquet downstream — re-reading the xlsx on every stage is slow and unnecessary.
