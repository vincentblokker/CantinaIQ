# CantinaIQ Dashboard — Bilingual (NL/EN) Support with Difficult-Word Glossary

**Date:** 2026-05-28
**Status:** Approved (design)
**Scope:** `CantinaIQ/dashboard` (Vite + React 19 + react-router + Tailwind)

## Problem

The CantinaIQ dashboard is currently English-only with hardcoded strings across
~10 pages, modals, and shared components (~3.846 LOC). The audience is partly
Dutch (Slurpini is a Dutch importer; the underlying consumer data is Dutch). We
want the dashboard to be bilingual with a live NL/EN language switch, and we want
Dutch readers to understand the difficult/technical English vocabulary without
translating every paragraph.

## Goals

1. A live **EN/NL language switch** in the header that translates the UI shell and
   key texts across all dashboard pages, persisted across reloads.
2. A **glossary/tooltip layer** that gives Dutch explanations for difficult English
   terms (including the canonical-English domain terms) where they appear in prose.

## Non-goals

- Translating the long analytical prose (region terroir/climate descriptions in
  `regionMeta.ts`, the dense explanatory paragraphs on `Methodology.tsx`, long
  modal narratives). These stay English in both modes; the glossary makes their
  hard words understandable instead.
- Translating the canonical domain terms themselves (segments like *Hidden Gem*,
  *Premium Icon*; recommendations like *Target*, *Avoid for Now*; methodology terms
  like *Bayesian shrinkage*). They remain English and are surfaced via the glossary.
- Translating proper nouns, data values, wine/region/producer names, citations.
- The Python-generated markdown/HTML reports under `supercharged/reports/`. Out of
  scope — this is a dashboard-only change.
- New test infrastructure (no vitest). Compile-time typing + visual verification
  cover this change (see Testing).

## Decisions (locked)

| Decision | Choice |
|---|---|
| i18n library | **react-i18next** (+ `i18next`) — battle-tested, runtime EN fallback |
| Default language | **English**; NL via switch; persisted in `localStorage` |
| Translation depth | **UI shell + key texts** across all pages; long prose stays EN |
| Domain terms | **Canonical English**, surfaced via glossary tooltips (not translated) |
| Glossary tooltips visible | **NL mode only** (Dutch comprehension aid) |
| Tooltip primitive | **`@radix-ui/react-tooltip`** (accessible, robust) |
| Glossing applied | Only inside designated prose containers (not nav/buttons/tables) |
| Key parity guard | Compile-time via `nl: typeof en` + existing `tsc -b` |

## Architecture

Two independent layers.

### Layer 1 — Language switch (react-i18next)

- **Deps:** `i18next`, `react-i18next`.
- **Init** (`src/i18n/index.ts`): `resources` from typed `en`/`nl` modules,
  `fallbackLng: 'en'`, `lng` read from `localStorage` (default `'en'`),
  `interpolation.escapeValue: false` (React already escapes). Imported once from
  `src/main.tsx` before `<App/>` renders.
- **Resources** (`src/i18n/locales/en.ts`, `nl.ts`): plain typed objects, namespaced
  by area: `nav.*`, `breadcrumb.*`, `footer.*`, `common.*`, and one namespace per
  page (`overview.*`, `recommendation.*`, `matrix.*`, `wines.*`, `regions.*`,
  `producers.*`, `bias.*`, `stability.*`, `methodology.*`, `forEvaluators.*`), plus
  `modal.*`. `en` is the source of truth; `nl` is typed `: typeof en`, so a missing
  NL key is a `tsc -b` compile error. Numbers use interpolation, e.g.
  `t('overview.wineCount', { count: 2986 })`.
- **Type augmentation** (`src/@types/i18next.d.ts`): bind the resource type to `t()`
  so keys autocomplete and unknown keys error. Requires `resolveJsonModule` not
  needed (TS modules, not JSON).
- **Switch UI:** a compact segmented `EN | NL` toggle in the header nav (and a
  subtle copy in the footer). Calls `i18n.changeLanguage('en'|'nl')`. On change,
  persist to `localStorage` and set `document.documentElement.lang`.
- **Usage:** components call `const { t } = useTranslation()` and replace hardcoded
  strings with `t('namespace.key')`.

**What Layer 1 translates (key texts):** nav/breadcrumb/footer, page titles +
section headings, metric labels/captions (`MetricCard`), button/tab/link text,
table column headers, short intro/lead sentences (1–2 per section), modal titles +
field labels + buttons, empty/loading states.

**What Layer 1 leaves English:** the long prose listed in Non-goals, domain terms,
data/proper nouns.

### Layer 2 — Glossary / tooltips

- **Data** (`src/i18n/glossary.ts`): a typed, *curated* map
  `Record<string, { nl: string }>` — term (canonical English) → short Dutch
  explanation. Seeded with ~20–40 terms harvested from methodology, region, and
  modal content. Initial candidates: *defensible shortlist, shrinkage threshold,
  weighted rating, Bayesian-shrunk / Bayesian shrinkage, value for money / value
  score, market confidence, premium fit, portfolio opportunity, composite score,
  contamination, Isolation Forest, Kendall-τ, bootstrap / confidence interval,
  terroir, macro-region, DOCG, DOC, varietal*, plus the segment and recommendation
  domain terms. Curated (not auto-NLP) for accuracy and control.
- **Render component** (`src/components/GlossedText.tsx`): takes a string, and when
  `i18n.language === 'nl'`, wraps known glossary terms (whole-word,
  case-insensitive, first occurrence per text block) with a tooltip; otherwise
  renders the string unchanged. A companion `<Term term="…">children</Term>` allows
  precise inline glossing where auto-wrap is undesirable.
- **Tooltip UI:** `@radix-ui/react-tooltip`. Glossed terms get a dotted underline;
  hover/focus shows a small popover with the NL explanation. Keyboard-accessible
  (focusable trigger, Esc closes); on touch, tap toggles.
- **Where applied:** inside designated prose containers only — `Methodology.tsx`
  paragraphs, region description blocks (`RegionDetailModal` / `regionMeta` notes),
  and long modal explanation paragraphs. Not in nav, buttons, or tables (avoids
  false matches and clutter).

## Data flow

1. `main.tsx` imports `./i18n` (initialises i18next with `en`/`nl` resources and the
   persisted language) before rendering `<App/>`.
2. Components read strings via `useTranslation().t(...)`.
3. The header toggle calls `i18n.changeLanguage(lng)` → react-i18next re-renders
   subscribed components → `localStorage` + `<html lang>` updated via an effect/event
   handler.
4. `GlossedText` reads `i18n.language` reactively (via `useTranslation`) and decides
   whether to wrap glossary terms.

## Components / units

| Unit | Responsibility | Depends on |
|---|---|---|
| `src/i18n/index.ts` | i18next config + init + localStorage helper | i18next, locale modules |
| `src/i18n/locales/en.ts` | English key dictionary (source of truth) | — |
| `src/i18n/locales/nl.ts` | Dutch dictionary, `: typeof en` | `en.ts` (type) |
| `src/i18n/glossary.ts` | curated term → NL explanation map | — |
| `src/@types/i18next.d.ts` | type-binds `t()` to resource shape | `en.ts` |
| `src/components/LanguageToggle.tsx` | EN/NL segmented switch | react-i18next |
| `src/components/GlossedText.tsx` + `Term` | render text with NL glossary tooltips | glossary, radix-tooltip |
| Pages + modals + `MetricCard` etc. | consume `t()`; wrap prose in `GlossedText` | i18n, GlossedText |

## Phasing

1. **Infra:** add deps; `src/i18n/index.ts`; type augmentation; `LanguageToggle` in
   header + footer; `<html lang>` sync; empty typed `en`/`nl` scaffolds.
2. **Shell + Overview:** translate header/breadcrumb/footer + Overview page as the
   proof-of-pattern for Layer 1.
3. **Remaining pages:** Recommendation, Matrix, Wines, Regions, Producers, Bias,
   Stability, Methodology, ForEvaluators — one at a time.
4. **Modals + shared components:** WineDetailModal, ProducerDetailModal,
   RegionDetailModal, Modal, MetricCard, RecommendationPill.
5. **Glossary:** curate `glossary.ts`; build `GlossedText`/`Term`; apply to prose
   containers (methodology, region descriptions, long modal text).
6. **Verify:** dev server; toggle EN/NL on several pages; test tooltips
   (hover/focus/Esc); screenshots; `tsc -b` for key parity and type binding.

## Testing / verification

No new test framework (YAGNI; the dashboard has none). Guarantees:
- **Key parity:** `nl: typeof en` makes a missing/renamed NL key a `tsc -b` error;
  `tsc -b` already runs in `npm run build`.
- **Type-safe keys:** `t()` is bound to the resource type via the d.ts augmentation.
- **Runtime safety:** `fallbackLng: 'en'` means any gap renders English, never a raw
  key.
- **Behavioural:** verified in-browser via the preview tools — switch EN/NL on
  Overview, Methodology, and a modal; confirm UI translates, prose stays English,
  and glossary tooltips appear in NL mode only and are keyboard-accessible.

## Risks / open points

- **Glossary false matches:** mitigated by whole-word matching, first-occurrence-only
  per block, and applying only inside prose containers.
- **Translation quality of key texts:** Dutch copy will be written to read naturally,
  not literally; reviewable in `nl.ts` in one place.
- **Radix dependency:** one small, well-maintained, accessible package; aligns with
  the "prefer robust libraries" preference. If undesired later, `GlossedText` can
  swap to a custom tooltip without touching call sites.
