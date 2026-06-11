"""
Berlin Airbnb Market Intelligence
----------------------------------
Author: Blessing Dediare
Description: Cleans Inside Airbnb listings data, engineers features,
             runs SQL analysis, and exports CSVs ready for Power BI.

Run: python clean.py
Output files in /output/ folder:
  - listings_clean.csv        (main cleaned dataset)
  - neighbourhood_summary.csv (avg price, listing count per area)
  - host_analysis.csv         (host concentration analysis)
  - room_type_summary.csv     (pricing by room type)
  - monthly_availability.csv  (availability trends)
"""

import pandas as pd
import numpy as np
import sqlite3
import os

# ── CONFIG ────────────────────────────────────────────────────────────
DATA_PATH  = "data/listings.csv"   # adjust if your filename differs
OUTPUT_DIR = "output"
DB_PATH    = "berlin_airbnb.db"

os.makedirs(OUTPUT_DIR, exist_ok=True)
print("=" * 60)
print("BERLIN AIRBNB MARKET INTELLIGENCE — DATA PIPELINE")
print("=" * 60)


# ── STEP 1: LOAD ──────────────────────────────────────────────────────
print("\n[1/6] Loading raw data...")
df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"      Raw rows: {len(df):,}  |  Columns: {df.shape[1]}")


# ── STEP 2: SELECT & RENAME COLUMNS ──────────────────────────────────
print("\n[2/6] Selecting relevant columns...")

keep_cols = {
    "id":                       "listing_id",
    "name":                     "listing_name",
    "host_id":                  "host_id",
    "host_name":                "host_name",
    "host_is_superhost":        "is_superhost",
    "host_listings_count":      "host_total_listings",
    "neighbourhood_cleansed":   "neighbourhood",
    "room_type":                "room_type",
    "accommodates":             "accommodates",
    "bedrooms":                 "bedrooms",
    "beds":                     "beds",
    "price":                    "price_raw",
    "minimum_nights":           "min_nights",
    "maximum_nights":           "max_nights",
    "number_of_reviews":        "num_reviews",
    "review_scores_rating":     "rating",
    "reviews_per_month":        "reviews_per_month",
    "availability_365":         "availability_365",
    "calculated_host_listings_count": "host_calculated_listings",
    "last_review":              "last_review_date",
    "latitude":                 "latitude",
    "longitude":                "longitude",
}

# Only keep columns that actually exist in this version of the dataset
existing = {k: v for k, v in keep_cols.items() if k in df.columns}
df = df[list(existing.keys())].rename(columns=existing)
print(f"      Kept {len(existing)} columns")


# ── STEP 3: CLEAN ─────────────────────────────────────────────────────
print("\n[3/6] Cleaning data...")

# Clean price: remove $ and commas, convert to float
df["price"] = (
    df["price_raw"]
    .astype(str)
    .str.replace(r"[\$,€]", "", regex=True)
    .str.strip()
    .replace("", np.nan)
    .astype(float)
)
df.drop(columns=["price_raw"], inplace=True)

# Remove obvious outliers: price must be between €5 and €2500
before = len(df)
df = df[(df["price"] >= 5) & (df["price"] <= 2500)]
print(f"      Removed {before - len(df):,} price outliers (kept €5–€2,500)")

# Fill numeric nulls with median
for col in ["bedrooms", "beds", "rating", "reviews_per_month"]:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# Superhost to boolean
if "is_superhost" in df.columns:
    df["is_superhost"] = df["is_superhost"].map({"t": True, "f": False}).fillna(False)

# Multi-listing host flag
df["is_multi_listing_host"] = df.get("host_total_listings", 1) > 1

# Price per guest
df["price_per_guest"] = (df["price"] / df["accommodates"].replace(0, 1)).round(2)

# Estimated monthly revenue (rough: price * min(availability, 20) * reviews_per_month proxy)
# Simple proxy: price * occupancy_rate * 30
df["est_monthly_revenue"] = (df["price"] * (df["availability_365"] / 365) * 30).round(2)

# Last review recency bucket
df["last_review_date"] = pd.to_datetime(df["last_review_date"], errors="coerce")
df["recently_reviewed"] = df["last_review_date"] >= pd.Timestamp("2024-01-01")

print(f"      Clean dataset: {len(df):,} listings")


# ── STEP 4: LOAD INTO SQLite FOR SQL QUERIES ──────────────────────────
print("\n[4/6] Loading into SQLite and running SQL analysis...")

conn = sqlite3.connect(DB_PATH)
df.to_sql("listings", conn, if_exists="replace", index=False)

# ── SQL QUERY 1: Neighbourhood Summary ────────────────────────────────
neighbourhood_sql = """
SELECT
    neighbourhood,
    COUNT(*)                        AS total_listings,
    ROUND(AVG(price), 2)            AS avg_price_eur,
    ROUND(MIN(price), 2)            AS min_price_eur,
    ROUND(MAX(price), 2)            AS max_price_eur,
    ROUND(AVG(rating), 2)           AS avg_rating,
    ROUND(AVG(accommodates), 1)     AS avg_guests,
    ROUND(AVG(availability_365), 0) AS avg_availability_days,
    ROUND(AVG(est_monthly_revenue), 2) AS avg_est_monthly_revenue,
    SUM(CASE WHEN is_superhost = 1 THEN 1 ELSE 0 END) AS superhost_count,
    ROUND(
        100.0 * SUM(CASE WHEN is_superhost = 1 THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS superhost_pct
FROM listings
GROUP BY neighbourhood
HAVING COUNT(*) >= 5
ORDER BY total_listings DESC
"""
neighbourhood_df = pd.read_sql(neighbourhood_sql, conn)

# Add price premium vs Berlin median
berlin_median_price = df["price"].median()
neighbourhood_df["price_vs_median_pct"] = (
    (neighbourhood_df["avg_price_eur"] - berlin_median_price) / berlin_median_price * 100
).round(1)
neighbourhood_df["berlin_median_price"] = round(berlin_median_price, 2)

print(f"      Neighbourhoods analysed: {len(neighbourhood_df)}")

# ── SQL QUERY 2: Host Concentration ───────────────────────────────────
host_sql = """
SELECT
    host_id,
    host_name,
    COUNT(*) AS listings_owned,
    ROUND(AVG(price), 2) AS avg_listing_price,
    ROUND(SUM(est_monthly_revenue), 2) AS est_total_monthly_revenue,
    MAX(is_superhost) AS is_superhost
FROM listings
GROUP BY host_id, host_name
ORDER BY listings_owned DESC
"""
host_df = pd.read_sql(host_sql, conn)

# Concentration metrics
total_listings = len(df)
multi_listing_hosts = host_df[host_df["listings_owned"] > 1]
top_10_pct_threshold = max(1, int(len(host_df) * 0.10))
top_10pct_hosts = host_df.head(top_10_pct_threshold)

concentration_stats = pd.DataFrame([{
    "total_unique_hosts":           len(host_df),
    "total_listings":               total_listings,
    "multi_listing_hosts":          len(multi_listing_hosts),
    "multi_listing_host_pct":       round(len(multi_listing_hosts) / len(host_df) * 100, 1),
    "listings_by_multi_hosts":      int(multi_listing_hosts["listings_owned"].sum()),
    "listings_by_multi_hosts_pct":  round(multi_listing_hosts["listings_owned"].sum() / total_listings * 100, 1),
    "top_10pct_hosts_count":        top_10_pct_threshold,
    "top_10pct_listings":           int(top_10pct_hosts["listings_owned"].sum()),
    "top_10pct_listings_pct":       round(top_10pct_hosts["listings_owned"].sum() / total_listings * 100, 1),
    "berlin_median_price":          round(berlin_median_price, 2),
}])

print(f"      Multi-listing hosts: {concentration_stats['multi_listing_host_pct'].iloc[0]}%")
print(f"      Top 10% hosts control: {concentration_stats['top_10pct_listings_pct'].iloc[0]}% of listings")

# ── SQL QUERY 3: Room Type Pricing ────────────────────────────────────
room_type_sql = """
SELECT
    room_type,
    COUNT(*)                        AS listing_count,
    ROUND(AVG(price), 2)            AS avg_price_eur,
    ROUND(AVG(rating), 2)           AS avg_rating,
    ROUND(AVG(accommodates), 1)     AS avg_guests,
    ROUND(AVG(availability_365), 0) AS avg_availability_days,
    ROUND(AVG(est_monthly_revenue), 2) AS avg_est_monthly_revenue
FROM listings
GROUP BY room_type
ORDER BY listing_count DESC
"""
room_type_df = pd.read_sql(room_type_sql, conn)

# ── SQL QUERY 4: Price Buckets for Distribution Chart ─────────────────
price_dist_sql = """
SELECT
    CASE
        WHEN price < 50  THEN '€0–50'
        WHEN price < 100 THEN '€50–100'
        WHEN price < 150 THEN '€100–150'
        WHEN price < 200 THEN '€150–200'
        WHEN price < 300 THEN '€200–300'
        WHEN price < 500 THEN '€300–500'
        ELSE '€500+'
    END AS price_bucket,
    COUNT(*) AS listing_count,
    ROUND(AVG(price), 2) AS avg_price_in_bucket
FROM listings
GROUP BY price_bucket
ORDER BY MIN(price)
"""
price_dist_df = pd.read_sql(price_dist_sql, conn)

# ── SQL QUERY 5: Superhost Premium ────────────────────────────────────
superhost_sql = """
SELECT
    CASE WHEN is_superhost = 1 THEN 'Superhost' ELSE 'Regular Host' END AS host_type,
    COUNT(*) AS listing_count,
    ROUND(AVG(price), 2) AS avg_price_eur,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(reviews_per_month), 2) AS avg_reviews_per_month,
    ROUND(AVG(availability_365), 0) AS avg_availability_days
FROM listings
GROUP BY is_superhost
"""
superhost_df = pd.read_sql(superhost_sql, conn)

conn.close()


# ── STEP 5: EXPORT ────────────────────────────────────────────────────
print("\n[5/6] Exporting CSVs for Power BI...")

exports = {
    "listings_clean.csv":         df,
    "neighbourhood_summary.csv":  neighbourhood_df,
    "host_concentration.csv":     concentration_stats,
    "host_detail.csv":            host_df.head(200),  # top 200 hosts
    "room_type_summary.csv":      room_type_df,
    "price_distribution.csv":     price_dist_df,
    "superhost_analysis.csv":     superhost_df,
}

for filename, dataframe in exports.items():
    path = os.path.join(OUTPUT_DIR, filename)
    dataframe.to_csv(path, index=False)
    print(f"      ✓ {filename} ({len(dataframe):,} rows)")


# ── STEP 6: PRINT SUMMARY FOR CV BULLET POINTS ────────────────────────
print("\n[6/6] KEY FINDINGS — use these in your CV and portfolio:\n")
print("─" * 60)

top_neighbourhood = neighbourhood_df.iloc[0]
highest_premium = neighbourhood_df.nlargest(1, "price_vs_median_pct").iloc[0]
lowest_price = neighbourhood_df.nsmallest(1, "avg_price_eur").iloc[0]

print(f"  Total listings analysed:     {len(df):,}")
print(f"  Neighbourhoods covered:      {len(neighbourhood_df)}")
print(f"  Berlin median nightly price: €{berlin_median_price:.0f}")
print(f"")
print(f"  Most listings:  {top_neighbourhood['neighbourhood']}")
print(f"                  {int(top_neighbourhood['total_listings']):,} listings @ €{top_neighbourhood['avg_price_eur']:.0f}/night avg")
print(f"")
print(f"  Highest premium neighbourhood: {highest_premium['neighbourhood']}")
print(f"                  €{highest_premium['avg_price_eur']:.0f}/night")
print(f"                  {highest_premium['price_vs_median_pct']:+.1f}% vs Berlin median")
print(f"")
print(f"  Most affordable area: {lowest_price['neighbourhood']}")
print(f"                  €{lowest_price['avg_price_eur']:.0f}/night avg")
print(f"")
print(f"  Multi-listing hosts: {concentration_stats['multi_listing_host_pct'].iloc[0]}% of hosts")
print(f"  They control:        {concentration_stats['listings_by_multi_hosts_pct'].iloc[0]}% of all listings")
print(f"")
print(f"  Top 10% of hosts control: {concentration_stats['top_10pct_listings_pct'].iloc[0]}% of listings")
print(f"")
print(f"  Room type breakdown:")
for _, row in room_type_df.iterrows():
    print(f"    {row['room_type']:<25} {int(row['listing_count']):>5,} listings  @ €{row['avg_price_eur']:.0f}/night avg")

print("\n─" * 60)
print("✅ All done! Open /output/ folder and load CSVs into Power BI.")
print("─" * 60)
