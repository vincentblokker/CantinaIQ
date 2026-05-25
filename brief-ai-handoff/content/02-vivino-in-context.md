# 02 — Vivino in Context

**Pages**: 3–5
**Tag (red, spaced caps)**: Section 02
**Title**: Vivino / in Context.
**Subtitle (spaced caps)**: What the dataset is and how it skews

Page 4 carries the section image (`02-vivino-context.jpg`, full-bleed, ~70mm tall) and the three-stat callout at the bottom: 2,986 wines · 762 producers · 96 % recall.

Page 5 carries a second blockquote and a second three-stat row: 5 factors · 3 baselines · 137 tests.

---

## Page 3 — body

Vivino is presented as a global consumer wine signal. In practice, it is a collection of ratings with a particular demographic and regional bias, a long tail of low-confidence rows, and a producer field that does not exist as such — only wine names from which producer identity has to be inferred.

That distinction matters. A team should not ask only whether Vivino can answer the question "which Italian producers should Slurpini prioritise?" Vivino can produce a ranking. The better question is whether the ranking it produces resembles the Dutch wine market in the way Slurpini cares about, and whether the analysis surfaces that gap or papers over it.

**Pull-quote**: The right question is not *"can this data answer the question?"* The right question is what the data gives us that the next-best evidence does not.

### What Vivino is good at

Vivino captures large-volume consumer preference at scale. For wines with thousands of reviews — Tenuta Masseto with 4,641, Ornellaia with 581,167, Antinori's Tignanello vintages — the rating is a stable, repeatable proxy for how Dutch consumers actually perceive the bottle. The Bayesian-shrunk weighted rating is the standard tool for this signal: as `n` grows the observed rating dominates, as `n` shrinks the global mean does. The math is uncontroversial.

### What Vivino is not

Vivino under-represents the Dutch wine market in two systematic ways. Its user base is Anglocentric and younger. Natural-wine and biodynamic producers are systematically under-counted. Producer names are not a field — they are a string-extraction problem. The pipeline addresses each of those explicitly. A pass-1 alias whitelist resolves the top fifty Italian producers; a pass-2 LLM disambiguation pass on OpenRouter handles the remainder, with a persistent cache so the same dataset never costs twice. A gold-set evaluation against `known_producers_top50.csv` measures the result: **88 % recall on exact match, 96 % on contains**. Schiopetto and Felsina are the only two misses.

---

## Page 4 — body (after the image)

### The bias question, quantified

The most important external-validity check in the supercharged track is the bias report. It compares the regional distribution of the cleaned Italian Vivino dataset against the regional shares of Italian wine imports into the Netherlands, drawn from ICE Amsterdam (Italian Trade Agency) annual reports.

The result is honest and uncomfortable. Toscana is over-represented in Vivino by a factor of 1.22. Puglia, by contrast, is under-represented by a factor of 0.61. Abruzzo sits at 0.52 and Campania at 0.55. These are not errors. They are the shape of Vivino's user base bleeding through into the dataset Slurpini would use to decide travel priorities.

Three things follow. First, any recommendation involving Puglia or Abruzzo — both regions where the analysis identifies high-value opportunities — should be marked as *under-sampled*, not low-priority. Second, anyone reading the executive summary should see the bias factor next to the recommendation, not buried in an appendix. Third, the Vivino signal is most reliable in regions Slurpini already knows well, which is the opposite of where it most needs help.

The bare track lists this limitation in four bullets at the end of the recommendation. The supercharged track produces an external CSV (`italian_trade_imports_nl.csv`) and a generated `bias-report.md` table that is regenerated on every run. The point is not to fix the bias. The point is that it should be measured, not hand-waved.

### Stat callout (3 columns)

| Number | Label |
|---|---|
| 2,986 | Italian wines after cleaning |
| 762 | Distinct producers after disambiguation |
| 96 % | Recall on known top-50 producers |

---

## Page 5 — body

### How robust is the top-20?

A ranking is only as defensible as its sensitivity to noise. The supercharged track answers this with a bootstrap of the wine dataset: a thousand resamples with replacement, the producer ranking recomputed in each, the rank of each top-twenty producer recorded across runs. The result is a confidence interval per producer.

Tenuta Masseto appears in the top-ten in **195 out of 200 resamples** in the published run. Dal Forno Romano: 185 out of 200. Biondi-Santi: 160 out of 200. Two producers — Terre di San Vincenzo and Valdicava — appear with extreme p95 ranks (412 and 228 respectively), which means they made the top-ten by accident with too few reviews. That detail does not exist in the bare track. The bare track simply lists them at face value.

The same question applied to the scoring parameter `bayesian_m` gives a sensitivity sweep. At `m` = 200 the top-twenty agrees with itself perfectly. At `m` = 500 the Kendall-τ similarity drops to 0.882. At `m` = 800 it drops to 0.765. The top is stable for the highest-volume producers; the further down the list, the more arbitrary the choice of shrinkage threshold becomes. That, too, is a finding, not a bug.

**Blockquote**: A producer ranking that does not declare its own stability is not a recommendation. It is a guess presented with confidence.

### Stat callout (3 columns)

| Number | Label |
|---|---|
| 5 | Composite-score factors per producer |
| 3 | External baselines used in evaluation |
| 137 | Tests passing before any submission |

---

## Editor notes

- The "Toscana ×1.22, Puglia ×0.61" set of numbers is the document's strongest external-validity moment. Don't soften it.
- The "Tenuta Masseto 195/200" stat is the single most memorable line in the brief. If it gets cut, replace with another equally specific bootstrap number — not a generalisation.
- The two blockquotes (one pull, one indented) carry the analytic argument. Both must stay.
