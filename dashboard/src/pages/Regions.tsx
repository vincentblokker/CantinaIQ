import { useEffect, useState } from "react";
import { Region, loadRegions } from "../lib/data";

export default function Regions() {
  const [rows, setRows] = useState<Region[]>([]);
  useEffect(() => {
    loadRegions().then((rs) =>
      setRows([...rs].sort((a, b) => b.weighted_rating - a.weighted_rating)),
    );
  }, []);

  return (
    <div>
      <h2 className="font-serif text-2xl text-ink mb-4">Region intelligence</h2>
      <table className="w-full text-sm border border-stone-200 rounded-lg overflow-hidden bg-white">
        <thead className="bg-stone-50 text-ink-2 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">Region</th>
            <th className="text-right px-3 py-2">Wines</th>
            <th className="text-right px-3 py-2">Weighted rating</th>
            <th className="text-right px-3 py-2">Avg price (€)</th>
            <th className="text-right px-3 py-2">Reviews</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {rows.slice(0, 50).map((r) => (
            <tr key={r.region}>
              <td className="px-3 py-2 font-serif">{r.region}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.wines}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.weighted_rating.toFixed(2)}</td>
              <td className="text-right tabular-nums px-3 py-2">{Math.round(r.avg_price)}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.total_reviews.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
