// Rubric mapping for /for-evaluators.
//
// Single source of truth for the rubric table on the dashboard page AND
// for the standalone evaluator-mapping.pdf. If you edit a row here, also
// update deploy/evaluator-pdf/source/evaluator-mapping.html to match.

const REPO = "https://github.com/vincentblokker/CantinaIQ";
const blob = (path: string) => `${REPO}/blob/main/${path}`;
const tree = (path: string) => `${REPO}/tree/main/${path}`;

export interface FiveMinuteRow {
  requirement: string;
  livesIn: string;
  href: string;
}

export const FIVE_MINUTE_READ: FiveMinuteRow[] = [
  {
    requirement: "(i) Crawler extension",
    livesIn: "bare/crawler-extension.py",
    href: blob("bare/crawler-extension.py"),
  },
  {
    requirement: "(ii) EDA + analysis",
    livesIn: "bare/notebooks/slurpini-analysis.ipynb",
    href: blob("bare/notebooks/slurpini-analysis.ipynb"),
  },
  {
    requirement: "(iii) Written recommendation",
    livesIn: "bare/recommendation.md",
    href: blob("bare/recommendation.md"),
  },
];

export interface RubricRow {
  criterion: string;
  briefSection: string;          // e.g. "§03 From the Field (p5)"
  artefacts: ArtefactLink[];     // 1+ artefact links shown in the Repo / Dashboard column
}

export interface ArtefactLink {
  label: string;                 // visible text
  href?: string;                 // external link (GitHub) — omit for plain text
  internal?: boolean;            // true for SPA links
}

export const RUBRIC: RubricRow[] = [
  {
    criterion: "Business framing of the problem",
    briefSection: "§03 From the Field · p5",
    artefacts: [{ label: "supercharged/PRD.md", href: blob("supercharged/PRD.md") }],
  },
  {
    criterion: "Crawler extension as deliverable",
    briefSection: "§07 Beyond the Brief · p14",
    artefacts: [{ label: "bare/crawler-extension.py", href: blob("bare/crawler-extension.py") }],
  },
  {
    criterion: "Exploratory data analysis",
    briefSection: "§02 Vivino in Context · p3-4",
    artefacts: [
      { label: "bare/notebooks/slurpini-analysis.ipynb", href: blob("bare/notebooks/slurpini-analysis.ipynb") },
      { label: "/matrix", internal: true },
    ],
  },
  {
    criterion: "Data cleaning + validation",
    briefSection: "§06 The Methodology · p13",
    artefacts: [{ label: "data-quality.md", href: blob("supercharged/reports/generated/data-quality.md") }],
  },
  {
    criterion: "Scoring methodology, transparent",
    briefSection: "§06 The Methodology · p12",
    artefacts: [
      { label: "methodology.md", href: blob("supercharged/reports/generated/methodology.md") },
      { label: "/methodology", internal: true },
    ],
  },
  {
    criterion: "Written recommendation, decision-ready",
    briefSection: "§05 The Recommendation · p10-11",
    artefacts: [
      { label: "bare/recommendation.md", href: blob("bare/recommendation.md") },
      { label: "/recommendation", internal: true },
    ],
  },
  {
    criterion: "Top-5 producers + regions ranking",
    briefSection: "§05 The Recommendation · p11",
    artefacts: [
      { label: "/producers", internal: true },
      { label: "/regions", internal: true },
    ],
  },
  {
    criterion: "Confidence intervals on the ranking",
    briefSection: "§02 · p4 · §07 · p15",
    artefacts: [
      { label: "bootstrap-ci.md", href: blob("supercharged/reports/generated/bootstrap-ci.md") },
      { label: "/stability", internal: true },
    ],
  },
  {
    criterion: "External validity / bias quantification",
    briefSection: "§02 · p4 · §07",
    artefacts: [
      { label: "bias-report.md", href: blob("supercharged/reports/generated/bias-report.md") },
      { label: "/bias", internal: true },
    ],
  },
  {
    criterion: "Reproducibility (config-hash, audit)",
    briefSection: "§06 · p13",
    artefacts: [
      { label: "supercharged/", href: tree("supercharged") },
      { label: "make demo", href: blob("Makefile") },
    ],
  },
  {
    criterion: "Sensitivity to parameters",
    briefSection: "§07 · p15",
    artefacts: [{ label: "sensitivity.md", href: blob("supercharged/reports/generated/sensitivity.md") }],
  },
  {
    criterion: "Anomaly detection",
    briefSection: "§07 · p15",
    artefacts: [{ label: "anomalies.md", href: blob("supercharged/reports/generated/anomalies.md") }],
  },
  {
    criterion: "Tests + schema contracts",
    briefSection: "§07 · p16",
    artefacts: [
      { label: "supercharged/tests/", href: tree("supercharged/tests") },
      { label: "make test", href: blob("Makefile") },
    ],
  },
  {
    criterion: "Dashboard / live data product",
    briefSection: "§07 · p16",
    artefacts: [{ label: "This site", internal: true }],
  },
  {
    criterion: "Enrichment scope discipline (shipped vs deferred)",
    briefSection: "§08 Enrichments · p17-19",
    artefacts: [
      { label: "ENRICHMENT-PLAN.md", href: blob("ENRICHMENT-PLAN.md") },
      { label: "/regions modal", internal: true },
    ],
  },
  {
    criterion: "Responsible-AI reflection",
    briefSection: "§09 Closing Observation · p20-21",
    artefacts: [{ label: "—" }],
  },
];
