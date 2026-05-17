# Slurpini Partner Intelligence Engine

A professional data-driven decision-support prototype for helping Slurpini prioritise Italian wine producers, regions and product opportunities for the Dutch market.

This project turns a raw Vivino export into a cleaned, validated and enriched dataset. It then applies transparent scoring logic, segmentation and visualisation to support evidence-based partner selection.

The goal is not to replace human wine expertise. The goal is to reduce selection risk, improve producer prioritisation and support smarter business decisions before Slurpini invests time and budget in on-site visits.

---

## 1. Project Context

Slurpini is an importer of high-quality Italian wines with a strong focus on sustainability. The company receives collaboration requests from many Italian wine producers and needs a more structured way to decide which producers, regions or wine types deserve attention.

The provided dataset contains Vivino wine data rated by consumers in the Netherlands. This makes it useful as a market signal, but not as a ready-made decision tool.

This project transforms that raw dataset into a partner intelligence model.

---

## 2. Core Research Question

How can Slurpini use Dutch Vivino consumer data to prioritise Italian wine producers and regions for future collaboration, based on consumer preference, market confidence, price positioning and value for money?

---

## 3. What This Project Does

The project follows a structured data product approach:

```text
Raw Vivino export
  ↓
Data ingestion
  ↓
Cleaning and normalisation
  ↓
Data quality validation
  ↓
Business-oriented enrichment
  ↓
Scoring model
  ↓
Segmentation
  ↓
Dashboard-ready exports
  ↓
Executive recommendation
```

The output is not just a list of highly rated wines. It is a repeatable framework for identifying commercially relevant wine opportunities.

---

## 4. Key Features

- Cleans and normalises the raw Vivino dataset.
- Filters the dataset to Italian wines relevant to Slurpini.
- Detects and handles duplicate records.
- Converts ratings, review counts and prices into usable numeric values.
- Adds business-oriented enrichment fields.
- Applies a Bayesian-style weighted rating to avoid overvaluing low-review wines.
- Calculates value-for-money indicators.
- Segments wines, producers and regions into strategic opportunity categories.
- Exports dashboard-ready datasets.
- Provides clear recommendations for producer and region prioritisation.

---

## 5. Recommended Tech Stack

This project intentionally avoids a basic one-off notebook approach. The preferred setup is a lightweight but professional analytics pipeline.

| Layer | Tooling | Purpose |
|---|---|---|
| Data processing | Polars | Fast dataframe processing |
| Analytical storage | DuckDB | Lightweight local analytical database |
| Data format | Parquet | Clean and efficient dataset storage |
| Validation | Pandera or Great Expectations | Data quality checks |
| Segmentation | scikit-learn | Optional clustering and opportunity grouping |
| Dashboard | Next.js | Professional decision-support interface |
| UI | Tailwind CSS + shadcn/ui | Clean product-grade interface |
| Charts | Recharts or Tremor | Visualisation layer |

A simpler version can also be built with pandas and notebooks, but the preferred version should feel like a real analytics product.

---

## 6. Repository Structure

Recommended structure:

```text
slurpini-partner-intelligence/
  README.md
  PRD.md

  data/
    raw/
      Vivino-export.xlsx
    interim/
    processed/
    exports/

  notebooks/
    01_data_understanding.ipynb
    02_data_cleaning.ipynb
    03_scoring_model.ipynb

  src/
    ingestion/
    cleaning/
    validation/
    enrichment/
    scoring/
    export/

  dashboard/
    app/
    components/
    data/

  reports/
    executive-summary.md
    final-report.md

  docs/
    methodology.md
    limitations.md
```

---

## 7. Data Sources

### Main Dataset

```text
Vivino-export.xlsx
```

The dataset contains wine records collected from Vivino. It includes wines rated by consumers in the Netherlands.

Expected fields:

- Wine name
- Country
- Region
- Rating
- Rating count
- Price

### Crawler Reference

```text
Pyton-script.docx
```

The provided Python crawler is used as a reference for how the data was originally collected. The main focus of this assignment is data cleaning, analysis, modelling and recommendation, not large-scale scraping.

---

## 8. Data Quality Issues

The raw data is not ready for direct analysis.

Known issues include:

- Inconsistent country formatting.
- Tuple-like string values.
- Encoding issues.
- Duplicate wine records.
- Mixed country data across sheets.
- Missing or invalid prices.
- Missing or invalid ratings.
- High ratings with very low review counts.
- Region names that mix macro-regions, appellations and local areas.

These issues are handled before scoring and recommendation.

---

## 9. Data Cleaning Requirements

The pipeline should:

- Load and combine the relevant Excel sheets.
- Standardise column names.
- Clean country and region fields.
- Convert rating, rating count and price to numeric values.
- Remove invalid rows.
- Remove or aggregate duplicate records.
- Filter the dataset to Italian wines.
- Export a clean dataset for further analysis.

Main output:

```text
data/processed/italian_wines_cleaned.parquet
```

---

## 10. Data Enrichment

The raw Vivino data is enriched with business-relevant features.

Recommended enriched fields:

| Field | Description | Example |
|---|---|---|
| `producer_name` | Extracted producer or winery name | Antinori |
| `macro_region` | Normalised broader Italian region | Tuscany |
| `price_segment` | Commercial price band | Premium |
| `confidence_segment` | Review-volume reliability label | Strong Market Signal |
| `market_segment` | Strategic opportunity category | Hidden Gem |
| `inferred_grape_or_style` | Optional grape or wine style inference | Sangiovese |
| `enrichment_confidence` | Confidence level for inferred fields | High |

The enrichment layer must remain transparent. Inferred fields should not pretend to be certain when the source data does not support that certainty.

---

## 11. Scoring Model

The central scoring model is the **Slurpini Partner Intelligence Score**.

It combines several business-relevant signals:

| Component | Purpose | Suggested Weight |
|---|---:|---:|
| Weighted Rating Score | Corrects rating using review volume | 35% |
| Market Confidence Score | Rewards reliable consumer signal | 20% |
| Value for Money Score | Identifies high quality at realistic price | 20% |
| Premium Fit Score | Supports Slurpini's premium positioning | 15% |
| Portfolio Opportunity Score | Highlights strategic opportunity | 10% |

---

## 12. Weighted Rating

A raw average rating can be misleading. A wine with a 4.8 rating and 12 reviews should not automatically outrank a wine with a 4.4 rating and 5,000 reviews.

The model should use a Bayesian-style weighted rating:

```text
Weighted Rating =
(rating_count / (rating_count + m)) * rating
+ (m / (rating_count + m)) * global_average_rating
```

Where:

- `rating` is the Vivino average rating.
- `rating_count` is the number of reviews.
- `m` is the minimum review threshold.
- `global_average_rating` is the average rating across the cleaned Italian dataset.

This creates a more reliable quality signal.

---

## 13. Value for Money

The model should also calculate a value-for-money score.

Suggested formula:

```text
Value Score = Weighted Rating / log(price + 1)
```

This helps identify wines or regions that deliver strong consumer ratings without extreme pricing.

---

## 14. Strategic Segments

The system should classify wines, producers or regions into clear business segments.

Suggested segments:

| Segment | Meaning |
|---|---|
| Premium Icons | High rating, high confidence, high price |
| Hidden Gems | High rating, good confidence, moderate price |
| Commercial Value | Solid rating, strong value, scalable price |
| Low Confidence Niche | Interesting signal, but too few reviews |
| Overpriced Risk | High price without matching consumer signal |

These segments make the recommendation easier to understand for non-technical stakeholders.

---

## 15. Dashboard Concept

The preferred presentation layer is a Next.js decision-support dashboard.

Suggested pages:

### Executive Overview

Shows the key business summary:

- Number of Italian wines analysed.
- Number of regions analysed.
- Average rating.
- Average price.
- Top recommended regions.
- Top producer opportunities.
- Key recommendation.

### Region Intelligence

Compares Italian regions by:

- Weighted rating.
- Review volume.
- Average price.
- Value score.
- Market segment.

### Producer Shortlist

Ranks producer opportunities by:

- Producer name.
- Region.
- Average weighted rating.
- Review volume.
- Average price.
- Segment.
- Recommendation status.

### Opportunity Matrix

A visual quadrant:

```text
Y-axis: Weighted Rating
X-axis: Price
Bubble size: Rating Count
```

Quadrants:

- Hidden Gems
- Premium Icons
- Budget Risk
- Overpriced Risk

### Methodology

Explains:

- Data source.
- Cleaning steps.
- Validation rules.
- Scoring logic.
- Assumptions.
- Limitations.

---

## 16. Example Commands

These commands are placeholders and should be adjusted once the implementation is created.

### Install dependencies

```bash
uv sync
```

or:

```bash
pip install -r requirements.txt
```

### Run the data pipeline

```bash
python -m src.ingestion.load_data
python -m src.cleaning.clean_data
python -m src.validation.validate_data
python -m src.enrichment.enrich_data
python -m src.scoring.score_wines
python -m src.export.export_dashboard_data
```

### Start the dashboard

```bash
cd dashboard
npm install
npm run dev
```

---

## 17. Expected Outputs

The project should generate:

```text
data/processed/italian_wines_cleaned.parquet
data/processed/italian_wines_enriched.parquet
data/exports/region_rankings.json
data/exports/producer_rankings.json
data/exports/wine_shortlist.json
data/exports/dashboard_summary.json
```

Reports:

```text
reports/executive-summary.md
reports/final-report.md
docs/methodology.md
docs/limitations.md
```

---

## 18. Recommendation Logic

The final recommendation should not simply select the wines with the highest average rating.

The recommendation should consider:

- Consumer preference.
- Rating reliability.
- Review volume.
- Price positioning.
- Value for money.
- Producer-level opportunity.
- Regional strategy.
- Fit with Slurpini's premium positioning.

The model should produce recommendation statuses such as:

| Status | Meaning |
|---|---|
| Target | Strong candidate for producer outreach |
| Monitor | Interesting but not strong enough yet |
| Premium Brand Builder | Strong for reputation and positioning |
| Value Opportunity | Good commercial/value potential |
| Avoid for Now | Weak signal or poor value |

---

## 19. Limitations

This project uses Vivino data as a consumer preference signal. It does not measure objective wine quality.

Important limitations:

- Vivino users are not fully representative of all Dutch consumers.
- Ratings may be influenced by brand awareness and price expectations.
- Price data may not reflect procurement cost or wholesale margins.
- Sustainability data is not reliably available in the provided dataset.
- Producer extraction from wine names may require manual validation.
- Scoring weights are business assumptions and should be adjustable.

The model should support human decision-making, not replace expert judgement.

---

## 20. Future Enhancements

Possible next steps:

- Add updated or live Vivino data.
- Add verified sustainability certification data.
- Add grape variety enrichment from trusted sources.
- Add procurement cost and margin data.
- Add restaurant or hospitality sales data.
- Add importer availability data.
- Add AI-generated producer summaries.
- Add CRM export for outreach planning.
- Add manual review workflow for shortlisted producers.

---

## 21. Final Deliverables

For the final assignment, the project should include:

- PRD.
- README.
- Cleaned dataset.
- Enriched dataset.
- Scoring model.
- Visual analysis.
- Dashboard prototype or dashboard-ready exports.
- Executive summary.
- Final report.
- Methodology and limitations.

---

## 22. Positioning

This project does not treat the Vivino export as a static spreadsheet.

It treats the dataset as the starting point for a repeatable partner intelligence system that helps Slurpini reduce selection risk and prioritise Italian producer outreach more efficiently.

The result is not just an analysis.

It is a lightweight decision-support engine.
