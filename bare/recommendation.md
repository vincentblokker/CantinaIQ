# Slurpini — recommendation

*Bare-essentials track. Half-page recommendation, written for a non-technical buying-committee reader. Numbers come from `notebooks/slurpini-analysis.ipynb`; full tables in `output/`.*

---

## What we did

Took the Vivino export, cleaned the known data issues (tuple-encoded country/region, Mac-Roman mojibake on diacritics, cross-sheet duplication), filtered to Italy, and ranked **179 regions** and **564 producer name-fragments** by a Bayesian-shrunk weighted rating. Shrinkage anchor: the dataset median review count (`m`); global mean rating: `μ`. Both shown in the notebook output.

Working set after cleaning: **5,786 unique Italian wines**.

## What the data says

**Regions to prioritise** (top of the weighted-rating ranking, ≥20 wines):

The top of the list is dominated by Tuscan blue-chip appellations: **Bolgheri Sassicaia** (4.62), **Bolgheri Superiore** (4.49), and **Brunello di Montalcino** (4.27), with **Amarone della Valpolicella Classico** (4.34) the strongest non-Tuscan entry. These are prestige holds — high rating, but also high average price (€196–€534).

The value-opportunity zone — above-median weighted rating, below-median average price — is led by **Primitivo di Manduria** (Puglia, 95 wines, avg €161), **Abruzzo** (33 wines, avg €103), **Lugana** (46 wines, avg €108), and **Südtirol – Alto Adige** (72 wines, avg €128). These are the regions where the data points to "expand" rather than "hold".

**Producers to prioritise** (top of the weighted-rating ranking, ≥3 wines):

The top of the list contains the names Slurpini almost certainly already knows: **Masseto**, **Biondi-Santi**, **Ornellaia**, **Gaja**, **Antinori**, plus the fragmented "Tenuta" row that almost certainly represents **Tenuta San Guido** (Sassicaia) — see limitations on producer extraction. These are low-risk, high-prestige anchors.

The more actionable finding is one tier down: producers with weighted ratings between 4.15 and 4.25 at price points €40–€200 — they outperform their price segment and are under-represented in most Dutch wine retail.

## Concretely, what we recommend

1. **Hold** the prestige tier (Masseto, Antinori, Gaja, Biondi-Santi, Tenuta San Guido, Ornellaia). The data confirms what Slurpini already does — these are defensible anchors.
2. **Expand** in Puglia (Primitivo di Manduria) and Abruzzo. Both regions sit in the value-opportunity zone — above-median weighted rating at well-below-median average price — and are under-represented in most Dutch wine retail.
3. **Audit** the producers with high rating but fewer than 10 reviews. The notebook excluded them from the ranking because the rating is signal-volatile, but several are worth a tasting before dismissing.

## What this analysis does *not* tell you

1. **Producer-extraction is heuristic.** The first-word rule mis-attributes multi-word names (*Tenuta San Guido*, *Castello di Ama*, *Marchesi Antinori*) — they show up as fragments ("Tenuta", "Castello", "Marchesi") in the producer ranking. A real extraction needs an alias whitelist. The supercharged track addresses this.
2. **Vivino is not the Dutch wine market.** Its user base skews Anglophone and younger; under-representation of natural wine and biodynamic producers is systematic.
3. **Sustainability is not in the data.** Slurpini's USP is invisible to this analysis — every recommendation here should be cross-checked against the producer's certification status before commitment.
4. **Vintage is mixed in.** Wines across multiple vintages are averaged together; producers with strong recent runs are under-weighted.

## Reproducibility

- Data: `data/raw/Vivino-export.xlsx`
- Pipeline: `notebooks/slurpini-analysis.ipynb` (run top-to-bottom)
- Crawler extension: `crawler-extension.py` adds vintage + producer hint columns
- Output tables: `output/top20_regions.csv`, `output/top30_producers.csv`, `output/wines_extended.csv`
- Environment: `pip install -r requirements.txt`
