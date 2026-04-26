# Zomato Delhi — Food Desert Analysis 🍽️

## The Problem I Was Solving
Delhi has thousands of restaurants but they are not 
distributed evenly. Some cuisines are everywhere. 
Others are completely absent from entire localities. 
I wanted to find where the gaps are — and turn that 
into a business recommendation.

## The Core Insight
Connaught Place has 29 Asian restaurants.
Rohini has 54 restaurants total and zero Asian options.
Rajouri Garden has 50 restaurants and zero Asian options.
West Delhi is a food desert for any cuisine that isn't 
North Indian.

## Surprising Findings

### Finding 1 — Asian cuisine gap in West Delhi
Rohini, Rajouri Garden, Janakpuri, Malviya Nagar — 
all have 30-54 restaurants each. None have Asian food.
Connaught Place has 29 Asian restaurants alone.
The entire Asian cuisine market in Delhi is concentrated 
in one area.

### Finding 2 — Cafe culture is missing from West Delhi
Punjabi Bagh has 39 restaurants and zero cafes.
This is a large residential area with young population 
and high footfall — classic underserved market.

### Finding 3 — North Indian is the worst business decision
Connaught Place has 200 North Indian restaurants.
Any new restaurant opening North Indian there is 
entering maximum competition for minimum differentiation.

### Finding 4 — Sector 29 is the top opportunity
Opportunity score 70.8 — highest in Delhi NCR.
Average spend ₹1,222 per visit.
Only 1 cafe in the entire locality.
High spending customers, low competition.

### Finding 5 — Star power doesn't equal value
Cyber Hub is Delhi's most expensive area at ₹1,285 avg.
But its average rating is only 4.1 — premium price, 
average experience. 

## How I Built This

### Step 1 — Multi-source data collection
Scraped 400+ live restaurants from Zomato using Selenium.
Zomato limits anonymous users to 9 results per locality — 
worked around this with multiple sort orders.
Merged with Kaggle historical dataset for statistical depth.
Final dataset: 3,119 restaurants across 15 localities.

### Step 2 — Built the Locality × Cuisine Gap Matrix
Pivot table showing restaurant counts for every 
cuisine × locality combination.
Zero cells = underserved market = opportunity.

### Step 3 — SQL analysis in MySQL
10 queries covering gaps, value scores, hidden gems,
overhyped restaurants and business recommendations.

### Step 4 — Built Opportunity Score
Opportunity Score = (total_restaurants × avg_price) / 1000

Higher score = bigger market with higher spending power.
Used to rank localities for new restaurant recommendations.

### Step 5 — 2-page Power BI dashboard
Page 1: Market analysis with heatmap
Page 2: Business recommendations with opportunity scores

## Tools Used
| Tool | Purpose |
|------|---------|
| Python + Selenium | Scraping Zomato live listings |
| pandas | Merging and cleaning 3 data sources |
| MySQL | Storage and 10 SQL analysis queries |
| Power BI | 2-page dashboard with IPL-style dark theme |

## Key Numbers
- 3,119 restaurants analysed
- 15 Delhi localities covered
- 12 cuisine types tracked
- Top opportunity score: Sector 29 at 70.8

## Files
| File | Description |
|------|-------------|
| zomato_scraper_v3.py | Selenium scraper with multi-sort approach |
| merge_clean.py | Merges 3 data sources, cleans localities |
| load_zomato_mysql.py | Loads into MySQL |
| zomato_analysis_queries.sql | 10 SQL queries including gap analysis |
| zomato_delhi_clean.csv | Final dataset 3,119 restaurants |
| cuisine_gap_matrix.csv | Locality × cuisine pivot |
| recommendations.csv | Opportunity scores by locality |
| zomato_dashboard.pdf | 2-page Power BI dashboard |

## Interview Answer
"I scraped and analysed 3,119 restaurants across 15 Delhi 
localities to find cuisine gaps. The biggest finding: Asian 
cuisine is completely absent from West Delhi — Rohini has 
54 restaurants but zero Asian options. I built an Opportunity 
Score combining restaurant density and average spend to 
identify Sector 29 as the top location for a new cafe or 
Asian restaurant. This is the kind of location intelligence 
Zomato, Swiggy and restaurant chains actually use internally."
