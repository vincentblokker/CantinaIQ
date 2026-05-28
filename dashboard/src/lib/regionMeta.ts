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
  /** Dutch translation of {@link notes}. */
  notesNl: string;
  /** Enrichment additions, may be undefined for unmapped regions or country-wide fallback. */
  docCount?: number;
  docgCount?: number;
  /** Approximate annual wine production in hectolitres, year ≈ 2022-2023 from ISTAT-published data. */
  annualHl?: number;
  /** 2018-2024 vintage assessments per region. Single-letter grade ("A+","A","B+","B","C","—"). Sourced from public-domain consensus ratings; not Wine Enthusiast specifically. */
  vintageScores?: Record<number, string>;
  /** 2-3 sentence climate description. */
  climate?: string;
  /** Dutch translation of {@link climate}. */
  climateNl?: string;
  /** 1-2 sentence terroir / geology note. */
  terroir?: string;
  /** Dutch translation of {@link terroir}. */
  terroirNl?: string;
}

const RAW: Record<string, RegionMeta> = {
  toscana: {
    bbox: "9.7,42.2,12.4,44.5",
    wikipediaSlug: "Tuscan_wine",
    varietals: ["Sangiovese", "Cabernet Sauvignon", "Merlot", "Cabernet Franc"],
    notes:
      "Italy's most internationally recognised wine region. Sangiovese dominates Chianti and Brunello; super-Tuscan blends drove the prestige tier from Bolgheri.",
    notesNl:
      "De internationaal meest erkende wijnregio van Italië. Sangiovese domineert in Chianti en Brunello; super-Tuscan-blends stuwden het prestigesegment vanuit Bolgheri.",
    docCount: 41,
    docgCount: 11,
    annualHl: 2_500_000,
    climate:
      "Mediterranean with continental pockets inland. Long, dry summers; mild, wet winters. Coastal Bolgheri benefits from sea breezes that moderate ripening; inland Chianti Classico runs cooler at altitude.",
    climateNl:
      "Mediterraan met continentale enclaves landinwaarts. Lange, droge zomers; milde, natte winters. Het kustgebied Bolgheri profiteert van zeebriezen die de rijping temperen; het binnenland van Chianti Classico is koeler door de hoogte.",
    terroir:
      "Galestro and alberese marl soils in Chianti; iron-rich clay around Montalcino; alluvial gravels close to the Tyrrhenian coast.",
    terroirNl:
      "Galestro- en alberese-mergelbodems in Chianti; ijzerrijke klei rond Montalcino; alluviale grindlagen dicht bij de Tyrreense kust.",
    vintageScores: { 2018: "B", 2019: "A", 2020: "B+", 2021: "A", 2022: "B+", 2023: "B", 2024: "—" },
  },
  piemonte: {
    bbox: "6.6,44.0,9.2,46.5",
    wikipediaSlug: "Piedmont_(wine)",
    varietals: ["Nebbiolo", "Barbera", "Dolcetto", "Moscato"],
    notes:
      "Cool continental climate, fog, low yields. Barolo and Barbaresco are the prestige expressions of Nebbiolo.",
    notesNl:
      "Koel continentaal klimaat, mist en lage opbrengsten. Barolo en Barbaresco zijn de prestige-uitdrukkingen van Nebbiolo.",
    docCount: 41,
    docgCount: 19,
    annualHl: 2_500_000,
    climate:
      "Continental with significant diurnal variation; thick autumn fog (nebbia) lent its name to Nebbiolo. Long ripening seasons produce structured, tannic reds.",
    climateNl:
      "Continentaal met grote dag-nachtverschillen; de dichte herfstmist (nebbia) gaf Nebbiolo zijn naam. Lange rijpingsperioden leveren gestructureerde, tanninerijke rode wijnen op.",
    terroir:
      "Marl, sandstone, and tufaceous limestones in the Langhe; iron-rich calcareous clays around La Morra and Castiglione Falletto.",
    terroirNl:
      "Mergel, zandsteen en tufhoudende kalkstenen in de Langhe; ijzerrijke kalkhoudende kleigronden rond La Morra en Castiglione Falletto.",
    vintageScores: { 2018: "B+", 2019: "A", 2020: "A-", 2021: "A", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  veneto: {
    bbox: "10.6,44.7,13.1,46.7",
    wikipediaSlug: "Veneto",
    varietals: ["Corvina", "Garganega", "Glera (Prosecco)", "Pinot Grigio"],
    notes:
      "Largest wine producer by volume in Italy. Prosecco volumes mask premium pockets in Valpolicella (Amarone) and Soave.",
    notesNl:
      "Qua volume de grootste wijnproducent van Italië. De grote Prosecco-volumes verhullen premium-enclaves in Valpolicella (Amarone) en Soave.",
    docCount: 29,
    docgCount: 14,
    annualHl: 11_000_000,
    climate:
      "Cool continental in the foothills, warmer Mediterranean influence near Lake Garda. Long ripening seasons in Valpolicella; sub-alpine cool in Prosecco hills.",
    climateNl:
      "Koel continentaal in de heuvels, met warmere mediterrane invloed nabij het Gardameer. Lange rijpingsperioden in Valpolicella; sub-alpiene koelte in de Prosecco-heuvels.",
    terroir:
      "Volcanic basalts in the Lessini hills (Soave); limestone-clay marl in Valpolicella; morainic gravels around Lake Garda.",
    terroirNl:
      "Vulkanische basalten in de Lessini-heuvels (Soave); kalk-kleimergel in Valpolicella; morenegrind rond het Gardameer.",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "A-", 2021: "A", 2022: "B", 2023: "B", 2024: "—" },
  },
  puglia: {
    bbox: "14.9,39.8,18.5,42.2",
    wikipediaSlug: "Apulia_wine",
    varietals: ["Primitivo", "Negroamaro", "Nero di Troia"],
    notes:
      "Warm climate, southern peninsula. Primitivo di Manduria is the most internationally legible appellation; value-zone darling.",
    notesNl:
      "Warm klimaat, het zuidelijke schiereiland. Primitivo di Manduria is de internationaal best herkenbare appellation; een favoriet in het prijs-kwaliteitsegment.",
    docCount: 28,
    docgCount: 4,
    annualHl: 10_000_000,
    climate:
      "Hot Mediterranean. Long, dry growing season tempered by sea breezes (Adriatic east, Ionian south). Ripening is reliable; acidity preservation is the challenge.",
    climateNl:
      "Heet mediterraan. Een lang, droog groeiseizoen dat wordt getemperd door zeebriezen (de Adriatische Zee in het oosten, de Ionische in het zuiden). De rijping verloopt betrouwbaar; het behoud van zuren is de uitdaging.",
    terroir:
      "Red iron-rich terra rossa over limestone bedrock; sandy alluvial plains in Salento. Limestone caves moderate cellar temperatures naturally.",
    terroirNl:
      "Rode, ijzerrijke terra rossa op een kalkstenen ondergrond; zandige alluviale vlakten in Salento. Kalkstenen grotten houden de keldertemperaturen van nature gematigd.",
    vintageScores: { 2018: "A-", 2019: "B+", 2020: "A-", 2021: "A-", 2022: "A-", 2023: "B+", 2024: "—" },
  },
  sicilia: {
    bbox: "12.4,36.6,15.7,38.3",
    wikipediaSlug: "Sicilian_wine",
    varietals: ["Nero d'Avola", "Nerello Mascalese", "Grillo", "Catarratto"],
    notes:
      "Etna's volcanic terroir produces some of Italy's most distinctive reds. Indigenous varietals dominate; growing biodynamic presence.",
    notesNl:
      "Het vulkanische terroir van de Etna levert enkele van de meest karakteristieke rode wijnen van Italië op. Inheemse druivenrassen domineren; de biodynamische aanwezigheid groeit.",
    docCount: 23,
    docgCount: 1,
    annualHl: 5_000_000,
    climate:
      "Mediterranean with strong altitude variation. Etna's vineyards sit between 400 and 1,200 m above sea level — alpine-cool by latitude. Coastal Marsala bakes in summer.",
    climateNl:
      "Mediterraan met sterke hoogteverschillen. De wijngaarden van de Etna liggen tussen 400 en 1.200 m boven zeeniveau — alpien koel voor de breedtegraad. Het kustgebied Marsala bakt in de zomer.",
    terroir:
      "Black volcanic basalt and ash on Etna's slopes; limestone-clay across the central interior; calcareous marl in western Marsala.",
    terroirNl:
      "Zwarte vulkanische basalt en as op de hellingen van de Etna; kalk-klei in het centrale binnenland; kalkhoudende mergel in het westelijke Marsala.",
    vintageScores: { 2018: "A-", 2019: "A-", 2020: "A", 2021: "A-", 2022: "A-", 2023: "B+", 2024: "—" },
  },
  abruzzo: {
    bbox: "13.0,41.7,14.8,42.9",
    wikipediaSlug: "Abruzzo_(wine)",
    varietals: ["Montepulciano", "Trebbiano", "Pecorino"],
    notes:
      "Mountainous, Adriatic-facing. Montepulciano d'Abruzzo offers reliable quality at sharply lower prices than equivalent Tuscan reds.",
    notesNl:
      "Bergachtig en op de Adriatische Zee gericht. Montepulciano d'Abruzzo biedt betrouwbare kwaliteit tegen veel lagere prijzen dan vergelijkbare Toscaanse rode wijnen.",
    docCount: 8,
    docgCount: 1,
    annualHl: 3_500_000,
    climate:
      "Two climates meeting: Apennine continental in the highlands, Adriatic Mediterranean on the coast. Daily temperature swings preserve aromatic intensity.",
    climateNl:
      "Twee klimaten ontmoeten elkaar: Apenijns continentaal in het hoogland, Adriatisch mediterraan aan de kust. De dagelijkse temperatuurschommelingen behouden de aromatische intensiteit.",
    terroir:
      "Clay, limestone, and gravel on hillside vineyards; sandier alluvial soils on coastal plains.",
    terroirNl:
      "Klei, kalksteen en grind in de heuvelwijngaarden; zandiger alluviale bodems op de kustvlakten.",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "B+", 2021: "A-", 2022: "B+", 2023: "B", 2024: "—" },
  },
  campania: {
    bbox: "13.7,40.0,15.8,41.5",
    wikipediaSlug: "Campania_(wine)",
    varietals: ["Aglianico", "Fiano", "Greco", "Falanghina"],
    notes:
      "Volcanic soils around Vesuvius and Avellino. Taurasi (Aglianico) is the prestige red; whites from Fiano di Avellino are world-class.",
    notesNl:
      "Vulkanische bodems rond de Vesuvius en Avellino. Taurasi (Aglianico) is de prestige-rode; witte wijnen uit Fiano di Avellino zijn van wereldklasse.",
    docCount: 15,
    docgCount: 4,
    annualHl: 750_000,
    climate:
      "Mediterranean coastal moderation at Sorrento; cooler high-altitude continental zones inland (Irpinia, Taurasi sits at 400-700m). Late-ripening varieties thrive.",
    climateNl:
      "Mediterrane kustmatiging bij Sorrento; koelere, hooggelegen continentale zones landinwaarts (Irpinia, Taurasi ligt op 400-700 m). Laatrijpende rassen gedijen hier.",
    terroir:
      "Volcanic ash from Vesuvius and the Phlegraean Fields; limestone and clay in higher Irpinia. Mineral-driven whites are the signature.",
    terroirNl:
      "Vulkanische as van de Vesuvius en de Flegreïsche Velden; kalksteen en klei in het hogere Irpinia. Mineraalgedreven witte wijnen zijn het handelsmerk.",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "A-", 2021: "A-", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  lazio: {
    bbox: "11.4,41.3,14.0,42.8",
    wikipediaSlug: "Lazio_(wine)",
    varietals: ["Malvasia", "Trebbiano", "Cesanese"],
    notes:
      "Rome's hinterland. Frascati dominates volume; quality-focused producers are emerging around Cesanese del Piglio.",
    notesNl:
      "Het achterland van Rome. Frascati domineert qua volume; kwaliteitsgerichte producenten komen op rond Cesanese del Piglio.",
    docCount: 27,
    docgCount: 3,
    annualHl: 800_000,
    climate:
      "Mediterranean with thermal influence from the Tyrrhenian. Castelli Romani volcanic hills moderate summer heat; coastal areas run warmer.",
    climateNl:
      "Mediterraan met thermische invloed vanaf de Tyrreense Zee. De vulkanische heuvels van de Castelli Romani temperen de zomerhitte; kustgebieden zijn warmer.",
    terroir:
      "Volcanic tuff and basalt around the Castelli Romani; clay-limestone in inland Frosinone (Cesanese country).",
    terroirNl:
      "Vulkanisch tuf en basalt rond de Castelli Romani; klei-kalksteen in het landinwaartse Frosinone (het gebied van Cesanese).",
    vintageScores: { 2018: "B", 2019: "B+", 2020: "B+", 2021: "B+", 2022: "B", 2023: "B", 2024: "—" },
  },
  "emilia-romagna": {
    bbox: "9.2,43.7,12.8,45.1",
    wikipediaSlug: "Emilia-Romagna_wine",
    varietals: ["Sangiovese", "Lambrusco", "Albana", "Trebbiano"],
    notes:
      "Sangiovese di Romagna is the underrated cousin of Tuscan Chianti; Lambrusco is the volume export.",
    notesNl:
      "Sangiovese di Romagna is de ondergewaardeerde neef van de Toscaanse Chianti; Lambrusco is het exportproduct in volume.",
    docCount: 19,
    docgCount: 2,
    annualHl: 7_000_000,
    climate:
      "Continental Po Valley climate — hot summers, cold winters, foggy autumns. Coastal Romagna runs slightly milder; the Apennine foothills bring cooler nights.",
    climateNl:
      "Continentaal klimaat van de Po-vlakte — hete zomers, koude winters, mistige herfsten. Het kustgebied van de Romagna is iets milder; de uitlopers van de Apenijnen brengen koelere nachten.",
    terroir:
      "Alluvial clay and silt in the Po flatlands (Lambrusco country); calcareous clay-marl in Romagna's hills (Sangiovese country).",
    terroirNl:
      "Alluviale klei en slib in de Po-vlakten (het gebied van Lambrusco); kalkhoudende klei-mergel in de heuvels van de Romagna (het gebied van Sangiovese).",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "B+", 2021: "A-", 2022: "B", 2023: "B", 2024: "—" },
  },
  marche: {
    bbox: "12.2,42.7,13.9,43.9",
    wikipediaSlug: "Marche_(wine)",
    varietals: ["Verdicchio", "Montepulciano", "Sangiovese"],
    notes:
      "Adriatic coast. Verdicchio dei Castelli di Jesi is one of Italy's most age-worthy whites.",
    notesNl:
      "De Adriatische kust. Verdicchio dei Castelli di Jesi is een van de best te rijpen witte wijnen van Italië.",
    docCount: 15,
    docgCount: 5,
    annualHl: 1_000_000,
    climate:
      "Adriatic Mediterranean tempered by Apennine altitude. Cool nights preserve aromatic intensity in Verdicchio whites; reds from coastal Conero ripen reliably.",
    climateNl:
      "Adriatisch mediterraan, getemperd door de hoogte van de Apenijnen. Koele nachten behouden de aromatische intensiteit van de Verdicchio-witte wijnen; rode wijnen uit het kustgebied Conero rijpen betrouwbaar.",
    terroir:
      "Calcareous clay-marl on hillsides; sandy alluvial soils near the coast. Conero's reds grow on mineral-rich volcanic-influenced ground.",
    terroirNl:
      "Kalkhoudende klei-mergel op de hellingen; zandige alluviale bodems nabij de kust. De rode wijnen van Conero groeien op mineraalrijke, vulkanisch beïnvloede grond.",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "A-", 2021: "A-", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  umbria: {
    bbox: "12.0,42.4,13.3,43.6",
    wikipediaSlug: "Umbria_(wine)",
    varietals: ["Sangiovese", "Sagrantino", "Trebbiano"],
    notes:
      "Sagrantino di Montefalco is one of the most tannic reds in Italy; small but distinctive output.",
    notesNl:
      "Sagrantino di Montefalco is een van de meest tanninerijke rode wijnen van Italië; een kleine maar onderscheidende productie.",
    docCount: 13,
    docgCount: 2,
    annualHl: 500_000,
    climate:
      "Continental inland — hot summers, cold winters. No coastal moderation. Montefalco's Sagrantino benefits from the long, dry ripening.",
    climateNl:
      "Continentaal landinwaarts — hete zomers, koude winters. Geen matigende invloed van de kust. De Sagrantino van Montefalco profiteert van de lange, droge rijping.",
    terroir:
      "Calcareous marl and sandstone in Montefalco; volcanic-influenced soils around Orvieto. Lakes (Trasimeno) moderate microclimate locally.",
    terroirNl:
      "Kalkhoudende mergel en zandsteen in Montefalco; vulkanisch beïnvloede bodems rond Orvieto. Meren (Trasimeno) temperen plaatselijk het microklimaat.",
    vintageScores: { 2018: "B", 2019: "A-", 2020: "B+", 2021: "A-", 2022: "B", 2023: "B+", 2024: "—" },
  },
  "trentino-alto adige": {
    bbox: "10.4,45.6,12.5,47.1",
    wikipediaSlug: "Trentino-Alto_Adige/S%C3%BCdtirol",
    varietals: ["Pinot Grigio", "Gewürztraminer", "Lagrein", "Schiava"],
    notes:
      "Alpine, German-speaking north. Crisp aromatic whites and indigenous reds (Lagrein, Schiava) with cool-climate elegance.",
    notesNl:
      "Het alpiene, Duitstalige noorden. Frisse aromatische witte wijnen en inheemse rode wijnen (Lagrein, Schiava) met de elegantie van een koel klimaat.",
    docCount: 8,
    docgCount: 1,
    annualHl: 1_200_000,
    climate:
      "Alpine continental — cold winters, warm but short summers, dramatic diurnal swings. The Adige valley acts as a warm corridor; mountain vineyards run cool at 500-1,000m.",
    climateNl:
      "Alpien continentaal — koude winters, warme maar korte zomers, sterke dag-nachtverschillen. Het Adige-dal fungeert als een warme corridor; bergwijngaarden zijn koel op 500-1.000 m.",
    terroir:
      "Porphyry and quartz in upper Adige; dolomitic limestone on hillsides; alluvial sands on valley floors.",
    terroirNl:
      "Porfier en kwarts in het bovenste Adige; dolomietische kalksteen op de hellingen; alluviale zanden op de dalbodems.",
    vintageScores: { 2018: "A-", 2019: "A-", 2020: "A-", 2021: "A", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  südtirol: {
    bbox: "10.4,45.6,12.5,47.1",
    wikipediaSlug: "Trentino-Alto_Adige/S%C3%BCdtirol",
    varietals: ["Pinot Grigio", "Gewürztraminer", "Lagrein"],
    notes:
      "Italian Tyrol — alpine viticulture with German cultural overlap. Premium aromatic whites.",
    notesNl:
      "Italiaans Tirol — alpiene wijnbouw met Duitse culturele overlap. Premium aromatische witte wijnen.",
    docCount: 8,
    docgCount: 1,
    annualHl: 350_000,
    climate:
      "Alpine — warm dry summers, cold winters. South-facing slopes catch maximum sun; cool nights at altitude preserve acidity in aromatic whites.",
    climateNl:
      "Alpien — warme droge zomers, koude winters. Op het zuiden gerichte hellingen vangen maximaal zonlicht; koele nachten op hoogte behouden de zuren in de aromatische witte wijnen.",
    terroir:
      "Porphyry, dolomite, and slate. Lagrein loves the warmer alluvial valley floors; Gewürztraminer thrives on hillsides.",
    terroirNl:
      "Porfier, dolomiet en leisteen. Lagrein houdt van de warmere alluviale dalbodems; Gewürztraminer gedijt op de hellingen.",
    vintageScores: { 2018: "A-", 2019: "A-", 2020: "A-", 2021: "A", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  "friuli-venezia giulia": {
    bbox: "12.3,45.4,13.9,46.6",
    wikipediaSlug: "Friuli-Venezia_Giulia_wine",
    varietals: ["Friulano", "Ribolla Gialla", "Pinot Grigio", "Refosco"],
    notes:
      "Italy's north-eastern frontier. Skin-contact 'orange' wines pioneered here; aromatic whites are a strength.",
    notesNl:
      "De noordoostelijke grens van Italië. Hier werden 'orange' wijnen met schilcontact gepionierd; aromatische witte wijnen vormen een sterk punt.",
    docCount: 12,
    docgCount: 4,
    annualHl: 2_000_000,
    climate:
      "Sub-alpine continental in Collio, Mediterranean influence on the coastal plain. Strong bora wind dries vineyards and reduces disease pressure.",
    climateNl:
      "Sub-alpien continentaal in Collio, met mediterrane invloed op de kustvlakte. De krachtige bora-wind droogt de wijngaarden en vermindert de ziektedruk.",
    terroir:
      "Ponca — alternating marl and sandstone layers — defines Collio whites. Alluvial gravels in the Isonzo plain.",
    terroirNl:
      "Ponca — afwisselende lagen mergel en zandsteen — bepaalt de witte wijnen van Collio. Alluviale grindlagen in de Isonzo-vlakte.",
    vintageScores: { 2018: "A-", 2019: "A-", 2020: "A-", 2021: "A", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  lombardia: {
    bbox: "8.5,44.7,11.4,46.6",
    wikipediaSlug: "Lombardy_wine",
    varietals: ["Nebbiolo", "Chardonnay", "Pinot Nero", "Pinot Bianco"],
    notes:
      "Franciacorta is Italy's answer to Champagne — méthode traditionelle sparkling. Valtellina produces alpine Nebbiolo.",
    notesNl:
      "Franciacorta is het Italiaanse antwoord op Champagne — mousserend volgens de méthode traditionelle. Valtellina produceert alpiene Nebbiolo.",
    docCount: 21,
    docgCount: 5,
    annualHl: 1_500_000,
    climate:
      "Two climates: alpine Valtellina (Nebbiolo on steep terraces, 400-700m); pre-alpine moraine in Franciacorta moderated by Lake Iseo (sparkling base wines).",
    climateNl:
      "Twee klimaten: alpien Valtellina (Nebbiolo op steile terrassen, 400-700 m); pre-alpiene morene in Franciacorta, getemperd door het Iseomeer (basiswijnen voor mousserend).",
    terroir:
      "Granite and schist in Valtellina; morainic gravels and limestone in Franciacorta — perfect for the chalk-loving Chardonnay and Pinot Noir.",
    terroirNl:
      "Graniet en schist in Valtellina; morenegrind en kalksteen in Franciacorta — perfect voor de kalkminnende Chardonnay en Pinot Noir.",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "A-", 2021: "A", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  liguria: {
    bbox: "7.5,43.7,10.0,44.7",
    wikipediaSlug: "Liguria_(wine)",
    varietals: ["Vermentino", "Pigato", "Rossese"],
    notes:
      "Mediterranean coast. Tiny output; Vermentino and Pigato are the regional whites worth knowing.",
    notesNl:
      "De mediterrane kust. Een minieme productie; Vermentino en Pigato zijn de regionale witte wijnen die het kennen waard zijn.",
    docCount: 8,
    docgCount: 0,
    annualHl: 75_000,
    climate:
      "Mediterranean coastal — mild winters, warm dry summers, strong sea influence. Terraced vineyards on impossibly steep cliffs (Cinque Terre, Sciacchetrà).",
    climateNl:
      "Mediterraan kustklimaat — milde winters, warme droge zomers, sterke zee-invloed. Terrasvormige wijngaarden op onwaarschijnlijk steile kliffen (Cinque Terre, Sciacchetrà).",
    terroir:
      "Schist, slate, and limestone fragments on terraced cliffs. Salt-laced sea air imprints the whites.",
    terroirNl:
      "Schist, leisteen en kalksteenfragmenten op terrasvormige kliffen. De met zout doortrokken zeelucht drukt zijn stempel op de witte wijnen.",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "A-", 2021: "A-", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  calabria: {
    bbox: "15.6,37.9,17.2,40.1",
    wikipediaSlug: "Calabrian_wine",
    varietals: ["Gaglioppo", "Greco", "Magliocco"],
    notes:
      "Southern tip, mountainous. Cirò is the historic appellation; emerging quality focus.",
    notesNl:
      "De zuidpunt, bergachtig. Cirò is de historische appellation; een opkomende focus op kwaliteit.",
    docCount: 9,
    docgCount: 0,
    annualHl: 400_000,
    climate:
      "Hot Mediterranean coastal, but the interior runs alpine — the Sila and Pollino massifs reach over 2,000m. High-altitude vineyards preserve acidity in the heat.",
    climateNl:
      "Heet mediterraan aan de kust, maar het binnenland is alpien — de massieven van de Sila en Pollino reiken tot boven de 2.000 m. Hooggelegen wijngaarden behouden de zuren ondanks de hitte.",
    terroir:
      "Granite, schist, and gneiss in the highlands; coastal sand and limestone in Cirò.",
    terroirNl:
      "Graniet, schist en gneis in het hoogland; kustzand en kalksteen in Cirò.",
    vintageScores: { 2018: "B+", 2019: "B+", 2020: "A-", 2021: "B+", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  basilicata: {
    bbox: "15.3,39.9,16.9,40.9",
    wikipediaSlug: "Basilicata_(wine)",
    varietals: ["Aglianico"],
    notes:
      "Aglianico del Vulture grows on volcanic slopes of Monte Vulture — one of Italy's most underrated prestige reds.",
    notesNl:
      "Aglianico del Vulture groeit op de vulkanische hellingen van de Monte Vulture — een van de meest ondergewaardeerde prestige-rode wijnen van Italië.",
    docCount: 4,
    docgCount: 1,
    annualHl: 150_000,
    climate:
      "Continental inland mountain — cold winters, hot summers, low rainfall. Monte Vulture's altitude (450-700m) brings dramatic diurnal swings.",
    climateNl:
      "Continentaal bergklimaat in het binnenland — koude winters, hete zomers, weinig neerslag. De hoogte van de Monte Vulture (450-700 m) zorgt voor sterke dag-nachtverschillen.",
    terroir:
      "Volcanic ash and tuff on the extinct Monte Vulture cone. Mineral-driven, structured Aglianico is the result.",
    terroirNl:
      "Vulkanische as en tuf op de uitgedoofde kegel van de Monte Vulture. Het resultaat is een mineraalgedreven, gestructureerde Aglianico.",
    vintageScores: { 2018: "A-", 2019: "A-", 2020: "B+", 2021: "A-", 2022: "B+", 2023: "B+", 2024: "—" },
  },
  sardegna: {
    bbox: "8.1,38.8,9.8,41.3",
    wikipediaSlug: "Sardinian_wine",
    varietals: ["Cannonau", "Vermentino", "Carignano"],
    notes:
      "Island viticulture. Cannonau (Grenache) and Vermentino define the modern Sardinian wine identity.",
    notesNl:
      "Wijnbouw op een eiland. Cannonau (Grenache) en Vermentino bepalen de moderne Sardijnse wijnidentiteit.",
    docCount: 15,
    docgCount: 1,
    annualHl: 600_000,
    climate:
      "Mediterranean island — sea on all sides, but the mountainous interior creates microclimates. Strong mistral wind ventilates vineyards.",
    climateNl:
      "Mediterraan eiland — aan alle kanten zee, maar het bergachtige binnenland schept microklimaten. De krachtige mistral-wind ventileert de wijngaarden.",
    terroir:
      "Granite and schist in the central highlands; limestone-clay in Cagliari's south; sandy coastal soils for Vermentino.",
    terroirNl:
      "Graniet en schist in het centrale hoogland; kalk-klei in het zuiden bij Cagliari; zandige kustbodems voor Vermentino.",
    vintageScores: { 2018: "B+", 2019: "A-", 2020: "B+", 2021: "A-", 2022: "A-", 2023: "B+", 2024: "—" },
  },
  molise: {
    bbox: "14.0,41.4,15.2,42.0",
    wikipediaSlug: "Molise_(wine)",
    varietals: ["Montepulciano", "Tintilia"],
    notes:
      "Tiny southern region. Tintilia is the indigenous red gaining slow recognition.",
    notesNl:
      "Een minuscule zuidelijke regio. Tintilia is de inheemse rode druif die langzaam erkenning krijgt.",
    docCount: 4,
    docgCount: 0,
    annualHl: 250_000,
    climate:
      "Continental-Adriatic. Cool nights even in summer due to Apennine proximity; hot dry afternoons reliably ripen Montepulciano and Tintilia.",
    climateNl:
      "Continentaal-Adriatisch. Koele nachten, zelfs in de zomer, door de nabijheid van de Apenijnen; hete droge middagen laten Montepulciano en Tintilia betrouwbaar rijpen.",
    terroir:
      "Calcareous clay-marl hillsides; sandy alluvial valleys.",
    terroirNl:
      "Kalkhoudende klei-mergelhellingen; zandige alluviale dalen.",
    vintageScores: { 2018: "B", 2019: "B+", 2020: "B+", 2021: "B+", 2022: "B", 2023: "B", 2024: "—" },
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
  notesNl:
    "Italië telt 20 wijnregio's en meer dan 400 erkende appellations. Raadpleeg de pagina's per macroregio voor terroirdetails; deze vermelding is de landelijke fallback.",
  docCount: 333,
  docgCount: 76,
  annualHl: 49_800_000,
  climate:
    "From alpine north to Mediterranean south. Every climate type in Europe represented within one country's vine-growing area.",
  climateNl:
    "Van het alpiene noorden tot het mediterrane zuiden. Elk klimaattype in Europa is vertegenwoordigd binnen het wijnbouwgebied van één land.",
  terroir:
    "Volcanic, calcareous, granitic, and alluvial soils all present. Italy's variety of terroir is one reason it sustains 400+ protected appellations.",
  terroirNl:
    "Vulkanische, kalkhoudende, granietachtige en alluviale bodems zijn allemaal aanwezig. De verscheidenheid aan terroir is een van de redenen waarom Italië meer dan 400 beschermde appellations in stand houdt.",
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
