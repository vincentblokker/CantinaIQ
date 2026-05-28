import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Region, loadRegions } from "../lib/data";
import RegionDetailModal from "../components/RegionDetailModal";

export default function Regions() {
  const { t } = useTranslation();
  const [rows, setRows] = useState<Region[]>([]);
  const [selected, setSelected] = useState<Region | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    loadRegions().then((rs) =>
      setRows([...rs].sort((a, b) => b.weighted_rating - a.weighted_rating)),
    );
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter(
      (r) =>
        r.region.toLowerCase().includes(q) ||
        (r.macro_region ?? "").toLowerCase().includes(q),
    );
  }, [rows, query]);

  return (
    <div>
      <div className="flex items-baseline justify-between gap-4 flex-wrap mb-2">
        <h2 className="font-serif text-2xl text-ink">{t("regions.title")}</h2>
        <p className="text-xs text-ink-2 italic">
          {t("regions.hintPre")} <span className="inline-flex w-4 h-4 rounded-full border border-tuscan/40 text-tuscan items-center justify-center text-[10px] font-bold align-middle">i</span> {t("regions.hintPost")}
        </p>
      </div>

      <div className="flex items-baseline justify-between gap-3 flex-wrap mb-4">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("regions.searchPlaceholder")}
          className="flex-1 min-w-[240px] max-w-md text-sm border border-stone-300 rounded px-3 py-1.5 bg-white focus:border-tuscan focus:outline-none focus:ring-1 focus:ring-tuscan/30"
        />
        <span className="text-xs text-ink-2 tabular-nums">
          {filtered.length === rows.length
            ? t("regions.countAll", { regions: rows.length })
            : t("regions.countFiltered", { shown: filtered.length, total: rows.length })}
        </span>
      </div>

      <table className="w-full text-sm border border-stone-200 rounded-lg overflow-hidden bg-white">
        <thead className="bg-stone-50 text-ink-2 text-xs uppercase tracking-wide">
          <tr>
            <th className="text-left px-3 py-2">{t("regions.colRegion")}</th>
            <th className="text-left px-3 py-2">{t("regions.colMacroRegion")}</th>
            <th className="text-right px-3 py-2">{t("regions.colWines")}</th>
            <th className="text-right px-3 py-2">{t("regions.colWeightedRating")}</th>
            <th className="text-right px-3 py-2">{t("regions.colAvgPrice")}</th>
            <th className="text-right px-3 py-2">{t("regions.colReviews")}</th>
            <th className="text-right px-3 py-2 w-10"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {filtered.map((r) => (
            <tr
              key={r.region}
              className="odd:bg-white even:bg-stone-50/60 hover:bg-stone-100/80 transition-colors"
            >
              <td className="px-3 py-2 font-serif">{r.region}</td>
              <td className="px-3 py-2 text-ink-2 text-xs">{r.macro_region ?? "—"}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.wines}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.weighted_rating.toFixed(2)}</td>
              <td className="text-right tabular-nums px-3 py-2">{Math.round(r.avg_price)}</td>
              <td className="text-right tabular-nums px-3 py-2">{r.total_reviews.toLocaleString()}</td>
              <td className="px-3 py-2 text-right">
                <button
                  onClick={() => setSelected(r)}
                  aria-label={t("regions.moreInfo", { name: r.region })}
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
                {t("regions.empty", { query })}
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <RegionDetailModal region={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
