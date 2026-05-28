import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import Modal from "./Modal";
import GlossedText from "./GlossedText";
import { useNl, useDomainLabels } from "../i18n/domainLabels";
import { fetchWikiSummary } from "../lib/wikiSummary";
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

const DEFERRED = [
  {
    label: "Estate website + contact info",
    labelNl: "Website van het landgoed + contactgegevens",
    why: "Direct outreach prep — who do you actually email at the estate?",
    whyNl: "Voorbereiding op direct contact — wie mail je eigenlijk op het landgoed?",
    source: "Producer's own .it or .com domain",
    sourceNl: "Eigen .it- of .com-domein van de producent",
    cost: "Firecrawl credits at 762-producer scale",
    costNl: "Firecrawl-credits op schaal van 762 producenten",
  },
  {
    label: "Hectares + farming method",
    labelNl: "Hectares + landbouwmethode",
    why: "Operational scale and certified sustainability practice.",
    whyNl: "Operationele schaal en gecertificeerde duurzaamheidspraktijk.",
    source: "Demeter + FederBio public registries",
    sourceNl: "Openbare registers van Demeter + FederBio",
    cost: "Firecrawl credits to scale existing 5-producer command to 762",
    costNl: "Firecrawl-credits om het bestaande commando voor 5 producenten op te schalen naar 762",
  },
  {
    label: "Annual production volume (bottles/yr)",
    labelNl: "Jaarlijks productievolume (flessen/jaar)",
    why: "Sense of whether Slurpini can secure a meaningful allocation.",
    whyNl: "Inschatting of Slurpini een betekenisvolle allocatie kan verzekeren.",
    source: "Producer website + Wine-Searcher producer pages",
    sourceNl: "Website van de producent + producentenpagina's van Wine-Searcher",
    cost: "Wine-Searcher trade API requires a paid commercial subscription",
    costNl: "De Wine-Searcher trade API vereist een betaald commercieel abonnement",
  },
  {
    label: "Critic scores per vintage",
    labelNl: "Critici-scores per jaargang",
    why: "Cross-check Vivino's consumer signal against expert opinion.",
    whyNl: "Controleer het consumentensignaal van Vivino tegen het oordeel van experts.",
    source: "Wine Advocate · James Suckling · Wine Spectator · Decanter",
    sourceNl: "Wine Advocate · James Suckling · Wine Spectator · Decanter",
    cost: "All four sources are paywalled critic databases",
    costNl: "Alle vier de bronnen zijn betaalde critici-databases",
  },
  {
    label: "Distribution markets",
    labelNl: "Distributiemarkten",
    why: "Already in NL? Operational overlap with Slurpini's existing portfolio.",
    whyNl: "Al in NL? Operationele overlap met het bestaande portfolio van Slurpini.",
    source: "Wine-Searcher trade locator",
    sourceNl: "Wine-Searcher trade locator",
    cost: "Wine-Searcher trade API is paid",
    costNl: "De Wine-Searcher trade API is betaald",
  },
  {
    label: "Travel from Amsterdam",
    labelNl: "Reis vanuit Amsterdam",
    why: "Operational cost input for the on-site visit decision.",
    whyNl: "Operationele kosteninput voor de beslissing over een bezoek ter plaatse.",
    source: "Google Maps Directions API",
    sourceNl: "Google Maps Directions API",
    cost: "Free tier exists but requires a billing-account credit card",
    costNl: "Er is een gratis laag, maar die vereist een creditcard met factureringsaccount",
  },
  {
    label: "Recent press mentions (2024–2026)",
    labelNl: "Recente persvermeldingen (2024–2026)",
    why: "Reputational direction — trending up or down with critics and trade press?",
    whyNl: "Reputatierichting — stijgend of dalend bij critici en vakpers?",
    source: "Decanter · Drinks Business · Wine Industry Advisor",
    sourceNl: "Decanter · Drinks Business · Wine Industry Advisor",
    cost: "Press monitoring requires either paid scraping infrastructure or LLM credits per query",
    costNl: "Persmonitoring vereist ofwel betaalde scraping-infrastructuur ofwel LLM-credits per query",
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
  const { t } = useTranslation();
  const [wiki, setWiki] = useState<WikiSummary | null>(null);
  const [wikiLoading, setWikiLoading] = useState(false);
  const [wikiError, setWikiError] = useState(false);

  const nl = useNl();
  const dl = useDomainLabels();
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
      // Last resort: the macro-region — keeps the Context section in Dutch when
      // the producer itself has no (Dutch) Wikipedia article.
      producer.macro_region,
    ].filter(Boolean) as string[];

    setWikiLoading(true);
    setWikiError(false);

    let cancelled = false;
    fetchWikiSummary(slugs, nl)
      .then((j) => {
        if (cancelled) return;
        if (j) setWiki(j);
        else setWikiError(true);
      })
      .finally(() => {
        if (!cancelled) setWikiLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [producer, nl]);

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
            {dl.recommendation(producer.recommendation)}
          </span>
          {segment && (
            <span
              className={`px-2 py-0.5 text-xs rounded-full border font-semibold ${segment.colorClass}`}
            >
              {nl ? segment.nameNl : segment.name}
            </span>
          )}
          {cert?.certification && (
            <span className="px-2 py-0.5 text-xs rounded-full border border-leaf/40 bg-leaf/10 text-leaf font-semibold">
              {t("producerModal.certifiedBadge", { certification: cert.certification })}
            </span>
          )}
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-4 gap-3">
          <Stat label={nl ? "Gewogen beoordeling" : "Weighted rating"} value={producer.weighted_rating.toFixed(2)} accent />
          <Stat label={t("producerModal.statReviews")} value={producer.total_reviews.toLocaleString()} />
          <Stat label={t("producerModal.statAvgPrice")} value={`€${Math.round(producer.avg_price)}`} />
          <Stat label={nl ? "Samengestelde score" : "Composite score"} value={producer.composite_score.toFixed(3)} accent />
        </div>

        {/* Segment + action explainer */}
        {(segment || action) && (
          <div className="rounded-lg border border-stone-200 bg-stone-50/40 p-4">
            {segment && (
              <div className="text-sm text-ink-2 mb-1">
                <span className="font-semibold text-ink">{nl ? segment.nameNl : segment.name}:</span> <GlossedText>{nl ? segment.ruleNl : segment.rule}</GlossedText>
              </div>
            )}
            {action && (
              <div className="text-sm text-ink-2">
                <span className="font-semibold text-ink">{nl ? action.nameNl : action.name}:</span> <GlossedText>{nl ? action.rationaleNl : action.rationale}</GlossedText>
              </div>
            )}
          </div>
        )}

        {/* Map + Wikipedia row */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              {t("producerModal.whereBasedTitle")}
            </h3>
            {mapUrl && (
              <div className="aspect-[4/3] rounded-lg overflow-hidden border border-stone-200">
                <iframe
                  src={mapUrl}
                  title={t("producerModal.mapAriaLabel", { region: producer.macro_region })}
                  className="w-full h-full"
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                />
              </div>
            )}
            {meta && (
              <p className="text-xs text-ink-2 mt-2 italic"><GlossedText>{nl ? meta.notesNl ?? meta.notes : meta.notes}</GlossedText></p>
            )}
          </div>
          <div>
            <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
              {t("producerModal.contextTitle")}
            </h3>
            {wikiLoading && (
              <div className="text-sm text-ink-2">{t("producerModal.wikiLoading", { producer: producer.producer_name })}</div>
            )}
            {wikiError && (
              <div className="text-sm text-ink-2 leading-relaxed">
                {t("producerModal.wikiErrorIntro")} <em>{producer.producer_name}</em>. The
                producer may be too small for an English-language Wikipedia entry,
                or the name needs disambiguation. Italian or producer-website
                lookup belongs in the next enrichment pass (see below).
              </div>
            )}
            {wiki && (
              <div>
                <p className="text-sm text-ink leading-relaxed">
                  <GlossedText>{wiki.extract}</GlossedText>
                </p>
                {wiki.content_urls?.desktop?.page && (
                  <a
                    href={wiki.content_urls.desktop.page}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 text-xs text-tuscan underline link-underline"
                  >
                    {t("producerModal.wikiReadMore")}
                  </a>
                )}
              </div>
            )}
            {meta && meta.varietals.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-1">
                  {t("producerModal.signatureVarietalsTitle")}
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

        {/* Enrichments — all deferred for producer level (paid sources) */}
        <div>
          <h3 className="text-xs uppercase tracking-widest text-ink-2 font-semibold mb-2">
            {t("producerModal.enrichmentsTitle")}
          </h3>
          <p className="text-sm text-ink-2 mb-3 max-w-3xl">
            <GlossedText>
              Producer-level data the pipeline does not yet pull. Every source
              below requires a paid service, a billing-account API key, or
              Firecrawl credits at a scale beyond the current run. Each item
              documents what the blocker is so a future budget decision can
              unlock the right one first:
            </GlossedText>
          </p>
          <ul className="space-y-2">
            {DEFERRED.map((idea) => (
              <li
                key={idea.label}
                className="rounded-lg border border-stone-200 px-4 py-3 bg-stone-50/40 hover-lift"
              >
                <div className="flex items-baseline justify-between gap-3 flex-wrap">
                  <span className="font-serif text-ink-2">
                    <span className="text-stone-400 mr-1.5">○</span>
                    {nl ? idea.labelNl : idea.label}
                  </span>
                  <span className="text-xs text-stone-500 italic">{t("producerModal.deferredTag")}</span>
                </div>
                <div className="text-xs text-ink-2 mt-1 ml-5"><GlossedText>{nl ? idea.whyNl : idea.why}</GlossedText></div>
                <div className="text-xs text-stone-500 mt-1 ml-5 italic">
                  <strong className="not-italic">{t("producerModal.sourceLabel")}</strong> <GlossedText>{nl ? idea.sourceNl : idea.source}</GlossedText> ·{" "}
                  <strong className="not-italic">{t("producerModal.blockerLabel")}</strong> <GlossedText>{nl ? idea.costNl : idea.cost}</GlossedText>
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
