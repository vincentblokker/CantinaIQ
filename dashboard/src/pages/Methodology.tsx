import {
  ACTIONS,
  CLEANING_CASCADE,
  COMPOSITE_WEIGHTS,
  EXTRACTION_EVAL,
  RUN,
  SEGMENTS,
  SUSTAINABILITY,
} from "../lib/pdfData";
import { useTranslation } from "react-i18next";
import GlossedText, { Term } from "../components/GlossedText";

export default function Methodology() {
  const { t } = useTranslation();
  return (
    <div className="space-y-10">
      <header>
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          {t("methodology.eyebrow")}
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2">
          {t("methodology.title")}
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl leading-relaxed">
          The recommendation in <a href="/recommendation" className="text-tuscan underline">/recommendation</a> rests on a{" "}
          <Term term="composite score">composite score</Term> whose components are visible, weighted, and
          reproducible. The score is not the value of the document. The
          transparency of the score is.
        </p>
      </header>

      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("methodology.bayesianTitle")}
        </h2>
        <p className="text-sm text-ink-2 max-w-3xl mb-4">
          <GlossedText>
            A wine with a 4.8 rating on 12 reviews must not outrank a wine with a
            4.4 rating on 5,000 reviews. Both tracks apply the same shrinkage:
          </GlossedText>
        </p>
        <div className="bg-stone-50 border-l-4 border-tuscan px-5 py-4 font-mono text-lg text-ink">
          WR = ( n / (n + m) ) · r + ( m / (n + m) ) · μ
        </div>
        <div className="grid grid-cols-4 gap-3 mt-4 text-sm">
          <Fact label="r" value={t("methodology.factVivinoRating")} />
          <Fact label="n" value={t("methodology.factRatingCount")} />
          <Fact label="m" value={`${RUN.bayesianM} (auto-median)`} />
          <Fact label="μ" value={`${RUN.globalMean.toFixed(1)} (global mean)`} />
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("methodology.compositeTitle")}
        </h2>
        <p className="text-sm text-ink-2 max-w-3xl mb-4">
          The Slurpini Partner Intelligence Score is a weighted average of five
          normalised components. Weights are business assumptions, versioned
          per config snapshot.
        </p>
        <div className="space-y-2">
          {COMPOSITE_WEIGHTS.map((c) => (
            <div
              key={c.component}
              className="bg-white border border-stone-200 rounded-lg p-3 flex items-center gap-4 hover-lift"
            >
              <div className="flex-1">
                <div className="font-serif text-ink">{c.component}</div>
                <div className="text-xs text-ink-2 mt-0.5">{c.captures}</div>
              </div>
              <div className="flex items-center gap-3 w-64">
                <div className="flex-1 h-2 bg-stone-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-tuscan rounded-full transition-[width] duration-700 ease-out"
                    style={{ width: `${c.weight * 2.5}%` }}
                  />
                </div>
                <span className="font-serif text-lg text-ink tabular-nums w-12 text-right">
                  {c.weight}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("methodology.cleaningTitle")}
        </h2>
        <p className="text-sm text-ink-2 max-w-3xl mb-4">
          The dataset arrives as a {RUN.rawRows.toLocaleString()}-row,
          16-sheet Excel file with <Term term="mojibake">mojibake</Term> on diacritics, tuple-encoded
          country fields, and cross-sheet duplication. The cascade from raw to
          scored:
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">{t("methodology.thStage")}</th>
                <th className="px-4 py-3 text-right font-semibold">{t("methodology.thRowsOut")}</th>
                <th className="px-4 py-3 text-left font-semibold">{t("methodology.thTopReason")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {CLEANING_CASCADE.map((row) => (
                <tr key={row.stage}>
                  <td className="px-4 py-3 text-tuscan font-semibold">{row.stage}</td>
                  <td className="px-4 py-3 text-right text-ink tabular-nums">
                    {row.rowsOut.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-ink-2 text-xs">{row.topReason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("methodology.extractionTitle")}
        </h2>
        <p className="text-sm text-ink-2 max-w-3xl mb-4">
          Producer names are a string-extraction problem, not a field. A pass-1
          alias whitelist resolves the top-50; pass-2 LLM disambiguation via
          OpenRouter handles the remainder. Measured against{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">
            known_producers_top50.csv
          </code>:
        </p>
        <div className="grid grid-cols-3 gap-3">
          <Stat
            value={`${(EXTRACTION_EVAL.recallExact * 100).toFixed(0)}%`}
            label={t("methodology.statRecallExact")}
            sub={`${Math.round(EXTRACTION_EVAL.recallExact * EXTRACTION_EVAL.goldSize)} of ${EXTRACTION_EVAL.goldSize} gold producers`}
          />
          <Stat
            value={`${(EXTRACTION_EVAL.recallContains * 100).toFixed(0)}%`}
            label={t("methodology.statRecallContains")}
            sub={`${Math.round(EXTRACTION_EVAL.recallContains * EXTRACTION_EVAL.goldSize)} of ${EXTRACTION_EVAL.goldSize} gold producers`}
          />
          <Stat
            value={EXTRACTION_EVAL.missed.length}
            label={t("methodology.statMissed")}
            sub={EXTRACTION_EVAL.missed.join(" · ")}
          />
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("methodology.segmentsTitle")}
        </h2>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="font-serif text-lg text-ink mb-2">{t("methodology.segmentsSubhead")}</h3>
            <div className="space-y-2">
              {SEGMENTS.map((s) => (
                <div key={s.name} className="flex items-start gap-3">
                  <span className={`px-2 py-0.5 text-xs rounded-full border font-semibold ${s.colorClass} whitespace-nowrap`}>
                    {s.name}
                  </span>
                  <span className="text-sm text-ink-2">{s.rule}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h3 className="font-serif text-lg text-ink mb-2">{t("methodology.actionsSubhead")}</h3>
            <div className="space-y-2">
              {ACTIONS.map((a) => (
                <div key={a.name} className="flex items-start gap-3">
                  <span className="px-2 py-0.5 text-xs rounded-full border border-stone-300 bg-stone-50 text-stone-700 font-semibold whitespace-nowrap">
                    {a.name}
                  </span>
                  <span className="text-sm text-ink-2">{a.rationale}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("methodology.sustainabilityTitle")}
        </h2>
        <p className="text-sm text-ink-2 max-w-3xl mb-4">
          Sustainability is Slurpini's stated USP and is absent from the Vivino
          dataset.{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">
            cantinaiq sustainability
          </code>{" "}
          fills the gap by querying FederBio and Demeter via Firecrawl.
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">{t("methodology.thProducer")}</th>
                <th className="px-4 py-3 text-left font-semibold">{t("methodology.thCertification")}</th>
                <th className="px-4 py-3 text-left font-semibold">{t("methodology.thSource")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {SUSTAINABILITY.map((s) => (
                <tr key={s.producer}>
                  <td className="px-4 py-3 text-ink font-serif">{s.producer}</td>
                  <td className="px-4 py-3">
                    {s.certification ? (
                      <span className="px-2 py-0.5 text-xs rounded-full border border-leaf/40 bg-leaf/10 text-leaf font-semibold">
                        {s.certification}
                      </span>
                    ) : (
                      <span className="text-ink-2 text-xs">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {s.link && (
                      <a href={s.link} target="_blank" rel="noopener noreferrer"
                         className="text-tuscan text-xs underline">
                        {t("methodology.registryLink")}
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="border-t border-stone-200 pt-4 text-xs text-ink-2">
        Config hash <code className="text-tuscan">{RUN.configHash}</code> · run{" "}
        <code className="text-ink-2">{RUN.runId}</code> · {RUN.testsPassing} tests pass ·{" "}
        {RUN.cliSubcommands} CLI subcommands
      </footer>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-stone-200 rounded-lg px-4 py-3 bg-white hover-lift">
      <div className="text-tuscan font-mono text-lg">{label}</div>
      <div className="text-xs text-ink-2 mt-1">{value}</div>
    </div>
  );
}

function Stat({ value, label, sub }: { value: string | number; label: string; sub: string }) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white px-5 py-4 hover-lift">
      <div className="font-serif text-3xl text-tuscan">{value}</div>
      <div className="text-xs uppercase tracking-wide text-ink-2 mt-1">{label}</div>
      <div className="text-xs text-ink-2 mt-2 italic">{sub}</div>
    </div>
  );
}
