import { useEffect, useMemo, useState } from "react";
import { Wine, loadWines } from "../lib/data";
import WineDetailModal from "../components/WineDetailModal";
import { SEGMENTS } from "../lib/pdfData";

function segmentStyle(segment: string): string {
  const seg = SEGMENTS.find((s) => s.name === segment);
  return seg?.colorClass ?? "bg-stone-50 text-stone-700 border-stone-200";
}

export default function Wines() {
  const [rows, setRows] = useState<Wine[]>([]);
  const [selected, setSelected] = useState<Wine | null>(null);
  const [query, setQuery] = useState("");
  const [segmentFilter, setSegmentFilter] = useState("all");

  useEffect(() => {
    loadWines().then((ws) =>
      setRows([...ws].sort((a, b) => b.composite_score - a.composite_score)),
    );
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((w) => {
      if (segmentFilter !== "all" && w.market_segment !== segmentFilter) return false;
      if (q) {
        const hay = `${w.wine_name} ${w.producer_name} ${w.region} ${w.macro_region}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [rows, query, segmentFilter]);

  return (
    <div>
      <div className="flex items-baseline gap-3 mb-1 flex-wrap">
        <h2 className="font-serif text-2xl text-ink">Wine shortlist</h2>
        <p className="text-xs text-ink-2 italic">
          Click <span className="inline-flex w-4 h-4 rounded-full border border-tuscan/40 text-tuscan items-center justify-center text-[10px] font-bold align-middle">i</span> on any wine for vintage, segment, region context, and per-wine enrichment ideas.
        </p>
      </div>

      <div className="rounded-lg border border-tuscan/30 bg-tuscan/5 px-4 py-3 mb-5 text-sm text-ink">
        <strong>Scope note.</strong> This page shows the top-100 wines by composite
        score — the deliberate <em>shortlist</em> the pipeline exports for the
        dashboard. The full 2,986-wine dataset lives in{" "}
        <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded text-xs">supercharged/data/processed/wines_scored.parquet</code>{" "}
        — replay the run with the supercharged CLI to query it directly. A
        future JSON export of all 2,986 is an obvious next step (see the
        Methodology page for the cleaning cascade).
      </div>

      <div className="flex items-baseline gap-3 flex-wrap mb-4">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search wine name, producer, region…"
          className="flex-1 min-w-[240px] max-w-md text-sm border border-stone-300 rounded px-3 py-1.5 bg-white focus:border-tuscan focus:outline-none focus:ring-1 focus:ring-tuscan/30"
        />
        <select
          value={segmentFilter}
          onChange={(e) => setSegmentFilter(e.target.value)}
          className="text-sm border border-stone-300 rounded px-2 py-1.5 bg-white focus:border-tuscan focus:outline-none focus:ring-1 focus:ring-tuscan/30"
        >
          <option value="all">All segments</option>
          {SEGMENTS.map((s) => (
            <option key={s.name} value={s.name}>
              {s.name}
            </option>
          ))}
        </select>
        <span className="ml-auto text-xs text-ink-2 tabular-nums">
          {filtered.length === rows.length
            ? `${rows.length} wines`
            : `${filtered.length} of ${rows.length}`}
        </span>
      </div>

      <table className="w-full text-sm border border-stone-200 rounded-lg overflow-hidden bg-white">
        <thead className="bg-stone-50 text-ink-2 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">Wine</th>
            <th className="text-left px-3 py-2">Producer</th>
            <th className="text-left px-3 py-2">Macro region</th>
            <th className="text-left px-3 py-2">Segment</th>
            <th className="text-right px-3 py-2">★</th>
            <th className="text-right px-3 py-2">Reviews</th>
            <th className="text-right px-3 py-2">€</th>
            <th className="text-right px-3 py-2 w-10"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {filtered.map((w) => (
            <tr
              key={w.wine_name}
              className="odd:bg-white even:bg-stone-50/60 hover:bg-stone-100/80 transition-colors"
            >
              <td className="px-3 py-2 font-serif">
                {w.wine_name}
                {w.vintage && (
                  <span className="ml-2 text-xs text-ink-2 font-mono">
                    {w.vintage}
                  </span>
                )}
              </td>
              <td className="px-3 py-2 text-ink-2 text-xs">{w.producer_name}</td>
              <td className="px-3 py-2 text-ink-2 text-xs">{w.macro_region}</td>
              <td className="px-3 py-2">
                <span
                  className={`px-2 py-0.5 text-[10px] rounded-full border font-semibold ${segmentStyle(w.market_segment)}`}
                >
                  {w.market_segment}
                </span>
              </td>
              <td className="text-right tabular-nums px-3 py-2">
                {w.weighted_rating.toFixed(2)}
              </td>
              <td className="text-right tabular-nums px-3 py-2 text-xs">
                {w.rating_count.toLocaleString()}
              </td>
              <td className="text-right tabular-nums px-3 py-2">
                {Math.round(w.price)}
              </td>
              <td className="px-3 py-2 text-right">
                <button
                  onClick={() => setSelected(w)}
                  aria-label={`More info about ${w.wine_name}`}
                  className="inline-flex items-center justify-center w-6 h-6 rounded-full border border-stone-300 text-ink-2 text-xs font-bold hover:border-tuscan hover:text-tuscan hover:scale-110 transition-all"
                >
                  i
                </button>
              </td>
            </tr>
          ))}
          {filtered.length === 0 && (
            <tr>
              <td colSpan={8} className="text-center text-ink-2 italic py-8">
                No wines match the current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <WineDetailModal wine={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
