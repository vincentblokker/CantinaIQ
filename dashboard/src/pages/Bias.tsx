import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { BIAS_REGIONS } from "../lib/pdfData";

function colorFor(factor: number): string {
  if (factor >= 1.3) return "#8B3A2F";   // tuscan — over-represented
  if (factor >= 0.7) return "#5A4F44";   // ink-2 — within band
  return "#1F3A5F";                       // sea — under-represented
}

export default function Bias() {
  const sorted = [...BIAS_REGIONS].sort((a, b) => b.factor - a.factor);
  const over = sorted.filter((r) => r.factor >= 1.3);
  const under = sorted.filter((r) => r.factor < 0.7);
  const balanced = sorted.filter((r) => r.factor >= 0.7 && r.factor < 1.3);

  return (
    <div className="space-y-8">
      <header>
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          Section 02b · Bias quantification
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2">
          Vivino is not the Dutch wine market.
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl leading-relaxed">
          Regional distribution of the cleaned Italian Vivino dataset against
          ICE Amsterdam import statistics for the Netherlands. Values above 1.3
          mean Vivino over-represents that region; values below 0.7 mean it
          under-represents it. The bias does not invalidate the analysis —
          it shapes which recommendations need an asterisk.
        </p>
      </header>

      <section className="grid grid-cols-3 gap-4 stagger">
        <Callout
          number={over.length}
          label="Over-represented (×>1.3)"
          accent="text-tuscan"
        />
        <Callout
          number={balanced.length}
          label="Within band (0.7 – 1.3)"
          accent="text-ink-2"
        />
        <Callout
          number={under.length}
          label="Under-represented (×<0.7)"
          accent="text-sea"
        />
      </section>

      <section className="bg-white rounded-lg border border-stone-200 p-6">
        <h2 className="font-serif text-xl text-ink mb-1">
          Vivino / ICE NL ratio per region
        </h2>
        <p className="text-sm text-ink-2 mb-5">
          Bars below 1.0 mean Vivino has fewer wines than NL import share would
          predict. Bars above 1.0 mean over-supply.
        </p>
        <ResponsiveContainer width="100%" height={520}>
          <BarChart
            data={sorted}
            layout="vertical"
            margin={{ top: 4, right: 24, left: 24, bottom: 12 }}
          >
            <CartesianGrid stroke="#EEE7DE" strokeDasharray="3 3" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, "dataMax"]}
              tick={{ fontSize: 11, fill: "#5A4F44" }}
              tickFormatter={(v) => `×${v.toFixed(1)}`}
            />
            <YAxis
              type="category"
              dataKey="region"
              tick={{ fontSize: 11, fill: "#1F1B16" }}
              width={150}
            />
            <ReferenceLine x={1.0} stroke="#5A4F44" strokeDasharray="4 4" />
            <ReferenceLine x={0.7} stroke="#1F3A5F" strokeDasharray="2 6" />
            <ReferenceLine x={1.3} stroke="#8B3A2F" strokeDasharray="2 6" />
            <Tooltip
              cursor={{ fill: "rgba(184,58,31,0.05)" }}
              formatter={(value: number) => [`×${value.toFixed(2)}`, "factor"]}
              labelStyle={{ color: "#1F1B16", fontWeight: 600 }}
            />
            <Bar dataKey="factor" radius={[0, 4, 4, 0]}>
              {sorted.map((entry) => (
                <Cell key={entry.region} fill={colorFor(entry.factor)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section className="grid grid-cols-2 gap-6">
        <BiasGroup
          title="Under-represented — flag with asterisk"
          accent="border-sea/40 bg-sea/5"
          intro="If a recommendation involves these regions, mark it under-sampled. The Vivino signal is sparse there."
          items={under}
        />
        <BiasGroup
          title="Over-represented — trim confidence"
          accent="border-tuscan/40 bg-tuscan/5"
          intro="Vivino's Anglo-young user base over-supplies these regions. Recommendations need extra scrutiny."
          items={over}
        />
      </section>

      <section className="bg-stone-50 border border-stone-200 rounded-lg p-5 text-sm text-ink-2">
        <strong className="text-ink">Reading the chart:</strong> Toscana ×1.22 means
        Vivino contains 22% more Tuscan wines than NL imports would predict.
        Puglia ×0.61 means Vivino under-represents Apulian wines by 39%. The
        Vivino signal is most reliable in regions Slurpini already knows well —
        the opposite of where it most needs help.
      </section>
    </div>
  );
}

interface CalloutProps {
  number: number;
  label: string;
  accent: string;
}

function Callout({ number, label, accent }: CalloutProps) {
  return (
    <div className="bg-white rounded-lg border border-stone-200 px-5 py-5 hover-lift">
      <div className={`font-serif text-4xl ${accent}`}>{number}</div>
      <div className="text-xs uppercase tracking-wide text-ink-2 mt-2">{label}</div>
    </div>
  );
}

interface GroupProps {
  title: string;
  accent: string;
  intro: string;
  items: { region: string; factor: number; vivinoN: number }[];
}

function BiasGroup({ title, accent, intro, items }: GroupProps) {
  return (
    <div className={`rounded-lg border ${accent} p-5 hover-lift`}>
      <h3 className="font-serif text-lg text-ink mb-1">{title}</h3>
      <p className="text-sm text-ink-2 mb-3">{intro}</p>
      <ul className="space-y-1.5 text-sm">
        {items.map((r) => (
          <li key={r.region} className="flex justify-between tabular-nums">
            <span className="text-ink">{r.region}</span>
            <span className="text-ink-2">
              ×{r.factor.toFixed(2)} · n={r.vivinoN}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
