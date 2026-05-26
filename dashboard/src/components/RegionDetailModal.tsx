import { useEffect, useState } from "react";
import Modal from "./Modal";
import { Region } from "../lib/data";
import { lookupRegion } from "../lib/regionMeta";
import { BIAS_REGIONS } from "../lib/pdfData";

interface Props {
  region: Region | null;
  onClose: () => void;
}

interface WikiSummary {
  extract: string;
  thumbnail?: { source: string };
  content_urls?: { desktop?: { page: string } };
}

const CRAWL_IDEAS = [
  {
    label: "DOC/DOCG appellation count",
    why: "Production-tier signal — how many sub-appellations does this region carry?",
    source: "Italian Ministry of Agriculture (MIPAAF) registry",
  },
  {
    label: "Producer biodynamic certifications",
    why: "Slurpini's USP is sustainability. Count of Demeter + FederBio producers per region.",
    source: "demeter.net + federbio.it",
  },
  {
    label: "Annual production volume (hl)",
    why: "Sense of regional scale relative to Vivino sample size.",
    source: "ICE Amsterdam annual reports + ISTAT viticulture data",
  },
  {
    label: "Climate + terroir summary",
    why: "Buying committee context — what makes this region's wine taste the way it does?",
    source: "Wine Folly · Jancis Robinson · regional consortia",
  },
  {
    label: "NL trade volume (€)",
    why: "Bias-correction depth — not just relative share, but absolute import euros.",
    source: "ICE Amsterdam customs statistics",
  },
  {
    label: "Travel cost from Amsterdam",
    why: "Operational input for the on-site visit decision — flight time and ground transport.",
    source: "Skyscanner + Google Maps APIs",
  },
  {
    label: "Recent vintage quality scores",
    why: "2018-2024 vintage variance per region — when not to recommend a producer.",
    source: "Wine Enthusiast vintage charts + Wine Advocate",
  },
];

export default function RegionDetailModal({ region, onClose }: Props) {
  const [wiki, setWiki] = useState<WikiSummary | null>(null);
  const [wikiLoading, setWikiLoading] = useState(false);
  const [wikiError, setWikiError] = useState(false);

  const meta = lookupRegion(region?.macro_region ?? region?.region);
  const bias = BIAS_REGIONS.find(
    (b) =>
      b.region.toLowerCase() === (region?.macro_region ?? "").toLowerCase() ||
      b.region.toLowerCase() === (region?.region ?? "").toLowerCase(),
  );

  useEffect(() => {
    if (!region || !meta) {
      setWiki(null);
      return;
    }
    setWikiLoading(true);
    setWikiError(false);
    fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${meta.wikipediaSlug}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((j) => setWiki(j))
      .catch(() => setWikiError(true))
      .finally(() => setWikiLoading(false));
  }, [region, meta]);

  if (!region) return null;

  const mapUrl = meta
    ? `https://www.openstreetmap.org/export/embed.html?bbox=${meta.bbox}&layer=mapnik`
    : null;
  const isFallback = meta?.wikipediaSlug === "Italian_wine";

  return (
    <Modal open={!!region} onClose={onClose} title={region.region}>
      <div className="space-y-6">
        {/* Header strip */}
        <div className="flex items-baseline gap-4 flex-wrap">
          {region.macro_region && (
            <span className="text-xs uppercase tracking-widest text-tuscan font-semibold">
              {region.macro_region}
            </span>
          )}
          {bias && (
            <span className="text-xs text-ink-2">
              Vivino vs ICE NL bias ·{" "}
              <span
                className={
                  bias.factor < 0.7
                    ? "text-sea font-semibold"
                    : bias.factor >= 1.3
                      ? "text-tuscan font-semibold"
                      : "text-ink-2"
                }
              >
                ×{bias.factor.toFixed(2)}
              </span>
            </span>
          )}
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-4 gap-3">
          <Stat label="Wines" value={region.wines.toString()} />
          <Stat label="Weighted rating" value={region.weighted_rating.toFixed(2)} accent />
          <Stat label="Avg price" value={`€${Math.round(region.avg_price)}`} />
          <Stat label="Reviews" value={region.total_reviews.toLocaleString()} />
        </div>

        {/* Map + Wikipedia row */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              Where it sits
            </h3>
            {mapUrl && (
              <div className="aspect-[4/3] rounded-lg overflow-hidden border border-stone-200">
                <iframe
                  src={mapUrl}
                  title={`Map of ${region.macro_region ?? region.region}`}
                  className="w-full h-full"
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                />
              </div>
            )}
            {meta && (
              <p className="text-xs text-ink-2 mt-2 italic">
                {isFallback && (
                  <span className="text-tuscan/80 font-semibold not-italic">
                    Macro-region not yet mapped —{" "}
                  </span>
                )}
                {meta.notes}
              </p>
            )}
          </div>
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              Context
            </h3>
            {wikiLoading && (
              <div className="text-sm text-ink-2">Loading Wikipedia summary…</div>
            )}
            {wikiError && (
              <div className="text-sm text-ink-2">
                Wikipedia summary unavailable for this region.
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
                  Signature varietals
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
            This modal is the start of the per-region story. A future pass
            could pull in any of the following — each is a public data source
            with a clean API:
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
