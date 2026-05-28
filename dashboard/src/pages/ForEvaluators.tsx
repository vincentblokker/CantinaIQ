import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { FIVE_MINUTE_READ, RUBRIC } from "../lib/evaluatorMapping";

export default function ForEvaluators() {
  const { t } = useTranslation();
  return (
    <div className="space-y-10">
      <header>
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          {t("forEvaluators.eyebrow")}
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2">
          {t("forEvaluators.title")}
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl">
          {t("forEvaluators.intro")}
        </p>
      </header>

      {/* Section 0 — walkthrough video */}
      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("forEvaluators.videoTitle")}
        </h2>
        <p className="text-sm text-ink-2 mb-4 max-w-3xl">
          {t("forEvaluators.videoLead")}
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden shadow-sm">
          <video
            controls
            preload="metadata"
            poster="/downloads/walkthrough-poster.jpg"
            className="w-full block"
          >
            <source src="/downloads/walkthrough.mp4" type="video/mp4" />
            {t("forEvaluators.videoFallback")}{" "}
            <a href="/downloads/walkthrough.mp4">walkthrough.mp4</a>
          </video>
        </div>
        <p className="text-xs text-ink-2 mt-2">
          {t("forEvaluators.videoMeta")}{" "}
          <a
            href="/downloads/walkthrough.mp4"
            download
            className="text-tuscan underline font-mono"
          >
            walkthrough.mp4
          </a>
        </p>
      </section>

      {/* Section 1 — five-minute read */}
      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("forEvaluators.fiveMinTitle")}
        </h2>
        <p className="text-sm text-ink-2 mb-4 max-w-3xl">
          {t("forEvaluators.fiveMinLeadPre")}<code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">bare/</code>{t("forEvaluators.fiveMinLeadPost")}
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">{t("forEvaluators.colRequirement")}</th>
                <th className="px-4 py-3 text-left font-semibold">{t("forEvaluators.colLivesIn")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 [&_tr]:transition-colors [&_tr:hover]:bg-stone-50">
              {FIVE_MINUTE_READ.map((row) => (
                <tr key={row.requirement}>
                  <td className="px-4 py-3 text-ink font-serif">{row.requirement}</td>
                  <td className="px-4 py-3">
                    <a
                      href={row.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-tuscan underline font-mono text-xs"
                    >
                      {row.livesIn}
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 2 — rubric mapping */}
      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("forEvaluators.rubricTitle")}
        </h2>
        <p className="text-sm text-ink-2 mb-4 max-w-3xl">
          {t("forEvaluators.rubricLead")}
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-x-auto">
          <table className="w-full text-sm min-w-[720px]">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold w-1/3">{t("forEvaluators.colCriterion")}</th>
                <th className="px-4 py-3 text-left font-semibold w-1/4">{t("forEvaluators.colBrief")}</th>
                <th className="px-4 py-3 text-left font-semibold">{t("forEvaluators.colRepo")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 [&_tr]:transition-colors [&_tr:hover]:bg-stone-50">
              {RUBRIC.map((row) => (
                <tr key={row.criterion}>
                  <td className="px-4 py-3 text-ink font-serif align-top">{row.criterion}</td>
                  <td className="px-4 py-3 text-ink-2 text-xs align-top">{row.briefSection}</td>
                  <td className="px-4 py-3 align-top">
                    <div className="flex flex-wrap gap-2">
                      {row.artefacts.map((a, i) => {
                        if (!a.href && !a.internal) {
                          return (
                            <span key={i} className="text-ink-2 text-xs">{a.label}</span>
                          );
                        }
                        if (a.internal) {
                          return (
                            <Link
                              key={i}
                              to={a.label === "This site" ? "/" : a.label}
                              className="text-tuscan underline font-mono text-xs"
                            >
                              {a.label}
                            </Link>
                          );
                        }
                        return (
                          <a
                            key={i}
                            href={a.href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-tuscan underline font-mono text-xs"
                          >
                            {a.label}
                          </a>
                        );
                      })}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 3 — downloads + run-it-yourself */}
      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          {t("forEvaluators.downloadTitle")}
        </h2>
        <div className="flex flex-wrap gap-3 mb-5">
          <a
            href="/downloads/CantinaIQ-in-Practice.pdf"
            className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-tuscan text-white text-sm font-semibold hover:bg-tuscan/90 transition-all hover-lift group"
          >
            <span aria-hidden className="transition-transform group-hover:-translate-y-0.5">↓</span>
            {t("forEvaluators.downloadBrief", { pages: 19 })}
          </a>
          <a
            href="/downloads/evaluator-mapping.pdf"
            className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-white border border-tuscan text-tuscan text-sm font-semibold hover:bg-tuscan/5 transition-all hover-lift group"
          >
            <span aria-hidden className="transition-transform group-hover:-translate-y-0.5">↓</span>
            {t("forEvaluators.downloadMapping", { pages: 1 })}
          </a>
        </div>
        <p className="text-sm text-ink-2 mb-3">
          {t("forEvaluators.cloneLead")}
        </p>
        <pre className="bg-ink text-cream font-mono text-xs p-4 rounded-lg overflow-x-auto leading-relaxed">
{`git clone https://github.com/vincentblokker/CantinaIQ
cd CantinaIQ
make setup && make demo`}
        </pre>
        <p className="text-xs text-ink-2 mt-3">
          {t("forEvaluators.runOutputPre")}{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">supercharged/reports/generated/</code>{" "}
          {t("forEvaluators.runOutputMid")} <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">dashboard/dist/</code>{t("forEvaluators.runOutputPost")}
        </p>
      </section>
    </div>
  );
}
