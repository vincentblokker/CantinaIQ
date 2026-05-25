# 01 — Introduction

**Page**: 2
**Tag (red, spaced caps)**: A brief on CantinaIQ in practice
**Title**: Introduction.

---

## Body

> The Slurpini case asks three things: extend the Vivino crawler, perform exploratory analysis, deliver an evidence-based recommendation. That is the brief. This document evaluates what changes when those three deliverables are answered as a reproducible data product instead of a one-off analysis.

I answered the brief twice. The first track, **/bare**, is the assignment in roughly 150 lines of code: one pandas notebook, a first-word producer heuristic, a half-page recommendation. It runs in thirty seconds and meets the brief honestly, including listing its own limitations.

The second track, **/supercharged**, treats the same business question as a data product. Polars and DuckDB for processing, Pandera schema contracts at every stage boundary, a five-factor Bayesian composite score, an OpenRouter-driven LLM disambiguation pass for producer names, property-based tests on the scoring math, Jinja-templated reports whose numbers come from a config-hashed run log, a Vite dashboard, and external-validity work that quantifies Vivino bias against Italian Trade Agency NL imports.

This document is not a summary of either track. It is an evaluation of when a heavyweight architecture earns its place against the next-best alternative — usually a notebook — and where the line between rigour and over-engineering actually sits for a final assignment. The course material understandably assumes you will pick one. The brief asks for one. The interesting professional question is which one, and why.

## Contents

| # | Section | Page |
|---|---|---:|
| 01 | Introduction | 02 |
| 02 | Vivino in Context | 03 |
| 03 | From the Field: the Slurpini Case | 06 |
| 04 | The Choice: When the Heavyweight Earns Its Place | 09 |
| 05 | Closing Observation | 11 |
| 06 | About the Author | 12 |

---

## Editor notes

- The opening blockquote is a load-bearing pull. Don't rewrite it without a reason.
- The "I answered the brief twice" sentence does heavy work. Keep it.
- The fourth paragraph contains the document's thesis. The last sentence ("The interesting professional question is which one, and why.") is the cliff-hanger that earns Section 02 — keep that rhythm.
