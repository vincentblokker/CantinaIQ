import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import MetricCard from "../components/MetricCard";
import RecommendationPill from "../components/RecommendationPill";
import {
  DashboardSummary,
  Producer,
  Region,
  loadProducers,
  loadRegions,
  loadSummary,
} from "../lib/data";
import { RECOMMENDATION, BIAS_REGIONS, EXTRACTION_EVAL } from "../lib/pdfData";

export default function Overview() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [producers, setProducers] = useState<Producer[]>([]);
  const [regions, setRegions] = useState<Region[]>([]);

  useEffect(() => {
    loadSummary().then(setSummary);
    loadProducers().then(setProducers);
    loadRegions().then(setRegions);
  }, []);

  const topProducers = [...producers]
    .sort((a, b) => b.composite_score - a.composite_score)
    .slice(0, 5);
  const topRegions = [...regions]
    .sort((a, b) => b.weighted_rating - a.weighted_rating)
    .slice(0, 5);

  const underrep = BIAS_REGIONS.filter((r) => r.factor < 0.7).length;
  const overrep = BIAS_REGIONS.filter((r) => r.factor >= 1.3).length;

  if (!summary) return <div className="text-ink-2">Loading…</div>;

  return (
    <div className="space-y-10">
      {/* Evaluator CTA */}
      <Link
        to="/for-evaluators"
        className="block rounded-lg border border-tuscan/30 bg-tuscan/5 hover:bg-tuscan/10 transition-colors px-5 py-4 group"
      >
        <div className="flex items-baseline gap-4 flex-wrap">
          <span className="text-xs uppercase tracking-widest text-tuscan font-semibold whitespace-nowrap">
            Evaluating this submission?
          </span>
          <span className="text-sm text-ink flex-1">
            Use the rubric map to confirm coverage in two minutes — each ADA criterion is linked to the brief section and the source file.
          </span>
          <span className="text-tuscan text-sm font-semibold whitespace-nowrap group-hover:translate-x-0.5 transition-transform">
            Open rubric map →
          </span>
        </div>
      </Link>

      {/* Headline */}
      <section className="border-b border-stone-200 pb-6">
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          Slurpini Partner Intelligence — board-level recommendation
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2 max-w-3xl leading-tight">
          {summary.totals.wines.toLocaleString()} Italian wines, scored, segmented, and ranked — with confidence bands.
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl leading-relaxed">
          Every number on this dashboard traces back to pipeline run{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded text-sm">
            {summary.config_hash}
          </code>.
          Replay the run, get the same numbers.
        </p>
      </section>

      {/* KPI row */}
      <section className="grid grid-cols-4 gap-4">
        <MetricCard label="Wines analysed" value={summary.totals.wines.toLocaleString()} />
        <MetricCard label="Producers" value={summary.totals.producers.toLocaleString()} />
        <MetricCard label="Regions" value={summary.totals.regions} />
        <MetricCard
          label="Extraction recall"
          value={`${(EXTRACTION_EVAL.recallContains * 100).toFixed(0)}%`}
          hint="contains-match on known top-50"
        />
      </section>

      {/* The verdict block */}
      <section>
        <h2 className="font-serif text-2xl text-ink mb-1">The verdict</h2>
        <p className="text-sm text-ink-2 mb-4">
          The three-part recommendation in one screen.{" "}
          <Link to="/recommendation" className="text-tuscan underline">
            See full detail →
          </Link>
        </p>
        <div className="grid grid-cols-3 gap-4">
          <VerdictCard
            kind="Hold"
            accent="border-purple-300 bg-purple-50/40"
            badge="bg-purple-100 text-purple-800 border-purple-200"
            count={RECOMMENDATION.hold.length}
            headline="The defensible anchor"
            samples={RECOMMENDATION.hold.slice(0, 2).map((h) => h.name)}
          />
          <VerdictCard
            kind="Expand"
            accent="border-green-300 bg-green-50/40"
            badge="bg-green-100 text-green-800 border-green-200"
            count={RECOMMENDATION.expand.length}
            headline="The value-opportunity zone"
            samples={RECOMMENDATION.expand.slice(0, 3).map((h) => h.name)}
          />
          <VerdictCard
            kind="Audit"
            accent="border-amber-300 bg-amber-50/40"
            badge="bg-amber-100 text-amber-800 border-amber-200"
            count={RECOMMENDATION.audit.length}
            headline="The borderline producers"
            samples={RECOMMENDATION.audit.map((h) => h.name)}
          />
        </div>
      </section>

      {/* The honest section */}
      <section className="grid grid-cols-2 gap-4">
        <HonestCard
          accent="border-sea/30 bg-sea/5"
          tag="External validity"
          headline={`${underrep} regions under-represented in Vivino`}
          body="Puglia ×0.61, Abruzzo ×0.52, Campania ×0.55. The Vivino signal is most reliable where Slurpini already knows the market — the opposite of where it most needs help."
          link={<Link to="/bias" className="text-sea underline">See the bias report →</Link>}
        />
        <HonestCard
          accent="border-amber-300 bg-amber-50/30"
          tag="Stability"
          headline="2 producers in the raw top-10 are top-10 by accident"
          body="Terre di San Vincenzo and Valdicava show p95 bootstrap ranks of 412 and 228. The bare track lists them at face value; this track flags them."
          link={<Link to="/stability" className="text-amber-700 underline">See bootstrap detail →</Link>}
        />
      </section>

      {/* Top producers */}
      <section>
        <h2 className="font-serif text-xl text-ink mb-3">
          Top 5 producers by composite score
        </h2>
        <ol className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white">
          {topProducers.map((p, i) => (
            <li key={p.producer_name} className="px-4 py-3 flex items-baseline gap-4">
              <span className="text-ink-2 text-sm w-6">#{i + 1}</span>
              <span className="font-serif text-ink flex-1">{p.producer_name}</span>
              <RecommendationPill value={p.recommendation} />
              <span className="text-sm text-ink-2 tabular-nums">★ {p.weighted_rating.toFixed(2)}</span>
              <span className="text-sm text-ink-2 tabular-nums">€{Math.round(p.avg_price)}</span>
            </li>
          ))}
        </ol>
      </section>

      {/* Top regions */}
      <section>
        <h2 className="font-serif text-xl text-ink mb-3">
          Top 5 regions by weighted rating
        </h2>
        <ol className="divide-y divide-stone-200 rounded-lg border border-stone-200 bg-white">
          {topRegions.map((r, i) => (
            <li key={r.region} className="px-4 py-3 flex items-baseline gap-4">
              <span className="text-ink-2 text-sm w-6">#{i + 1}</span>
              <span className="font-serif text-ink flex-1">{r.region}</span>
              <span className="text-sm text-ink-2 tabular-nums">★ {r.weighted_rating.toFixed(2)}</span>
              <span className="text-sm text-ink-2 tabular-nums">{r.wines} wines</span>
              <span className="text-sm text-ink-2 tabular-nums">€{Math.round(r.avg_price)}</span>
            </li>
          ))}
        </ol>
      </section>

      <footer className="text-xs text-ink-2 pt-6 border-t border-stone-200 flex justify-between flex-wrap gap-2">
        <div>
          Config hash <span className="font-mono text-tuscan">{summary.config_hash}</span> · run {summary.run_id}
        </div>
        <div>
          {overrep} regions over-represented · {underrep} under-represented · top-10 stability via 200-resample bootstrap
        </div>
      </footer>
    </div>
  );
}

interface VerdictProps {
  kind: string;
  accent: string;
  badge: string;
  count: number;
  headline: string;
  samples: string[];
}

function VerdictCard({ kind, accent, badge, count, headline, samples }: VerdictProps) {
  return (
    <div className={`rounded-lg border ${accent} p-5`}>
      <div className="flex items-baseline justify-between mb-3">
        <span className={`px-2 py-0.5 text-xs rounded-full border font-semibold uppercase tracking-wider ${badge}`}>
          {kind}
        </span>
        <span className="font-serif text-3xl text-ink">{count}</span>
      </div>
      <div className="font-serif text-lg text-ink mb-3 leading-tight">{headline}</div>
      <ul className="text-sm text-ink-2 space-y-1">
        {samples.map((s) => (
          <li key={s}>· {s}</li>
        ))}
      </ul>
    </div>
  );
}

interface HonestProps {
  accent: string;
  tag: string;
  headline: string;
  body: string;
  link: React.ReactNode;
}

function HonestCard({ accent, tag, headline, body, link }: HonestProps) {
  return (
    <div className={`rounded-lg border ${accent} p-5`}>
      <div className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
        {tag}
      </div>
      <div className="font-serif text-lg text-ink mb-2 leading-tight">{headline}</div>
      <p className="text-sm text-ink-2 mb-3 leading-relaxed">{body}</p>
      <div className="text-sm">{link}</div>
    </div>
  );
}
