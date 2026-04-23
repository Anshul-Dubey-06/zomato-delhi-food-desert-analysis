-- ============================================================
--  PROJECT 2: Zomato Delhi Food Desert Analysis
--  Database: zomato_delhi | Table: restaurants
-- ============================================================

USE zomato_delhi;

-- ────────────────────────────────────────────────────────────
--  Q1: How many restaurants per locality?
-- ────────────────────────────────────────────────────────────
SELECT 
    locality,
    COUNT(*) AS total_restaurants,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(price_for_two), 0) AS avg_price
FROM restaurants
WHERE locality != 'Unknown'
GROUP BY locality
ORDER BY total_restaurants DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
--  Q2: Which cuisine dominates each locality?
-- ────────────────────────────────────────────────────────────
SELECT 
    locality,
    primary_cuisine,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY locality), 1) AS pct_of_locality
FROM restaurants
WHERE locality != 'Unknown'
  AND primary_cuisine != 'Unknown'
GROUP BY locality, primary_cuisine
ORDER BY locality, count DESC;


-- ────────────────────────────────────────────────────────────
--  Q3: Cuisine gaps — which cuisines are MISSING per locality?
--  (localities with 10+ restaurants but 0 of a top cuisine)
-- ────────────────────────────────────────────────────────────
SELECT 
    l.locality,
    l.total_restaurants,
    'Asian'       AS missing_cuisine
FROM (
    SELECT locality, COUNT(*) AS total_restaurants
    FROM restaurants
    WHERE locality != 'Unknown'
    GROUP BY locality
    HAVING total_restaurants >= 10
) l
LEFT JOIN (
    SELECT locality FROM restaurants WHERE primary_cuisine = 'Asian'
) a ON l.locality = a.locality
WHERE a.locality IS NULL

UNION ALL

SELECT 
    l.locality,
    l.total_restaurants,
    'Cafe' AS missing_cuisine
FROM (
    SELECT locality, COUNT(*) AS total_restaurants
    FROM restaurants
    WHERE locality != 'Unknown'
    GROUP BY locality
    HAVING total_restaurants >= 10
) l
LEFT JOIN (
    SELECT locality FROM restaurants WHERE primary_cuisine = 'Cafe'
) a ON l.locality = a.locality
WHERE a.locality IS NULL

UNION ALL

SELECT 
    l.locality,
    l.total_restaurants,
    'Continental' AS missing_cuisine
FROM (
    SELECT locality, COUNT(*) AS total_restaurants
    FROM restaurants
    WHERE locality != 'Unknown'
    GROUP BY locality
    HAVING total_restaurants >= 10
) l
LEFT JOIN (
    SELECT locality FROM restaurants WHERE primary_cuisine = 'Continental'
) a ON l.locality = a.locality
WHERE a.locality IS NULL

ORDER BY total_restaurants DESC;


-- ────────────────────────────────────────────────────────────
--  Q4: Price vs Rating by locality
--  Which area gives best value for money?
-- ────────────────────────────────────────────────────────────
SELECT 
    locality,
    ROUND(AVG(rating), 2)        AS avg_rating,
    ROUND(AVG(price_for_two), 0) AS avg_price,
    COUNT(*)                      AS restaurants,
    ROUND(AVG(rating) / (AVG(price_for_two) / 100), 3) AS value_score
FROM restaurants
WHERE locality != 'Unknown'
  AND rating IS NOT NULL
  AND price_for_two IS NOT NULL
  AND price_for_two > 0
GROUP BY locality
HAVING restaurants >= 5
ORDER BY value_score DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────
--  Q5: Which cuisine has best rating-to-price ratio?
-- ────────────────────────────────────────────────────────────
SELECT 
    primary_cuisine,
    ROUND(AVG(rating), 2)        AS avg_rating,
    ROUND(AVG(price_for_two), 0) AS avg_price,
    COUNT(*)                      AS restaurants,
    ROUND(AVG(rating) / (AVG(price_for_two) / 100), 3) AS value_score
FROM restaurants
WHERE primary_cuisine != 'Unknown'
  AND rating IS NOT NULL
  AND price_for_two IS NOT NULL
  AND price_for_two > 0
GROUP BY primary_cuisine
HAVING restaurants >= 10
ORDER BY value_score DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────
--  Q6: Hidden Gems — high rating, low votes
--  (great food but not famous yet)
-- ────────────────────────────────────────────────────────────
SELECT 
    name,
    locality,
    primary_cuisine,
    rating,
    votes,
    price_for_two,
    'Hidden Gem' AS segment
FROM restaurants
WHERE rating >= 4.3
  AND votes <= 100
  AND votes > 5
  AND rating IS NOT NULL
  AND locality != 'Unknown'
ORDER BY rating DESC, votes ASC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
--  Q7: Overhyped — low rating, high votes
--  (famous but disappointing)
-- ────────────────────────────────────────────────────────────
SELECT 
    name,
    locality,
    primary_cuisine,
    rating,
    votes,
    price_for_two,
    'Overhyped' AS segment
FROM restaurants
WHERE rating < 3.8
  AND votes >= 500
  AND rating IS NOT NULL
  AND locality != 'Unknown'
ORDER BY votes DESC, rating ASC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
--  Q8: Price band distribution by locality
-- ────────────────────────────────────────────────────────────
SELECT 
    locality,
    SUM(CASE WHEN price_band = 'Budget (≤₹300)'      THEN 1 ELSE 0 END) AS budget,
    SUM(CASE WHEN price_band = 'Mid (₹300-700)'       THEN 1 ELSE 0 END) AS mid,
    SUM(CASE WHEN price_band = 'Premium (₹700-1500)'  THEN 1 ELSE 0 END) AS premium,
    SUM(CASE WHEN price_band = 'Luxury (>₹1500)'      THEN 1 ELSE 0 END) AS luxury,
    COUNT(*) AS total
FROM restaurants
WHERE locality != 'Unknown'
GROUP BY locality
ORDER BY total DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────
--  Q9: North Indian dominance — how saturated is each area?
-- ────────────────────────────────────────────────────────────
SELECT 
    locality,
    COUNT(*) AS total_restaurants,
    SUM(CASE WHEN primary_cuisine = 'North Indian' THEN 1 ELSE 0 END) AS north_indian_count,
    ROUND(SUM(CASE WHEN primary_cuisine = 'North Indian' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS north_indian_pct
FROM restaurants
WHERE locality != 'Unknown'
GROUP BY locality
HAVING total_restaurants >= 10
ORDER BY north_indian_pct DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────
--  Q10: Business recommendation — 
--  Top 3 localities for opening a new Cafe
-- ────────────────────────────────────────────────────────────
SELECT 
    r.locality,
    r.total_restaurants,
    COALESCE(c.cafe_count, 0) AS existing_cafes,
    ROUND(r.avg_rating, 2) AS area_avg_rating,
    ROUND(r.avg_price, 0) AS area_avg_price,
    CASE 
        WHEN COALESCE(c.cafe_count, 0) = 0 THEN 'No cafes — high opportunity'
        WHEN COALESCE(c.cafe_count, 0) <= 2 THEN 'Very few cafes — good opportunity'
        ELSE 'Some cafes exist'
    END AS opportunity
FROM (
    SELECT 
        locality,
        COUNT(*) AS total_restaurants,
        AVG(rating) AS avg_rating,
        AVG(price_for_two) AS avg_price
    FROM restaurants
    WHERE locality != 'Unknown'
    GROUP BY locality
    HAVING total_restaurants >= 15
) r
LEFT JOIN (
    SELECT locality, COUNT(*) AS cafe_count
    FROM restaurants
    WHERE primary_cuisine = 'Cafe'
    GROUP BY locality
) c ON r.locality = c.locality
ORDER BY existing_cafes ASC, total_restaurants DESC
LIMIT 10;


USE zomato_delhi;

-- Gap Score = total_restaurants × avg_price / 1000
-- Higher score = bigger opportunity
SELECT 
    r.locality,
    r.total_restaurants,
    COALESCE(c.cafe_count, 0)        AS existing_cafes,
    COALESCE(a.asian_count, 0)       AS existing_asian,
    COALESCE(cn.continental_count, 0) AS existing_continental,
    ROUND(r.avg_price, 0)            AS avg_price,
    ROUND(r.avg_rating, 2)           AS avg_rating,
    ROUND(
        (r.total_restaurants * r.avg_price) / 1000
    , 1) AS opportunity_score
FROM (
    SELECT locality,
           COUNT(*) AS total_restaurants,
           AVG(price_for_two) AS avg_price,
           AVG(rating) AS avg_rating
    FROM restaurants
    WHERE locality != 'Unknown'
      AND price_for_two IS NOT NULL
      AND rating IS NOT NULL
    GROUP BY locality
    HAVING total_restaurants >= 15
) r
LEFT JOIN (
    SELECT locality, COUNT(*) AS cafe_count
    FROM restaurants WHERE primary_cuisine = 'Cafe'
    GROUP BY locality
) c ON r.locality = c.locality
LEFT JOIN (
    SELECT locality, COUNT(*) AS asian_count
    FROM restaurants WHERE primary_cuisine = 'Asian'
    GROUP BY locality
) a ON r.locality = a.locality
LEFT JOIN (
    SELECT locality, COUNT(*) AS continental_count
    FROM restaurants WHERE primary_cuisine = 'Continental'
    GROUP BY locality
) cn ON r.locality = cn.locality
ORDER BY opportunity_score DESC
LIMIT 10;