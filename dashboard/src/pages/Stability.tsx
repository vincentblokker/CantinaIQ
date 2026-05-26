import {
  ANOMALIES,
  ANOMALIES_CONTAMINATION,
  ANOMALIES_TOTAL,
  BOOTSTRAP,
  RUN,
  SENSITIVITY,
} from "../lib/pdfData";

export default function Stability() {
  const stable = BOOTSTRAP.filter((b) => b.appearances >= 160);
  const borderline = BOOTSTRAP.filter((b) => b.p95 > 100);

  return (
    <div className="space-y-10">
      <header>
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          Section 07 · Stability and anomalies
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2">
          How defensible is the ranking?
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl leading-relaxed">
          Three complementary checks. Bootstrap rank intervals tell you which
          top-ten positions hold up under resampling. The sensitivity sweep
          tells you whether the answer changes if you turn the shrinkage knob.
          The anomaly forest flags rows that don't behave like the rest of the
          dataset.
        </p>
      </header>

      <section>
        <h2 className="font-serif text-2xl text-ink">Bootstrap rank stability</h2>
        <p className="text-sm text-ink-2 mt-1 mb-4 max-w-3xl">
          200 resamples of the cleaned dataset. Producers that fall outside the
          top-10 in a resample receive rank 11. A p95 above 100 means the
          producer made the top-10 by accident in this run — too few reviews to
          be stable.
        </p>
        <div className="grid grid-cols-2 gap-4 mb-5">
          <Note
            accent="border-purple-300 bg-purple-50/50"
            label="Stable picks"
            num={stable.length}
            desc="≥ 160 of 200 resamples in top-10"
          />
          <Note
            accent="border-amber-300 bg-amber-50/50"
            label="Borderline (audit)"
            num={borderline.length}
            desc="p95 > 100 — top-10 by accident"
          />
        </div>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Producer</th>
                <th className="px-4 py-3 text-right font-semibold">p05</th>
                <th className="px-4 py-3 text-right font-semibold">p50</th>
                <th className="px-4 py-3 text-right font-semibold">p95</th>
                <th className="px-4 py-3 text-right font-semibold">Appearances</th>
                <th className="px-4 py-3 text-right font-semibold">Verdict</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 [&_tr]:transition-colors [&_tr:hover]:bg-stone-50">
              {BOOTSTRAP.map((b) => {
                const stable = b.appearances >= 160;
                const flagged = b.p95 > 100;
                return (
                  <tr key={b.producer} className={flagged ? "bg-amber-50/40" : ""}>
                    <td className="px-4 py-3 text-ink font-serif">{b.producer}</td>
                    <td className="px-4 py-3 text-right text-ink-2 tabular-nums">{b.p05}</td>
                    <td className="px-4 py-3 text-right text-ink-2 tabular-nums">{b.p50}</td>
                    <td className={`px-4 py-3 text-right tabular-nums font-semibold ${flagged ? "text-amber-700" : "text-ink-2"}`}>
                      {b.p95}
                    </td>
                    <td className="px-4 py-3 text-right text-ink-2 tabular-nums">
                      {b.appearances}/{b.total}
                    </td>
                    <td className="px-4 py-3 text-right text-xs">
                      {flagged ? (
                        <span className="text-amber-700 font-semibold">audit</span>
                      ) : stable ? (
                        <span className="text-purple-700 font-semibold">stable</span>
                      ) : (
                        <span className="text-ink-2">noisy</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink">Sensitivity to shrinkage</h2>
        <p className="text-sm text-ink-2 mt-1 mb-4 max-w-3xl">
          Kendall-τ rank correlation of the top-twenty against a baseline of{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m = 200</code>.
          Larger <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m</code> pulls
          low-review producers further toward the global mean. The recommendation does not
          depend on a hair-thin choice of <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m</code>.
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">bayesian_m</th>
                <th className="px-4 py-3 text-left font-semibold">Kendall-τ</th>
                <th className="px-4 py-3 text-left font-semibold">Reading</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 [&_tr]:transition-colors [&_tr:hover]:bg-stone-50">
              {SENSITIVITY.map((s) => (
                <tr key={s.bayesianM} className={s.bayesianM === 200 ? "bg-tuscan/5" : ""}>
                  <td className="px-4 py-3 text-tuscan font-mono">{s.bayesianM}</td>
                  <td className="px-4 py-3 text-ink-2 tabular-nums">{s.kendallTau.toFixed(3)}</td>
                  <td className="px-4 py-3 text-ink-2">{s.reading}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-ink-2 mt-2">
          Logged run uses <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m = {RUN.bayesianM}</code> (auto-median strategy).
        </p>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink">Anomaly detection</h2>
        <p className="text-sm text-ink-2 mt-1 mb-4 max-w-3xl">
          An Isolation Forest at{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">
            contamination = {ANOMALIES_CONTAMINATION}
          </code>{" "}
          over the <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">
            (rating, log₁₀(reviews))
          </code>{" "}
          feature space flagged <strong className="text-ink">{ANOMALIES_TOTAL} of {RUN.winesTotal.toLocaleString()}</strong>{" "}
          wines as pattern-divergent. Flagged wines are not removed — the flag is
          informational. Top 10:
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Wine</th>
                <th className="px-4 py-3 text-left font-semibold">Region</th>
                <th className="px-4 py-3 text-right font-semibold">Rating</th>
                <th className="px-4 py-3 text-right font-semibold">Reviews</th>
                <th className="px-4 py-3 text-right font-semibold">Price</th>
                <th className="px-4 py-3 text-right font-semibold">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 [&_tr]:transition-colors [&_tr:hover]:bg-stone-50">
              {ANOMALIES.map((a) => (
                <tr key={a.name}>
                  <td className="px-4 py-3 text-ink font-serif">{a.name}</td>
                  <td className="px-4 py-3 text-ink-2 text-xs">{a.region}</td>
                  <td className="px-4 py-3 text-right text-ink-2 tabular-nums">{a.rating.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right text-ink-2 tabular-nums">{a.reviews.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-ink-2 tabular-nums">€{a.price.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right text-tuscan tabular-nums">{a.score.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-ink-2 mt-3 max-w-3xl">
          Typical hits: ratings ≥ 4.8 on fewer than 20 reviews (over-confident
          niches); ratings ≤ 3.2 on tens of thousands of reviews (controversial
          mass-market wines); price-against-rating outliers. The reviewer
          decides what to do with that.
        </p>
      </section>
    </div>
  );
}

interface NoteProps {
  label: string;
  num: number;
  desc: string;
  accent: string;
}

function Note({ label, num, desc, accent }: NoteProps) {
  return (
    <div className={`rounded-lg border ${accent} px-5 py-4 hover-lift`}>
      <div className="text-xs uppercase tracking-wide text-ink-2">{label}</div>
      <div className="font-serif text-3xl text-ink mt-1">{num}</div>
      <div className="text-xs text-ink-2 mt-1">{desc}</div>
    </div>
  );
}
