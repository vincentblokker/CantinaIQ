// Display-label translations for canonical domain values that live in the data
// (market segments, recommendations, action buckets). The data keeps the
// canonical ENGLISH value (logic, color maps, and filters key off it); only the
// DISPLAYED label is localised. Keep these in sync with the *Nl fields in
// pdfData.ts.
import { useTranslation } from "react-i18next";

const SEGMENT_NL: Record<string, string> = {
  "Hidden Gem": "Verborgen parel",
  "Premium Icon": "Premium-icoon",
  "Commercial Value": "Commerciële waarde",
  "Overpriced Risk": "Te duur risico",
  "Low Confidence Niche": "Niche met weinig signaal",
};

const RECOMMENDATION_NL: Record<string, string> = {
  Target: "Benaderen",
  "Premium Brand Builder": "Premium merkbouwer",
  "Value Opportunity": "Waardekans",
  Monitor: "Monitoren",
  "Avoid for Now": "Nu vermijden",
};

const ACTION_BUCKET_NL: Record<string, string> = {
  Hold: "Behouden",
  Expand: "Uitbreiden",
  Audit: "Toetsen",
};

/** True when the active language is Dutch. Use to pick `*Nl` data fields. */
export function useNl(): boolean {
  const { i18n } = useTranslation();
  return i18n.language.startsWith("nl");
}

/** Language-aware resolvers for canonical domain values. Returns the Dutch
 *  label in NL mode, otherwise the canonical English value unchanged. */
export function useDomainLabels() {
  const nl = useNl();
  return {
    segment: (v: string) => (nl ? SEGMENT_NL[v] ?? v : v),
    recommendation: (v: string) => (nl ? RECOMMENDATION_NL[v] ?? v : v),
    action: (v: string) => (nl ? ACTION_BUCKET_NL[v] ?? v : v),
  };
}
