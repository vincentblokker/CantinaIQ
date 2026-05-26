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

const SHIPPED = [
  {
    label: "DOC/DOCG appellation count",
    why: "Production-tier signal — how many sub-appellations does this region carry?",
    source: "Curated from public MIPAAF / EU eAmbrosia registry data",
  },
  {
    label: "Annual production volume (hl)",
    why: "Regional scale relative to Vivino sample size.",
    source: "ISTAT viticulture statistics, 2022–2023",
  },
  {
    label: "Vintage quality grades 2018–2024",
    why: "Cross-check Vivino's aggregate score against consensus expert opinion per year.",
    source: "Consensus expert ratings (Decanter / Jancis Robinson / Wine Enthusiast public charts)",
  },
  {
    label: "Climate + terroir summary",
    why: "Buying-committee context — what makes this region's wine taste the way it does?",
    source: "Curated from regional consorzio publications and Italian Wine Central",
  },
];

const DEFERRED = [
  {
    label: "Producer biodynamic certifications at scale (762)",
    why: "Slurpini's USP is sustainability — would surface Demeter + FederBio counts per region.",
    blocker: "Firecrawl credits required for a 762-producer crawl. Pipeline command exists for 5; scale is the constraint.",
  },
  {
    label: "NL trade volume (€)",
    why: "Bias-correction depth — absolute import euros, not just relative share.",
    blocker: "ICE Amsterdam customs data is published only as bound PDF reports; manual extraction required.",
  },
  {
    label: "Travel cost from Amsterdam",
    why: "Operational input for the on-site visit decision — flight time and ground transport.",
    blocker: "Google Maps Directions API requires a billing account; deferred until budget is allocated.",
  },
];

function vintageColour(grade: string): string {
  if (grade.startsWith("A")) return "bg-leaf/15 text-leaf border-leaf/30";
  if (grade.startsWith("B")) return "bg-stone-100 text-ink border-stone-300";
  if (grade === "—") return "bg-stone-50 text-stone-400 border-stone-200 italic";
  return "bg-rose-50 text-rose-700 border-rose-200";
}

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
  const vintageYears = meta?.vintageScores
    ? Object.keys(meta.vintageScores).map(Number).sort()
    : [];

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

        {/* Stats grid — Vivino data */}
        <div className="grid grid-cols-4 gap-3 stagger">
          <Stat label="Wines (Vivino)" value={region.wines.toString()} />
          <Stat label="Weighted rating" value={region.weighted_rating.toFixed(2)} accent />
          <Stat label="Avg price" value={`€${Math.round(region.avg_price)}`} />
          <Stat label="Reviews" value={region.total_reviews.toLocaleString()} />
        </div>

        {/* Regional facts — enriched */}
        {meta && (meta.docCount !== undefined || meta.annualHl !== undefined) && (
          <div className="rounded-lg border border-tuscan/20 bg-tuscan/5 p-4">
            <div className="text-xs uppercase tracking-widest text-tuscan font-semibold mb-3">
              Regional facts {isFallback && <span className="text-ink-2 italic">(country-wide totals)</span>}
            </div>
            <div className="grid grid-cols-4 gap-3">
              {meta.docgCount !== undefined && (
                <Stat label="DOCG appellations" value={meta.docgCount.toString()} />
              )}
              {meta.docCount !== undefined && (
                <Stat label="DOC appellations" value={meta.docCount.toString()} />
              )}
              {meta.annualHl !== undefined && (
                <Stat
                  label="Annual production"
                  value={meta.annualHl >= 1_000_000
                    ? `${(meta.annualHl / 1_000_000).toFixed(1)}M hl`
                    : `${(meta.annualHl / 1000).toFixed(0)}k hl`}
                  accent
                />
              )}
              {meta.docCount !== undefined && meta.docgCount !== undefined && (
                <Stat
                  label="Total protected"
                  value={(meta.docCount + meta.docgCount).toString()}
                />
              )}
            </div>
          </div>
        )}

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
                <p className="text-sm text-ink leading-relaxed line-clamp-[8]">
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

        {/* Climate + terroir */}
        {meta && (meta.climate || meta.terroir) && (
          <div className="grid md:grid-cols-2 gap-4">
            {meta.climate && (
              <div className="rounded-lg border border-stone-200 bg-white p-4">
                <h4 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
                  Climate
                </h4>
                <p className="text-sm text-ink leading-relaxed">{meta.climate}</p>
              </div>
            )}
            {meta.terroir && (
              <div className="rounded-lg border border-stone-200 bg-white p-4">
                <h4 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
                  Terroir
                </h4>
                <p className="text-sm text-ink leading-relaxed">{meta.terroir}</p>
              </div>
            )}
          </div>
        )}

        {/* Vintage chart strip */}
        {meta?.vintageScores && vintageYears.length > 0 && (
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              Vintage assessment 2018 – 2024
            </h3>
            <div className="grid grid-cols-7 gap-2">
              {vintageYears.map((year) => {
                const grade = meta.vintageScores![year];
                return (
                  <div
                    key={year}
                    className={`rounded-lg border px-2 py-3 text-center hover-lift ${vintageColour(grade)}`}
                  >
                    <div className="text-[10px] font-mono text-ink-2">{year}</div>
                    <div className="font-serif text-2xl tabular-nums mt-1">{grade}</div>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-ink-2 mt-2 italic">
              Letter grades reflect consensus expert assessment of vintage
              quality across the region. "—" = too recent for full
              assessment. Higher grade ≠ higher individual wine quality;
              great producers can outperform their vintage.
            </p>
          </div>
        )}

        {/* Enrichments — shipped + deferred */}
        <div>
          <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
            Enrichments
          </h3>
          <p className="text-sm text-ink-2 mb-4 max-w-3xl">
            What the modal pulls in beyond Vivino's raw export. Four
            curated enrichments are integrated; three more are deferred
            because they require paid services or manual PDF extraction.
          </p>

          <h4 className="text-xs uppercase tracking-widest text-leaf font-semibold mb-2 mt-3">
            ✓ Shipped ({SHIPPED.length})
          </h4>
          <ul className="space-y-2 mb-5">
            {SHIPPED.map((item) => (
              <li
                key={item.label}
                className="rounded-lg border border-leaf/30 bg-leaf/5 px-4 py-3 hover-lift"
              >
                <div className="flex items-baseline justify-between gap-3 flex-wrap">
                  <span className="font-serif text-ink">
                    <span className="text-leaf mr-1.5">✓</span>
                    {item.label}
                  </span>
                  <span className="text-xs text-ink-2 font-mono">{item.source}</span>
                </div>
                <div className="text-xs text-ink-2 mt-1 ml-5">{item.why}</div>
              </li>
            ))}
          </ul>

          <h4 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
            Deferred ({DEFERRED.length}) — paid sources
          </h4>
          <ul className="space-y-2">
            {DEFERRED.map((item) => (
              <li
                key={item.label}
                className="rounded-lg border border-stone-200 bg-stone-50/40 px-4 py-3 hover-lift"
              >
                <div className="flex items-baseline justify-between gap-3 flex-wrap">
                  <span className="font-serif text-ink-2">
                    <span className="text-stone-400 mr-1.5">○</span>
                    {item.label}
                  </span>
                  <span className="text-xs text-stone-500 italic">deferred</span>
                </div>
                <div className="text-xs text-ink-2 mt-1 ml-5">{item.why}</div>
                <div className="text-xs text-stone-500 mt-1 ml-5 italic">
                  <strong className="not-italic">Blocker:</strong> {item.blocker}
                </div>
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
