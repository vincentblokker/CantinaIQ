import { useEffect, useState } from "react";
import { Producer, loadProducers } from "../lib/data";
import RecommendationPill from "../components/RecommendationPill";

export default function Producers() {
  const [rows, setRows] = useState<Producer[]>([]);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    loadProducers().then((ps) =>
      setRows([...ps].sort((a, b) => b.composite_score - a.composite_score)),
    );
  }, []);

  const filtered =
    filter === "all" ? rows : rows.filter((r) => r.recommendation === filter);

  return (
    <div>
      <div className="flex items-baseline gap-3 mb-4">
        <h2 className="font-serif text-2xl text-ink">Producer shortlist</h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="ml-auto text-sm border border-stone-300 rounded px-2 py-1 bg-white"
        >
          <option value="all">All recommendations</option>
          <option value="Premium Brand Builder">Premium Brand Builder</option>
          <option value="Target">Target</option>
          <option value="Value Opportunity">Value Opportunity</option>
          <option value="Monitor">Monitor</option>
          <option value="Avoid for Now">Avoid for Now</option>
        </select>
      </div>
      <table className="w-full text-sm border border-stone-200 rounded-lg overflow-hidden bg-white">
        <thead className="bg-stone-50 text-ink-2 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">Producer</th>
            <th className="text-left px-3 py-2">Macro region</th>
            <th className="text-left px-3 py-2">Recommendation</th>
            <th className="text-right px-3 py-2">Weighted rating</th>
            <th className="text-right px-3 py-2">Avg price (€)</th>
            <th className="text-right px-3 py-2">Composite</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {filtered.slice(0, 100).map((p) => (
            <tr
              key={p.producer_name}
              className="odd:bg-white even:bg-stone-50/60 hover:bg-stone-100/80 transition-colors"
            >
              <td className="px-3 py-2 font-serif">{p.producer_name}</td>
              <td className="px-3 py-2 text-ink-2">{p.macro_region}</td>
              <td className="px-3 py-2"><RecommendationPill value={p.recommendation} /></td>
              <td className="text-right tabular-nums px-3 py-2">{p.weighted_rating.toFixed(2)}</td>
              <td className="text-right tabular-nums px-3 py-2">{Math.round(p.avg_price)}</td>
              <td className="text-right tabular-nums px-3 py-2">{p.composite_score.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
