# Product Requirements Document

# Slurpini Partner Intelligence Engine

## 1. Product Summary

Slurpini Partner Intelligence Engine is a data-driven decision-support system that helps Slurpini prioritise Italian wine producers, regions and product opportunities for the Dutch market.

The system transforms a raw Vivino export into a cleaned, validated and enriched analytical dataset. It then applies transparent scoring logic and market segmentation to identify high-potential partner opportunities.

The goal is not to replace human wine expertise, but to reduce selection risk, improve travel prioritisation and support more evidence-based producer outreach.

---

## 2. Business Context

Slurpini is an importer of high-quality Italian wines with a strong focus on sustainability. The company receives collaboration requests from many Italian wine producers. Visiting producers in Italy requires time, budget and operational planning.

Currently, partner selection can be influenced by reputation, personal judgement and incomplete market signals. Vivino consumer data provides an opportunity to add a structured, data-driven layer to this decision-making process.

This project uses Dutch Vivino rating data to identify which Italian wines, producers and regions show the strongest market potential based on consumer preference, review confidence, price positioning and value for money.

---

## 3. Problem Statement

Slurpini needs a more efficient and evidence-based way to decide which Italian wine producers and regions should be prioritised for partnership exploration.

The raw Vivino dataset contains useful consumer market signals, but it is not immediately suitable for decision-making. It contains data quality issues such as inconsistent formatting, duplicate records, mixed country data, noisy region names and unreliable high ratings based on low review counts.

Without cleaning, validation and scoring, the dataset may lead to misleading recommendations.

---

## 4. Product Vision

Create a professional, reproducible and transparent partner intelligence system that turns raw consumer wine data into actionable business recommendations for Slurpini.

The system should feel like a lightweight analytics product, not a one-off notebook or student dashboard.

---

## 5. Goals

### Primary Goals

- Clean and validate the Vivino dataset.
- Filter and analyse Italian wines relevant to Slurpini.
- Identify the strongest Italian regions and producers based on Dutch consumer signals.
- Build a transparent scoring model for partner prioritisation.
- Identify both premium opportunities and value-for-money opportunities.
- Present the results through a professional decision-support interface and executive report.

### Secondary Goals

- Demonstrate modern data pipeline thinking.
- Use AI-assisted enrichment where useful, without making the model opaque.
- Provide a reusable structure that can be extended with future data sources.
- Clearly communicate limitations and assumptions.

---

## 6. Non-Goals

- Building a complete production-grade wine procurement platform.
- Replacing sommelier or commercial expertise.
- Scraping large-scale live Vivino data as the core project objective.
- Creating a complex LangChain or agentic AI system without clear business need.
- Optimising for academic complexity instead of practical business value.

---

## 7. Target Users

### Primary User

**Slurpini decision maker**

A business owner, buyer or commercial manager who needs to decide which Italian producers, regions or wine types deserve attention.

Needs:

- Quickly understand market signals.
- Compare regions and producers.
- Identify premium and value opportunities.
- Reduce time spent on weak partnership leads.
- Support travel and outreach planning.

### Secondary User

**Data/AI reviewer or bootcamp evaluator**

A reviewer who wants to understand the technical approach, data cleaning decisions, scoring logic, limitations and business relevance.

Needs:

- Transparent methodology.
- Reproducible pipeline.
- Clear evidence-based recommendations.
- Well-structured documentation.

---

## 8. Key Questions

The system should answer the following questions:

1. Which Italian wines, producers and regions are most preferred by Dutch Vivino consumers?
2. Which wines and regions offer the best value for money?
3. Which ratings are reliable enough to support business decisions?
4. Which regions are premium brand builders versus commercial value opportunities?
5. Which producers should Slurpini prioritise for outreach or further investigation?
6. What are the limitations of using Vivino data for partner selection?

---

## 9. Data Sources

### Provided Dataset

- File: `Vivino-export.xlsx`
- Source: Vivino crawler export
- Content: wines rated by consumers in the Netherlands
- Main fields:
  - Wine name
  - Country
  - Region
  - Rating
  - Rating count
  - Price

### Provided Crawler Reference

- File: `Pyton-script.docx`
- Purpose: Example crawler used to collect Vivino data
- Use: Reference only, not the main focus of the final assignment

---

## 10. Data Quality Requirements

The pipeline must address the following data quality issues:

- Inconsistent country and region formatting.
- Tuple-like string values caused by crawler output.
- Encoding issues in country names.
- Duplicate wine records.
- Mixed country data across sheets.
- Missing or invalid price values.
- Missing or invalid rating values.
- Ratings based on very low review counts.
- Potentially misleading average ratings without confidence adjustment.

### Required Validation Rules

- Rating must be numeric.
- Rating must be between 0 and 5.
- Rating count must be numeric and greater than 0.
- Price must be numeric and greater than 0.
- Country and region must not be empty after cleaning.
- Duplicate records must be identified and removed or aggregated.
- Only Italian wines should be used for the main recommendation model.

---

## 11. Technical Architecture

### Recommended Stack

- **Polars** for fast, modern dataframe processing.
- **DuckDB** as lightweight analytical database.
- **Parquet** as cleaned and scored data format.
- **Pandera or Great Expectations** for data quality validation.
- **scikit-learn** for optional clustering or segmentation.
- **Next.js** for the professional decision-support interface.
- **Tailwind CSS + shadcn/ui** for clean UI components.
- **Recharts or Tremor** for visualisation.

### Architecture Flow

```text
Raw Excel dataset
  ↓
Ingestion layer
  ↓
Cleaning and normalisation
  ↓
Data quality validation
  ↓
Feature enrichment
  ↓
Scoring model
  ↓
Segmentation and clustering
  ↓
Export to Parquet / JSON
  ↓
Next.js decision interface
  ↓
Executive report and recommendations
```

---

## 12. Data Pipeline Requirements

### 12.1 Ingestion

The system must read the provided Excel dataset and combine relevant sheets into a unified raw dataset.

### 12.2 Cleaning

The system must clean:

- Country names
- Region names
- Wine names
- Numeric fields
- Duplicates
- Invalid rows

### 12.3 Filtering

The main analysis must focus on Italian wines only.

### 12.4 Enrichment

The system should enrich raw wine records with business-relevant decision features. The goal of enrichment is not to make the project more complex, but to transform raw Vivino records into features that better support Slurpini's partner selection process.

The enrichment layer should remain transparent, explainable and reproducible. Where enrichment is based on inference rather than direct source data, the system should store an enrichment confidence level.

#### Required Enriched Fields

| Field | Description | Example | Purpose |
|---|---|---|---|
| `producer_name` | Extracted producer or winery name from the wine name | Antinori | Supports partner-level analysis |
| `macro_region` | Normalised Italian macro-region | Tuscany | Allows regional strategy comparison |
| `price_segment` | Commercial price band | Premium | Supports portfolio positioning |
| `confidence_segment` | Review-volume reliability segment | Strong Market Signal | Prevents weak signals from being overvalued |
| `market_segment` | Business opportunity classification | Hidden Gem | Makes recommendations easier to interpret |
| `inferred_grape_or_style` | Optional inferred grape variety or wine style | Sangiovese | Supports portfolio and category thinking |
| `enrichment_confidence` | Confidence level for inferred enrichments | High / Medium / Low | Keeps assumptions transparent |

#### Producer Extraction

The system should attempt to extract the producer name from the wine name using rule-based parsing. This is important because Slurpini makes partnership decisions at producer level, not only at individual wine level.

Example:

```text
Antinori Tignanello Toscana 2020
→ producer_name: Antinori
→ wine_name_cleaned: Tignanello Toscana
```

Producer extraction should be treated as heuristic and should be manually validated for the final shortlist.

#### Price Segmentation

The system should classify wines into commercial price segments.

Suggested segmentation:

| Price Range | Segment |
|---:|---|
| < €15 | Entry |
| €15–€30 | Accessible Premium |
| €30–€75 | Premium |
| > €75 | Prestige |

These thresholds may be adjusted after exploratory analysis.

#### Confidence Segmentation

The system should classify wines based on review volume.

Suggested segmentation:

| Rating Count | Confidence Segment |
|---:|---|
| < 50 | Low Confidence |
| 50–250 | Emerging Signal |
| 250–1,000 | Reliable Signal |
| > 1,000 | Strong Market Signal |

This prevents wines with very few ratings from being treated as equally reliable as wines with thousands of ratings.

#### Macro-Region Mapping

The system should map specific Italian regions and appellations to broader macro-regions where possible.

Examples:

| Region / Appellation | Macro-Region |
|---|---|
| Chianti Classico | Tuscany |
| Brunello di Montalcino | Tuscany |
| Bolgheri | Tuscany |
| Barolo | Piedmont |
| Barbaresco | Piedmont |
| Langhe | Piedmont |
| Amarone della Valpolicella | Veneto |
| Prosecco | Veneto |
| Etna | Sicily |
| Primitivo di Manduria | Puglia |

This allows Slurpini to compare both specific wine regions and broader strategic areas.

#### Grape or Style Inference

The system may infer grape variety or wine style only where the inference is reliable.

Examples:

| Region / Wine Signal | Inferred Grape or Style | Confidence |
|---|---|---|
| Barolo | Nebbiolo | High |
| Barbaresco | Nebbiolo | High |
| Brunello di Montalcino | Sangiovese | High |
| Chianti Classico | Sangiovese dominant | Medium |
| Prosecco | Glera / Sparkling | High |
| Amarone della Valpolicella | Corvina blend | Medium |

The model should avoid pretending that all grape varieties can be inferred with certainty. If inference confidence is low, the value should remain empty or be marked as low confidence.

#### Sustainability Enrichment

Sustainability is strategically relevant to Slurpini, but the provided Vivino dataset does not reliably contain sustainability certification data.

The system should not use sustainability as a hard scoring factor unless reliable external certification data is added. Sustainability should be documented as a future enrichment opportunity.

Potential future sustainability fields:

- Organic certification
- Biodynamic certification
- Sustainable farming label
- Producer sustainability statement
- External certification source

#### Enrichment Principles

- Enrichment must support business decision-making.
- Inferred fields must be transparent and marked with confidence levels.
- Low-confidence enrichments should not strongly influence final recommendations.
- The final shortlist should be manually reviewed before business use.
- Enrichment should improve interpretation, not create fake precision.

### 12.5 Scoring

The system must calculate a transparent partner intelligence score.

### 12.6 Export

The system must export:

- Cleaned Italian wine dataset.
- Enriched Italian wine dataset.
- Region rankings.
- Producer rankings.
- Wine opportunity shortlist.
- Dashboard-ready JSON files.

---

## 13. Scoring Model

### Slurpini Partner Intelligence Score

The Slurpini Partner Intelligence Score is a transparent scoring model used to prioritise producer and region opportunities.

Proposed components:

| Component | Purpose | Suggested Weight |
|---|---:|---:|
| Weighted Rating Score | Corrects rating using review volume | 35% |
| Market Confidence Score | Rewards reliable consumer signal | 20% |
| Value for Money Score | Identifies high quality at realistic price | 20% |
| Premium Fit Score | Supports Slurpini's premium positioning | 15% |
| Portfolio Opportunity Score | Highlights strategic opportunity | 10% |

### Weighted Rating

A Bayesian-style weighted rating should be used to avoid overvaluing wines with very few reviews.

```text
Weighted Rating =
(rating_count / (rating_count + m)) * rating
+ (m / (rating_count + m)) * global_average_rating
```

Where:

- `rating` = average Vivino rating
- `rating_count` = number of ratings
- `m` = minimum review threshold
- `global_average_rating` = average rating across the cleaned Italian dataset

### Value for Money Score

A value score should compare quality signal against price.

```text
Value Score = Weighted Rating / log(price + 1)
```

The exact formula may be adjusted after exploratory analysis.

---

## 14. Segmentation Model

The system should classify wines, regions or producers into meaningful decision segments.

Suggested segments:

| Segment | Description |
|---|---|
| Premium Icons | High rating, high confidence, high price |
| Hidden Gems | High rating, good confidence, moderate price |
| Commercial Value | Solid rating, strong value for money, scalable price |
| Low Confidence Niche | Interesting rating, but too few reviews |
| Overpriced Risk | High price without matching consumer signal |

Optional clustering can be used to validate whether these segments naturally appear in the data.

---

## 15. Dashboard Requirements

The dashboard should present the analysis as a decision-support product.

### Page 1: Executive Overview

Must include:

- Number of Italian wines analysed.
- Number of regions analysed.
- Average rating.
- Average price.
- Top recommended regions.
- Top recommended producer opportunities.
- Key strategic insight.

### Page 2: Region Intelligence

Must include:

- Region ranking table.
- Weighted rating by region.
- Average price by region.
- Review confidence by region.
- Value score by region.
- Filters by segment or price band.

### Page 3: Producer Shortlist

Must include:

- Producer ranking.
- Region.
- Average weighted rating.
- Review volume.
- Average price.
- Segment.
- Recommendation status.

Recommendation statuses:

- Target
- Monitor
- Premium Brand Builder
- Value Opportunity
- Avoid for Now

### Page 4: Opportunity Matrix

Must include a quadrant visual:

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

### Page 5: Methodology

Must explain:

- Dataset source.
- Cleaning steps.
- Validation rules.
- Scoring logic.
- Assumptions.
- Limitations.

---

## 16. Reporting Requirements

The final assignment should include:

1. Executive summary.
2. Business context.
3. Data quality analysis.
4. Methodology.
5. Key findings.
6. Visual analysis.
7. Partner recommendations.
8. Limitations.
9. Future improvements.
10. Technical appendix.

---

## 17. Success Metrics

The project is successful if it:

- Produces a cleaned and validated Italian wine dataset.
- Provides transparent, evidence-based rankings.
- Clearly distinguishes between popularity, quality signal and value.
- Avoids misleading conclusions based on raw average ratings.
- Gives Slurpini actionable partner recommendations.
- Demonstrates a professional data product approach.
- Can be reproduced by running the pipeline again.

---

## 18. Risks and Limitations

### Data Limitations

- Vivino users are not fully representative of all Dutch wine consumers.
- Ratings reflect consumer preference, not objective wine quality.
- Price data may vary over time and may not reflect Slurpini's procurement cost.
- Sustainability data is not reliably available in the provided dataset.
- Producer extraction from wine names may be imperfect.

### Methodological Limitations

- Scoring weights are business assumptions and should be adjustable.
- High review volume may favour well-known brands over emerging producers.
- Low-volume niche wines may be undervalued despite strong potential.
- The model supports decision-making but should not replace expert judgement.

---

## 19. Future Enhancements

Potential future improvements:

- Add live or updated Vivino data collection.
- Add sustainability certification data.
- Add grape variety enrichment.
- Add margin and procurement cost data.
- Add restaurant/hospitality preference data.
- Add importer availability data.
- Add AI-generated producer summaries.
- Add human review workflow for shortlisted producers.
- Add CRM export for outreach planning.

---

## 20. Deliverables

### Required Deliverables

- Cleaned dataset.
- Analysis notebook or reproducible pipeline.
- Scoring model.
- Dashboard or interactive prototype.
- Executive report.
- README documentation.

### Recommended Repository Structure

```text
slurpini-partner-intelligence/
  README.md
  PRD.md
  data/
    raw/
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

## 21. Definition of Done

The project is complete when:

- The raw dataset can be ingested successfully.
- Italian wines are cleaned, validated and filtered.
- Scores are calculated reproducibly.
- Rankings are exported for dashboard use.
- Dashboard or report clearly presents the recommendations.
- The methodology is understandable to both technical and business audiences.
- Limitations are clearly documented.
- Slurpini receives a clear shortlist of regions and producer opportunities.

---

## 22. Positioning Statement

This assignment does not treat the Vivino export as a static dataset. It treats it as the starting point for a repeatable decision-support system that helps Slurpini reduce selection risk and prioritise producer outreach more efficiently.

The result is not just an analysis. It is a lightweight partner intelligence engine.
