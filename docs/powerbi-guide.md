# Power BI dashboard enhancement guide

Use the existing PBIX as the visual reporting layer and keep metric definitions aligned with the Python app.

## Page 1 — Executive overview
- Cards: record count, total purchase amount across records, average purchase amount, average rating.
- Bar chart: purchase amount by category.
- Slicers: category, age group, subscription status, season.
- Label total as a sum across source records, not verified order revenue.

## Page 2 — Customer insights
- Show age group and purchase frequency distributions.
- Compare average purchase amount by subscription status and purchase-history band.
- Avoid labels such as “loyal” unless defined by validated behavior over time.

## Page 3 — Product performance
- Product record count, average rating, rating sample size, average purchase amount.
- Show sample size beside average ratings.
- Do not equate row count with units sold unless quantity/order data exists.

## Page 4 — Shipping and promotions
- Record count and average purchase amount by shipping type, payment method, and discount flag.
- Add a visible note that observational comparisons do not prove causation.
- Do not claim discount lift or profit impact from this dataset.

## Quality and usability
- Use consistent number formats, accessible contrast, descriptive chart titles, meaningful tooltips, and slicers that avoid misleading comparisons.
- Document KPI definitions and denominators.
- Add screenshots only after verifying the final dashboard visuals.
