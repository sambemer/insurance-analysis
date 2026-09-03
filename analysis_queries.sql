-- =========================================================================
-- Multi-Line Insurance Premium Analysis
-- Database: insurance.db (tables: customers, auto_policies, home_policies)
-- =========================================================================

-- 1. Average auto premium by credit tier
-- Shows credit tier as a primary driver of premium variation.
SELECT
    c.credit_tier,
    COUNT(*)                         AS policy_count,
    ROUND(AVG(a.annual_premium), 2)  AS avg_premium
FROM auto_policies a
JOIN customers c ON a.customer_id = c.customer_id
GROUP BY c.credit_tier
ORDER BY avg_premium DESC;


-- 2. Bundled vs. non-bundled customers: average combined premium
-- Quantifies the value of the multi-policy discount.
SELECT
    c.bundled_discount,
    CASE WHEN c.bundled_discount = 1 THEN 'Bundled' ELSE 'Not Bundled' END AS bundle_status,
    COUNT(DISTINCT c.customer_id)                                          AS customers,
    ROUND(AVG(combined.total_premium), 2)                                  AS avg_combined_premium
FROM customers c
JOIN (
    SELECT customer_id, SUM(annual_premium) AS total_premium
    FROM (
        SELECT customer_id, annual_premium FROM auto_policies
        UNION ALL
        SELECT customer_id, annual_premium FROM home_policies
    )
    GROUP BY customer_id
) combined ON combined.customer_id = c.customer_id
GROUP BY c.bundled_discount
ORDER BY avg_combined_premium DESC;


-- 3. Age bracket segmentation using CASE WHEN
-- Buckets customers into risk-relevant age groups to compare premiums.
SELECT
    CASE
        WHEN c.age < 25 THEN 'Under 25'
        WHEN c.age BETWEEN 25 AND 29 THEN '25-29'
        WHEN c.age BETWEEN 30 AND 64 THEN '30-64'
        ELSE '65+'
    END AS age_bracket,
    COUNT(*)                        AS policy_count,
    ROUND(AVG(a.annual_premium), 2) AS avg_auto_premium
FROM auto_policies a
JOIN customers c ON a.customer_id = c.customer_id
GROUP BY age_bracket
ORDER BY avg_auto_premium DESC;


-- 4. Prior claims impact on premium, by policy line
-- Compares how claims history drives cost differently for auto vs. home.
SELECT
    'Auto' AS policy_line,
    c.prior_claims_5yr,
    COUNT(*)                        AS policy_count,
    ROUND(AVG(a.annual_premium), 2) AS avg_premium
FROM auto_policies a
JOIN customers c ON a.customer_id = c.customer_id
GROUP BY c.prior_claims_5yr

UNION ALL

SELECT
    'Home' AS policy_line,
    c.prior_claims_5yr,
    COUNT(*)                        AS policy_count,
    ROUND(AVG(h.annual_premium), 2) AS avg_premium
FROM home_policies h
JOIN customers c ON h.customer_id = c.customer_id
GROUP BY c.prior_claims_5yr

ORDER BY policy_line, prior_claims_5yr;


-- 5. State-level premium comparison with high/low flag
-- Uses CASE WHEN to flag states above the overall average.
WITH state_avg AS (
    SELECT c.state, ROUND(AVG(a.annual_premium), 2) AS avg_premium
    FROM auto_policies a
    JOIN customers c ON a.customer_id = c.customer_id
    GROUP BY c.state
),
overall_avg AS (
    SELECT AVG(annual_premium) AS overall FROM auto_policies
)
SELECT
    s.state,
    s.avg_premium,
    CASE
        WHEN s.avg_premium > (SELECT overall FROM overall_avg) THEN 'Above Average'
        ELSE 'Below Average'
    END AS relative_to_book
FROM state_avg s
ORDER BY s.avg_premium DESC;


-- 6. Vehicle type and coverage level premium matrix
-- Two-dimensional GROUP BY to find the highest-cost combinations.
SELECT
    vehicle_type,
    coverage_level,
    COUNT(*)                        AS policy_count,
    ROUND(AVG(annual_premium), 2)   AS avg_premium
FROM auto_policies
GROUP BY vehicle_type, coverage_level
ORDER BY avg_premium DESC
LIMIT 10;


-- 7. Customer tenure discount effect
-- Buckets tenure and shows the discount curve for loyal customers.
SELECT
    CASE
        WHEN c.years_with_company < 2 THEN '0-1 yrs'
        WHEN c.years_with_company < 5 THEN '2-4 yrs'
        WHEN c.years_with_company < 10 THEN '5-9 yrs'
        ELSE '10+ yrs'
    END AS tenure_bracket,
    COUNT(*)                        AS policy_count,
    ROUND(AVG(a.annual_premium), 2) AS avg_premium
FROM auto_policies a
JOIN customers c ON a.customer_id = c.customer_id
GROUP BY tenure_bracket
ORDER BY avg_premium DESC;
