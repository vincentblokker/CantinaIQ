import { useEffect, useMemo, useState } from "react";
import { Producer, loadProducers } from "../lib/data";
import RecommendationPill from "../components/RecommendationPill";
import ProducerDetailModal from "../components/ProducerDetailModal";

export default function Producers() {
  const [rows, setRows] = useState<Producer[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Producer | null>(null);

  useEffect(() => {
    loadProducers().then((ps) =>
      setRows([...ps].sort((a, b) => b.composite_score - a.composite_score)),
    );
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((r) => {
      if (filter !== "all" && r.recommendation !== filter) return false;
      if (q && !r.producer_name.toLowerCase().includes(q) && !r.macro_region.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [rows, filter, query]);

  return (
    <div>
      <div className="flex items-baseline gap-3 mb-2 flex-wrap">
        <h2 className="font-serif text-2xl text-ink">Producer shortlist</h2>
        <p className="text-xs text-ink-2 italic ml-2">
          Click <span className="inline-flex w-4 h-4 rounded-full border border-tuscan/40 text-tuscan items-center justify-center text-[10px] font-bold align-middle">i</span> for context, map, and enrichment roadmap.
        </p>
      </div>

      <div className="flex items-baseline gap-3 flex-wrap mb-4">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search producer or macro-region…"
          className="flex-1 min-w-[240px] max-w-md text-sm border border-stone-300 rounded px-3 py-1.5 bg-white focus:border-tuscan focus:outline-none focus:ring-1 focus:ring-tuscan/30"
        />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="text-sm border border-stone-300 rounded px-2 py-1.5 bg-white focus:border-tuscan focus:outline-none focus:ring-1 focus:ring-tuscan/30"
        >
          <option value="all">All recommendations</option>
          <option value="Premium Brand Builder">Premium Brand Builder</option>
          <option value="Target">Target</option>
          <option value="Value Opportunity">Value Opportunity</option>
          <option value="Monitor">Monitor</option>
          <option value="Avoid for Now">Avoid for Now</option>
        </select>
        <span className="ml-auto text-xs text-ink-2 tabular-nums">
          {filtered.length === rows.length
            ? `${rows.length} producers`
            : `${filtered.length} of ${rows.length}`}
        </span>
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
            <th className="text-right px-3 py-2 w-10"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {filtered.map((p) => (
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
              <td className="px-3 py-2 text-right">
                <button
                  onClick={() => setSelected(p)}
                  aria-label={`More info about ${p.producer_name}`}
                  className="inline-flex items-center justify-center w-6 h-6 rounded-full border border-stone-300 text-ink-2 text-xs font-bold hover:border-tuscan hover:text-tuscan hover:scale-110 transition-all"
                >
                  i
                </button>
              </td>
            </tr>
          ))}
          {filtered.length === 0 && (
            <tr>
              <td colSpan={7} className="text-center text-ink-2 italic py-8">
                No producers match the current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <ProducerDetailModal producer={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
