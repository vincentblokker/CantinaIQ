# CantinaIQ

Two deliverables for the ADA Applied AI Bootcamp Final Assignment — the **Slurpini wine case**.

```
/bare           ← the assignment as briefed: one notebook, pandas, EDA, recommendation
/supercharged   ← a Partner Intelligence Engine: Polars + DuckDB pipeline,
                  Bayesian-shrunk composite scoring, Pandera contracts,
                  Hypothesis property tests, instrumented run-logging,
                  Jinja2-templated methodology + findings one-pager,
                  Next.js dashboard (planned in /supercharged/docs)
```

The brief was answered twice on purpose. The delta between the two is the argument.

## Why two tracks

ADA's final assignment asks for **(i)** a Vivino crawler extension, **(ii)** EDA on the export, and **(iii)** a written recommendation for Slurpini. That's the minimum interpretation and `/bare/` delivers it in ~30 seconds of notebook run-time.

The same business problem — *which Italian producers should Slurpini prioritise, with what confidence, at what price band, with what defensible methodology?* — is a much larger question if treated at HBO/academic level. `/supercharged/` answers it as a reproducible data-product with explicit research question, transparent scoring assumptions, schema contracts at every stage boundary, property-based tests on the scoring math, deterministic run logs, and configurable sensitivity analysis.

Both tracks use the same input data (`data/raw/Vivino-export.xlsx`, kept in each track's own `data/raw/` so each can run standalone). Both produce a producer ranking, a regional ranking, and a written recommendation. They differ in how much of the reasoning is *visible* and *testable*.

## The contrast

| | `bare/` | `supercharged/` |
|---|---|---|
| **Lines of code** | ~150 (one notebook + one script) | ~3,000+ (planned, full spec written) |
| **Producer extraction** | First-word heuristic ("Tenuta San Guido" → "Tenuta") | Alias whitelist + LLM disambiguation with persistent cache + post-hoc validation against known top-50 |
| **Rating aggregation** | Bayesian shrinkage to global mean | Same, but with `m`-strategy logged + configurable + sensitivity-tested |
| **Scoring** | Single weighted rating | 5-factor composite (rating · confidence · value · premium fit · opportunity), weights versioned per config snapshot |
| **Data quality** | Inline `print()` of drop cascade | Instrumented `RunBundle` JSON per stage, drop-cascade rendered via Jinja2 from real run data |
| **Validation** | `if rating > 5: drop` | Pandera schema contract, fail-loud, failures captured to `validation-failures.parquet` |
| **Testing** | None | Pytest + Hypothesis properties on the Bayesian math, Pandera schema tests, integration tests |
| **Reproducibility** | "Run all cells" | Deterministic CLI, every output stamped with `run_config_hash`, snapshot configs versioned, `cantinaiq audit <hash>` cross-references outputs to commits |
| **Reporting** | One markdown file written by hand | Jinja2 templates rendered from run-log; numbers in the methodology document cannot drift from the code |
| **Dashboard** | None | Next.js + Tailwind + shadcn/ui (designed in `/supercharged/reports/findings-one-pager.html`, planned in `/supercharged/docs/superpowers/specs/`) |
| **Limitations discussion** | 4 bullets | Bias quantification, external-validity discussion, sensitivity sweeps on scoring weights, top-N stability analysis |

Both arrive at recommendations of comparable directional shape (Bolgheri Sassicaia / Brunello / Amarone Classico at the top by weighted rating; Primitivo di Manduria, Abruzzo and Lugana as value plays). The difference is **how defensibly** that recommendation is reached.

## Pick a path

- **You only have 5 minutes:** read [`bare/recommendation.md`](bare/recommendation.md).
- **You want to see the analysis:** open [`bare/notebooks/slurpini-analysis.ipynb`](bare/notebooks/slurpini-analysis.ipynb) (outputs baked in, no need to run).
- **You want to see what HBO-level looks like:** read [`supercharged/docs/superpowers/specs/2026-05-15-cantinaiq-data-pipeline-design.md`](supercharged/docs/superpowers/specs/2026-05-15-cantinaiq-data-pipeline-design.md) and the implementation plan in [`supercharged/docs/superpowers/plans/`](supercharged/docs/superpowers/plans/).
- **You want to see the executive one-pager mock:** open [`supercharged/reports/findings-one-pager.html`](supercharged/reports/findings-one-pager.html) in a browser.

## Status

- `bare/` — **complete and runnable.** Notebook produces outputs end-to-end; recommendation written; crawler extension demonstrated.
- `supercharged/` — **fully specified, plan written, implementation pending.** Every stage of the planned pipeline has a TDD task list in `/supercharged/docs/superpowers/plans/`. Reference designs from Claude Design committed in `/supercharged/reports/`.

## Author

Vincent Blokker · vincentblokker@gmail.com
