export type Recommendation =
  | "Target"
  | "Premium Brand Builder"
  | "Value Opportunity"
  | "Monitor"
  | "Avoid for Now";

export interface Producer {
  producer_name: string;
  macro_region: string;
  recommendation: Recommendation;
  market_segment: string;
  weighted_rating: number;
  total_reviews: number;
  avg_price: number;
  composite_score: number;
  value_score?: number;
}

interface RawRegion {
  region: string;
  macro_region?: string;
  weighted_rating: number;
  avg_price: number;
  wines?: number;
  wines_in_dataset?: number;
  total_reviews: number;
  value_score?: number;
}

export interface Region {
  region: string;
  macro_region?: string;
  weighted_rating: number;
  avg_price: number;
  wines: number;
  total_reviews: number;
  value_score?: number;
}

interface RawSummary {
  run_id: string;
  config_hash: string;
  wines_total: number;
  producers_total: number;
  regions_total: number;
  avg_weighted_rating?: number;
  avg_price?: number;
}

export interface DashboardSummary {
  totals: { wines: number; producers: number; regions: number };
  config_hash: string;
  run_id: string;
  avg_weighted_rating?: number;
  avg_price?: number;
}

const base = (path: string) => `/data/${path}`;

async function safeJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const r = await fetch(base(path));
    if (!r.ok) return fallback;
    return (await r.json()) as T;
  } catch {
    return fallback;
  }
}

export const loadProducers = () =>
  safeJson<Producer[]>("producer_rankings.json", []);

export interface Wine {
  wine_name: string;
  region: string;
  macro_region: string;
  rating: number;
  rating_count: number;
  price: number;
  weighted_rating: number;
  value_score: number;
  composite_score: number;
  market_segment: string;
  vintage: number | null;
  producer_name: string;
  inferred_grape_or_style: string;
  price_segment: string;
  confidence_segment: string;
}

export const loadWines = () => safeJson<Wine[]>("wine_shortlist.json", []);

export async function loadRegions(): Promise<Region[]> {
  const raw = await safeJson<RawRegion[]>("region_rankings.json", []);
  return raw.map((r) => ({
    region: r.region,
    macro_region: r.macro_region,
    weighted_rating: r.weighted_rating,
    avg_price: r.avg_price,
    wines: r.wines ?? r.wines_in_dataset ?? 0,
    total_reviews: r.total_reviews,
    value_score: r.value_score,
  }));
}

export async function loadSummary(): Promise<DashboardSummary> {
  const raw = await safeJson<RawSummary | null>("dashboard_summary.json", null);
  if (!raw) {
    return {
      totals: { wines: 0, producers: 0, regions: 0 },
      config_hash: "unknown",
      run_id: "(no data)",
    };
  }
  return {
    run_id: raw.run_id,
    config_hash: raw.config_hash,
    avg_weighted_rating: raw.avg_weighted_rating,
    avg_price: raw.avg_price,
    totals: {
      wines: raw.wines_total ?? 0,
      producers: raw.producers_total ?? 0,
      regions: raw.regions_total ?? 0,
    },
  };
}
