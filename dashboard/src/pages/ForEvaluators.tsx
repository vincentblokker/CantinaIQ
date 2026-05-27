import { Link } from "react-router-dom";
import { FIVE_MINUTE_READ, RUBRIC } from "../lib/evaluatorMapping";

export default function ForEvaluators() {
  return (
    <div className="space-y-10">
      <header>
        <div className="text-xs uppercase tracking-widest text-tuscan font-semibold">
          For evaluators
        </div>
        <h1 className="font-serif text-4xl text-ink mt-2">
          Map the rubric to the evidence.
        </h1>
        <p className="text-ink-2 mt-3 max-w-3xl">
          A click-through index from each evaluation criterion to where the
          evidence lives — in the strategy brief PDF and in the repo.
        </p>
      </header>

      {/* Section 0 — walkthrough video */}
      <section>
        <h2 className="font-serif text-2xl text-ink mb-3">
          Watch the 3-minute walkthrough
        </h2>
        <p className="text-sm text-ink-2 mb-4 max-w-3xl">
          A guided tour through the strategy brief, the dashboard, and how the
          rubric maps onto the evidence. The fastest way to orient before
          diving into the artefacts below.
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden shadow-sm">
          <video
            controls
            preload="metadata"
            poster="/downloads/walkthrough-poster.jpg"
            className="w-full block"
          >
            <source src="/downloads/walkthrough.mp4" type="video/mp4" />
            Your browser does not support HTML5 video. Download:{" "}
            <a href="/downloads/walkthrough.mp4">walkthrough.mp4</a>
          </video>
        </div>
        <p className="text-xs text-ink-2 mt-2">
          3:00 · 36 MB · also downloadable:{" "}
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
          If you only have five minutes
        </h2>
        <p className="text-sm text-ink-2 mb-4 max-w-3xl">
          Everything ADA's brief literally asks for sits in <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">bare/</code> —
          one notebook, one crawler-extension script, one half-page recommendation. The three deliverables, mapped:
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Brief requirement</th>
                <th className="px-4 py-3 text-left font-semibold">Lives in</th>
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
          Rubric mapping
        </h2>
        <p className="text-sm text-ink-2 mb-4 max-w-3xl">
          The complete index. Each row points to a section in the strategy brief PDF
          and to a file in the repo or a page on this dashboard.
        </p>
        <div className="bg-white rounded-lg border border-stone-200 overflow-x-auto">
          <table className="w-full text-sm min-w-[720px]">
            <thead className="bg-stone-50 text-xs uppercase tracking-wide text-ink-2">
              <tr>
                <th className="px-4 py-3 text-left font-semibold w-1/3">Criterion</th>
                <th className="px-4 py-3 text-left font-semibold w-1/4">Strategy Brief PDF</th>
                <th className="px-4 py-3 text-left font-semibold">Repo / Dashboard</th>
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
          Download or run it yourself
        </h2>
        <div className="flex flex-wrap gap-3 mb-5">
          <a
            href="/downloads/CantinaIQ-in-Practice.pdf"
            className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-tuscan text-white text-sm font-semibold hover:bg-tuscan/90 transition-all hover-lift group"
          >
            <span aria-hidden className="transition-transform group-hover:-translate-y-0.5">↓</span>
            Strategy brief PDF (19 pages)
          </a>
          <a
            href="/downloads/evaluator-mapping.pdf"
            className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-white border border-tuscan text-tuscan text-sm font-semibold hover:bg-tuscan/5 transition-all hover-lift group"
          >
            <span aria-hidden className="transition-transform group-hover:-translate-y-0.5">↓</span>
            Evaluator mapping PDF (1 page)
          </a>
        </div>
        <p className="text-sm text-ink-2 mb-3">
          Or clone the repo and run the full pipeline locally:
        </p>
        <pre className="bg-ink text-cream font-mono text-xs p-4 rounded-lg overflow-x-auto leading-relaxed">
{`git clone https://github.com/vincentblokker/CantinaIQ
cd CantinaIQ
make setup && make demo`}
        </pre>
        <p className="text-xs text-ink-2 mt-3">
          End-to-end run completes in ~30 seconds. Outputs land in{" "}
          <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">supercharged/reports/generated/</code>{" "}
          and the dashboard build in <code className="text-tuscan bg-tuscan/10 px-1 py-0.5 rounded">dashboard/dist/</code>.
        </p>
      </section>
    </div>
  );
}
