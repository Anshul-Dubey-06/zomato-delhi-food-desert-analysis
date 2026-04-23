import pandas as pd
import re

# ─────────────────────────────────────────
#  LOAD DATASETS
# ─────────────────────────────────────────

print("Loading datasets...")

# 1. Your scraped data
scraped = pd.read_csv("zomato_delhi.csv", encoding="utf-8-sig")
scraped.columns = scraped.columns.str.replace('ï»¿', '').str.strip()
print(f"Scraped data: {len(scraped)} rows")

# 2. Kaggle India dataset — filter Delhi/NCR only
kaggle = pd.read_csv("zomato_restaurants_in_India_kaggle.csv", encoding="latin1")
print(f"Kaggle full: {len(kaggle)} rows")

delhi_cities = ["New Delhi", "Delhi", "Noida", "Gurgaon", "Gurugram", "Faridabad", "Ghaziabad"]
kaggle_delhi = kaggle[kaggle["city"].isin(delhi_cities)].copy()
print(f"Kaggle Delhi/NCR only: {len(kaggle_delhi)} rows")

# ─────────────────────────────────────────
#  STANDARDISE KAGGLE DATA
# ─────────────────────────────────────────

kaggle_clean = pd.DataFrame()
kaggle_clean["name"]          = kaggle_delhi["name"]
kaggle_clean["locality"]      = kaggle_delhi["locality"].str.split(",").str[0].str.strip()
kaggle_clean["cuisines"]      = kaggle_delhi["cuisines"]
kaggle_clean["rating"]        = pd.to_numeric(kaggle_delhi["aggregate_rating"], errors="coerce")
kaggle_clean["price_for_two"] = pd.to_numeric(kaggle_delhi["average_cost_for_two"], errors="coerce")
kaggle_clean["votes"]         = pd.to_numeric(kaggle_delhi["votes"], errors="coerce")
kaggle_clean["city"]          = kaggle_delhi["city"]
kaggle_clean["source"]        = "kaggle"

# ─────────────────────────────────────────
#  STANDARDISE SCRAPED DATA
# ─────────────────────────────────────────

scraped_clean = pd.DataFrame()
scraped_clean["name"]          = scraped["name"]
scraped_clean["locality"]      = scraped["locality"]
scraped_clean["cuisines"]      = scraped["cuisines"]

# Clean rating — remove non-numeric chars
def clean_rating(val):
    try:
        val = str(val).replace("NEW", "").replace("-", "").strip()
        nums = re.findall(r'\d+\.?\d*', val)
        if nums:
            r = float(nums[0])
            return r if 1 <= r <= 5 else None
        return None
    except Exception:
        return None

scraped_clean["rating"] = scraped["rating"].apply(clean_rating)

# Clean price — extract numbers
def clean_price(val):
    try:
        val = str(val).replace("₹", "").replace(",", "").strip()
        nums = re.findall(r'\d+', val)
        if nums:
            return float(nums[0])
        return None
    except Exception:
        return None

scraped_clean["price_for_two"] = scraped["price_for_two"].apply(clean_price)

# Clean votes
def clean_votes(val):
    try:
        val = str(val).replace("K", "000").replace("k", "000")
        nums = re.findall(r'\d+', val)
        return float(nums[0]) if nums else None
    except Exception:
        return None

scraped_clean["votes"]  = scraped["votes"].apply(clean_votes)
scraped_clean["city"]   = "New Delhi"
scraped_clean["source"] = "scraped"

# ─────────────────────────────────────────
#  MERGE
# ─────────────────────────────────────────

df = pd.concat([kaggle_clean, scraped_clean], ignore_index=True)
print(f"\nMerged total: {len(df)} rows")

# Deduplicate by name + locality
df["name_clean"] = df["name"].str.lower().str.strip()
df["loc_clean"]  = df["locality"].str.lower().str.strip()
df.drop_duplicates(subset=["name_clean", "loc_clean"], inplace=True)
df.drop(columns=["name_clean", "loc_clean"], inplace=True)
print(f"After deduplication: {len(df)} rows")

# ─────────────────────────────────────────
#  CLEAN LOCALITY NAMES
# ─────────────────────────────────────────

LOCALITY_MAP = {
    "connaught place": "Connaught Place",
    "connaught circus": "Connaught Place",
    "cp": "Connaught Place",
    "hauz khas": "Hauz Khas",
    "hauz khas village": "Hauz Khas",
    "lajpat nagar": "Lajpat Nagar",
    "lajpat nagar i": "Lajpat Nagar",
    "lajpat nagar ii": "Lajpat Nagar",
    "lajpat nagar iii": "Lajpat Nagar",
    "lajpat nagar iv": "Lajpat Nagar",
    "saket": "Saket",
    "karol bagh": "Karol Bagh",
    "chandni chowk": "Chandni Chowk",
    "vasant kunj": "Vasant Kunj",
    "greater kailash": "Greater Kailash",
    "greater kailash i": "Greater Kailash",
    "greater kailash ii": "Greater Kailash",
    "gk i": "Greater Kailash",
    "gk ii": "Greater Kailash",
    "rohini": "Rohini",
    "rohini sector 7": "Rohini",
    "rohini sector 9": "Rohini",
    "dwarka": "Dwarka",
    "dwarka sector 10": "Dwarka",
    "dwarka sector 12": "Dwarka",
    "pitampura": "Pitampura",
    "janakpuri": "Janakpuri",
    "defence colony": "Defence Colony",
    "south extension": "South Extension",
    "nehru place": "Nehru Place",
    "rajouri garden": "Rajouri Garden",
    "punjabi bagh": "Punjabi Bagh",
    "malviya nagar": "Malviya Nagar",
    "green park": "Green Park",
    "khan market": "Khan Market",
    "delhi": "Other Delhi",
    "new delhi": "Other Delhi",
}

def clean_locality(loc):
    if pd.isna(loc):
        return "Unknown"
    return LOCALITY_MAP.get(str(loc).lower().strip(), str(loc).strip().title())

df["locality"] = df["locality"].apply(clean_locality)

# ─────────────────────────────────────────
#  CLEAN CUISINES
# ─────────────────────────────────────────

def clean_cuisines(val):
    if pd.isna(val) or str(val).strip() in ["", "nan"]:
        return "Unknown"
    # Remove brackets from kaggle format ['North Indian', 'Chinese']
    val = re.sub(r"[\[\]']", "", str(val))
    return val.strip()

df["cuisines"] = df["cuisines"].apply(clean_cuisines)

# ─────────────────────────────────────────
#  ADD PRICE BAND
# ─────────────────────────────────────────

def price_band(price):
    if pd.isna(price):
        return "Unknown"
    if price <= 300:
        return "Budget (≤₹300)"
    elif price <= 700:
        return "Mid (₹300-700)"
    elif price <= 1500:
        return "Premium (₹700-1500)"
    else:
        return "Luxury (>₹1500)"

df["price_band"] = df["price_for_two"].apply(price_band)

# ─────────────────────────────────────────
#  ADD PRIMARY CUISINE
# ─────────────────────────────────────────

def primary_cuisine(cuisines):
    if pd.isna(cuisines) or cuisines == "Unknown":
        return "Unknown"
    first = str(cuisines).split(",")[0].strip()
    return first if first else "Unknown"

df["primary_cuisine"] = df["cuisines"].apply(primary_cuisine)

# ─────────────────────────────────────────
#  SAVE
# ─────────────────────────────────────────

OUTPUT = "zomato_delhi_clean.csv"
df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

# ─────────────────────────────────────────
#  REPORT
# ─────────────────────────────────────────

print(f"\n{'='*55}")
print(f"  Saved {len(df)} restaurants → {OUTPUT}")
print(f"{'='*55}")

print(f"\n  Source breakdown:")
print(df["source"].value_counts().to_string())

print(f"\n  Top 20 localities:")
print(df["locality"].value_counts().head(20).to_string())

print(f"\n  Top 15 primary cuisines:")
print(df["primary_cuisine"].value_counts().head(15).to_string())

print(f"\n  Price band distribution:")
print(df["price_band"].value_counts().to_string())

print(f"\n  Rating stats:")
print(df["rating"].describe().round(2).to_string())

print(f"\n  Columns in final dataset:")
print(df.columns.tolist())
