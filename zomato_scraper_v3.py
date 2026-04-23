from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
OUTPUT_FILE = "zomato_delhi.csv"
HEADLESS    = False
DELAY_MIN   = 2.0
DELAY_MAX   = 4.0

# Each locality scraped with 3 different sort orders
# to maximize unique restaurants collected
SORT_ORDERS = [
    "",                  # default (relevance)
    "?sort=rating",      # by rating
    "?sort=cost-asc",    # by cost low to high
    "?sort=cost-desc",   # by cost high to low
]

LOCALITIES = [
    {"name": "Connaught Place",  "slug": "connaught-place"},
    {"name": "Hauz Khas",        "slug": "hauz-khas"},
    {"name": "Lajpat Nagar",     "slug": "lajpat-nagar"},
    {"name": "Saket",            "slug": "saket"},
    {"name": "Karol Bagh",       "slug": "karol-bagh"},
    {"name": "Chandni Chowk",    "slug": "chandni-chowk"},
    {"name": "Vasant Kunj",      "slug": "vasant-kunj"},
    {"name": "Greater Kailash",  "slug": "greater-kailash"},
    {"name": "Rohini",           "slug": "rohini"},
    {"name": "Dwarka",           "slug": "dwarka"},
    {"name": "Pitampura",        "slug": "pitampura"},
    {"name": "Janakpuri",        "slug": "janakpuri"},
]

BASE_URL = "https://www.zomato.com/ncr/restaurants/in/{slug}{sort}"

# ─────────────────────────────────────────
#  DRIVER
# ─────────────────────────────────────────

def make_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts,
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

# ─────────────────────────────────────────
#  GET CARDS
# ─────────────────────────────────────────

def get_cards(driver):
    for sel in [
        "div[class*='jumbo-tracker']",
        "div[class*='sc-beqWAB']",
        "div[class*='RestaurantCard']",
    ]:
        cards = driver.find_elements(By.CSS_SELECTOR, sel)
        if len(cards) > 2:
            return cards
    return []

# ─────────────────────────────────────────
#  SCROLL
# ─────────────────────────────────────────

def scroll_and_load(driver):
    prev = 0
    no_change = 0
    for _ in range(20):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        curr = len(get_cards(driver))
        if curr == prev:
            no_change += 1
            if no_change >= 3:
                break
        else:
            no_change = 0
        prev = curr

# ─────────────────────────────────────────
#  PARSE CARD
# ─────────────────────────────────────────

def safe_text(el, selectors):
    for sel in selectors:
        try:
            found = el.find_element(By.CSS_SELECTOR, sel)
            text = found.text.strip()
            if text:
                return text
        except Exception:
            continue
    return ""

def parse_card(card, locality):
    name     = safe_text(card, ["h4", "h3", "h2"])
    cuisines = safe_text(card, ["[class*='Cuisine']", "p"])
    rating   = safe_text(card, ["[class*='sc-UoWgt']", "[class*='rating']"])
    price    = safe_text(card, ["[class*='sc-ifAKCX']", "[class*='price']", "[class*='cost']"])
    votes    = safe_text(card, ["[class*='vote']"])

    url = ""
    try:
        url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href") or ""
    except Exception:
        pass

    return {
        "name":          name,
        "locality":      locality,
        "cuisines":      cuisines,
        "rating":        rating,
        "price_for_two": price,
        "votes":         votes,
        "url":           url[:300],
        "scraped_at":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

# ─────────────────────────────────────────
#  SCRAPE ONE URL
# ─────────────────────────────────────────

def scrape_url(driver, url, locality_name):
    driver.get(url)
    try:
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                "div[class*='jumbo-tracker'], div[class*='sc-beqWAB']"))
        )
    except Exception:
        return []

    time.sleep(2)
    scroll_and_load(driver)

    cards = get_cards(driver)
    results = []
    for card in cards:
        try:
            r = parse_card(card, locality_name)
            if r["name"] and len(r["name"]) > 1:
                results.append(r)
        except Exception:
            continue
    return results

# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

def scrape_zomato():
    driver = make_driver()
    all_data = []
    seen_names = set()  # track duplicates across sort orders

    try:
        for i, loc in enumerate(LOCALITIES):
            print(f"\n[{i+1}/{len(LOCALITIES)}] {loc['name']}")
            loc_count = 0

            for sort in SORT_ORDERS:
                url = BASE_URL.format(slug=loc["slug"], sort=sort)
                print(f"  Sort: '{sort or 'default'}' → ", end="", flush=True)

                results = scrape_url(driver, url, loc["name"])

                # Add only new restaurants (deduplicate by name+locality)
                new = 0
                for r in results:
                    key = f"{r['name']}_{r['locality']}"
                    if key not in seen_names and r["name"]:
                        seen_names.add(key)
                        all_data.append(r)
                        new += 1
                        loc_count += 1

                print(f"{len(results)} found, {new} new")
                time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

            print(f"  Total for {loc['name']}: {loc_count} | Grand total: {len(all_data)}")

            # Save progress
            if all_data:
                pd.DataFrame(all_data).to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    finally:
        driver.quit()

    return pd.DataFrame(all_data)


def save_and_report(df):
    if df.empty:
        print("\n[!] No data scraped.")
        return

    df.drop_duplicates(subset=["name", "locality"], inplace=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n{'='*52}")
    print(f"  Saved {len(df)} restaurants → {OUTPUT_FILE}")
    print(f"{'='*52}")
    print(f"\n  Per locality:")
    print(df["locality"].value_counts().to_string())
    print(f"\n  Sample:")
    print(df[["name", "locality", "cuisines", "rating", "price_for_two"]].head(10).to_string(index=False))


if __name__ == "__main__":
    print("Zomato Delhi scraper v3 — multi sort orders")
    df = scrape_zomato()
    save_and_report(df)
