# /dashboard — CantinaIQ SPA

A single-page React + Vite + Tailwind + Recharts app over the JSON exports
produced by the [supercharged pipeline](../supercharged/).

This is the *visible* face of the CantinaIQ submission — open it in a browser
to see what an examiner-facing decision-support tool looks like, instead of
reading markdown reports.

---

## Run locally

```bash
# from the repo root
make serve-dashboard          # http://localhost:5175
```

Or directly:

```bash
cd dashboard
npm install
npm run dev
```

Open http://localhost:5175.

---

## Data source

The dashboard reads JSON from `public/data/`, which is symlinked to
`../supercharged/data/exports/`. Refresh the data with:

```bash
make demo          # full pipeline + reports + dashboard build
# or
cd ../supercharged && uv run cantinaiq run all
```

The dashboard consumes:

| File | Used by |
|---|---|
| `dashboard_summary.json` | Overview — totals, run/config metadata |
| `producer_rankings.json` | Producers + Matrix + Overview top-5 |
| `region_rankings.json` | Regions + Overview top-5 |

---

## Pages

| Route | Content |
|---|---|
| `/` | Overview — 3 KPI cards + top 5 producers + top 5 regions |
| `/regions` | Top 50 regions sorted by weighted rating |
| `/producers` | 100 producers with a recommendation filter dropdown |
| `/matrix` | Opportunity matrix scatter — log-price × weighted rating, bubble size ∝ reviews, colour = segment (Hidden Gem · Premium Icon · Commercial Value · Overpriced Risk) |

---

## Build for production

```bash
npm run build
```

`dist/` is a static SPA — deploy to Vercel, Netlify, or GitHub Pages with no
backend.

---

## Design notes

- Off-white background (`#FAF7F2`), serif headings (Source Serif 4), Tailwind primitives.
- Recommendation pills colour-coded:
  - Premium Brand Builder → purple
  - Target → blue
  - Value Opportunity → green
  - Monitor → stone
  - Avoid for Now → rose
- Opportunity matrix scatter colours match the methodology document's quadrant colours, so the dashboard and the printed reports speak the same visual language.
