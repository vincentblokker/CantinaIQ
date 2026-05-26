import { useEffect, useState } from "react";
import Modal from "./Modal";
import { Producer } from "../lib/data";
import { lookupRegion } from "../lib/regionMeta";
import { SUSTAINABILITY, SEGMENTS, ACTIONS } from "../lib/pdfData";

interface Props {
  producer: Producer | null;
  onClose: () => void;
}

interface WikiSummary {
  extract: string;
  thumbnail?: { source: string };
  content_urls?: { desktop?: { page: string } };
}

const CRAWL_IDEAS = [
  {
    label: "Estate website + contact info",
    why: "Direct outreach prep — who do you actually email at the estate?",
    source: "Producer's own .it or .com domain (Firecrawl-scrapable)",
  },
  {
    label: "Annual production volume (bottles/yr)",
    why: "Sense of whether Slurpini can secure a meaningful allocation.",
    source: "Producer website + Wine-Searcher producer pages",
  },
  {
    label: "Hectares + farming method",
    why: "Operational scale and sustainability practice — biodynamic, organic, conventional.",
    source: "Demeter + FederBio public registries · ICEA · Suolo e Salute",
  },
  {
    label: "Critic scores per vintage",
    why: "Cross-check Vivino's consumer signal against expert opinion.",
    source: "Wine Advocate · James Suckling · Wine Spectator · Decanter",
  },
  {
    label: "Distribution markets",
    why: "Already in NL? Already in BeNeLux? Operational overlap with Slurpini's existing portfolio.",
    source: "Wine-Searcher trade locator + producer press kits",
  },
  {
    label: "Travel from Amsterdam",
    why: "Cost input for an on-site visit decision — flight + ground transport time.",
    source: "Skyscanner + Google Maps APIs",
  },
  {
    label: "Recent press mentions (2024-2026)",
    why: "Reputational direction — are they trending up or down with critics and trade press?",
    source: "Decanter + Drinks Business + Wine Industry Advisor",
  },
];

function recommendationStyle(rec: string): string {
  switch (rec) {
    case "Premium Brand Builder":
      return "bg-purple-50 text-purple-800 border-purple-200";
    case "Target":
      return "bg-blue-50 text-blue-800 border-blue-200";
    case "Value Opportunity":
      return "bg-green-50 text-green-800 border-green-200";
    case "Monitor":
      return "bg-stone-50 text-stone-700 border-stone-200";
    case "Avoid for Now":
      return "bg-rose-50 text-rose-800 border-rose-200";
    default:
      return "bg-stone-50 text-stone-700 border-stone-200";
  }
}

export default function ProducerDetailModal({ producer, onClose }: Props) {
  const [wiki, setWiki] = useState<WikiSummary | null>(null);
  const [wikiLoading, setWikiLoading] = useState(false);
  const [wikiError, setWikiError] = useState(false);

  const meta = lookupRegion(producer?.macro_region);
  const segment = SEGMENTS.find((s) => s.name === producer?.market_segment);
  const action = ACTIONS.find((a) => a.name === producer?.recommendation);
  const cert = SUSTAINABILITY.find(
    (s) => producer && s.producer.toLowerCase() === producer.producer_name.toLowerCase(),
  );

  useEffect(() => {
    if (!producer) {
      setWiki(null);
      return;
    }

    // Try a chain of slugs until one returns a real article.
    // Wikipedia patterns for Italian producers vary:
    //   "Masseto (wine)" not "Tenuta Masseto"
    //   "Antinori" not "Marchesi Antinori"
    //   "Castello di Ama" — direct
    const name = producer.producer_name;
    const stripped = name
      .replace(/^(Tenuta|Marchesi|Castello|Cantina|Fattoria|Casa|Az\.\s*Agr\.|Azienda Agricola)\s+/i, "")
      .replace(/\s+(estate|winery|winemaker)$/i, "")
      .trim();

    const slugs = [
      name.replace(/ /g, "_"),
      stripped !== name ? stripped.replace(/ /g, "_") : null,
      `${stripped.replace(/ /g, "_")}_(wine)`,
      `${stripped.replace(/ /g, "_")}_(winery)`,
    ].filter(Boolean) as string[];

    setWikiLoading(true);
    setWikiError(false);

    let cancelled = false;
    (async () => {
      for (const slug of slugs) {
        if (cancelled) return;
        try {
          const r = await fetch(
            `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(slug)}`,
          );
          if (!r.ok) continue;
          const j: WikiSummary = await r.json();
          // Skip too-short / disambiguation extracts
          if (j.extract && j.extract.length > 80 && !/may refer to/i.test(j.extract)) {
            if (!cancelled) {
              setWiki(j);
              setWikiLoading(false);
            }
            return;
          }
        } catch {
          // try next
        }
      }
      if (!cancelled) {
        setWikiError(true);
        setWikiLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [producer]);

  if (!producer) return null;

  const mapUrl = meta
    ? `https://www.openstreetmap.org/export/embed.html?bbox=${meta.bbox}&layer=mapnik`
    : null;

  return (
    <Modal open={!!producer} onClose={onClose} title={producer.producer_name}>
      <div className="space-y-6">
        {/* Header strip */}
        <div className="flex items-baseline gap-3 flex-wrap">
          <span className="text-xs uppercase tracking-widest text-tuscan font-semibold">
            {producer.macro_region}
          </span>
          <span
            className={`px-2 py-0.5 text-xs rounded-full border font-semibold ${recommendationStyle(producer.recommendation)}`}
          >
            {producer.recommendation}
          </span>
          {segment && (
            <span
              className={`px-2 py-0.5 text-xs rounded-full border font-semibold ${segment.colorClass}`}
            >
              {segment.name}
            </span>
          )}
          {cert?.certification && (
            <span className="px-2 py-0.5 text-xs rounded-full border border-leaf/40 bg-leaf/10 text-leaf font-semibold">
              {cert.certification} certified
            </span>
          )}
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-4 gap-3">
          <Stat label="Weighted rating" value={producer.weighted_rating.toFixed(2)} accent />
          <Stat label="Reviews" value={producer.total_reviews.toLocaleString()} />
          <Stat label="Avg price" value={`€${Math.round(producer.avg_price)}`} />
          <Stat label="Composite score" value={producer.composite_score.toFixed(3)} accent />
        </div>

        {/* Segment + action explainer */}
        {(segment || action) && (
          <div className="rounded-lg border border-stone-200 bg-stone-50/40 p-4">
            {segment && (
              <div className="text-sm text-ink-2 mb-1">
                <span className="font-semibold text-ink">{segment.name}:</span> {segment.rule}
              </div>
            )}
            {action && (
              <div className="text-sm text-ink-2">
                <span className="font-semibold text-ink">{action.name}:</span> {action.rationale}
              </div>
            )}
          </div>
        )}

        {/* Map + Wikipedia row */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              Where it's based
            </h3>
            {mapUrl && (
              <div className="aspect-[4/3] rounded-lg overflow-hidden border border-stone-200">
                <iframe
                  src={mapUrl}
                  title={`Map of ${producer.macro_region}`}
                  className="w-full h-full"
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                />
              </div>
            )}
            {meta && (
              <p className="text-xs text-ink-2 mt-2 italic">{meta.notes}</p>
            )}
          </div>
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              Context
            </h3>
            {wikiLoading && (
              <div className="text-sm text-ink-2">Looking up {producer.producer_name} on Wikipedia…</div>
            )}
            {wikiError && (
              <div className="text-sm text-ink-2 leading-relaxed">
                No Wikipedia page found for <em>{producer.producer_name}</em>. The
                producer may be too small for an English-language Wikipedia entry,
                or the name needs disambiguation. Italian or producer-website
                lookup belongs in the next enrichment pass (see below).
              </div>
            )}
            {wiki && (
              <div>
                <p className="text-sm text-ink leading-relaxed">
                  {wiki.extract}
                </p>
                {wiki.content_urls?.desktop?.page && (
                  <a
                    href={wiki.content_urls.desktop.page}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 text-xs text-tuscan underline link-underline"
                  >
                    Read full article on Wikipedia ↗
                  </a>
                )}
              </div>
            )}
            {meta && meta.varietals.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-1">
                  Region's signature varietals
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {meta.varietals.map((v) => (
                    <span
                      key={v}
                      className="text-xs px-2 py-0.5 rounded-full bg-tuscan/10 text-tuscan border border-tuscan/20"
                    >
                      {v}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* What we could crawl next */}
        <div>
          <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
            What we could enrich with next
          </h3>
          <p className="text-sm text-ink-2 mb-3 max-w-3xl">
            Producer-level data the pipeline does not yet pull — each is a
            scrapable or API-accessible public source. Adding any of these
            would change the recommendation from "this producer ranks high"
            to "this producer ranks high <em>and</em> they can supply, <em>and</em>
            they're already in NL retail, <em>and</em> they're biodynamic":
          </p>
          <ul className="space-y-2">
            {CRAWL_IDEAS.map((idea) => (
              <li
                key={idea.label}
                className="rounded-lg border border-stone-200 px-4 py-3 bg-stone-50/40 hover-lift"
              >
                <div className="flex items-baseline justify-between gap-3 flex-wrap">
                  <span className="font-serif text-ink">{idea.label}</span>
                  <span className="text-xs text-ink-2 font-mono">{idea.source}</span>
                </div>
                <div className="text-xs text-ink-2 mt-1">{idea.why}</div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Modal>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="rounded-lg border border-stone-200 bg-white px-3 py-3 hover-lift">
      <div className="text-[10px] uppercase tracking-widest text-ink-2 font-semibold">
        {label}
      </div>
      <div className={`font-serif text-lg ${accent ? "text-tuscan" : "text-ink"}`}>
        {value}
      </div>
    </div>
  );
}
