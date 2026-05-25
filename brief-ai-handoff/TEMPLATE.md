# TEMPLATE.md — visual identity

The document is a 12-page A4 strategy brief. It is *not* a slide deck and it is *not* a marketing one-pager. It is a magazine-feature-style report.

The visual identity below mirrors Vincent's [Azure-AI-in-Practice.pdf](reference/Azure-AI-in-Practice.pdf) exactly. Page-by-page screenshots of the original are in [`reference/azure-template-pages/`](reference/azure-template-pages/). Open `p-01.png` through `p-12.png` and compare side-by-side with the current `source/brief.pdf`.

---

## Page

- **Format**: A4 portrait (210 × 297 mm).
- **Margins**: 14 mm top, 16 mm sides, 13 mm bottom (cover has 0 margins; full bleed).
- **Background**: white. No off-whites in the layout itself (off-white belongs to the photography only).
- **Page count**: exactly 12. Cover is unnumbered; pages 02–12 are numbered.

---

## Colour palette

The palette is intentionally small. Adding new colours breaks the identity.

| Token | Hex | Use |
|---|---|---|
| `--red`    | `#B83A1F` | All accent text, the dot punctuation, header/footer labels, stat-callout numbers, table left column, decorative blocks. |
| `--ink`    | `#1A1815` | Headings and body text. |
| `--ink-2`  | `#5A4F44` | Subtle subtitles and meta. Used sparingly. |
| `--rule`   | `#DDD8D2` | All thin rules (between table rows, around stat callouts, around blockquotes). |
| `--cream`  | `#FAF7F2` | Reserved for photography palette only. Never used as a background in the layout. |
| `--red-soft` | `rgba(184,58,31,0.10)` | Background of inline `code` chips. |

Two-colour rules:

- **The red dot punctuation** (`<span class="dot">.</span>`) sits at the end of every section title and the author name. Removing it removes the identity.
- **Red is always the same red.** Never an orange, never a brick. `#B83A1F`.
- **No gradients in the layout.** The cover hero has a single linear red-to-transparent overlay; nowhere else.

---

## Typography

- **Family**: Inter (loaded from Google Fonts).
- **Weights used**: 400 (body), 500 (header/footer labels), 600 (spaced caps, table headers, red accent labels), 700 (h3/h4, pull-quote), 800 (cover hero text, stat callouts, author name, big section titles), 900 (cover title, "About the Author" wordmark).
- **No display serif.** The original Azure brief looks like a sans-serif throughout. Keep it that way.

### Type scale (in pt)

| Element | Size | Weight | Notes |
|---|---:|---:|---|
| Cover title | 56 | 900 | Letter-spacing `-0.02em`, line-height `0.95`. Two lines, "CANTINAIQ / IN PRACTICE." |
| Section title | 32 | 900 | Same letter-spacing/line-height treatment as cover title. |
| Section sub | 8 | 600 | Spaced caps, letter-spacing `0.22em`. |
| Section tag | 8 | 600 | Spaced caps, red. |
| Cover hero text | 26 | 800 | White on red overlay. |
| Stat number | 32 | 800 | Red, letter-spacing `-0.02em`. |
| Stat label | 7.2 | 600 | Spaced caps, ink. |
| Pull-quote | 10.5 | 700 | Ink with red `em` highlights. |
| h3 (body section heading) | 10.5 | 700 | Letter-spacing `-0.01em`. |
| h4 (sub-heading) | 9 | 700 | |
| Body | 8.5 | 400 | Line-height `1.42`. Max-width `175mm`. |
| Blockquote | 8.8 | 400 | Red left border, 3px wide. |
| Header / footer stamp | 7 | 500 | Spaced caps. |
| Table header | 7.2 | 600 | Spaced caps. Bottom border solid ink. |
| Table body | 8.4 | 400 | First-column cells: red, 600 weight. |
| Author name | 30 | 900 | Two lines, with red dot punctuation. |
| Inline code chip | ~7.8 | mono | Background `--red-soft`, monospace. |

---

## Layout components

### 1. Cover (page 1, unnumbered)

Structure top-to-bottom:

1. **Spaced-caps red tag** ("AMSTERDAM DATA ACADEMY / FINAL ASSIGNMENT").
2. **Big black title** in two lines with red dot punctuation. On the right of the title block, a **decorative dot grid** (8 columns × 4 rows, mostly grey dots, 5 red dots — see `source/brief.html` for the exact pattern).
3. **Greyish subtitle** (max 130 mm wide).
4. **Hero image** (full-bleed across the page width), with a **red gradient overlay** from 0% at top to 75% opacity at bottom, and **bold white tagline** lower-left ("From notebook / to data product.").
5. **Bottom strip**: left = small spaced-caps "PREPARED FOR" label + 2-line address; right = oversized "20**26**" with red 26.

### 2. Section opener (pages 3, 6, 9, 11)

1. **Header row**: section name top-left in spaced caps, page number top-right.
2. **Red spaced-caps "SECTION 0X"**.
3. **Big two-line title** with red dot.
4. **Spaced-caps subtitle**.
5. Body follows.

### 3. Body page (pages 2, 4, 5, 7, 8, 10)

1. Header row (same as opener).
2. Body content.
3. Footer row: left = "CANTINAIQ IN PRACTICE / STRATEGY BRIEF" in spaced caps, right = page number.

### 4. Blockquote

A red 3-px left border, no background fill, slightly smaller body text. Used to set off a single load-bearing observation. Maximum two per section.

### 5. Pull-quote

Bold body weight, framed by two thin horizontal rules (top and bottom). The interesting word(s) inside are coloured red via `<em>` — but always one short phrase, never a full sentence.

### 6. Comparison table

Three columns. Header row in spaced caps, bottom border solid ink. Body rows: first column red bold, other columns ink regular. Thin rule between body rows.

### 7. Stat callouts

Three columns, equal width. Each column: huge red number, then spaced-caps label below. Always exactly three numbers per row. Always preceded by a thin rule.

### 8. Numbered breakdown

A two-column grid where the left column is `01 / LABEL` in spaced caps red (40 mm wide), and the right column carries an h4 heading + a paragraph. Used for the "when the heavyweight is the wrong choice" enumeration.

### 9. Author block (page 12)

A two-column grid: left = b&w portrait or environmental still life (4:5 aspect ratio), right = section card with red "AUTHOR" label, oversized two-line name with red dot, two short paragraphs, and a three-column meta grid (Programme | Module | Year).

Decorative element: a small **red rectangle** (16 mm × 5 mm) sits between the section title and the author grid as visual punctuation.

---

## Imagery

All photographic content follows the same look:

- **Editorial restraint.** Apartamento meets Monocle.
- **No people, no faces, no readable text, no logos.**
- **Palette**: clay red, deep olive, navy shadow, cream paper, dark walnut.
- **Lighting**: warm directional, soft shadows, "medium-format film" feel.
- **Aspect ratio**: 16:9 for full-bleed section openers, 1:1 for the inline detail shots (currently used on page 12 as the author placeholder).

Each image must read at thumbnail size — meaning composition is anchored by a single dominant element (one bottle, one map, one glass-pair). Avoid busy compositions.

Generation prompts and per-image rationale are in the `images/*.prompt.md` sidecars.

---

## Footer stamp

Every page (except the cover) carries this footer:

```text
CANTINAIQ IN PRACTICE / STRATEGY BRIEF            [page number]
```

Spaced caps, 7 pt, weight 500, ink. Sits at the absolute bottom of the page.

When adapting this template to a different Vincent submission, change `CANTINAIQ IN PRACTICE` to `[NEW TOPIC] IN PRACTICE` — the `/ STRATEGY BRIEF` half is fixed.

---

## Things that look minor but break the identity

- Replacing Inter with another sans-serif.
- Centring any text (everything is left-aligned).
- Justified body text (use ragged-right).
- A red that drifts toward orange or magenta.
- Removing the red dot punctuation from section titles.
- Adding drop shadows, rounded corners, or any 2010-era "card UI" affordances.
- Using emoji.
- Using a serif typeface for body or quotes.
- Adding new section types not in this template (sidebars, callout boxes, info boxes).

---

## Reference

Open `reference/Azure-AI-in-Practice.pdf` and `source/brief.pdf` side by side. The current document should look like the same designer made both. If it doesn't, fix the document before fixing the words.
