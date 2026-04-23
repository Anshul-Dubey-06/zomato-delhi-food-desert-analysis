# Zomato Delhi — Food Desert Analysis

## Overview
Scraped and analysed 3,119 restaurants across 15 Delhi localities 
to find cuisine gaps, food deserts and restaurant opportunities.

## Key Findings
- Asian cuisine is absent from West Delhi — Rohini (54 restaurants) 
  and Rajouri Garden (50) have zero Asian options
- Punjabi Bagh has zero cafes despite 39 restaurants and strong 
  residential footfall
- Sector 29 has the highest opportunity score (70.8) — high spend 
  area (₹1,222 avg) with only 1 cafe
- North Indian dominates everywhere — worst category to enter in 
  Connaught Place (200 existing restaurants)
- Cyber Hub is Delhi's most expensive area at ₹1,285 avg price for two

## Tools Used
| Tool | Purpose |
|------|---------|
| Python + Selenium | Scraping Zomato live listings |
| pandas | Data cleaning & merging |
| MySQL | Storage & SQL analysis |
| Power BI | Dashboard & recommendations |

## Files
| File | Description |
|------|-------------|
| zomato_scraper_v3.py | Selenium scraper for Zomato Delhi |
| merge_clean.py | Merges scraped + Kaggle data, cleans localities |
| load_zomato_mysql.py | Loads clean data into MySQL |
| zomato_analysis_queries.sql | 10 SQL analysis queries |
| zomato_delhi_clean.csv | Final clean dataset (3,119 restaurants) |
| cuisine_gap_matrix.csv | Locality × cuisine pivot table |
| recommendations.csv | Opportunity scores by locality |
| zomato_dashboard.pdf | 2-page Power BI dashboard |

## How to Run
1. pip install selenium webdriver-manager pandas mysql-connector-python
2. python zomato_scraper_v3.py
3. python merge_clean.py
4. python load_zomato_mysql.py
5. Open zomato_analysis_queries.sql in MySQL Workbench
6. Open zomato_dashboard.pdf to view dashboard

## Dashboard Preview
[View Dashboard PDF](zomato_dashboard.pdf)
