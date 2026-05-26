import { useEffect, useState } from "react";
import { Region, loadRegions } from "../lib/data";
import RegionDetailModal from "../components/RegionDetailModal";

export default function Regions() {
  const [rows, setRows] = useState<Region[]>([]);
  const [selected, setSelected] = useState<Region | null>(null);

  useEffect(() => {
    loadRegions().then((rs) =>
      setRows([...rs].sort((a, b) => b.weighted_rating - a.weighted_rating)),
    );
  }, []);

  return (
    <div>
      <div className="flex items-baseline justify-between gap-4 flex-wrap mb-4">
        <h2 className="font-serif text-2xl text-ink">Region intelligence</h2>
        <p className="text-xs text-ink-2 italic">
          Click <span className="inline-flex w-4 h-4 rounded-full border border-tuscan/40 text-tuscan items-center justify-center text-[10px] font-bold align-middle">i</span> next to any region for context, map, and enrichment roadmap.
        </p>
      </div>
      <table className="w-full text-sm border border-stone-200 rounded-lg overflow-hidden bg-white">
        <thead className="bg-stone-50 text-ink-2 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">Region</th>
            <th className="text-right px-3 py-2">Wines</th>
            <th className="text-right px-3 py-2">Weighted rating</th>
            <th className="text-right px-3 py-2">Avg price (€)</th>
            <th className="text-right px-3 py-2">Reviews</th>
            <th className="text-right px-3 py-2 w-10"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {rows.slice(0, 50).map((r) => (
            <tr
              key={r.region}
              className="odd:bg-white even:bg-stone-50/60 hover:bg-stone-100/80 transition-colors group"
            >
              <td className="px-3 py-2 font-serif">{r.region}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.wines}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.weighted_rating.toFixed(2)}</td>
              <td className="text-right tabular-nums px-3 py-2">{Math.round(r.avg_price)}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.total_reviews.toLocaleString()}</td>
              <td className="px-3 py-2 text-right">
                <button
                  onClick={() => setSelected(r)}
                  aria-label={`More info about ${r.region}`}
                  className="inline-flex items-center justify-center w-6 h-6 rounded-full border border-stone-300 text-ink-2 text-xs font-bold hover:border-tuscan hover:text-tuscan hover:scale-110 transition-all"
                >
                  i
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <RegionDetailModal region={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
