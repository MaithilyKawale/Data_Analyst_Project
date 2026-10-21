# Data dictionary and interpretation guide

The exact source schema may vary by version. The app normalizes common source labels into snake_case names.

| Field | Meaning | Notes |
|---|---|---|
| customer_id | Customer identifier | Expected to be unique only if the source schema guarantees one row per customer. |
| age | Customer age | Validate non-negative values and the source-specific allowed range. |
| gender | Recorded gender category | Use only for appropriate aggregate analysis. |
| item_purchased | Item/product label | Item-level rows are not necessarily complete basket histories. |
| category | Product category | Check spelling/casing consistency. |
| purchase_amount | Purchase-related amount (sample source label indicates USD) | Confirm currency and whether it represents order value, line value, or customer-level purchase amount. |
| review_rating | Customer review rating | Expected scale 1–5. The notebook may impute missing values using category medians. |
| previous_purchases | Prior-purchase count recorded by the source | Not a dated transaction history or retention metric. |
| discount_applied | Discount indicator | Verify coding and business definition. |
| promo_code_used | Promotion-code indicator | May correlate with, but need not mean the same as, a discount flag. |
| subscription_status | Subscription indicator | Observational group comparisons are not causal evidence. |
| shipping_type | Shipping option | Group differences can reflect customer or product mix. |
| payment_method | Payment method label | Use aggregate analysis only. |
| purchase_frequency | Purchase frequency label | A category, not necessarily a dated interval. |
| season | Season label | Does not substitute for a transaction date. |
| size, color, location | Product/customer attributes | Confirm definitions and permitted use from the original source. |
| age_group | Derived age band | Keep band boundaries consistent across the notebook and dashboard. |

## Important caveats

- Counts refer to rows/records unless an order-level key establishes otherwise.
- Do not infer sales over time without transaction timestamps.
- Do not calculate profit without cost and margin fields.
- Do not claim causal discount impact from simple observational comparisons.
- Confirm source provenance, license, currency, and definitions before publication.
