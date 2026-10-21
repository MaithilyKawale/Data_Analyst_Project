-- Customer Shopping Behavior Analysis
-- Assumption: this dataset contains one row per customer, not a transaction-level history.
-- Therefore COUNT(*) is a row/customer count for this dataset, not a general order count.

-- Q1. Revenue and average purchase amount by gender.
SELECT gender,
       COUNT(*) AS customer_records,
       ROUND(SUM(purchase_amount)::numeric, 2) AS total_revenue,
       ROUND(AVG(purchase_amount)::numeric, 2) AS average_purchase_amount
FROM customer
GROUP BY gender
ORDER BY total_revenue DESC;

-- Q2. Customers using a discount whose purchase amount is at least the dataset average.
SELECT customer_id, purchase_amount
FROM customer
WHERE discount_applied = 'Yes'
  AND purchase_amount >= (SELECT AVG(purchase_amount) FROM customer)
ORDER BY purchase_amount DESC;

-- Q3. Five products with the highest average review rating, including sample size.
SELECT item_purchased,
       COUNT(review_rating) AS ratings_count,
       ROUND(AVG(review_rating::numeric), 2) AS average_product_rating
FROM customer
WHERE review_rating IS NOT NULL
GROUP BY item_purchased
ORDER BY average_product_rating DESC, ratings_count DESC
LIMIT 5;

-- Q4. Average purchase amount by shipping type.
SELECT shipping_type,
       COUNT(*) AS customer_records,
       ROUND(AVG(purchase_amount)::numeric, 2) AS average_purchase_amount
FROM customer
GROUP BY shipping_type
ORDER BY average_purchase_amount DESC;

-- Q5. Compare spending for subscribers and non-subscribers.
SELECT subscription_status,
       COUNT(*) AS customer_records,
       ROUND(AVG(purchase_amount)::numeric, 2) AS average_purchase_amount,
       ROUND(SUM(purchase_amount)::numeric, 2) AS total_revenue,
       ROUND(
           100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2
       ) AS share_of_records_pct
FROM customer
GROUP BY subscription_status
ORDER BY total_revenue DESC;

-- Q6. Discount-use rate by product. Interpret as an association, not proof of impact.
SELECT item_purchased,
       COUNT(*) AS customer_records,
       ROUND(
           100.0 * COUNT(*) FILTER (WHERE discount_applied = 'Yes') / COUNT(*), 2
       ) AS discount_use_rate_pct
FROM customer
GROUP BY item_purchased
ORDER BY discount_use_rate_pct DESC, customer_records DESC
LIMIT 5;

-- Q7. Descriptive purchase-history bands.
-- The dataset does not include customer acquisition dates or transaction history,
-- so these bands must not be described as verified New/Returning/Loyal segments.
SELECT
    CASE
        WHEN previous_purchases = 0 THEN '0 previous purchases'
        WHEN previous_purchases BETWEEN 1 AND 2 THEN '1-2 previous purchases'
        WHEN previous_purchases BETWEEN 3 AND 10 THEN '3-10 previous purchases'
        ELSE '11+ previous purchases'
    END AS purchase_history_band,
    COUNT(*) AS customer_records,
    ROUND(AVG(purchase_amount)::numeric, 2) AS average_purchase_amount
FROM customer
GROUP BY purchase_history_band
ORDER BY MIN(previous_purchases);

-- Q8. Top three products within each category by record count.
WITH item_counts AS (
    SELECT category, item_purchased, COUNT(*) AS record_count,
           DENSE_RANK() OVER (
               PARTITION BY category ORDER BY COUNT(*) DESC
           ) AS item_rank
    FROM customer
    GROUP BY category, item_purchased
)
SELECT category, item_purchased, record_count, item_rank
FROM item_counts
WHERE item_rank <= 3
ORDER BY category, item_rank, item_purchased;

-- Q9. Subscription status among customers with more than five previous purchases.
SELECT subscription_status,
       COUNT(*) AS customer_records,
       ROUND(AVG(purchase_amount)::numeric, 2) AS average_purchase_amount
FROM customer
WHERE previous_purchases > 5
GROUP BY subscription_status
ORDER BY customer_records DESC;

-- Q10. Revenue contribution by age group.
SELECT age_group,
       COUNT(*) AS customer_records,
       ROUND(SUM(purchase_amount)::numeric, 2) AS total_revenue,
       ROUND(
           100.0 * SUM(purchase_amount) / SUM(SUM(purchase_amount)) OVER (), 2
       ) AS revenue_share_pct
FROM customer
GROUP BY age_group
ORDER BY total_revenue DESC;
