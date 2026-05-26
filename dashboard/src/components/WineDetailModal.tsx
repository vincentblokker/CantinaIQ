import { useEffect, useState } from "react";
import Modal from "./Modal";
import { Wine } from "../lib/data";
import { lookupRegion } from "../lib/regionMeta";
import { SEGMENTS } from "../lib/pdfData";

interface Props {
  wine: Wine | null;
  onClose: () => void;
}

interface WikiSummary {
  extract: string;
  content_urls?: { desktop?: { page: string } };
}

const CRAWL_IDEAS = [
  {
    label: "Vintage variation per wine",
    why: "2018 vs 2019 vs 2020 — same wine, different vintage scores. Vivino aggregates across vintages.",
    source: "Vivino vintage-specific endpoints + Wine Advocate / James Suckling",
  },
  {
    label: "Grape composition",
    why: "The 'inferred grape or style' is a heuristic. Real DOCG / DOC rules constrain blends per appellation.",
    source: "Consorzio rules per appellation + producer technical sheets",
  },
  {
    label: "Cellar-aging recommendation",
    why: "Slurpini's hospitality clients care about service-readiness. When should this be drunk?",
    source: "Wine-Searcher drinking windows + Decanter vintage charts",
  },
  {
    label: "Food-pairing notes",
    why: "Restaurant-channel sales material. What plate does this wine sell against?",
    source: "Producer tasting notes + Wine Folly pairing data",
  },
  {
    label: "Alcohol percentage + residual sugar",
    why: "Practical labelling + dry/off-dry classification — missing from Vivino aggregation.",
    source: "Producer technical sheets · Vivino product pages (deep scrape)",
  },
];

function segmentStyle(segment: string): string {
  const seg = SEGMENTS.find((s) => s.name === segment);
  return seg?.colorClass ?? "bg-stone-50 text-stone-700 border-stone-200";
}

export default function WineDetailModal({ wine, onClose }: Props) {
  const [wiki, setWiki] = useState<WikiSummary | null>(null);
  const [wikiLoading, setWikiLoading] = useState(false);
  const [wikiError, setWikiError] = useState(false);

  const meta = lookupRegion(wine?.macro_region ?? wine?.region);

  useEffect(() => {
    if (!wine || !meta) {
      setWiki(null);
      return;
    }
    setWikiLoading(true);
    setWikiError(false);
    fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${meta.wikipediaSlug}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((j: WikiSummary) => setWiki(j))
      .catch(() => setWikiError(true))
      .finally(() => setWikiLoading(false));
  }, [wine, meta]);

  if (!wine) return null;

  const mapUrl = meta
    ? `https://www.openstreetmap.org/export/embed.html?bbox=${meta.bbox}&layer=mapnik`
    : null;

  return (
    <Modal open={!!wine} onClose={onClose} title={wine.wine_name}>
      <div className="space-y-6">
        {/* Header strip */}
        <div className="flex items-baseline gap-3 flex-wrap">
          <span className="text-xs uppercase tracking-widest text-tuscan font-semibold">
            {wine.macro_region}
          </span>
          {wine.vintage && (
            <span className="text-xs text-ink-2 font-mono">
              vintage {wine.vintage}
            </span>
          )}
          <span
            className={`px-2 py-0.5 text-xs rounded-full border font-semibold ${segmentStyle(wine.market_segment)}`}
          >
            {wine.market_segment}
          </span>
          <span className="text-xs text-ink-2">
            by{" "}
            <span className="font-semibold text-ink">{wine.producer_name}</span> ·{" "}
            <span className="italic">{wine.region}</span>
          </span>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-4 gap-3">
          <Stat label="Weighted rating" value={wine.weighted_rating.toFixed(2)} accent />
          <Stat label="Reviews" value={wine.rating_count.toLocaleString()} />
          <Stat label="Price" value={`€${Math.round(wine.price)}`} />
          <Stat label="Composite" value={wine.composite_score.toFixed(3)} accent />
        </div>

        {/* Sub-stats: price segment, confidence, inferred grape */}
        <div className="rounded-lg border border-stone-200 bg-stone-50/40 p-4 text-sm">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <div className="text-[10px] uppercase tracking-widest text-ink-2 font-semibold mb-1">
                Price segment
              </div>
              <div className="text-ink">{wine.price_segment}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-widest text-ink-2 font-semibold mb-1">
                Confidence signal
              </div>
              <div className="text-ink">{wine.confidence_segment}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-widest text-ink-2 font-semibold mb-1">
                Inferred grape / style
              </div>
              <div className="text-ink italic">{wine.inferred_grape_or_style}</div>
            </div>
          </div>
        </div>

        {/* Map + Wikipedia */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              Where it's from
            </h3>
            {mapUrl && (
              <div className="aspect-[4/3] rounded-lg overflow-hidden border border-stone-200">
                <iframe
                  src={mapUrl}
                  title={`Map of ${wine.macro_region}`}
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
              Region context
            </h3>
            {wikiLoading && (
              <div className="text-sm text-ink-2">Loading region context…</div>
            )}
            {wikiError && (
              <div className="text-sm text-ink-2">
                Wikipedia region context unavailable.
              </div>
            )}
            {wiki && (
              <div>
                <p className="text-sm text-ink leading-relaxed line-clamp-[10]">
                  {wiki.extract}
                </p>
                {wiki.content_urls?.desktop?.page && (
                  <a
                    href={wiki.content_urls.desktop.page}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 text-xs text-tuscan underline link-underline"
                  >
                    Read full region article on Wikipedia ↗
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

        {/* Enrichment ideas */}
        <div>
          <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
            What we could enrich with next
          </h3>
          <p className="text-sm text-ink-2 mb-3 max-w-3xl">
            Per-wine attributes the Vivino export aggregates away — recoverable
            with targeted scraping or paid critic-database access:
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
