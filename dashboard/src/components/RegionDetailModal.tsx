import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import Modal from "./Modal";
import GlossedText from "./GlossedText";
import { useNl } from "../i18n/domainLabels";
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

const SHIPPED_KEYS = [
  { label: "shippedAppellationLabel", why: "shippedAppellationWhy", source: "shippedAppellationSource" },
  { label: "shippedProductionLabel", why: "shippedProductionWhy", source: "shippedProductionSource" },
  { label: "shippedVintageLabel", why: "shippedVintageWhy", source: "shippedVintageSource" },
  { label: "shippedClimateLabel", why: "shippedClimateWhy", source: "shippedClimateSource" },
] as const;

const DEFERRED_KEYS = [
  { label: "deferredBiodynamicLabel", why: "deferredBiodynamicWhy", blocker: "deferredBiodynamicBlocker" },
  { label: "deferredTradeLabel", why: "deferredTradeWhy", blocker: "deferredTradeBlocker" },
  { label: "deferredTravelLabel", why: "deferredTravelWhy", blocker: "deferredTravelBlocker" },
] as const;

function vintageColour(grade: string): string {
  if (grade.startsWith("A")) return "bg-leaf/15 text-leaf border-leaf/30";
  if (grade.startsWith("B")) return "bg-stone-100 text-ink border-stone-300";
  if (grade === "—") return "bg-stone-50 text-stone-400 border-stone-200 italic";
  return "bg-rose-50 text-rose-700 border-rose-200";
}

export default function RegionDetailModal({ region, onClose }: Props) {
  const { t } = useTranslation();
  const nl = useNl();
  const [wiki, setWiki] = useState<WikiSummary | null>(null);
  const [wikiLoading, setWikiLoading] = useState(false);
  const [wikiError, setWikiError] = useState(false);

  const shipped = SHIPPED_KEYS.map((item) => ({
    label: t(`regionModal.${item.label}`),
    why: t(`regionModal.${item.why}`),
    source: t(`regionModal.${item.source}`),
  }));
  const deferred = DEFERRED_KEYS.map((item) => ({
    label: t(`regionModal.${item.label}`),
    why: t(`regionModal.${item.why}`),
    blocker: t(`regionModal.${item.blocker}`),
  }));

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
              {t("regionModal.biasLabel")} ·{" "}
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
          <Stat label={t("regionModal.statWines")} value={region.wines.toString()} />
          <Stat label={t("regionModal.statWeightedRating")} value={region.weighted_rating.toFixed(2)} accent />
          <Stat label={t("regionModal.statAvgPrice")} value={`€${Math.round(region.avg_price)}`} />
          <Stat label={t("regionModal.statReviews")} value={region.total_reviews.toLocaleString()} />
        </div>

        {/* Regional facts — enriched */}
        {meta && (meta.docCount !== undefined || meta.annualHl !== undefined) && (
          <div className="rounded-lg border border-tuscan/20 bg-tuscan/5 p-4">
            <div className="text-xs uppercase tracking-widest text-tuscan font-semibold mb-3">
              {t("regionModal.regionalFactsTitle")} {isFallback && <span className="text-ink-2 italic">{t("regionModal.regionalFactsCountryWide")}</span>}
            </div>
            <div className="grid grid-cols-4 gap-3">
              {meta.docgCount !== undefined && (
                <Stat label={t("regionModal.statDocgAppellations")} value={meta.docgCount.toString()} />
              )}
              {meta.docCount !== undefined && (
                <Stat label={t("regionModal.statDocAppellations")} value={meta.docCount.toString()} />
              )}
              {meta.annualHl !== undefined && (
                <Stat
                  label={t("regionModal.statAnnualProduction")}
                  value={meta.annualHl >= 1_000_000
                    ? `${(meta.annualHl / 1_000_000).toFixed(1)}M hl`
                    : `${(meta.annualHl / 1000).toFixed(0)}k hl`}
                  accent
                />
              )}
              {meta.docCount !== undefined && meta.docgCount !== undefined && (
                <Stat
                  label={t("regionModal.statTotalProtected")}
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
              {t("regionModal.whereItSits")}
            </h3>
            {mapUrl && (
              <div className="aspect-[4/3] rounded-lg overflow-hidden border border-stone-200">
                <iframe
                  src={mapUrl}
                  title={t("regionModal.mapTitle", { region: region.macro_region ?? region.region })}
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
                    {t("regionModal.macroRegionNotMapped")}{" "}
                  </span>
                )}
                <GlossedText>{nl ? meta.notesNl ?? meta.notes : meta.notes}</GlossedText>
              </p>
            )}
          </div>
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              {t("regionModal.contextHeading")}
            </h3>
            {wikiLoading && (
              <div className="text-sm text-ink-2">{t("regionModal.wikiLoading")}</div>
            )}
            {wikiError && (
              <div className="text-sm text-ink-2">
                {t("regionModal.wikiUnavailable")}
              </div>
            )}
            {wiki && (
              <div>
                <p className="text-sm text-ink leading-relaxed line-clamp-[8]">
                  <GlossedText>{wiki.extract}</GlossedText>
                </p>
                {wiki.content_urls?.desktop?.page && (
                  <a
                    href={wiki.content_urls.desktop.page}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 text-xs text-tuscan underline link-underline"
                  >
                    {t("regionModal.readFullArticle")} ↗
                  </a>
                )}
              </div>
            )}
            {meta && meta.varietals.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-1">
                  {t("regionModal.signatureVarietals")}
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
                  {t("regionModal.climateHeading")}
                </h4>
                <p className="text-sm text-ink leading-relaxed"><GlossedText>{nl ? meta.climateNl ?? meta.climate : meta.climate}</GlossedText></p>
              </div>
            )}
            {meta.terroir && (
              <div className="rounded-lg border border-stone-200 bg-white p-4">
                <h4 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
                  {t("regionModal.terroirHeading")}
                </h4>
                <p className="text-sm text-ink leading-relaxed"><GlossedText>{nl ? meta.terroirNl ?? meta.terroir : meta.terroir}</GlossedText></p>
              </div>
            )}
          </div>
        )}

        {/* Vintage chart strip */}
        {meta?.vintageScores && vintageYears.length > 0 && (
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              {t("regionModal.vintageAssessmentTitle")}
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
              {t("regionModal.vintageNote")}
            </p>
          </div>
        )}

        {/* Enrichments — shipped + deferred */}
        <div>
          <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
            {t("regionModal.enrichmentsHeading")}
          </h3>
          <p className="text-sm text-ink-2 mb-4 max-w-3xl">
            {t("regionModal.enrichmentsLead")}
          </p>

          <h4 className="text-xs uppercase tracking-widest text-leaf font-semibold mb-2 mt-3">
            {t("regionModal.shippedHeading", { shipped: shipped.length })}
          </h4>
          <ul className="space-y-2 mb-5">
            {shipped.map((item) => (
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
            {t("regionModal.deferredHeading", { deferred: deferred.length })}
          </h4>
          <ul className="space-y-2">
            {deferred.map((item) => (
              <li
                key={item.label}
                className="rounded-lg border border-stone-200 bg-stone-50/40 px-4 py-3 hover-lift"
              >
                <div className="flex items-baseline justify-between gap-3 flex-wrap">
                  <span className="font-serif text-ink-2">
                    <span className="text-stone-400 mr-1.5">○</span>
                    {item.label}
                  </span>
                  <span className="text-xs text-stone-500 italic">{t("regionModal.deferredBadge")}</span>
                </div>
                <div className="text-xs text-ink-2 mt-1 ml-5">{item.why}</div>
                <div className="text-xs text-stone-500 mt-1 ml-5 italic">
                  <strong className="not-italic">{t("regionModal.blockerLabel")}</strong> {item.blocker}
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
