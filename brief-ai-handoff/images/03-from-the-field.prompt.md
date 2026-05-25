# Image 03 — From the Field

**File**: `03-from-the-field.jpg`
**Used at**: page 7, full-bleed (16 mm bleed each side), ~70 mm tall.
**Aspect ratio**: 16:9
**Higgsfield model**: `gpt_image_2`
**Resolution at generation**: 2k

---

## PROMPT

Editorial photograph: an Italian wine importer's office. Wide horizontal view. Foreground: an open wooden case of unlabelled bottles on a stone floor, surrounded by carefully labelled cream tags marked only with single capital letters (A, B, C). Middle ground: a worn oak desk, a black-paged tasting notebook open with handwritten scoring rubric, two crystal glasses with different reds. Background: through a window, soft afternoon light on terraced vineyards. Mood: warm, working, deliberate. No people, no faces, no readable wine labels, no logos. Color palette: clay red, deep olive, navy shadow, cream paper, dark walnut, cream stone walls. Medium format film, slight grain.

---

## Why this image

This section is "From the Field: Slurpini Partner Intelligence". The image needs to read as "an importer is actually doing this work" — a desk, a notebook, anonymised bottles tagged A/B/C/D, the suggestion of a process. The window onto vineyards anchors the Italian context without being a cliché vineyard shot.

## Iteration notes

- Keep the A/B/C/D tags anonymous (single letters). Names break the editorial restraint.
- The black-paged notebook is a deliberate detail — it reads as "real working notebook", not "Instagram prop". Don't replace with a beige notebook.
- Two glasses with two different reds suggests comparison; one glass would suggest tasting.
- The vineyard through the window should be **soft / blurred**, not the sharpest thing in frame. The work is in the office.

## What does NOT belong

- A human being at the desk (we have no faces, no people anywhere in the brief).
- Sharp focus on the vineyard outside — that competes with the foreground.
- Branded materials, real wine labels, or anything that reads as advertising a producer.
- A modern laptop or screen.

## Regenerate

```bash
higgsfield generate create gpt_image_2 \
  --prompt "[PROMPT ABOVE]" \
  --aspect_ratio 16:9 --resolution 2k --wait
```
