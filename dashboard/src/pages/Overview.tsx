import { useEffect, useState } from "react";
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

  if (!summary) return <div className="text-ink-2">Loading…</div>;

  return (
    <div className="space-y-8">
      <section className="grid grid-cols-3 gap-4">
        <MetricCard label="Wines analysed" value={summary.totals.wines.toLocaleString()} />
        <MetricCard label="Regions" value={summary.totals.regions} />
        <MetricCard label="Producers" value={summary.totals.producers.toLocaleString()} />
      </section>

      <section>
        <h2 className="font-serif text-xl text-ink mb-3">Top 5 producers</h2>
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

      <section>
        <h2 className="font-serif text-xl text-ink mb-3">Top 5 regions</h2>
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

      <footer className="text-xs text-ink-2 pt-6 border-t border-stone-200">
        Config hash <span className="font-mono">{summary.config_hash}</span> · run {summary.run_id}
      </footer>
    </div>
  );
}
