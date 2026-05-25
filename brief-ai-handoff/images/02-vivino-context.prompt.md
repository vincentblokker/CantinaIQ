# Image 02 — Vivino in Context

**File**: `02-vivino-context.jpg`
**Used at**: page 4, full-bleed (16 mm bleed each side), ~70 mm tall.
**Aspect ratio**: 16:9
**Higgsfield model**: `gpt_image_2`
**Resolution at generation**: 2k

---

## PROMPT

Editorial photograph. A flat lay on a worn dark walnut table, top-down 90-degree overhead view. A printed market-research-style map of Italy where each region is filled with a clay-red gradient indicating consumer rating density (some regions darker, some lighter). Around the map: scattered cream paper cards each labeled with a tiny handwritten regional name, a few stamped corks, an espresso cup half-drunk, a fountain pen, and a printed bar chart on cream paper showing "NL imports vs Vivino dataset" as two side-by-side bar groups (without readable text). Lighting: warm directional, soft shadows. Mood: editorial, analytical, restrained. No people, no faces, no readable text, no logos. Color palette: clay red, deep olive, navy ink, cream paper, dark walnut. Medium format film, slight grain.

---

## Why this image

This section quantifies Vivino's bias against ICE NL import data. The flat-lay map with clay-red regional gradients literally illustrates the regional bias the text discusses, and the paired bar chart visually mirrors the "Vivino vs ICE" comparison. The result reads as analytic without becoming a screenshot.

## Iteration notes

- The Italy map must remain the focal point. Anything that competes (a large wine bottle, for instance) should be removed.
- The regional gradients should be clay-red specifically — not pink, not orange. Drift here breaks identity.
- The "bar chart" is a concept, not a real chart. Keep it deliberately imprecise.
- If you regenerate, try asking for a slightly tighter crop on the map (more map, less surrounding clutter) — increases readability at the small render size.

## What does NOT belong

- A globe, multiple country maps, or any non-Italian geography.
- Real numbers on the bar chart (Higgsfield will generate gibberish that looks fake).
- A computer screen anywhere in frame — the document is editorial, not techbro.
- Bright primary colours — the palette is desaturated warm.

## Regenerate

```bash
higgsfield generate create gpt_image_2 \
  --prompt "[PROMPT ABOVE]" \
  --aspect_ratio 16:9 --resolution 2k --wait
```
