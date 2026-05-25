# 04 — The Choice

**Pages**: 9–10
**Tag**: Section 04
**Title**: The Choice.
**Subtitle**: When the heavyweight earns its place and when it does not

Page 9 carries the section image (`04-the-choice.jpg`, non-bleed, ~62mm tall) and the two-by-two "when right" grid, then the numbered "when wrong" breakdown.

Page 10 carries the deeper-question pivot and the closing pull-quote.

---

## Page 9 — body

### When the heavyweight is the right choice

**Decisions that will be revisited**
If the analysis will be run again — quarterly, annually, on updated data — the cost of reproducibility amortises. Config-hash snapshots mean the seventh run agrees with the first or documents the delta.

**Recommendations that move money**
If a buying committee will travel to Italy on the basis of the ranking, the ranking should declare its own confidence. Bootstrap CIs and bias quantification are the difference between defensible and a guess.

**Audiences that interrogate methodology**
Notebooks do not survive sceptical questioning. A reproducible pipeline does. Every number traces to a parquet, every parquet to a config hash, every hash to a snapshot in version control.

**Datasets with non-trivial bias**
If the data has a known skew — Vivino's Anglo-young demographic — the analysis should measure that skew, not assume it cancels out. The bias report is load-bearing for external validity.

### When the heavyweight is the wrong choice

| # / Label | Heading + body |
|---|---|
| **01 / Small questions** | "What's the average rating of wines under €15?" — A one-line pandas query. Building a Polars + DuckDB pipeline for it is theatre, not engineering. The bare track is the right scale. |
| **02 / One-off analyses** | Discovery work that will not be run again — If the result will be screenshot, pasted into a slide and never revisited, reproducibility infrastructure is wasted effort. The cost of building it does not amortise against zero re-runs. |
| **03 / Pre-decided recommendations** | Analyses that are decorative, not decision-supporting — If the recommendation is already made and the analysis is rationalisation, reproducibility makes the rationalisation slightly more defensible without changing the underlying problem. The honest move is to stop producing the analysis. |

---

## Page 10 — body

### The deeper question

Most final assignments do not need a reproducible data product. The course brief asks for a notebook and a recommendation, and a notebook and a recommendation is a complete answer. The bare track is the right scale for the assignment in scope.

The supercharged track was built because the same business question — partner selection at a Dutch wine importer — looks materially different when treated as a problem that will be solved more than once. The bias question becomes load-bearing. The bootstrap CIs become the difference between confidence and false confidence. The methodology document becomes the artefact, not the rating.

That is not because the supercharged track is "better" in some absolute sense. It is because the question changed shape. The right tool for the brief-as-stated is the bare track. The right tool for the brief-as-it-would-be-asked-in-industry is the supercharged track. Both are valid. The professional skill is recognising which question is actually being asked.

**Pull-quote**: The better question is not *"is more rigour better?"* The better question is whether the additional rigour produces a different decision.

For Slurpini, the additional rigour does produce different decisions. The bare track lists "Tenuta", "Marchesi" and "Castello" as top producer fragments — uninterpretable for a buying committee. The supercharged track lists "Tenuta San Guido", "Marchesi Antinori", "Castello di Ama" — directly actionable. The bare track recommends "Expand in Puglia" without flagging that Vivino under-represents Puglia. The supercharged track flags the under-representation factor (×0.61) next to the recommendation, which changes how the committee should interpret it.

Those are not stylistic improvements. They are decisions changing.

---

## Editor notes

- The "right choice / wrong choice" symmetric pair mirrors the equivalent section in Vincent's Azure brief. Keep the bracket: positive list first, then negative list.
- The closing line "Those are not stylistic improvements. They are decisions changing." is the section's strongest closer. Don't dilute it with additional sentences after.
- The numbered "01 / SMALL / QUESTIONS" labels wrap to two lines in the rendered layout. That's deliberate; the spaced-caps treatment looks right at that wrap.
