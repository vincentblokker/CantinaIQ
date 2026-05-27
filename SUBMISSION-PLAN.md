# SUBMISSION PLAN — CantinaIQ → ADA Final Assignment

The plan to ship CantinaIQ to the Amsterdam Data Academy as the Final
Assignment for the AI Professional programme. Written so a docent
spends 2 minutes (not 30) confirming the submission meets the rubric.

---

## The goal

Make the submission **scannable**. ADA's docent has finite attention.
The work is real but lives across multiple artefacts — a 22-page strategy
brief, a 762-bubble dashboard, a 3,500-line pipeline, a notebook track,
137 tests, a rubric map. Without curation, the docent either spends
hours navigating or skims and misses substance. Either outcome under-sells
the work.

Four anchors get the docent from "what is this?" to "I can score it" in
ten minutes. Everything below serves that.

---

## The four anchors

```text
1. STRATEGY BRIEF PDF       22 pages of narrative — the argument
2. LIVE DASHBOARD           cantinaiq.clubventure.nl — the data product
3. RUBRIC MAP               /for-evaluators — the click-through index
4. WALKTHROUGH VIDEO        2 minutes — the orientation
```

The video is the highest-friction asset to make and the lowest-friction
asset to consume. The dashboard is the inverse. The PDF anchors the
narrative. The rubric map shortens evaluation. They reinforce, they
don't repeat.

---

## Status — what is shipped vs. pending

| # | Anchor | Where it lives | Status |
|---|---|---|---|
| 1 | Strategy brief PDF (22 p, incl. §08 Enrichments) | [`CantinaIQ-in-Practice.pdf`](CantinaIQ-in-Practice.pdf) · [GitHub](https://github.com/vincentblokker/CantinaIQ/blob/main/CantinaIQ-in-Practice.pdf) | ✓ done |
| 2 | Live dashboard | https://cantinaiq.clubventure.nl/ | ✓ deployed on Hetzner (Traefik + nginx:alpine, ACME via Let's Encrypt) |
| 2a | Dashboard narrative pages | `/recommendation` · `/bias` · `/stability` · `/methodology` | ✓ live |
| 2b | Opportunity Matrix | `/matrix` (762 bubbles, log-price × weighted rating) | ✓ live |
| 2c | Region / Producer / Wine detail modals | (i) icons across Overview, /regions, /producers, /wines | ✓ live |
| 2d | Region enrichments — 4 shipped, 3 deferred with blockers | `/regions` modal · `dashboard/src/lib/regionMeta.ts` | ✓ live |
| 3 | Rubric map page (16 criteria) | https://cantinaiq.clubventure.nl/for-evaluators | ✓ live |
| 3a | Evaluator one-pager PDF | `/downloads/evaluator-mapping.pdf` (1 A4, 240 KB) | ✓ rendered |
| 3b | Evaluator CTA on Overview | Soft tuscan banner above the fold | ✓ live |
| 3c | ENRICHMENT-PLAN.md governance doc | [`ENRICHMENT-PLAN.md`](ENRICHMENT-PLAN.md) | ✓ committed |
| 4 | Walkthrough video | Self-hosted at https://cantinaiq.clubventure.nl/downloads/walkthrough.mp4 · embedded on `/for-evaluators` | ✓ done — 3:00, 36 MB, 1080p H.264 |
| 5 | ADA submission email | [ADA-SUBMISSION-EMAIL.md](ADA-SUBMISSION-EMAIL.md) | ⏳ draft ready, awaiting send |

---

## What's left to do

### A. Video production — ✓ done

Final delivery: 3:00, 36 MB, 1080p H.264, English VO. Self-hosted at
https://cantinaiq.clubventure.nl/downloads/walkthrough.mp4 with poster
frame and inline HTML5 player embedded on `/for-evaluators`. Source
files (Higgsfield stills, ElevenLabs lipsync clips, build scripts) in
`video-assets/`.

Notes on delivery vs. earlier plan:
- **Self-hosted, not Vimeo** — Vimeo free tier limits public links to
  7 days; self-hosting on the existing Hetzner box is permanent and
  matches the rest of the stack.
- **3:00 instead of 2:00** — the screencast + bridge segments needed
  more breathing room than the original ~2-min target allowed.
- **Outro music added** (~13s under the aerial vineyard close) — the
  earlier "no music bed" decision applied to the body; the outro
  benefits from a soft cinematic landing without compromising the
  governance-aware tone of the body.

### B. Embed video URL — ✓ done

1. README.md — quick-links block lists strategy brief, dashboard,
   rubric map, walkthrough video.
2. `/for-evaluators` page — embedded inline as the first section
   below the header (HTML5 player + poster + download fallback).
3. ADA submission email — included in [ADA-SUBMISSION-EMAIL.md](ADA-SUBMISSION-EMAIL.md).

### C. Draft the ADA submission email (~30 minutes)

Short, factual, four-anchor email. Draft format:

> Subject: Final Assignment — CantinaIQ (Slurpini case) — Vincent Blokker
>
> Dag [docent-naam],
>
> Bij deze mijn Final Assignment voor de AI Professional bootcamp — de
> Slurpini wijn-case, uitgewerkt als CantinaIQ.
>
> Voor het beoordelen, vier ankers:
>
> 1. **Strategy brief PDF** — 22 pagina's, narratieve laag van het werk
>    *(bijlage of GitHub-link)*
> 2. **Live dashboard** — https://cantinaiq.clubventure.nl/
>    *(start linksboven, "Open rubric map" links direct naar de rubric)*
> 3. **Repo** — https://github.com/vincentblokker/CantinaIQ
> 4. **Walkthrough video** — [Vimeo URL]
>    *(2 minuten, voor een snelle oriëntatie)*
>
> De ADA-brief vraagt drie deliverables (crawler-extensie, EDA,
> evidence-based aanbeveling). Alle drie zitten in `/bare/` — de
> minimum-viable tak die in 30 seconden draait. De `/supercharged/`
> tak en het dashboard behandelen dezelfde businessvraag als
> reproduceerbaar data-product. De delta tussen de twee tracks is in
> de strategy brief het centrale argument.
>
> Mocht u liever offline scoren: op `/for-evaluators` staan beide PDFs
> als download, plus een 1-page rubric mapping.
>
> Met vriendelijke groet,
> Vincent Blokker
> [contact details]

I'll draft this in full when the video URL is ready. Subject line and
greeting personalise to whoever the email goes to.

---

## Timeline — the suggested sequence

A realistic 3-day cadence. Each day under 2 hours of focused work.

```text
Day 1 — Higgsfield + go/no-go on avatars
  ├─ Generate shot 1 (intro avatar)         ~10 min Higgsfield + wait
  ├─ Review the output                       ~5 min
  ├─ Decision: keep Soul or go iPhone Plan B
  └─ Generate the other three shots          ~20 min Higgsfield + wait

Day 2 — Screencast + voice-over
  ├─ QuickTime: PDF walkthrough               ~15 min including retakes
  ├─ QuickTime: dashboard tour                ~15 min
  ├─ QuickTime: /for-evaluators               ~10 min
  ├─ Voice-over recording                     ~30 min
  └─ Light VO clean-up in Audacity            ~10 min

Day 3 — Edit + ship
  ├─ Timeline assembly                        ~30 min
  ├─ Lower-thirds, title card, captions       ~20 min
  ├─ Export 1080p H.264                       ~5 min
  ├─ Upload to Vimeo                          ~10 min
  ├─ Embed URL in README + dashboard          ~10 min
  └─ Draft + send ADA email                   ~20 min
```

Total: ~3.5 hours of focused work plus ~1 hour of wait/render time.

---

## Decisions already made (don't re-litigate)

These were settled in earlier rounds. Don't loop back on them unless
something material changes.

- **English over Dutch** for all artefacts (PDF, dashboard, video VO).
  Academic-English is standard at ADA level; the PDF and dashboard are
  already in English; switching would create inconsistency.
- **Soul avatar for bookend shots only**, not the full video. Soul
  artefacts at long talking-head scale are a distraction; bookends
  hide them.
- **Vimeo unlisted-with-link**, not YouTube. ADA's own case intro is
  on Vimeo (`vimeo.com/1135863784`); mirroring is professional courtesy.
- **No music bed under the body of the video** — the brief's tone is
  measured and governance-aware; body music would marketing-ise it.
  *Revised in production:* outro carries ~13s of soft cinematic music
  under the aerial vineyard close only. The body remains music-free.
- **Subdomain `cantinaiq.clubventure.nl`**, not a path on an existing
  domain. The dashboard fetches assets and data from absolute paths
  (`/data/*`, `/assets/*`); a subpath would require a code change for
  no reader-side benefit.

---

## What's not in this plan (and why)

- **Reaching out to Slurpini directly.** They are a real Dutch importer
  used as a case study by ADA. They didn't commission this work and
  shouldn't receive it cold. The data layer here is consumer-public
  (Vivino + ICE NL imports), not partner-internal.
- **A Higgsfield Marketing Studio variant**. The "viral hook" format
  is the wrong register for an academic submission. The walkthrough
  video is the right format.
- **Per-platform short-form clips** (TikTok / Reels / LinkedIn). The
  audience here is one docent, not a feed. Reuse the long-form video
  later if you want a portfolio piece.
- **A second pass on the bare track**. The bare track is deliberately
  minimum-viable. Adding rigour would erase the contrast that makes
  the supercharged track legible. See `CLAUDE.md` for the rule.
- **Dutch translation of the strategy brief**. English is the working
  language of the bootcamp. The PDF mood, voice, and typography all
  assume English copy.

---

## Acceptance — when is this "done"?

The submission is shippable when **all four anchors** are reachable and
internally consistent:

- [x] Strategy brief PDF renders, 22 pages, all numbers traceable
- [x] Live dashboard reachable on HTTPS, all 10 routes 200, both PDF
      downloads serve `application/pdf`
- [x] Rubric map page lists 16 criteria with working repo + SPA links
- [x] ENRICHMENT-PLAN.md committed; region modal shows 4 shipped / 3 deferred
- [x] Walkthrough video produced, self-hosted, embedded in 3 places
- [ ] ADA email drafted (✓), anchors verified, sent

When the last row is checked, the submission goes out.

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Hetzner box goes down during evaluation window | low | high | PDF + repo work without the box; rubric one-pager is downloadable from `/for-evaluators` |
| Soul avatar shots look uncanny | medium | low | Plan B in VIDEO-BRIEF §10 — iPhone front-cam fallback |
| Video runs long (>3 min) | medium | low | Trim Shot 4 (dashboard) first; it has the most slack |
| Docent never opens the video | medium | low | Brief PDF + dashboard + rubric map already cover everything; the video is the orientation aid, not the substance |
| ADA submission portal restricts URL count | low | medium | Use one cover note + bundled artefacts; rubric one-pager substitutes for live links if needed |
| Higgsfield account out of credits | very low | low | 685 credits cover full production ~3× over; can also recharge or fall back to Plan B |

---

## File map (where everything lives)

```text
CantinaIQ/
├── CantinaIQ-in-Practice.pdf      ← strategy brief, 22 pages (anchor 1)
├── ENRICHMENT-PLAN.md              ← shipped vs deferred enrichments + Phase A-D unlock
├── README.md                        ← root readme with quick-start
├── FOR_REVIEWERS.md                 ← reviewer roadmap (5/30/60 min reads)
├── DEMO.md                          ← 3-min screencast script
├── VIDEO-BRIEF.md                   ← video production plan
├── SUBMISSION-PLAN.md               ← you are here
├── bare/                            ← brief-compliant minimum (anchor at /bare)
│   ├── crawler-extension.py
│   ├── notebooks/slurpini-analysis.ipynb
│   ├── recommendation.md
│   └── output/*.csv
├── supercharged/                    ← the data product
│   ├── PRD.md
│   ├── src/cantinaiq/               ← pipeline + 14 CLI subcommands
│   ├── tests/                       ← 137 tests
│   ├── reports/generated/           ← bias, bootstrap, sensitivity, anomalies, etc.
│   └── docs/superpowers/            ← spec + plans
├── dashboard/                       ← Vite SPA (anchor 2)
│   ├── src/pages/                   ← 9 pages incl. /for-evaluators (anchor 3)
│   ├── src/lib/pdfData.ts           ← embedded narrative data
│   ├── src/lib/evaluatorMapping.ts  ← rubric data
│   └── public/downloads/            ← both PDFs for download
├── brief-ai-handoff/                ← strategy brief source
│   ├── source/brief.html            ← HTML source for the PDF
│   ├── render.sh                    ← headless Chrome → PDF
│   └── images/                      ← mood images + Higgsfield prompts
├── deploy/                          ← deployment artefacts
│   ├── DEPLOY.md
│   ├── package.sh                   ← rebuilds dashboard + tarball
│   ├── traefik/                     ← docker-compose + nginx for clubventure
│   └── evaluator-pdf/               ← rubric one-pager HTML + render.sh
└── CLAUDE.md                        ← guidance for AI coding agents
```

---

*Last edited 2026-05-27 after video production wrapped and deploy
landed. Next edit: mark email sent.*
