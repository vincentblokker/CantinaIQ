# 03 — From the Field

**Pages**: 6–8
**Tag**: Section 03
**Title**: From / the Field.
**Subtitle**: Use case: Slurpini partner intelligence

Page 7 carries the section image (`03-from-the-field.jpg`, full-bleed).
Page 8 carries the comparison table and the closing three-stat callout: 14 CLIs · 10 reports · 1 dashboard.

---

## Page 6 — body

Slurpini is a Dutch importer of high-quality Italian wines with an explicit sustainability focus. The company receives more collaboration requests from Italian producers than it can investigate. Each on-site visit costs travel, time and managerial attention. The brief is to add a structured, data-driven layer to that prioritisation problem.

This is a realistic business problem, not a textbook exercise. The challenge is not whether the data can produce a ranking — it can — but whether the ranking will hold up to the constraints of the actual decision: limited budget, sensitive about brand fit, sceptical of black-box scoring, and unforgiving when an importer flies to a region only to discover the data was misleading.

### The problem in scope

The technical pipeline is known. Clean and validate the Vivino export (mojibake, tuple-encoded country fields, cross-sheet dedupe). Extract producer identity from wine names — heuristic in the bare track, alias + LLM in the supercharged track. Aggregate per producer with Bayesian shrinkage on review counts. Apply a multi-factor composite score that captures more than just rating. Classify into actionable segments (Hidden Gem, Premium Icon, Commercial Value, Overpriced Risk, Low Confidence Niche) and recommendations (Target, Premium Brand Builder, Value Opportunity, Monitor, Avoid for Now). Quantify bias, declare confidence intervals, surface limitations.

None of these steps require new research. Combining them into a reproducible, defensible pipeline that the buying committee can interrogate is the actual engineering.

---

## Page 7 — body (after the image)

### The bare route

The bare track is the brief, literally. One Jupyter notebook reads the Vivino export, fixes the obvious data issues, applies a first-word producer heuristic, computes a Bayesian-shrunk weighted rating, ranks the top regions and producer fragments, exports three CSVs and writes a half-page recommendation. The notebook outputs are baked in. The reviewer can read the recommendation in five minutes without running anything. The limitations are surfaced in the same document. "Tenuta San Guido" becomes "Tenuta". Producer extraction is wrong on purpose. The recommendation still arrives at directionally correct findings because the high-volume signal is robust enough that even a crude pipeline can extract it.

### The supercharged route

The supercharged track answers the same business question as a data product. Polars and DuckDB instead of pandas. Pandera schema contracts at every stage boundary. Hydra-validated Pydantic configs with config-hash snapshots. A two-pass producer disambiguator with persistent LLM cache. Property-based tests on the scoring math via Hypothesis. Jinja-templated reports whose numbers come from a run log, not from the author. A Vite + React + Recharts dashboard. Fourteen CLI subcommands for operations, comparison, sensitivity sweeps, bootstrap CIs, clustering, bias quantification, anomaly detection, and Firecrawl-driven sustainability lookup.

---

## Page 8 — body

### Comparison

| Area | /bare route | /supercharged route |
|---|---|---|
| Lines of code | ~150, single notebook | ~3,500, layered package |
| Producer extraction | First-word heuristic, ~30 % wrong | Alias + LLM disambiguation, 96 % recall |
| Confidence intervals | None | Bootstrap CIs on top-20 ranking |
| External validity | Four-bullet caveat | Quantified bias vs ICE NL baseline |
| Reproducibility | "Run all cells" | Config-hash stamped; `cantinaiq audit <hash>` |
| Reporting | One markdown file | Eight Jinja-templated artefacts + dashboard |
| Time to first read | 5 minutes | 30 minutes |
| Defensibility under questioning | Limited | Every number traces to a run log |

### Why both, not one

The temptation is to delete the bare track once the supercharged track is finished. The temptation should be resisted. The bare track is the assignment compliance document. It demonstrates that the brief was answered as briefed, with the limitations the brief is meant to surface. The first-word producer heuristic is deliberately wrong — and the supercharged track exists in part to demonstrate exactly why it is wrong.

The supercharged track is the professional document. It is the version of the analysis I would defend to a buying committee that intends to spend money. The numbers come from a config-hash-stamped run log, traceable end-to-end. The bias is measured and printed at the top of the report, not hand-waved away in a paragraph.

**Blockquote**: The delta between the two tracks is the argument. Removing either one removes the argument.

### Stat callout

| Number | Label |
|---|---|
| 14 | CLI subcommands in the pipeline |
| 10 | Generated reports per run |
| 1 | Dashboard SPA over the same exports |

---

## Editor notes

- The comparison table is the centrepiece of this section. Don't add columns. Don't remove rows.
- The "The temptation is to delete the bare track" sentence is doing a lot of work — it explains why the project ships *both* tracks. Keep it.
- The blockquote *"The delta between the two tracks is the argument"* is the document's two-line synopsis. Don't move it earlier; let it land where it does.
