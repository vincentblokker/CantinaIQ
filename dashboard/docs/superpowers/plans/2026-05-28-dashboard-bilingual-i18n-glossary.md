# CantinaIQ Dashboard Bilingual (NL/EN) + Glossary — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a live EN/NL language switch (react-i18next) translating the UI shell + key texts across all dashboard pages, plus a glossary tooltip layer giving Dutch explanations of difficult English terms in prose.

**Architecture:** Two independent layers. Layer 1 = react-i18next with typed `en`/`nl` resource modules (`nl: typeof en` guarantees key parity at compile time), a header toggle, localStorage persistence, and `<html lang>` sync. Layer 2 = a curated glossary map + a `GlossedText` component that wraps known terms in accessible Radix tooltips, shown only in NL mode and only inside prose containers.

**Tech Stack:** Vite · React 19 · react-router-dom 6 · TypeScript (strict) · Tailwind · `i18next` · `react-i18next` · `@radix-ui/react-tooltip`.

**Verification model:** The dashboard has no unit-test framework and we are not adding one (YAGNI). Each task is verified by (a) `npx tsc -b` type-check — `nl: typeof en` turns any missing key into a compile error — and (b) browser checks via the dev server. "Run the test" steps below mean "run the type-check and/or load the page".

---

## File Structure

| File | Responsibility | New? |
|---|---|---|
| `src/i18n/index.ts` | i18next init, localStorage persistence, `<html lang>` sync | new |
| `src/i18n/locales/en.ts` | English dictionary (source of truth) | new |
| `src/i18n/locales/nl.ts` | Dutch dictionary, typed `: typeof en` | new |
| `src/i18n/glossary.ts` | curated term → NL explanation map | new |
| `src/@types/i18next.d.ts` | bind `t()` to resource shape | new |
| `src/components/LanguageToggle.tsx` | EN/NL segmented switch | new |
| `src/components/GlossedText.tsx` | render prose with NL glossary tooltips (+ `Term`) | new |
| `src/main.tsx` | import i18n; wrap app in Radix `Tooltip.Provider` | modify |
| `src/App.tsx` | use `t()` for nav/breadcrumb/footer; mount `LanguageToggle` | modify |
| `src/pages/*.tsx` (10) | replace key strings with `t()` | modify |
| `src/components/*Modal.tsx`, `MetricCard.tsx`, `RecommendationPill.tsx` | `t()` + `GlossedText` | modify |

---

## Task 1: Install dependencies

**Files:** `package.json` (modify, via npm)

- [ ] **Step 1: Install**

```bash
cd CantinaIQ/dashboard
npm install i18next react-i18next @radix-ui/react-tooltip
```

- [ ] **Step 2: Verify**

Run: `node -e "require('i18next');require('react-i18next');require('@radix-ui/react-tooltip');console.log('ok')"`
Expected: `ok` (deps resolve). `package.json` dependencies now list the three packages.

---

## Task 2: i18n core + empty typed resources

**Files:**
- Create: `src/i18n/locales/en.ts`, `src/i18n/locales/nl.ts`, `src/i18n/index.ts`, `src/@types/i18next.d.ts`

- [ ] **Step 1: Create `src/i18n/locales/en.ts`** (do NOT use `as const` — values must infer as `string` so `nl` may differ)

```ts
export const en = {
  brand: {
    name: "CantinaIQ",
    tagline: "Slurpini Partner Intelligence",
  },
  nav: {
    overview: "Overview",
    recommendation: "Recommendation",
    matrix: "Matrix",
    wines: "Wines",
    regions: "Regions",
    producers: "Producers",
    bias: "Bias",
    stability: "Stability",
    methodology: "Methodology",
    forEvaluators: "For Evaluators",
  },
  breadcrumb: {
    overview: "Overview",
    recommendation: "Recommendation",
    matrix: "Opportunity Matrix",
    wines: "Wines",
    regions: "Regions",
    producers: "Producers",
    bias: "Bias",
    stability: "Stability",
    methodology: "Methodology",
    forEvaluators: "For Evaluators",
  },
  footer: {
    overview: "Overview",
    recommendation: "Recommendation",
    forEvaluators: "For Evaluators",
  },
  common: {
    language: "Language",
  },
};
```

- [ ] **Step 2: Create `src/i18n/locales/nl.ts`** (typed against `en` — missing keys become compile errors)

```ts
import { en } from "./en";

export const nl: typeof en = {
  brand: {
    name: "CantinaIQ",
    tagline: "Slurpini Partner Intelligence",
  },
  nav: {
    overview: "Overzicht",
    recommendation: "Aanbeveling",
    matrix: "Matrix",
    wines: "Wijnen",
    regions: "Regio's",
    producers: "Producenten",
    bias: "Vertekening",
    stability: "Stabiliteit",
    methodology: "Methodologie",
    forEvaluators: "Voor beoordelaars",
  },
  breadcrumb: {
    overview: "Overzicht",
    recommendation: "Aanbeveling",
    matrix: "Kansenmatrix",
    wines: "Wijnen",
    regions: "Regio's",
    producers: "Producenten",
    bias: "Vertekening",
    stability: "Stabiliteit",
    methodology: "Methodologie",
    forEvaluators: "Voor beoordelaars",
  },
  footer: {
    overview: "Overzicht",
    recommendation: "Aanbeveling",
    forEvaluators: "Voor beoordelaars",
  },
  common: {
    language: "Taal",
  },
};
```

- [ ] **Step 3: Create `src/i18n/index.ts`**

```ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { en } from "./locales/en";
import { nl } from "./locales/nl";

export const LANGUAGES = ["en", "nl"] as const;
export type Language = (typeof LANGUAGES)[number];

const STORAGE_KEY = "cantinaiq.lang";

function initialLanguage(): Language {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "nl" || stored === "en" ? stored : "en";
}

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, nl: { translation: nl } },
  lng: initialLanguage(),
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

i18n.on("languageChanged", (lng) => {
  localStorage.setItem(STORAGE_KEY, lng);
  document.documentElement.lang = lng;
});
document.documentElement.lang = i18n.language;

export default i18n;
```

- [ ] **Step 4: Create `src/@types/i18next.d.ts`**

```ts
import "i18next";
import type { en } from "../i18n/locales/en";

declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: "translation";
    resources: { translation: typeof en };
  }
}
```

- [ ] **Step 5: Wire i18n + Radix provider in `src/main.tsx`**

Replace the file with:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import * as Tooltip from "@radix-ui/react-tooltip";
import App from "./App";
import "./i18n";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Tooltip.Provider delayDuration={150}>
        <App />
      </Tooltip.Provider>
    </BrowserRouter>
  </React.StrictMode>,
);
```

- [ ] **Step 6: Type-check**

Run: `npx tsc -b`
Expected: PASS (no errors). If `nl.ts` is missing a key, this is where it fails.

- [ ] **Step 7: Commit** (only if the user has authorised commits)

```bash
git add src/i18n src/@types src/main.tsx package.json package-lock.json
git commit -m "feat(dashboard): add i18n core (react-i18next) + radix tooltip provider"
```

---

## Task 3: Language toggle component + header/breadcrumb/footer

**Files:**
- Create: `src/components/LanguageToggle.tsx`
- Modify: `src/App.tsx`

- [ ] **Step 1: Create `src/components/LanguageToggle.tsx`**

```tsx
import { useTranslation } from "react-i18next";
import { LANGUAGES } from "../i18n";

export default function LanguageToggle() {
  const { i18n, t } = useTranslation();
  const current = i18n.language.startsWith("nl") ? "nl" : "en";
  return (
    <div
      role="group"
      aria-label={t("common.language")}
      className="inline-flex items-center rounded-full border border-stone-300 overflow-hidden text-xs"
    >
      {LANGUAGES.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => void i18n.changeLanguage(l)}
          aria-pressed={current === l}
          className={`px-2.5 py-1 font-semibold uppercase tracking-wider transition-colors ${
            current === l ? "bg-tuscan text-white" : "text-ink-2 hover:text-tuscan"
          }`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Update `src/App.tsx`** — import `useTranslation` and `LanguageToggle`; derive `NAV_ITEMS`/`PAGE_LABEL` labels from `t()`; render `<LanguageToggle/>` at the end of the header `<nav>` (after the For-Evaluators pill); replace the hardcoded "Overview" in `Breadcrumb` and `Footer`, the tagline, and footer links with `t()` calls.

Key replacements (mechanical):
- `NAV_ITEMS` labels → `t("nav.overview")` … built inside the component (move the array inside `App`/`Breadcrumb` so `t` is in scope, or map `to`→key).
- Breadcrumb `label` → `t("breadcrumb.<key>")` keyed off pathname.
- Tagline `"— Slurpini Partner Intelligence"` → `t("brand.tagline")`.
- Footer links → `t("footer.*")`.

- [ ] **Step 3: Type-check**

Run: `npx tsc -b`
Expected: PASS.

- [ ] **Step 4: Browser check**

Start dev server (`npm run dev`), load `/`. Confirm the `EN | NL` toggle renders in the header; clicking `NL` switches nav/footer labels to Dutch; reload preserves the choice (localStorage); `<html lang>` updates.

- [ ] **Step 5: Commit** (if authorised)

```bash
git add src/components/LanguageToggle.tsx src/App.tsx
git commit -m "feat(dashboard): language toggle + translated header/breadcrumb/footer"
```

---

## Task 4: Translate Overview page (proof-of-pattern)

**Files:**
- Modify: `src/i18n/locales/en.ts`, `src/i18n/locales/nl.ts`, `src/pages/Overview.tsx`

- [ ] **Step 1:** Read `src/pages/Overview.tsx`. List every key text: page title, section headings, metric labels/captions, button/link text, table headers, short lead sentences. Leave long prose, data values, and domain terms (segment/recommendation names) untouched.

- [ ] **Step 2:** Add an `overview: { … }` namespace to `en.ts` with one key per string from Step 1. Use interpolation for embedded numbers, e.g. `wineCount: "{{count}} Italian wines"`.

- [ ] **Step 3:** Add the matching `overview: { … }` block to `nl.ts` with Dutch copy (natural, not literal). Same keys (enforced by `: typeof en`).

- [ ] **Step 4:** In `Overview.tsx`, `const { t } = useTranslation();` and replace each listed string with `t("overview.<key>", { count })` as needed.

- [ ] **Step 5: Type-check** — `npx tsc -b` → PASS.

- [ ] **Step 6: Browser check** — load `/`, toggle EN/NL, confirm Overview UI translates while prose/domain terms stay English. Screenshot both languages.

- [ ] **Step 7: Commit** (if authorised) — `feat(dashboard): translate Overview page`.

---

## Tasks 5–13: Translate remaining pages (one per task)

For each of: **Recommendation, Matrix, Wines, Regions, Producers, Bias, Stability, Methodology, ForEvaluators** — repeat the exact Task 4 procedure against `src/pages/<Page>.tsx`, using a namespace named after the page (`recommendation.*`, `matrix.*`, `wines.*`, `regions.*`, `producers.*`, `bias.*`, `stability.*`, `methodology.*`, `forEvaluators.*`).

Per page:
- [ ] Read the page; list key texts (titles, headings, labels, buttons, table headers, lead sentences).
- [ ] Add namespace to `en.ts`; add matching Dutch block to `nl.ts`.
- [ ] Replace strings with `t("<ns>.<key>")` (interpolate numbers).
- [ ] `npx tsc -b` → PASS.
- [ ] Browser check: toggle EN/NL on the page; long prose stays English. Screenshot.
- [ ] Commit (if authorised): `feat(dashboard): translate <Page> page`.

**Methodology + Regions note:** these are prose-heavy. Translate only headings/labels/lead sentences; the dense explanatory paragraphs and `regionMeta` descriptions stay English (they receive glossary tooltips in Task 15).

---

## Task 14: Translate modals + shared components

**Files:**
- Modify: `src/components/Modal.tsx`, `WineDetailModal.tsx`, `ProducerDetailModal.tsx`, `RegionDetailModal.tsx`, `MetricCard.tsx`, `RecommendationPill.tsx`
- Modify: `src/i18n/locales/en.ts`, `nl.ts`

- [ ] **Step 1:** Read each component; list key texts (modal titles, field labels, section headings, close/action buttons, "no data" states). Leave long explanatory paragraphs for the glossary layer; leave domain terms (RecommendationPill text) canonical English.
- [ ] **Step 2:** Add a `modal: { … }` namespace (plus per-component sub-keys) to `en.ts`; matching Dutch in `nl.ts`.
- [ ] **Step 3:** Replace strings with `t()` in each component.
- [ ] **Step 4: Type-check** — `npx tsc -b` → PASS.
- [ ] **Step 5: Browser check** — open each modal in EN and NL; labels translate, domain terms + long prose stay English. Screenshot one modal in both languages.
- [ ] **Step 6: Commit** (if authorised) — `feat(dashboard): translate modals + shared components`.

---

## Task 15: Glossary data + GlossedText component

**Files:**
- Create: `src/i18n/glossary.ts`, `src/components/GlossedText.tsx`

- [ ] **Step 1: Create `src/i18n/glossary.ts`** — curated map. Seed from methodology/region/modal vocabulary. Keys are canonical English terms (lower-cased lookup), values the Dutch explanation.

```ts
export interface GlossEntry {
  /** Dutch explanation shown on hover/focus in NL mode. */
  nl: string;
}

// Keyed by the exact display term (case-insensitive match at render time).
export const GLOSSARY: Record<string, GlossEntry> = {
  "defensible shortlist": { nl: "Een onderbouwde, verdedigbare selectie — elke keuze is herleidbaar naar de data en config." },
  "weighted rating": { nl: "Bayesiaans gewogen beoordeling: weinig reviews trekken richting het dataset-gemiddelde, zodat 4.8/12 niet boven 4.4/5000 eindigt." },
  "bayesian shrinkage": { nl: "Statistische correctie die onzekere scores (weinig reviews) naar het gemiddelde 'krimpt'." },
  "shrinkage threshold": { nl: "De parameter m die bepaalt hoe sterk weinig-gereviewde wijnen naar het gemiddelde worden getrokken." },
  "value for money": { nl: "Kwaliteit per euro — de verhouding tussen beoordeling en prijs." },
  "market confidence": { nl: "Betrouwbaarheid van het signaal op basis van het aantal reviews." },
  "premium fit": { nl: "Hoe goed een producent past bij Slurpini's premium-positionering." },
  "portfolio opportunity": { nl: "Strategische meerwaarde: vult een gat in het assortiment." },
  "composite score": { nl: "De gewogen totaalscore over alle vijf de factoren." },
  "contamination": { nl: "Aangenomen aandeel afwijkingen (anomalieën) dat het Isolation-Forest-model verwacht." },
  "isolation forest": { nl: "Machine-learning-methode die ongebruikelijke reviewpatronen (uitschieters) detecteert." },
  "bootstrap": { nl: "Herhaald herbemonsteren van de data om betrouwbaarheidsintervallen op de ranking te schatten." },
  "confidence interval": { nl: "Bandbreedte (5e–95e percentiel) waarbinnen de werkelijke ranking-positie waarschijnlijk valt." },
  "terroir": { nl: "Samenspel van bodem, klimaat en ligging dat het karakter van een wijn bepaalt." },
  "macro-region": { nl: "Overkoepelende wijnregio waaronder appellaties en subregio's vallen." },
  "docg": { nl: "Denominazione di Origine Controllata e Garantita — hoogste Italiaanse herkomstklasse." },
  "doc": { nl: "Denominazione di Origine Controllata — gecontroleerde Italiaanse herkomstbenaming." },
  "kendall-τ": { nl: "Rangcorrelatie (Kendall's tau): meet hoe stabiel de top-ranking blijft als een parameter verandert." },
};
```

- [ ] **Step 2: Create `src/components/GlossedText.tsx`** — renders a string; in NL mode wraps each glossary term's first occurrence (whole-word, case-insensitive) in a Radix tooltip; otherwise renders plain text. Includes a `Term` for explicit inline glossing.

```tsx
import { useMemo, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import * as Tooltip from "@radix-ui/react-tooltip";
import { GLOSSARY } from "../i18n/glossary";

function Glossed({ term, children }: { term: string; children: ReactNode }) {
  const entry = GLOSSARY[term.toLowerCase()];
  if (!entry) return <>{children}</>;
  return (
    <Tooltip.Root>
      <Tooltip.Trigger asChild>
        <span
          tabIndex={0}
          className="underline decoration-dotted decoration-tuscan/60 underline-offset-2 cursor-help"
        >
          {children}
        </span>
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Content
          side="top"
          sideOffset={6}
          className="max-w-xs rounded-md bg-ink text-cream text-xs leading-snug px-3 py-2 shadow-lg z-50"
        >
          {entry.nl}
          <Tooltip.Arrow className="fill-ink" />
        </Tooltip.Content>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}

export function Term({ term, children }: { term: string; children?: ReactNode }) {
  return <Glossed term={term}>{children ?? term}</Glossed>;
}

export default function GlossedText({ children }: { children: string }) {
  const { i18n } = useTranslation();
  const nl = i18n.language.startsWith("nl");

  const nodes = useMemo<ReactNode[]>(() => {
    if (!nl) return [children];
    const terms = Object.keys(GLOSSARY).sort((a, b) => b.length - a.length);
    // Build a single alternation regex, longest-first, word-boundaried.
    const escaped = terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const re = new RegExp(`\\b(${escaped.join("|")})\\b`, "gi");
    const seen = new Set<string>();
    const out: ReactNode[] = [];
    let last = 0;
    let m: RegExpExecArray | null;
    let i = 0;
    while ((m = re.exec(children)) !== null) {
      const key = m[0].toLowerCase();
      if (seen.has(key)) continue; // first occurrence per term only
      seen.add(key);
      if (m.index > last) out.push(children.slice(last, m.index));
      out.push(<Glossed key={i++} term={m[0]}>{m[0]}</Glossed>);
      last = m.index + m[0].length;
    }
    if (last < children.length) out.push(children.slice(last));
    return out;
  }, [children, nl]);

  return <>{nodes}</>;
}
```

- [ ] **Step 3: Type-check** — `npx tsc -b` → PASS.

- [ ] **Step 4: Commit** (if authorised) — `feat(dashboard): glossary data + GlossedText tooltip component`.

---

## Task 16: Apply glossary to prose containers

**Files:**
- Modify: `src/pages/Methodology.tsx`, `src/components/RegionDetailModal.tsx` (and other long-prose blocks identified in Tasks 5–14)

- [ ] **Step 1:** In `Methodology.tsx`, wrap the long explanatory paragraph blocks: `<GlossedText>{paragraphString}</GlossedText>`. Where prose is composed of inline JSX rather than a plain string, use explicit `<Term term="…">` around the difficult words instead.
- [ ] **Step 2:** In `RegionDetailModal.tsx`, wrap the region `notes`/`climate`/`terroir` description strings in `<GlossedText>`.
- [ ] **Step 3:** Wrap any other long-prose paragraphs noted during page/modal tasks.
- [ ] **Step 4: Type-check** — `npx tsc -b` → PASS.
- [ ] **Step 5: Browser check** — in NL mode, hover/focus a glossed term in Methodology and in a region modal; tooltip shows Dutch explanation; Esc closes; in EN mode no glossing appears. Screenshot a tooltip open in NL.
- [ ] **Step 6: Commit** (if authorised) — `feat(dashboard): apply glossary tooltips to prose`.

---

## Task 17: Final verification

- [ ] **Step 1: Full type-check + build** — `npx tsc -b && npm run build` → PASS (this is the authoritative key-parity guard).
- [ ] **Step 2: Cross-page browser sweep** — load every route; toggle EN→NL→EN; confirm: no raw `t()` keys visible, no console errors, domain terms + long prose stay English, glossary tooltips only in NL. Screenshot Overview + Methodology in both languages.
- [ ] **Step 3: Commit** (if authorised) — `chore(dashboard): finalise bilingual NL/EN + glossary`.

---

## Self-Review (completed)

- **Spec coverage:** Layer 1 switch → Tasks 2–14; Layer 2 glossary → Tasks 15–16; default EN + persistence + `<html lang>` → Task 2; key parity → `nl: typeof en` + `tsc -b` throughout; NL-only tooltips → `GlossedText` language guard; Radix tooltip → Tasks 1/2/15. All spec sections mapped.
- **Placeholder scan:** Infra tasks (1–3, 15) contain complete code. Repetitive page/modal tasks (4–14) give the full mechanical procedure + concrete namespace names + interpolation rule rather than transcribing ~3.8k LOC of strings; the executor extracts strings by reading each file. This is intentional, not a placeholder.
- **Type consistency:** `en`/`nl` use identical namespace keys; `GlossedText` default export + named `Term`; `LANGUAGES`/`Language` exported from `src/i18n/index.ts` and consumed by `LanguageToggle`. Consistent.
