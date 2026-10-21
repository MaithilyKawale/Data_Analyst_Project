-- Run after code.ipynb has created the public.customer table.
-- These checks report potential issues; review results before changing source data.

-- 1. Row count and duplicate customer IDs.
SELECT COUNT(*) AS row_count,
       COUNT(DISTINCT customer_id) AS distinct_customer_ids
FROM customer;

SELECT customer_id, COUNT(*) AS duplicate_rows
FROM customer
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY duplicate_rows DESC;

-- 2. Nulls in important fields.
SELECT
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer_id,
    COUNT(*) FILTER (WHERE purchase_amount IS NULL) AS missing_purchase_amount,
    COUNT(*) FILTER (WHERE review_rating IS NULL) AS missing_review_rating,
    COUNT(*) FILTER (WHERE age IS NULL) AS missing_age,
    COUNT(*) FILTER (WHERE item_purchased IS NULL) AS missing_item
FROM customer;

-- 3. Values outside expected ranges. Confirm business rules before treating these as errors.
SELECT *
FROM customer
WHERE age < 0
   OR purchase_amount < 0
   OR (review_rating IS NOT NULL AND (review_rating < 1 OR review_rating > 5))
   OR previous_purchases < 0;

-- 4. Check whether the two promotion fields agree.
-- A result of zero mismatches supports redundancy, but does not prove identical business meaning.
SELECT COUNT(*) AS promotion_field_mismatches
FROM customer
WHERE discount_applied IS DISTINCT FROM promo_code_used;

-- 5. Review categorical values for unexpected spelling/casing.
SELECT 'gender' AS field_name, gender AS field_value, COUNT(*) AS records
FROM customer GROUP BY gender
UNION ALL
SELECT 'shipping_type', shipping_type, COUNT(*)
FROM customer GROUP BY shipping_type
UNION ALL
SELECT 'subscription_status', subscription_status, COUNT(*)
FROM customer GROUP BY subscription_status
ORDER BY field_name, records DESC;
