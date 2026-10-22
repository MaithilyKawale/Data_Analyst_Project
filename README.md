# Customer Intelligence Platform — Shopping Analytics

An end-to-end analytics portfolio project that turns customer shopping data into a tested, interactive customer-intelligence app using Python, pandas, SQL, PostgreSQL, Streamlit, and Power BI.

## What this project does

- **Data preparation:** clean column names, handle missing review ratings, and derive descriptive features.
- **Data-quality pipeline:** check duplicate IDs, missing values, invalid ranges, category consistency, and promotion-field mismatches.
- **Business analytics:** summarize purchase amounts, categories, products, ratings, shipping, payment methods, subscriptions, and discount usage.
- **Multi-page BI dashboard:** use a clear sidebar menu for executive KPIs, customer demographics, product/category performance, purchase and promotion comparisons, shipping/payments, customer segments, data quality, and reports. Pages contain multiple interactive Plotly charts.
- **Customer segmentation:** run reproducible K-Means segments on available numeric features, with a silhouette score when it can be calculated.
- **AI chatbot:** ask general questions or questions about the dataset in a conversational chat interface. With an OpenAI API key, it answers broad questions and uses aggregate dataset context for data-related answers; without a key, a limited local analytics fallback remains available.
- **AI-assisted insights:** optionally generate narrative summaries with an OpenAI API key. Deterministic insights remain available without an API key.
- **Product discovery baseline:** find popular and well-rated products within a category. This is a popularity baseline, not a personalized recommender trained on transaction histories.
- **Downloadable reports:** export filtered records and an analysis snapshot as Markdown/CSV.
- **Automated checks:** run tests and Python compilation through GitHub Actions.
- **Forecasting readiness:** a validation scaffold explains the transaction-date requirements before a time-series forecast can be run.

## Repository map

| Path | Purpose |
|---|---|
| `customer_shopping_behavior.csv` | Source dataset |
| `code.ipynb` | Original notebook workflow for cleaning, feature engineering, and PostgreSQL loading |
| `customer-database.sql` | Business analysis queries |
| `sql/data_quality_checks.sql` | PostgreSQL data-quality queries |
| `app.py` | Streamlit customer analytics application |
| `src/analytics.py` | Reusable analysis, segmentation, and recommendation functions |
| `src/data_quality.py` | Reusable data validation checks |
| `src/llm_insights.py` | Optional AI narrative insights |
| `src/forecasting.py` | Forecast readiness checks for future transaction-level data |
| `scripts/generate_report.py` | Generate a dated Markdown snapshot report and CSV summary |
| `tests/` | Automated unit tests |
| `docs/data_dictionary.md` | Field definitions and interpretation notes |
| `docs/powerbi-guide.md` | Suggested Power BI pages and measures |
| `.github/workflows/ci.yml` | Continuous integration workflow |
| `requirements.txt` | Python dependencies |

## Quick start

Python 3.10+ is recommended.

### 1. Create an environment

```bash
python -m venv .venv
```

Activate it, then install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Launch the app

```bash
streamlit run app.py
```

The app looks for `customer_shopping_behavior.csv` in the repository root. You can also upload a CSV from the app. It normalizes column names and shows data-quality results before analysis.

### 3. Optional AI-generated narrative

Set `OPENAI_API_KEY` in your local environment to enable AI-written insights. Optionally set `OPENAI_MODEL` to choose an available model. Without a key, the app uses deterministic, local summaries. Do not place a real API key in source code or commit it.

### 4. Optional PostgreSQL workflow

Create a PostgreSQL database, then set these environment variables in your terminal or IDE:

| Variable | Purpose |
|---|---|
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_DB` | Database name (default: `customer_behavior`) |
| `POSTGRES_HOST` | Host (default: `localhost`) |
| `POSTGRES_PORT` | Port (default: `5432`) |

Run `code.ipynb` cells in order. Run `customer-database.sql` and `sql/data_quality_checks.sql` after the table is loaded. The notebook reads environment variables directly; it does not automatically load a `.env` file.

### 5. Generate a snapshot report

```bash
python scripts/generate_report.py
```

The script writes a dated Markdown report and CSV summary under `reports/generated/`. It is a point-in-time snapshot, not a measurement of week-over-week change: the source data has no transaction date.

### 6. Run tests

```bash
pytest -q
```

## Streamlit app features

1. **Overview:** key totals, average purchase amount, ratings, category breakdowns, and interactive filters.
2. **Data quality:** validation summary and row-level issue counts.
3. **Customer segments:** K-Means clusters based on available numeric features.
4. **Discount analysis:** compare observed purchase amounts for discount vs. non-discount records.
5. **Ask the data:** natural-language questions mapped to a small set of safe, predefined analyses.
6. **Product discovery:** popular and highly rated products by category.
7. **Reports:** download a Markdown snapshot and filtered CSV.

## Power BI dashboard enhancement plan

The existing `customer_behavior_dashboard.pbix` can complement the app with four report pages:

- **Executive Overview:** total purchase amount in the dataset, average purchase amount, average rating, record count, and category contribution.
- **Customer Insights:** age group, subscription status, purchase-history bands, and purchase frequency.
- **Product Performance:** product/category counts, average rating with sample size, and purchase amount distribution.
- **Shipping & Promotions:** shipping method, payment method, discount usage, and observed purchase amount comparisons.

Use clear titles, dynamic slicers, consistent number formatting, tooltips, and visible sample sizes. Add a note that the source represents customer/purchase-related records rather than a full event-level transaction ledger.

## Forecasting and recommender scope

The source dataset does **not** contain a reliable transaction timestamp, order ID, customer acquisition date, product cost/margin, or a complete basket-level purchase history. Therefore, the current project does not claim to calculate sales trends, churn, retention, customer lifetime value, profit, causal discount lift, or a valid time-series forecast. The forecasting module checks for a date column and fails with a clear explanation until transaction-level dated data is supplied.

The product discovery feature is a popularity/rating baseline, not a personalized recommender. A stronger recommender would require multiple dated orders and item-level baskets per customer.

## Data interpretation

- Counts in this dataset are record/customer counts, not universal order counts.
- Purchase-history groups are descriptive bands, not verified lifecycle labels such as “new,” “returning,” or “loyal.”
- Discount and subscription comparisons are observational. They do not prove causation.
- Review ratings may be imputed during notebook cleaning; distinguish observed values from imputed values when reporting conclusions.
- Confirm the source dataset's provenance and license before redistributing it.

## Development

```bash
pytest -q
python -m compileall -q app.py src scripts
```

GitHub Actions runs the automated checks on pushes and pull requests.

## Next data upgrades

To unlock credible forecasting, retention, customer lifetime value, profit analysis, and personalized recommendations, collect a transaction-level table with order ID, customer ID, timestamp, product ID, quantity, unit price, discount amount, cost, and order/basket relationships.
