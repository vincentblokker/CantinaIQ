# AI Handoff Brief — improve this document

**For the receiving AI.** Read this file first. It contains everything you need to pick up the *CantinaIQ in Practice — Strategy Brief* and improve it without ever opening the source repository.

---

## 1. What this document is

A 12-page A4 strategy brief written by Vincent Blokker as the final assignment for the Amsterdam Data Academy AI Professional programme. It evaluates the CantinaIQ submission (a Slurpini wine-importer partner-intelligence engine) from the perspective of when a reproducible data product earns its place against a one-notebook analysis.

The brief follows a strict visual template (see [TEMPLATE.md](TEMPLATE.md)) and a specific authorial voice (see [VOICE.md](VOICE.md)) that Vincent uses across all ADA submissions. Both must be preserved.

The current rendered PDF is at [`source/brief.pdf`](source/brief.pdf). The HTML source is at [`source/brief.html`](source/brief.html). The receiving AI can re-render with one command — see §6 below.

---

## 2. Folder map

```text
brief-ai-handoff/
├── HANDOFF.md                    ← you are here
├── VOICE.md                      ← Vincent's authorial voice, with examples
├── TEMPLATE.md                   ← visual identity (colours, type, layout patterns)
├── content/                      ← all six section texts as standalone markdown
│   ├── 01-introduction.md
│   ├── 02-vivino-in-context.md
│   ├── 03-from-the-field.md
│   ├── 04-the-choice.md
│   ├── 05-closing-observation.md
│   └── 06-about-the-author.md
├── images/                       ← all six images currently used in the document
│   ├── 01-cover.jpg
│   ├── 01-cover.prompt.md        ← the Higgsfield prompt used; iterate from here
│   ├── 02-vivino-context.jpg
│   ├── 02-vivino-context.prompt.md
│   ├── 03-from-the-field.jpg
│   ├── 03-from-the-field.prompt.md
│   ├── 04-the-choice.jpg
│   ├── 04-the-choice.prompt.md
│   ├── 05-closing.jpg
│   ├── 05-closing.prompt.md
│   ├── 06-author.jpg
│   └── 06-author.prompt.md
├── reference/
│   ├── Azure-AI-in-Practice.pdf       ← Vincent's original ADA template; the visual reference
│   └── azure-template-pages/p-01.png … p-12.png   ← page-by-page screenshots
└── source/
    ├── brief.html                ← the editable source
    └── brief.pdf                 ← the current rendered output
```

---

## 3. The job

You are asked to improve the document. The improvements that matter, in priority order:

### 3.1 Tighten the writing
Vincent's voice is **measured, comparative, governance-aware**. Read [VOICE.md](VOICE.md) before editing. Then look for:

- **Hedge words to remove.** "really", "very", "actually", "basically", "essentially", "quite". Cut.
- **Run-on sentences** beyond ~28 words. Break into two.
- **Promotional phrasing.** Anything that praises the project rather than describing it. Cut.
- **Repeats across sections.** The "bias is measured, not hand-waved" claim appears three times. Once is enough.
- **Passive voice** where active is sharper.
- **Vague intensifiers** ("significantly", "considerably") — replace with a number or remove.

### 3.2 Improve the images
Each image has a sidecar `.prompt.md` file with the Higgsfield GPT Image 2 prompt that produced it. To regenerate an image:

```bash
higgsfield generate create gpt_image_2 \
  --prompt "$(cat images/02-vivino-context.prompt.md | sed -n '/^PROMPT/,/^---/p' | sed '1d;$d')" \
  --aspect_ratio 16:9 --resolution 2k --wait
```

Iterate the prompt. Better prompts get better images. Hard constraints (must remain in every prompt regardless of edits):

- **No people, no faces.** This document is editorial, not a brand-with-people piece.
- **No readable text, no logos.** Avoids fake brand names in the output.
- **Colour palette anchored in clay red (`#B83A1F`), deep olive, navy shadow, cream paper, dark walnut.** This is the document's visual identity. Drift breaks consistency.
- **Editorial photography aesthetic.** Reference points: *Apartamento*, *Monocle*, *Financial Times* weekend features. Not stock photography, not commercial.
- **Medium-format film feel.** Slight grain, soft shadows, restraint.

Image-specific notes are in each `*.prompt.md` sidecar.

### 3.3 The author photo
The author slot now uses a real B&W environmental portrait supplied by Vincent (`images/06-author.jpg`, also `source/author.jpg`). See [`images/06-author.prompt.md`](images/06-author.prompt.md) for treatment notes if a fresher portrait needs to be swapped in. Do **not** replace with an AI-generated face under any circumstance.

### 3.4 Verify the numbers
Every statistic in the body text refers to a real run of the CantinaIQ pipeline. The receiving AI should not invent new numbers. If a number needs updating, update from the source-of-truth files (these live in the parent CantinaIQ repo at `supercharged/reports/generated/`).

Current numbers cited:

| Claim | Value | Source file |
|---|---|---|
| Italian wines after cleaning | 2,986 | `data-quality.md` |
| Distinct producers after disambiguation | 762 | `producers_scored.parquet` |
| Gold-set recall, exact | 88 % | `producer-extraction-eval.json` |
| Gold-set recall, contains | 96 % | `producer-extraction-eval.json` |
| Tenuta Masseto bootstrap stability | 195 / 200 | `bootstrap-ci.md` |
| Toscana over-representation factor | × 1.22 | `bias-report.md` |
| Puglia under-representation factor | × 0.61 | `bias-report.md` |
| Abruzzo under-representation factor | × 0.52 | `bias-report.md` |
| Campania under-representation factor | × 0.55 | `bias-report.md` |
| Kendall-τ at m=500 vs baseline | 0.882 | `sensitivity.md` |
| Kendall-τ at m=800 vs baseline | 0.765 | `sensitivity.md` |
| Tests passing | 137 | `pytest` output |
| CLI subcommands | 14 | `cantinaiq --help` |

If you update a number, update the corresponding text wherever it appears.

### 3.5 Pagination must stay at 12
The visual identity calls for exactly twelve A4 pages, page numbered 02–12 (the cover is unnumbered). If your edits push the document to 13 or 11 pages, tighten copy or adjust CSS (in `source/brief.html`, the `body` font-size and line-height knobs are at the top). The receiving AI must verify the final PDF has `Pages: 12` before declaring the work done.

---

## 4. What NOT to change

- **The 6-section structure** (Introduction → Vivino in Context → From the Field → The Choice → Closing Observation → About the Author). Mirror of Vincent's Azure brief.
- **The two pull-quotes** that frame the argument: *"The right question is not 'can this data answer the question?' The right question is what the data gives us that the next-best evidence does not."* and *"Methodology choices are governance choices."* These carry the document's argument.
- **The "From notebook to data product." cover tagline.** Parallels Vincent's Azure brief tagline *"From platform to architecture."*
- **The author block layout** on page 12. Cosmetics may improve; structure stays.
- **The visual identity in [TEMPLATE.md](TEMPLATE.md).** Clay-red accent, Inter typography, spaced caps, footer stamp. Don't introduce new colours, new fonts, new layout patterns.

---

## 5. Success criteria

When you finish:

- [ ] The PDF still renders to exactly 12 pages.
- [ ] No page has obvious vertical overflow (no orphan tables, no half-empty pages with one trailing line).
- [ ] The voice matches [VOICE.md](VOICE.md) — particularly: no promotional phrasing, no hedge words, no padding.
- [ ] All cited numbers are either unchanged or updated in lock-step with the parent repo's report files.
- [ ] Images either preserve the existing palette/aesthetic or are regenerated from updated prompts that still honour the §3.2 hard constraints.
- [ ] The author photo remains the real Vincent portrait — not replaced with anything AI-generated.

---

## 6. How to re-render

```bash
cd brief-ai-handoff/source
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
  --print-to-pdf=brief.pdf --virtual-time-budget=5000 \
  "file://$(pwd)/brief.html"
```

Then `pdfinfo brief.pdf` to confirm 12 pages, and `pdftoppm -r 90 -png brief.pdf preview/p` to render page screenshots for visual review.

If Chrome is not available, any Chromium-derived browser works (`chromium --headless …`). WeasyPrint (`weasyprint`) is a Python alternative; layout will be close but the dot-grid component may need tweaking.

---

## 7. Author voice — one paragraph crib

If you remember nothing else: Vincent writes in measured, comparative, governance-aware first-person, like an applied architect explaining a decision to a thoughtful senior colleague. He uses concrete named projects from his own work (ClubDuty, BV Hoofddorp, Scoupy, Slurpini) as anchors. He never advocates — he compares. He treats limitations as load-bearing, not as caveats. He closes by zooming out from the specific case to a broader governance principle. Read three random pages of `reference/Azure-AI-in-Practice.pdf` before you write a single sentence.
