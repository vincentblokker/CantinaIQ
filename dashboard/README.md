# CantinaIQ Dashboard

Single-page React + Vite + Tailwind + Recharts app over the JSON exports
produced by the supercharged pipeline.

## Run locally

```bash
npm install
npm run dev
```

Open http://localhost:5175.

## Data source

The dashboard expects JSON in `public/data/`, which is symlinked to
`../supercharged/data/exports/`. Refresh the data with:

```bash
cd ../supercharged
uv run cantinaiq run all
uv run cantinaiq report build
```

The dashboard reads:

- `dashboard_summary.json` — totals + run/config metadata
- `producer_rankings.json` — top producers with composite_score + segments
- `region_rankings.json` — regional rankings with weighted ratings

## Pages

| Route | Content |
|---|---|
| `/` | Overview — 3 KPI cards + top 5 producers + top 5 regions |
| `/regions` | Top 50 regions sorted by weighted rating |
| `/producers` | 100 producers with recommendation filter dropdown |
| `/matrix` | Opportunity matrix scatter (log-price × weighted rating, bubble = reviews, colour = segment) |

## Build for production

```bash
npm run build
```

`dist/` is a static SPA — deploy to Vercel, Netlify, or GitHub Pages.

## Design

- Off-white background (`#FAF7F2`), serif headings (Source Serif 4), Tailwind primitives.
- Recommendation pills colour-coded: Premium Brand Builder (purple), Target (blue), Value Opportunity (green), Monitor (stone), Avoid (rose).
- Opportunity matrix scatter colours match the methodology document's quadrant colours.
