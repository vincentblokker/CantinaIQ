// Macro-region metadata used by the RegionDetailModal.
//
// Each macro region carries:
//   - bbox (OSM "minLon,minLat,maxLon,maxLat") for the embed map
//   - wikipediaSlug (en.wikipedia.org/wiki/<slug>) for fetching summary
//   - varietals: signature grape varieties
//   - notes: one-sentence terroir snapshot
//
// The data lookup tries multiple key variants (Italian, Dutch, English,
// lowercased) so it works against whatever spelling the pipeline emits.

export interface RegionMeta {
  bbox: string;
  wikipediaSlug: string;
  varietals: string[];
  notes: string;
}

const RAW: Record<string, RegionMeta> = {
  toscana: {
    bbox: "9.7,42.2,12.4,44.5",
    wikipediaSlug: "Tuscan_wine",
    varietals: ["Sangiovese", "Cabernet Sauvignon", "Merlot", "Cabernet Franc"],
    notes:
      "Italy's most internationally recognised wine region. Sangiovese dominates Chianti and Brunello; super-Tuscan blends drove the prestige tier from Bolgheri.",
  },
  piemonte: {
    bbox: "6.6,44.0,9.2,46.5",
    wikipediaSlug: "Piedmont_(wine)",
    varietals: ["Nebbiolo", "Barbera", "Dolcetto", "Moscato"],
    notes:
      "Cool continental climate, fog, low yields. Barolo and Barbaresco are the prestige expressions of Nebbiolo.",
  },
  veneto: {
    bbox: "10.6,44.7,13.1,46.7",
    wikipediaSlug: "Veneto",
    varietals: ["Corvina", "Garganega", "Glera (Prosecco)", "Pinot Grigio"],
    notes:
      "Largest wine producer by volume in Italy. Prosecco volumes mask premium pockets in Valpolicella (Amarone) and Soave.",
  },
  puglia: {
    bbox: "14.9,39.8,18.5,42.2",
    wikipediaSlug: "Apulia_wine",
    varietals: ["Primitivo", "Negroamaro", "Nero di Troia"],
    notes:
      "Warm climate, southern peninsula. Primitivo di Manduria is the most internationally legible appellation; value-zone darling.",
  },
  sicilia: {
    bbox: "12.4,36.6,15.7,38.3",
    wikipediaSlug: "Sicilian_wine",
    varietals: ["Nero d'Avola", "Nerello Mascalese", "Grillo", "Catarratto"],
    notes:
      "Etna's volcanic terroir produces some of Italy's most distinctive reds. Indigenous varietals dominate; growing biodynamic presence.",
  },
  abruzzo: {
    bbox: "13.0,41.7,14.8,42.9",
    wikipediaSlug: "Abruzzo_(wine)",
    varietals: ["Montepulciano", "Trebbiano", "Pecorino"],
    notes:
      "Mountainous, Adriatic-facing. Montepulciano d'Abruzzo offers reliable quality at sharply lower prices than equivalent Tuscan reds.",
  },
  campania: {
    bbox: "13.7,40.0,15.8,41.5",
    wikipediaSlug: "Campania_(wine)",
    varietals: ["Aglianico", "Fiano", "Greco", "Falanghina"],
    notes:
      "Volcanic soils around Vesuvius and Avellino. Taurasi (Aglianico) is the prestige red; whites from Fiano di Avellino are world-class.",
  },
  lazio: {
    bbox: "11.4,41.3,14.0,42.8",
    wikipediaSlug: "Lazio_(wine)",
    varietals: ["Malvasia", "Trebbiano", "Cesanese"],
    notes:
      "Rome's hinterland. Frascati dominates volume; quality-focused producers are emerging around Cesanese del Piglio.",
  },
  "emilia-romagna": {
    bbox: "9.2,43.7,12.8,45.1",
    wikipediaSlug: "Emilia-Romagna_wine",
    varietals: ["Sangiovese", "Lambrusco", "Albana", "Trebbiano"],
    notes:
      "Sangiovese di Romagna is the underrated cousin of Tuscan Chianti; Lambrusco is the volume export.",
  },
  marche: {
    bbox: "12.2,42.7,13.9,43.9",
    wikipediaSlug: "Marche_(wine)",
    varietals: ["Verdicchio", "Montepulciano", "Sangiovese"],
    notes:
      "Adriatic coast. Verdicchio dei Castelli di Jesi is one of Italy's most age-worthy whites.",
  },
  umbria: {
    bbox: "12.0,42.4,13.3,43.6",
    wikipediaSlug: "Umbria_(wine)",
    varietals: ["Sangiovese", "Sagrantino", "Trebbiano"],
    notes:
      "Sagrantino di Montefalco is one of the most tannic reds in Italy; small but distinctive output.",
  },
  "trentino-alto adige": {
    bbox: "10.4,45.6,12.5,47.1",
    wikipediaSlug: "Trentino-Alto_Adige/S%C3%BCdtirol",
    varietals: ["Pinot Grigio", "Gewürztraminer", "Lagrein", "Schiava"],
    notes:
      "Alpine, German-speaking north. Crisp aromatic whites and indigenous reds (Lagrein, Schiava) with cool-climate elegance.",
  },
  südtirol: {
    bbox: "10.4,45.6,12.5,47.1",
    wikipediaSlug: "Trentino-Alto_Adige/S%C3%BCdtirol",
    varietals: ["Pinot Grigio", "Gewürztraminer", "Lagrein"],
    notes:
      "Italian Tyrol — alpine viticulture with German cultural overlap. Premium aromatic whites.",
  },
  "friuli-venezia giulia": {
    bbox: "12.3,45.4,13.9,46.6",
    wikipediaSlug: "Friuli-Venezia_Giulia_wine",
    varietals: ["Friulano", "Ribolla Gialla", "Pinot Grigio", "Refosco"],
    notes:
      "Italy's north-eastern frontier. Skin-contact 'orange' wines pioneered here; aromatic whites are a strength.",
  },
  lombardia: {
    bbox: "8.5,44.7,11.4,46.6",
    wikipediaSlug: "Lombardy_wine",
    varietals: ["Nebbiolo", "Chardonnay", "Pinot Nero", "Pinot Bianco"],
    notes:
      "Franciacorta is Italy's answer to Champagne — méthode traditionelle sparkling. Valtellina produces alpine Nebbiolo.",
  },
  liguria: {
    bbox: "7.5,43.7,10.0,44.7",
    wikipediaSlug: "Liguria_(wine)",
    varietals: ["Vermentino", "Pigato", "Rossese"],
    notes:
      "Mediterranean coast. Tiny output; Vermentino and Pigato are the regional whites worth knowing.",
  },
  calabria: {
    bbox: "15.6,37.9,17.2,40.1",
    wikipediaSlug: "Calabrian_wine",
    varietals: ["Gaglioppo", "Greco", "Magliocco"],
    notes:
      "Southern tip, mountainous. Cirò is the historic appellation; emerging quality focus.",
  },
  basilicata: {
    bbox: "15.3,39.9,16.9,40.9",
    wikipediaSlug: "Basilicata_(wine)",
    varietals: ["Aglianico"],
    notes:
      "Aglianico del Vulture grows on volcanic slopes of Monte Vulture — one of Italy's most underrated prestige reds.",
  },
  sardegna: {
    bbox: "8.1,38.8,9.8,41.3",
    wikipediaSlug: "Sardinian_wine",
    varietals: ["Cannonau", "Vermentino", "Carignano"],
    notes:
      "Island viticulture. Cannonau (Grenache) and Vermentino define the modern Sardinian wine identity.",
  },
  molise: {
    bbox: "14.0,41.4,15.2,42.0",
    wikipediaSlug: "Molise_(wine)",
    varietals: ["Montepulciano", "Tintilia"],
    notes:
      "Tiny southern region. Tintilia is the indigenous red gaining slow recognition.",
  },
};

// Common spelling variants → canonical macro key
const ALIASES: Record<string, string> = {
  toscane: "toscana",
  tuscany: "toscana",
  apulia: "puglia",
  sicily: "sicilia",
  sicilië: "sicilia",
  campanië: "campania",
  abruzzen: "abruzzo",
  piedmont: "piemonte",
  "trentino-zuid-tirol": "trentino-alto adige",
  "alto adige": "trentino-alto adige",
  "südtirol – alto adige": "südtirol",
};

// Appellation / sub-region keywords → canonical macro key.
// When a region name contains any of these words, we resolve to the macro.
const APPELLATION_TO_MACRO: Record<string, string> = {
  // Toscana
  bolgheri: "toscana",
  brunello: "toscana",
  montalcino: "toscana",
  montepulciano: "toscana", // ambiguous with Abruzzo's Montepulciano d'Abruzzo — handled below
  chianti: "toscana",
  "vino nobile": "toscana",
  "carmignano": "toscana",
  "morellino": "toscana",
  // Piemonte
  barolo: "piemonte",
  barbaresco: "piemonte",
  "asti": "piemonte",
  langhe: "piemonte",
  monferrato: "piemonte",
  // Veneto
  valpolicella: "veneto",
  amarone: "veneto",
  soave: "veneto",
  prosecco: "veneto",
  "conegliano": "veneto",
  bardolino: "veneto",
  // Puglia
  "manduria": "puglia",
  primitivo: "puglia",
  negroamaro: "puglia",
  "salice salentino": "puglia",
  "gioia del colle": "puglia",
  "castel del monte": "puglia",
  // Sicilia
  etna: "sicilia",
  "nero d'avola": "sicilia",
  pantelleria: "sicilia",
  marsala: "sicilia",
  // Abruzzo
  "d'abruzzo": "abruzzo",
  "terre di chieti": "abruzzo",
  // Campania
  taurasi: "campania",
  fiano: "campania",
  irpinia: "campania",
  greco: "campania",
  // Emilia-Romagna
  lambrusco: "emilia-romagna",
  sangiovese: "emilia-romagna",
  // Marche
  verdicchio: "marche",
  conero: "marche",
  // Umbria
  sagrantino: "umbria",
  montefalco: "umbria",
  orvieto: "umbria",
  torgiano: "umbria",
  // Trentino-Alto Adige
  trentino: "trentino-alto adige",
  // Friuli
  collio: "friuli-venezia giulia",
  friuli: "friuli-venezia giulia",
  // Lombardia
  franciacorta: "lombardia",
  valtellina: "lombardia",
  oltrepò: "lombardia",
  "provincia di pavia": "lombardia",
  // Sardegna
  cannonau: "sardegna",
  // Basilicata
  vulture: "basilicata",
};

// Whole-Italy fallback so the modal always has a map + wiki.
const ITALY_DEFAULT: RegionMeta = {
  bbox: "6.6,36.6,18.5,47.1",
  wikipediaSlug: "Italian_wine",
  varietals: ["Sangiovese", "Nebbiolo", "Glera", "Primitivo", "Pinot Grigio"],
  notes:
    "Italy has 20 wine regions and 400+ recognised appellations. Use the macro-region pages for terroir specifics; this entry is the country-wide fallback.",
};

export function lookupRegion(name?: string): RegionMeta | null {
  if (!name) return ITALY_DEFAULT;
  const key = name.trim().toLowerCase();

  // 1. Direct macro key (e.g. "toscana")
  if (RAW[key]) return RAW[key];

  // 2. Alias for spelling variants (e.g. "toscane")
  const alias = ALIASES[key];
  if (alias && RAW[alias]) return RAW[alias];

  // 3. Appellation map — match any keyword inside the region name
  for (const phrase of Object.keys(APPELLATION_TO_MACRO)) {
    if (key.includes(phrase)) {
      const macro = APPELLATION_TO_MACRO[phrase];
      // Disambiguate "Montepulciano d'Abruzzo" from Tuscan Montepulciano
      if (phrase === "montepulciano" && key.includes("d'abruzzo")) {
        return RAW["abruzzo"];
      }
      if (RAW[macro]) return RAW[macro];
    }
  }

  // 4. Direct partial match against macro keys (catches "umbrië" → umbria via substring umbria)
  for (const macroKey of Object.keys(RAW)) {
    if (key.includes(macroKey) || macroKey.includes(key)) return RAW[macroKey];
  }

  // 5. Country-wide fallback
  return ITALY_DEFAULT;
}
