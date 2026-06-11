# Berlin Short-Term Rental Market Intelligence — BI Dashboard

**Self-initiated Data Analytics & Business Intelligence project · 2026**

> Analysing 9,240 real Airbnb listings across 112 Berlin neighbourhoods to surface pricing intelligence, host concentration patterns, and neighbourhood-level market segmentation — structured as a client-ready interactive dashboard.

🔗 **[View Live Dashboard](https://blessinghub25.github.io/berlin-airbnb-bi)**

---

## Key Findings

| Metric | Value |
|--------|-------|
| Listings analysed | 9,240 across 112 neighbourhoods |
| Berlin median nightly price | €104 |
| Highest-premium neighbourhood | West 5 @ €382/night (+267% vs median) |
| Most listings | Alexanderplatz (712 listings @ €169/night) |
| Multi-listing hosts | **60.6%** of hosts manage more than one listing |
| Average rating | 4.76 ★ |
| Data source | Inside Airbnb (insideairbnb.com) — open dataset, Sept 2025 |

---

## Project Structure

```
berlin-airbnb/
├── data/
│   └── listings.csv              # Source: Inside Airbnb Berlin (Sept 2025)
├── output/
│   ├── listings_clean.csv        # Cleaned main dataset
│   ├── neighbourhood_summary.csv # Avg price, listings, premium per area
│   ├── host_concentration.csv    # Host market concentration stats
│   ├── host_detail.csv           # Top 200 hosts by portfolio size
│   ├── room_type_summary.csv     # Pricing breakdown by room type
│   ├── price_distribution.csv    # Price bucket distribution
│   ├── superhost_analysis.csv    # Superhost vs regular host comparison
│   └── dashboard.html            # Standalone interactive dashboard
├── clean.py                      # Data cleaning & SQL analysis pipeline
├── dashboard.py                  # Interactive visualisation (Plotly)
├── berlin_airbnb.db              # SQLite database (auto-generated)
├── index.html                    # Live dashboard (GitHub Pages)
└── README.md
```

---

## Tools & Skills Demonstrated

- **Python / pandas** — data ingestion, cleaning, feature engineering
- **SQL (SQLite)** — analytical queries for segmentation and aggregation
- **Plotly** — interactive multi-section BI dashboard
- **Data storytelling** — findings framed as client-ready business insights

---

## How to Run

```bash
# 1. Download listings.csv from insideairbnb.com/get-the-data (Berlin)
# 2. Place in data/ folder
# 3. Install dependencies
pip install pandas numpy plotly

# 4. Run the data pipeline
python clean.py

# 5. Build the dashboard
python dashboard.py

# 6. Open output/dashboard.html in your browser
```

---

## Dashboard Sections

| Section | Content |
|---------|---------|
| KPI Bar | Total listings, median price, avg rating, neighbourhoods, multi-host %, top premium |
| Market Overview | Listings by neighbourhood (top 15) + Berlin map coloured by price |
| Pricing Intelligence | Avg price by neighbourhood, price distribution, room type breakdown |
| Host Analysis | Top 20 hosts by portfolio size, superhost vs regular comparison |
| Business Insights | 3 client-ready insight cards with actionable findings |

---

## Business Insights

1. **Premium Neighbourhood Opportunity** — West 5 commands a 267% price premium over Berlin median. A property there generates significantly more estimated monthly revenue than the city average.

2. **Market Professionalisation** — 60.6% of Berlin hosts manage multiple listings. This is not a peer-to-peer sharing economy — it is a professionalised operator market with pricing power implications for new entrants.

3. **Volume vs. Premium Trade-off** — Alexanderplatz has the most listings but at only moderate pricing. Lower-volume premium areas offer better yield with less competition.

---

## Data Source

Data from **[Inside Airbnb](http://insideairbnb.com/get-the-data)** — an independent, non-commercial project providing open Airbnb listing data for cities worldwide. Berlin dataset dated September 2025.

---

*Part of my data analytics portfolio — [blessinghub25.github.io/Portfolio](https://blessinghub25.github.io/Portfolio)*
