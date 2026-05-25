# Image 01 — Cover

**File**: `01-cover.jpg`
**Used at**: page 1, full-bleed hero (page-wide, ~105 mm tall), with a red linear gradient overlay (transparent top → 75 % red at bottom) and white tagline "From notebook / to data product." overlaid lower-left.
**Aspect ratio**: 16:9
**Higgsfield model**: `gpt_image_2`
**Resolution at generation**: 2k

---

## PROMPT

Editorial photograph: a wooden importer's tasting table in a stone-walled Italian cellar, viewed slightly from above. On the table: three open wine bottles standing back-to-back without labels (anonymised), each with a slightly different label-paper colour (cream, dusty olive, deep clay). Beside them: a printed shortlist of producer names on cream paper with a small bar chart and a hand-annotated star rating system. A single stemmed glass with deep ruby wine catches warm window light. Atmosphere: deliberate, considered, restrained. Mood: Apartamento magazine + Monocle. No people, no faces, no readable text, no logos. Color palette: clay red, deep olive, navy shadow, cream paper, dark walnut. Medium format film, slight grain, soft shadows.

---

## Why this image

The cover should not look like a wine catalogue. It should look like the working surface where a decision is being made about wine. Three bottles with different label-paper colours imply a choice in progress. The bar chart on the shortlist visually signals "this is a data-product brief, not a tasting note."

The red overlay on top of the image carries the document identity and provides legibility for the white tagline.

## Iteration notes

- The bottles must remain **unlabelled**. Generated label text reads as gibberish and breaks the editorial restraint.
- Keep the bar chart small and partial — it is a visual hint, not a chart to read.
- The single ruby-wine glass anchors the warm right side; don't add a second one. Asymmetry beats symmetry here.
- If you regenerate, try shifting the camera angle down 10–15° to make the bottles read taller — improves the cover crop.

## What does NOT belong in a regeneration

- Cork screws, decanters, fruit, cheese, baguettes — anything that signals "Italian wine cliché".
- People, hands, or any human element.
- Readable text on the shortlist (the squiggles are correct).
- A second glass with a different wine — disrupts the "single anchor object" rule.

## Regenerate

```bash
higgsfield generate create gpt_image_2 \
  --prompt "[PROMPT ABOVE]" \
  --aspect_ratio 16:9 --resolution 2k --wait
```
