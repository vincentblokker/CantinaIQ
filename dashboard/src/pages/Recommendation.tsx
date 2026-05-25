import { RECOMMENDATION, VerdictItem } from "../lib/pdfData";

export default function Recommendation() {
  return (
    <div className="space-y-10">
      <header>
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          Section 05 · The Recommendation
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2">
          What the data tells Slurpini to do
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl leading-relaxed">
          A three-part verdict. <strong>Hold</strong> the prestige tier,{" "}
          <strong>Expand</strong> in the value-opportunity zone,{" "}
          <strong>Audit</strong> the high-rating borderline. Each is qualified by
          Vivino bias and bootstrap stability — see <a href="/bias" className="text-tuscan underline">/bias</a> and{" "}
          <a href="/stability" className="text-tuscan underline">/stability</a>.
        </p>
      </header>

      <VerdictBlock
        kind="Hold"
        accent="border-purple-300 bg-purple-50/30"
        badge="bg-purple-100 text-purple-800 border-purple-200"
        title="The defensible anchor"
        intro="The data confirms what Slurpini already does. These are the wines whose presence in the portfolio is uncontroversial."
        items={RECOMMENDATION.hold}
      />

      <VerdictBlock
        kind="Expand"
        accent="border-green-300 bg-green-50/30"
        badge="bg-green-100 text-green-800 border-green-200"
        title="The value-opportunity zone"
        intro="Above-median weighted rating at well-below-median price. Bias-corrected — under-represented regions carry a tag."
        items={RECOMMENDATION.expand}
      />

      <VerdictBlock
        kind="Audit"
        accent="border-amber-300 bg-amber-50/30"
        badge="bg-amber-100 text-amber-800 border-amber-200"
        title="The borderline producers"
        intro="Top-ten by accident with too few reviews. Worth a tasting before either dismissing or recommending."
        items={RECOMMENDATION.audit}
      />
    </div>
  );
}

interface BlockProps {
  kind: string;
  title: string;
  intro: string;
  accent: string;
  badge: string;
  items: readonly VerdictItem[];
}

function VerdictBlock({ kind, title, intro, accent, badge, items }: BlockProps) {
  return (
    <section className={`rounded-2xl border ${accent} p-6`}>
      <div className="flex items-baseline gap-3 mb-2">
        <span className={`px-2 py-0.5 text-xs rounded-full border font-semibold uppercase tracking-wider ${badge}`}>
          {kind}
        </span>
        <h2 className="font-serif text-2xl text-ink">{title}</h2>
      </div>
      <p className="text-ink-2 text-sm mb-4 max-w-3xl">{intro}</p>
      <ol className="space-y-3">
        {items.map((item) => (
          <li
            key={item.name}
            className="bg-white rounded-lg border border-stone-200 px-5 py-4"
          >
            <div className="flex items-baseline justify-between gap-4 flex-wrap">
              <div>
                <div className="font-serif text-lg text-ink">{item.name}</div>
                <div className="text-xs uppercase tracking-wide text-ink-2 mt-0.5">
                  {item.detail}
                </div>
              </div>
              <div className="flex gap-5 text-sm text-ink-2 tabular-nums">
                <span>★ {item.weightedRating.toFixed(2)}</span>
                {item.reviews !== undefined && (
                  <span>{item.reviews.toLocaleString()} reviews</span>
                )}
                {item.avgPrice !== undefined && (
                  <span>€{item.avgPrice.toLocaleString()}</span>
                )}
              </div>
            </div>
            {item.note && (
              <p className="text-sm text-ink-2 mt-2 leading-relaxed">{item.note}</p>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
