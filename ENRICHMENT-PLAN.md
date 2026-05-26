# ENRICHMENT PLAN

The dashboard's region / producer / wine modals each surface a list of
"enrichments" — additional data sources that would change the
recommendation if integrated. This document tracks **what is shipped**,
**what is deferred**, and **what unlocks each deferred item**.

The framing is deliberate. The roadmap is not a wish-list. Each item
has a concrete source, a concrete cost, and a concrete reason it sits
where it sits.

---

## Decision rule

> **Paid services are skipped for the ADA submission window.**
>
> Anything that requires a paid critic database, a billing-account API
> key, or Firecrawl credits beyond the existing pipeline run is deferred
> with an explicit blocker note. The decision can be revisited if a
> budget is allocated.

This rule is what separates "shipped" from "deferred" below. It is
visible in the modals — green check for shipped, grey ring for deferred,
with the specific blocker named on each item.

---

## Region modal — 4 shipped, 3 deferred

### ✓ Shipped — curated from open sources

1. **DOC/DOCG appellation count**
   *Per macro region. Curated from MIPAAF / EU eAmbrosia registry data,
   point-in-time approximation as of 2023.*

2. **Annual production volume (hl)**
   *ISTAT viticulture statistics, 2022–2023.*

3. **Vintage quality grades 2018–2024**
   *Letter grades A+/A/A-/B+/B/C reflecting consensus expert
   assessment per region per year. Sourced from public-domain
   summaries of Decanter, Jancis Robinson, and Wine Enthusiast charts.
   Honest about approximation — "—" used for vintages too recent for
   full assessment.*

4. **Climate + terroir summary**
   *2–3 sentence climate description and 1–2 sentence terroir note per
   macro region. Curated from regional consorzio publications and
   Italian Wine Central reference material.*

All four sit in [`dashboard/src/lib/regionMeta.ts`](dashboard/src/lib/regionMeta.ts)
as a single source of truth. The modal renders them with explicit
provenance text so the evaluator sees both the data and where it came
from.

### ○ Deferred — paid sources

1. **NL trade volume (€) per region**
   - **Source**: ICE Amsterdam customs statistics
   - **Blocker**: published only as bound PDF annual reports;
     no API. Manual extraction required, possibly via Eurostat Comext
     or CBS Trade as alternative.
   - **Cost to unlock**: ~4–5 hours of one-off data wrangling.

2. **Travel cost from Amsterdam per region**
   - **Source**: Google Maps Directions API (free tier exists but
     a billing-account credit card is required)
   - **Blocker**: billing-account requirement equates to a paid
     service per project policy.
   - **Cost to unlock**: trivial — ~2 hours to integrate once the
     account is set up.

3. **Producer biodynamic certifications at 762-producer scale**
   - **Source**: Demeter (demeter.net) + FederBio (federbio.it)
     public registries, queried via Firecrawl
   - **Blocker**: existing `cantinaiq sustainability` command already
     proves the integration for 5 producers; scaling to 762 requires
     additional Firecrawl credits beyond the current run budget.
   - **Cost to unlock**: ~5 hours of pipeline work; Firecrawl credits
     proportional to producer count.

---

## Producer modal — 0 shipped, 7 deferred

All producer-level enrichments require paid services or paid scraping
at scale. None of them have been delivered. The modal lists each with
its source and blocker:

| Item | Source | Blocker |
|---|---|---|
| Estate website + contact info | Producer's own .it/.com domain | Firecrawl credits at 762-producer scale |
| Hectares + farming method | Demeter + FederBio public registries | Firecrawl credits to scale from 5 to 762 |
| Annual production volume (bottles/yr) | Producer site + Wine-Searcher | Wine-Searcher trade API is paid commercial subscription |
| Critic scores per vintage | Wine Advocate · Suckling · Spectator · Decanter | All four are paywalled critic databases |
| Distribution markets | Wine-Searcher trade locator | Wine-Searcher trade API is paid |
| Travel from Amsterdam | Google Maps Directions API | Billing-account credit card required |
| Recent press mentions (2024–2026) | Decanter · Drinks Business · Wine Industry Advisor | Press monitoring requires paid scraping or LLM credits per query |

Each item is explicitly listed in [`ProducerDetailModal.tsx`](dashboard/src/components/ProducerDetailModal.tsx)
with its blocker visible to the evaluator. Honest scope is the
substance of this section.

---

## Wine modal — 0 shipped, 5 deferred

Per-wine attributes the Vivino export aggregates away. All require
either a paid critic source or per-wine Firecrawl scraping.

| Item | Source | Blocker |
|---|---|---|
| Vintage variation per wine | Vivino vintage endpoints · Wine Advocate · Suckling | Vivino partner credentials + paywalled critics |
| Grape composition (DOC/DOCG-rule compliant) | Consorzio + producer technical sheets | Per-producer scraping → Firecrawl credits at scale |
| Cellar-aging window | Wine-Searcher drinking windows · Decanter | Wine-Searcher API is paid |
| Food-pairing notes | Producer tasting notes | Firecrawl per-wine scrape + LLM normalisation pass |
| Alcohol % + residual sugar | Producer technical sheets · Vivino product pages | Deep per-wine scrape → Firecrawl credits |

---

## What changes if a budget is allocated

A reasonable phased unlock, ordered by impact per euro:

### Phase A — ~€50–100 of Firecrawl credits, ~1 day

1. Demeter + FederBio scale-up to 762 producers
   - Highest impact: directly ties to Slurpini's stated USP
   - Already-built pipeline command, just needs more credits
   - Output: badge per producer + count per region in the bias report

### Phase B — Google Maps billing-account + ~5 hours dev

2. Travel time + cost from Amsterdam per region
   - Free tier comfortably covers one-off region lookups (~20 calls)
   - Unblocks the operational dimension of the recommendation

### Phase C — ICE Amsterdam manual extraction + ~5 hours

3. NL trade volume (€) per region
   - No software cost, just data-wrangling time
   - Unblocks bias-report absolute-scale calibration

### Phase D — Paid critic-database subscription, ongoing

4. Wine Advocate / James Suckling integration
   - Highest cost, highest defensibility against critic-aware buyers
   - Outside the scope of this submission

Total to fully close the producer + wine roadmaps: ~3–5 days dev work
plus the per-source paid access. Not in scope for the ADA window.

---

## Why this matters for the submission

The PDF argues that *methodology choices are governance choices*.
The same applies to *enrichment choices*. Surfacing the deferred items
with their blockers, rather than hiding them or making vague "we could
do more" claims, is the same governance discipline applied to scope.

A future maintainer (or evaluator) can answer three questions from
this file alone:

1. What does the dashboard currently enrich beyond Vivino? — see Shipped
2. What was considered but not done? — see Deferred
3. What would it take to unlock each? — see Phase A–D

That is the same shape of governance the brief PDF closes on.

---

*Last edited as Region modal shipped its 4 enrichments. Next edit will
be either: (a) one of the deferred items moves to Shipped, or (b) the
"why this matters" framing gets retired because the entire roadmap is
empty.*
