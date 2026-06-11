# Berlin Short-Term Rental Market Intelligence — BI Dashboard

**Self-initiated Data Analytics & Business Intelligence project · 2026**

> Analysing 6,329 real Airbnb listings across Berlin to surface pricing intelligence, host concentration patterns, and neighbourhood-level market segmentation — structured as a client-ready Power BI report.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Listings analysed | 6,329 across 23 neighbourhoods |
| Berlin median nightly price | €132.35 |
| Highest-premium neighbourhood | Brunnenstr. Süd @ €181/night (+37% vs median) |
| Most listings | Alexanderplatz (712 listings @ €169.37/night) |
| Multi-listing hosts | **60.6%** of hosts manage more than one listing |
| Data source | Inside Airbnb (insideairbnb.com) — open dataset |

---

## Project Structure

```
berlin-airbnb/
├── data/
│   └── listings.csv          # Source: Inside Airbnb Berlin (Sept 2025)
├── output/
│   ├── listings_clean.csv        # Cleaned main dataset
│   ├── neighbourhood_summary.csv # Avg price, listings, premium per area
│   ├── host_concentration.csv    # Host market concentration stats
│   ├── host_detail.csv           # Top 200 hosts by portfolio size
│   ├── room_type_summary.csv     # Pricing breakdown by room type
│   ├── price_distribution.csv    # Price bucket distribution
│   └── superhost_analysis.csv    # Superhost vs regular host comparison
├── clean.py                  # Python cleaning & SQL analysis pipeline
├── berlin_airbnb.db          # SQLite database (auto-generated)
└── README.md
```

---

## Tools & Skills Demonstrated

- **Python / pandas** — data ingestion, cleaning, feature engineering
- **SQL (SQLite)** — analytical queries for segmentation and aggregation
- **Power BI** — 4-page interactive dashboard
- **Data storytelling** — findings framed as client-ready business insights

---

## How to Run

```bash
# 1. Download listings.csv from insideairbnb.com/get-the-data (Berlin)
# 2. Place in data/ folder
# 3. Install dependencies
pip install pandas numpy

# 4. Run the pipeline
python clean.py

# 5. Load CSVs from /output/ into Power BI
```

---

## Power BI Dashboard Pages

| Page | Content |
|------|---------|
| 1 — Market Overview | KPI cards, listing count by neighbourhood, map by price |
| 2 — Pricing Intelligence | Price by neighbourhood & room type, superhost premium, price distribution |
| 3 — Host Analysis | Multi-listing concentration, top hosts, single vs multi-listing split |
| 4 — Recommendations | 3 client-ready business insights |

---

## Data Source

Data from **[Inside Airbnb](http://insideairbnb.com/get-the-data)** — an independent, non-commercial project that provides open Airbnb listing data for cities worldwide. Berlin dataset dated September 2025.

---

*Part of my data analytics portfolio — [blessinghub25.github.io/Portfolio](https://blessinghub25.github.io/Portfolio)*
