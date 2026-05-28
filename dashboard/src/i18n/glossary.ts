// Curated glossary of difficult / technical English terms used across the
// dashboard. In NL mode, <GlossedText> wraps the first occurrence of each term
// inside prose containers and shows the Dutch explanation on hover/focus.
//
// Keys are the canonical English term, lower-cased (lookup is case-insensitive).
// We deliberately keep the term itself English (it is a domain term) and only
// explain it in Dutch — so the canonical vocabulary stays stable while a Dutch
// reader still understands it.
export interface GlossEntry {
  /** Dutch explanation shown on hover/focus in NL mode. */
  nl: string;
}

export const GLOSSARY: Record<string, GlossEntry> = {
  "defensible shortlist": {
    nl: "Een onderbouwde, verdedigbare selectie — elke keuze is herleidbaar naar de data en de config.",
  },
  "weighted rating": {
    nl: "Bayesiaans gewogen beoordeling: weinig reviews trekken richting het dataset-gemiddelde, zodat 4.8 uit 12 reviews niet boven 4.4 uit 5000 eindigt.",
  },
  "bayesian shrinkage": {
    nl: "Statistische correctie die onzekere scores (weinig reviews) naar het gemiddelde 'krimpt'.",
  },
  "bayesian-shrunk": {
    nl: "Met Bayesiaanse krimp gecorrigeerd: weinig-gereviewde wijnen worden naar het gemiddelde getrokken.",
  },
  "shrinkage threshold": {
    nl: "De parameter m die bepaalt hoe sterk weinig-gereviewde wijnen naar het gemiddelde worden getrokken.",
  },
  shrinkage: {
    nl: "Het naar het gemiddelde 'krimpen' van onzekere scores op basis van het aantal reviews.",
  },
  "value for money": {
    nl: "Kwaliteit per euro — de verhouding tussen beoordeling en prijs.",
  },
  "value score": {
    nl: "Maat voor prijs-kwaliteitverhouding: kwaliteit afgezet tegen de prijs.",
  },
  "market confidence": {
    nl: "Betrouwbaarheid van het signaal op basis van het aantal reviews.",
  },
  "premium fit": {
    nl: "Hoe goed een producent past bij Slurpini's premium-positionering.",
  },
  "portfolio opportunity": {
    nl: "Strategische meerwaarde: vult een gat in het assortiment.",
  },
  "composite score": {
    nl: "De gewogen totaalscore over alle vijf de factoren.",
  },
  contamination: {
    nl: "Aangenomen aandeel afwijkingen (anomalieën) dat het Isolation-Forest-model verwacht.",
  },
  "isolation forest": {
    nl: "Machine-learning-methode die ongebruikelijke reviewpatronen (uitschieters) detecteert.",
  },
  bootstrap: {
    nl: "Herhaald herbemonsteren van de data om betrouwbaarheidsintervallen op de ranglijst te schatten.",
  },
  "confidence interval": {
    nl: "Bandbreedte (5e–95e percentiel) waarbinnen de werkelijke ranglijstpositie waarschijnlijk valt.",
  },
  "confidence bands": {
    nl: "De onzekerheidsmarges rond een score of ranglijstpositie.",
  },
  terroir: {
    nl: "Samenspel van bodem, klimaat en ligging dat het karakter van een wijn bepaalt.",
  },
  "macro-region": {
    nl: "Overkoepelende wijnregio waaronder appellaties en subregio's vallen.",
  },
  "macro region": {
    nl: "Overkoepelende wijnregio waaronder appellaties en subregio's vallen.",
  },
  docg: {
    nl: "Denominazione di Origine Controllata e Garantita — hoogste Italiaanse herkomstklasse.",
  },
  doc: {
    nl: "Denominazione di Origine Controllata — gecontroleerde Italiaanse herkomstbenaming.",
  },
  "kendall-τ": {
    nl: "Rangcorrelatie (Kendall's tau): meet hoe stabiel de top-ranglijst blijft als een parameter verandert.",
  },
  "gold-set recall": {
    nl: "Aandeel van een bekende referentielijst (gold set) dat de extractie correct terugvindt.",
  },
  recall: {
    nl: "Aandeel van de werkelijk relevante items dat het model correct terugvindt.",
  },
  "isolation forest at": {
    nl: "Isolation Forest: detecteert uitschieters in reviewpatronen.",
  },
  pandera: {
    nl: "Python-bibliotheek die dataframes valideert tegen expliciete schema-contracten.",
  },
  reproducibility: {
    nl: "Reproduceerbaarheid: dezelfde config + data levert exact dezelfde uitkomsten.",
  },
};
