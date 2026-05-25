// Embedded data from the supercharged pipeline run b7f16c72.
//
// Numbers here mirror the markdown reports in
// `supercharged/reports/generated/` and the strategy brief PDF. Embedded
// as TypeScript constants because the pipeline does not yet export them
// as JSON. When that lands, replace these constants with fetches from
// `/data/<name>.json` — the page components should not need to change.

export const RUN = {
  configHash: "b7f16c72",
  runId: "2026-05-25T13-27__b7f16c72",
  bayesianM: 948,
  globalMean: 4.0,
  winesTotal: 2986,
  producersTotal: 762,
  regionsTotal: 179,
  rawRows: 409777,
  testsPassing: 137,
  cliSubcommands: 14,
} as const;

// ── Recommendation (executive-summary.md) ──────────────────────────────

export interface VerdictItem {
  name: string;
  detail: string;
  weightedRating: number;
  reviews?: number;
  avgPrice?: number;
  note?: string;
}

export const RECOMMENDATION = {
  hold: [
    {
      name: "Tenuta Masseto",
      detail: "Toscane · Premium Icon",
      weightedRating: 4.30,
      reviews: 4641,
      avgPrice: 1567,
      note: "Top-10 in 195 of 200 bootstrap resamples — defensible anchor.",
    },
    {
      name: "Tenuta San Guido",
      detail: "Bolgheri Sassicaia · Premium Icon",
      weightedRating: 4.24,
      reviews: 6199,
      avgPrice: 764,
      note: "Same prestige band as Masseto.",
    },
    {
      name: "Marchesi Antinori",
      detail: "Toscane · Premium Icon",
      weightedRating: 4.20,
      reviews: 13363,
      avgPrice: 289,
      note: "Tignanello vintages anchor the portfolio.",
    },
  ] as VerdictItem[],

  expand: [
    {
      name: "Roma",
      detail: "Region · Value Opportunity",
      weightedRating: 4.12,
      note: "Above-median quality at below-median price. Not in the Toscana over-represented band.",
    },
    {
      name: "Torgiano",
      detail: "Region · Value Opportunity",
      weightedRating: 4.16,
      note: "Umbrian micro-region with strong rating-per-euro signal.",
    },
    {
      name: "Ischia",
      detail: "Region · Value Opportunity",
      weightedRating: 4.10,
      note: "Campanian island wines — niche but consistent.",
    },
    {
      name: "Puglia (Primitivo di Manduria)",
      detail: "Region · Value Opportunity",
      weightedRating: 4.13,
      note: "Strongest bare-track signal — but flag ×0.61 under-sample factor.",
    },
    {
      name: "Abruzzo",
      detail: "Region · Value Opportunity",
      weightedRating: 4.29,
      note: "×0.52 under-represented in Vivino vs ICE NL imports.",
    },
  ] as VerdictItem[],

  audit: [
    {
      name: "Terre di San Vincenzo",
      detail: "Bootstrap-borderline",
      weightedRating: 4.32,
      note: "p95 bootstrap rank = 412. Top-ten by accident with too few reviews.",
    },
    {
      name: "Valdicava",
      detail: "Bootstrap-borderline",
      weightedRating: 4.28,
      note: "p95 bootstrap rank = 228. Worth a tasting before either dismissing or recommending.",
    },
  ] as VerdictItem[],
} as const;

// ── Bias (bias-report.md, Vivino vs ICE NL imports) ────────────────────

export interface BiasRegion {
  region: string;
  vivinoN: number;
  vivinoPct: number;
  baselinePct: number;
  factor: number;       // <0.7 = under-represented, >1.3 = over-represented
}

export const BIAS_REGIONS: BiasRegion[] = [
  { region: "Toscana",              vivinoN: 1023, vivinoPct: 34.3, baselinePct: 28.0, factor: 1.22 },
  { region: "Piemonte",             vivinoN: 487,  vivinoPct: 16.3, baselinePct: 15.0, factor: 1.09 },
  { region: "Trentino-Alto Adige",  vivinoN: 90,   vivinoPct: 3.0,  baselinePct: 3.0,  factor: 1.00 },
  { region: "Veneto",               vivinoN: 526,  vivinoPct: 17.6, baselinePct: 18.0, factor: 0.98 },
  { region: "Lombardia",            vivinoN: 65,   vivinoPct: 2.2,  baselinePct: 2.5,  factor: 0.87 },
  { region: "Sicilia",              vivinoN: 241,  vivinoPct: 8.1,  baselinePct: 10.0, factor: 0.81 },
  { region: "Umbria",               vivinoN: 37,   vivinoPct: 1.2,  baselinePct: 2.0,  factor: 0.62 },
  { region: "Puglia",               vivinoN: 201,  vivinoPct: 6.7,  baselinePct: 11.0, factor: 0.61 },
  { region: "Emilia-Romagna",       vivinoN: 42,   vivinoPct: 1.4,  baselinePct: 2.5,  factor: 0.56 },
  { region: "Campania",             vivinoN: 41,   vivinoPct: 1.4,  baselinePct: 2.5,  factor: 0.55 },
  { region: "Marche",               vivinoN: 40,   vivinoPct: 1.3,  baselinePct: 2.5,  factor: 0.54 },
  { region: "Abruzzo",              vivinoN: 77,   vivinoPct: 2.6,  baselinePct: 5.0,  factor: 0.52 },
  { region: "Sardegna",             vivinoN: 38,   vivinoPct: 1.3,  baselinePct: 2.5,  factor: 0.51 },
  { region: "Friuli-Venezia Giulia",vivinoN: 37,   vivinoPct: 1.2,  baselinePct: 3.0,  factor: 0.41 },
  { region: "Other",                vivinoN: 18,   vivinoPct: 0.6,  baselinePct: 2.5,  factor: 0.24 },
  { region: "Lazio",                vivinoN: 8,    vivinoPct: 0.3,  baselinePct: 2.5,  factor: 0.11 },
  { region: "Basilicata",           vivinoN: 7,    vivinoPct: 0.2,  baselinePct: 2.5,  factor: 0.09 },
  { region: "Calabria",             vivinoN: 5,    vivinoPct: 0.2,  baselinePct: 2.5,  factor: 0.07 },
  { region: "Molise",               vivinoN: 3,    vivinoPct: 0.1,  baselinePct: 2.5,  factor: 0.04 },
];

// ── Bootstrap CI (bootstrap-ci.md, top-10) ─────────────────────────────

export interface BootstrapItem {
  producer: string;
  p05: number;
  p50: number;
  p95: number;
  mean: number;
  appearances: number;
  total: number;
}

export const BOOTSTRAP: BootstrapItem[] = [
  { producer: "Carpano",                p05: 1, p50: 1, p95: 11,  mean: 4.6,  appearances: 130, total: 200 },
  { producer: "Terre di San Vincenzo",  p05: 1, p50: 6, p95: 412, mean: 95.0, appearances: 124, total: 200 },
  { producer: "Tenuta Masseto",         p05: 2, p50: 4, p95: 9,   mean: 4.8,  appearances: 195, total: 200 },
  { producer: "Valdicava",              p05: 1, p50: 5, p95: 228, mean: 29.5, appearances: 126, total: 200 },
  { producer: "Biondi-Santi",           p05: 2, p50: 6, p95: 15,  mean: 7.9,  appearances: 160, total: 200 },
  { producer: "Capannelle",             p05: 3, p50: 7, p95: 11,  mean: 7.3,  appearances: 131, total: 200 },
  { producer: "Dal Forno Romano",       p05: 2, p50: 5, p95: 11,  mean: 5.9,  appearances: 185, total: 200 },
  { producer: "Rinforzo",               p05: 4, p50: 9, p95: 11,  mean: 8.6,  appearances: 118, total: 200 },
  { producer: "Villa Degli",            p05: 5, p50: 8, p95: 30,  mean: 12.0, appearances: 127, total: 200 },
  { producer: "Tenuta San Guido",       p05: 2, p50: 9, p95: 21,  mean: 9.9,  appearances: 129, total: 200 },
];

// ── Sensitivity (sensitivity.md) ───────────────────────────────────────

export const SENSITIVITY = [
  { bayesianM: 200, kendallTau: 1.000, reading: "Reference ranking" },
  { bayesianM: 500, kendallTau: 0.882, reading: "Strong agreement; minor re-orderings" },
  { bayesianM: 800, kendallTau: 0.765, reading: "Material re-ordering; small-n producers drop" },
] as const;

// ── Anomalies (anomalies.md, top-10 of 90) ─────────────────────────────

export interface AnomalyWine {
  name: string;
  region: string;
  rating: number;
  reviews: number;
  price: number;
  score: number;
}

export const ANOMALIES_TOTAL = 90;
export const ANOMALIES_CONTAMINATION = 0.03;

export const ANOMALIES: AnomalyWine[] = [
  { name: "Moncaro Brut Verdicchio Opale N.V.",       region: "Marche",                  rating: 3.20, reviews: 141,    price: 3.27,    score: -0.079 },
  { name: "San Marzano 60 Sessantanni Primitivo",     region: "Primitivo di Manduria",   rating: 4.50, reviews: 19020,  price: 184.00,  score: -0.075 },
  { name: "Mionetto Prestige Brut Prosecco N.V.",     region: "Prosecco di Treviso",     rating: 3.60, reviews: 26323,  price: 115.90,  score: -0.074 },
  { name: "Piccini Memoro Rosso N.V.",                region: "Toscane",                 rating: 3.80, reviews: 66173,  price: 9.95,    score: -0.067 },
  { name: "Farnese Edizione Cinque Autoctoni N.V.",   region: "Abruzzo",                 rating: 4.30, reviews: 63460,  price: 64.99,   score: -0.067 },
  { name: "Antinori Tignanello 2016",                 region: "Toscane",                 rating: 4.60, reviews: 13363,  price: 289.00,  score: -0.065 },
  { name: "Antinori Tignanello 2015",                 region: "Toscane",                 rating: 4.60, reviews: 13180,  price: 305.65,  score: -0.064 },
  { name: "San Marzano Cinquanta Collezione N.V.",    region: "Vino d'Italia",           rating: 4.30, reviews: 35850,  price: 19.95,   score: -0.061 },
  { name: "Antinori Tignanello 2018",                 region: "Toscane",                 rating: 4.70, reviews: 7145,   price: 247.07,  score: -0.058 },
  { name: "Giacomo Conterno Barolo Cascina Francia",  region: "Barolo",                  rating: 4.70, reviews: 148,    price: 866.25,  score: -0.055 },
];

// ── Methodology — 5-factor composite weights (methodology.md) ──────────

export const COMPOSITE_WEIGHTS = [
  { component: "Weighted Rating Score",      captures: "Bayesian-shrunk consumer preference",       weight: 35 },
  { component: "Market Confidence Score",    captures: "Rewards reliable consumer signal (review volume)", weight: 20 },
  { component: "Value for Money Score",      captures: "Quality at realistic price",                 weight: 20 },
  { component: "Premium Fit Score",          captures: "Alignment with Slurpini's premium positioning", weight: 15 },
  { component: "Portfolio Opportunity Score", captures: "Strategic gap-filling versus current import mix", weight: 10 },
] as const;

// ── Market segments and recommendations (taxonomy) ─────────────────────

export const SEGMENTS = [
  { name: "Hidden Gem",          rule: "High rating, low price, low review count.",   colorClass: "bg-green-50 border-green-200 text-green-800" },
  { name: "Premium Icon",        rule: "High rating, high price, high review count.", colorClass: "bg-purple-50 border-purple-200 text-purple-800" },
  { name: "Commercial Value",    rule: "Solid rating, low price, high review count.", colorClass: "bg-blue-50 border-blue-200 text-blue-800" },
  { name: "Overpriced Risk",     rule: "Moderate rating at premium price.",           colorClass: "bg-rose-50 border-rose-200 text-rose-800" },
  { name: "Low Confidence Niche", rule: "Rating present but signal too thin.",        colorClass: "bg-stone-50 border-stone-200 text-stone-700" },
] as const;

export const ACTIONS = [
  { name: "Target",                rationale: "Investigate now." },
  { name: "Premium Brand Builder", rationale: "Hold for prestige positioning." },
  { name: "Value Opportunity",     rationale: "Scale into volume." },
  { name: "Monitor",               rationale: "Re-evaluate next quarter." },
  { name: "Avoid for Now",         rationale: "Signal does not justify outreach cost." },
] as const;

// ── Cleaning cascade (data-quality.md) ─────────────────────────────────

export const CLEANING_CASCADE = [
  { stage: "Ingestion",  rowsOut: 409777, removed: 0,      topReason: "—" },
  { stage: "Cleaning",   rowsOut: 2986,   removed: 406791, topReason: "non_italian: 332,376 · duplicate: 74,396" },
  { stage: "Validation", rowsOut: 2986,   removed: 0,      topReason: "Pandera contracts pass" },
  { stage: "Enrichment", rowsOut: 2986,   removed: 0,      topReason: "Columns added, no rows dropped" },
  { stage: "Scoring",    rowsOut: 2986,   removed: 0,      topReason: "Composite added" },
  { stage: "Export",     rowsOut: 2986,   removed: 0,      topReason: "JSON + Parquet artefacts" },
] as const;

// ── Producer extraction eval (producer-extraction-eval.json mirror) ────

export const EXTRACTION_EVAL = {
  goldSize: 50,
  recallExact: 0.88,
  recallContains: 0.96,
  missed: ["Felsina", "Schiopetto"],
} as const;

// ── Sustainability (sustainability.md) ─────────────────────────────────

export const SUSTAINABILITY = [
  { producer: "Querciabella",          certification: "Demeter" as const,
    link: "https://www.demeter.net/producers/?search=Querciabella" },
  { producer: "Avignonesi",            certification: "Demeter" as const,
    link: "https://www.demeter.net/producers/?search=Avignonesi" },
  { producer: "Castello dei Rampolla", certification: null,
    link: null },
  { producer: "Antinori",              certification: "Demeter" as const,
    link: "https://www.demeter.net/producers/?search=Antinori" },
  { producer: "Tenuta San Guido",      certification: null,
    link: null },
];
