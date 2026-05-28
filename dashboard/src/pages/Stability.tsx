import { useTranslation } from "react-i18next";
import GlossedText, { Term } from "../components/GlossedText";
import { useNl } from "../i18n/domainLabels";
import {
  ANOMALIES,
  ANOMALIES_CONTAMINATION,
  ANOMALIES_TOTAL,
  BOOTSTRAP,
  RUN,
  SENSITIVITY,
} from "../lib/pdfData";

export default function Stability() {
  const { t } = useTranslation();
  const nl = useNl();
  const stable = BOOTSTRAP.filter((b) => b.appearances >= 160);
  const borderline = BOOTSTRAP.filter((b) => b.p95 > 100);

  return (
    <div className="space-y-10">
      <header>
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          {t("stability.eyebrow")}
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2">
          {t("stability.title")}
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl leading-relaxed">
          <GlossedText>
            {nl
              ? "Drie complementaire controles. Bootstrap-rangintervallen tonen welke top-tien-posities standhouden onder resampling. De gevoeligheidsanalyse laat zien of het antwoord verandert wanneer je aan de shrinkage-knop draait. Het anomalie-forest markeert rijen die zich niet gedragen zoals de rest van de dataset."
              : "Three complementary checks. Bootstrap rank intervals tell you which top-ten positions hold up under resampling. The sensitivity sweep tells you whether the answer changes if you turn the shrinkage knob. The anomaly forest flags rows that don't behave like the rest of the dataset."}
          </GlossedText>
        </p>
      </header>

      <section>
        <h2 className="font-serif text-2xl text-ink">{t("stability.bootstrapTitle")}</h2>
        <p className="text-sm text-ink-2 mt-1 mb-4 max-w-3xl">
          <GlossedText>
            {nl
              ? "200 resamples van de opgeschoonde dataset. Producenten die in een resample buiten de top-10 vallen, krijgen rang 11. Een p95 boven de 100 betekent dat de producent in deze run per ongeluk de top-10 haalde — te weinig reviews om stabiel te zijn."
              : "200 resamples of the cleaned dataset. Producers that fall outside the top-10 in a resample receive rank 11. A p95 above 100 means the producer made the top-10 by accident in this run — too few reviews to be stable."}
          </GlossedText>
        </p>
        <div className="grid grid-cols-2 gap-4 mb-5">
          <Note
            accent="border-purple-300 bg-purple-50/50"
            label={t("stability.noteStableLabel")}
            num={stable.length}
            desc={t("stability.noteStableDesc")}
          />
          <Note
            accent="border-amber-300 bg-amber-50/50"
            label={t("stability.noteBorderlineLabel")}
            num={borderline.length}
            desc={t("stability.noteBorderlineDesc")}
          />
        </div>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">{t("stability.colProducer")}</th>
                <th className="px-4 py-3 text-right font-semibold">p05</th>
                <th className="px-4 py-3 text-right font-semibold">p50</th>
                <th className="px-4 py-3 text-right font-semibold">p95</th>
                <th className="px-4 py-3 text-right font-semibold">{t("stability.colAppearances")}</th>
                <th className="px-4 py-3 text-right font-semibold">{t("stability.colVerdict")}</th>
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
                        <span className="text-amber-700 font-semibold">{t("stability.verdictAudit")}</span>
                      ) : stable ? (
                        <span className="text-purple-700 font-semibold">{t("stability.verdictStable")}</span>
                      ) : (
                        <span className="text-ink-2">{t("stability.verdictNoisy")}</span>
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
        <h2 className="font-serif text-2xl text-ink">{t("stability.sensitivityTitle")}</h2>
        <p className="text-sm text-ink-2 mt-1 mb-4 max-w-3xl">
          <Term term="kendall-τ">Kendall-τ</Term>
          {nl ? "-rangcorrelatie van de top-twintig tegen een baseline van" : " rank correlation of the top-twenty against a baseline of"}{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m = 200</code>.
          {nl ? " Een grotere " : " Larger "}<code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m</code>
          {nl
            ? " trekt producenten met weinig reviews verder naar het globale gemiddelde. De aanbeveling hangt niet af van een haarscherpe keuze van "
            : " pulls low-review producers further toward the global mean. The recommendation does not depend on a hair-thin choice of "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m</code>.
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">bayesian_m</th>
                <th className="px-4 py-3 text-left font-semibold">Kendall-τ</th>
                <th className="px-4 py-3 text-left font-semibold">{t("stability.colReading")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 [&_tr]:transition-colors [&_tr:hover]:bg-stone-50">
              {SENSITIVITY.map((s) => (
                <tr key={s.bayesianM} className={s.bayesianM === 200 ? "bg-tuscan/5" : ""}>
                  <td className="px-4 py-3 text-tuscan font-mono">{s.bayesianM}</td>
                  <td className="px-4 py-3 text-ink-2 tabular-nums">{s.kendallTau.toFixed(3)}</td>
                  <td className="px-4 py-3 text-ink-2">{nl ? s.readingNl : s.reading}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-ink-2 mt-2">
          {t("stability.loggedRunPre")}{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">m = {RUN.bayesianM}</code>{" "}
          {nl ? "(auto-mediaan-strategie)." : "(auto-median strategy)."}
        </p>
      </section>

      <section>
        <h2 className="font-serif text-2xl text-ink">{t("stability.anomalyTitle")}</h2>
        <p className="text-sm text-ink-2 mt-1 mb-4 max-w-3xl">
          {nl ? "Een " : "An "}<Term term="isolation forest">Isolation Forest</Term>{nl ? " bij " : " at "}{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">
            contamination = {ANOMALIES_CONTAMINATION}
          </code>{" "}
          {nl ? "over de feature-ruimte " : "over the "}<code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">
            (rating, log₁₀(reviews))
          </code>{" "}
          {nl ? "markeerde " : "feature space flagged "}<strong className="text-ink">{nl ? `${ANOMALIES_TOTAL} van de ${RUN.winesTotal.toLocaleString()}` : `${ANOMALIES_TOTAL} of ${RUN.winesTotal.toLocaleString()}`}</strong>{" "}
          {nl
            ? "wijnen als patroonafwijkend. Gemarkeerde wijnen worden niet verwijderd — de markering is informatief. Top 10:"
            : "wines as pattern-divergent. Flagged wines are not removed — the flag is informational. Top 10:"}
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">{t("stability.colWine")}</th>
                <th className="px-4 py-3 text-left font-semibold">{t("stability.colRegion")}</th>
                <th className="px-4 py-3 text-right font-semibold">{t("stability.colRating")}</th>
                <th className="px-4 py-3 text-right font-semibold">{t("stability.colReviews")}</th>
                <th className="px-4 py-3 text-right font-semibold">{t("stability.colPrice")}</th>
                <th className="px-4 py-3 text-right font-semibold">{t("stability.colScore")}</th>
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
          {nl
            ? "Typische treffers: beoordelingen ≥ 4,8 op minder dan 20 reviews (overmoedige niches); beoordelingen ≤ 3,2 op tienduizenden reviews (controversiële massamarktwijnen); prijs-tegen-beoordeling-uitschieters. De beoordelaar beslist wat daarmee te doen."
            : "Typical hits: ratings ≥ 4.8 on fewer than 20 reviews (over-confident niches); ratings ≤ 3.2 on tens of thousands of reviews (controversial mass-market wines); price-against-rating outliers. The reviewer decides what to do with that."}
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
