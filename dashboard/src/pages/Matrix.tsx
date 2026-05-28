import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useDomainLabels } from "../i18n/domainLabels";
import { Producer, loadProducers } from "../lib/data";
import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

const COLOUR_BY_SEGMENT: Record<string, string> = {
  "Hidden Gem": "#4A6B36",
  "Premium Icon": "#1F3A5F",
  "Commercial Value": "#8B7355",
  "Overpriced Risk": "#9B3A2F",
  "Low Confidence Niche": "#8B7355",
};

export default function Matrix() {
  const { t } = useTranslation();
  const dl = useDomainLabels();
  const [rows, setRows] = useState<Producer[]>([]);
  useEffect(() => {
    loadProducers().then(setRows);
  }, []);

  const data = rows.map((p) => ({
    x: p.avg_price,
    y: p.weighted_rating,
    z: p.total_reviews,
    name: p.producer_name,
    segment: p.market_segment,
    fill: COLOUR_BY_SEGMENT[p.market_segment] ?? "#888",
  }));

  return (
    <div>
      <h2 className="font-serif text-2xl text-ink mb-4">{t("matrix.title")}</h2>
      <div className="bg-white border border-stone-200 rounded-lg p-4">
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 30 }}>
            <CartesianGrid stroke="#eee" />
            <XAxis
              type="number"
              dataKey="x"
              name={t("matrix.axisPrice")}
              scale="log"
              domain={[1, 3000]}
              ticks={[5, 20, 50, 100, 300, 1000, 3000]}
              tickFormatter={(v) => `€${v}`}
            />
            <YAxis
              type="number"
              dataKey="y"
              name={t("matrix.axisRating")}
              domain={[3.0, 5.0]}
              tickFormatter={(v) => v.toFixed(1)}
            />
            <ZAxis dataKey="z" range={[20, 400]} />
            <Tooltip
              cursor={{ strokeDasharray: "3 3" }}
              content={({ payload }) => {
                if (!payload || payload.length === 0) return null;
                const p = payload[0].payload as {
                  name: string;
                  y: number;
                  x: number;
                  z: number;
                  segment: string;
                };
                return (
                  <div className="bg-white border border-stone-200 rounded p-2 text-xs">
                    <div className="font-serif text-ink">{p.name}</div>
                    <div>★ {p.y.toFixed(2)} · €{Math.round(p.x)} · {t("matrix.tooltipReviews", { reviews: p.z.toLocaleString() })}</div>
                    <div className="text-ink-2">{dl.segment(p.segment)}</div>
                  </div>
                );
              }}
            />
            <Scatter data={data} fill="#888" shape="circle" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-ink-2 mt-3">
        {t("matrix.legendAxes")} {t("matrix.legendQuadrants")}
      </p>
    </div>
  );
}
