# Customer Shopping Behavior Analysis

An end-to-end data analytics portfolio project exploring customer shopping behavior with Python, SQL, PostgreSQL, and Power BI.

## Project objective

Turn a customer shopping dataset into understandable business insights about purchase amounts, product preferences, ratings, discounts, shipping, payment methods, and subscription status.

## Tools

- **Python:** pandas, Jupyter Notebook
- **SQL:** PostgreSQL
- **Database integration:** SQLAlchemy and psycopg2
- **Visualization:** Microsoft Power BI

## Repository contents

| File | Purpose |
|---|---|
| `customer_shopping_behavior.csv` | Source dataset used in the analysis |
| `code.ipynb` | Data inspection, cleaning, feature engineering, and PostgreSQL loading workflow |
| `customer-database.sql` | Business analysis queries |
| `customer_behavior_dashboard.pbix` | Power BI dashboard |
| `Customer Shopping Behavior Analysis.pdf` | Exported project report |
| `requirements.txt` | Python dependencies |
| `.env.example` | Example environment-variable names; contains no credentials |
| `sql/data_quality_checks.sql` | SQL checks to run after loading the data |

## Workflow

1. Load the CSV and inspect dimensions, data types, missing values, and summary statistics.
2. Impute missing review ratings using the median rating within the relevant category.
3. Standardize column names and derive age-group and purchase-frequency features.
4. Check whether `discount_applied` and `promo_code_used` carry duplicate information before retaining one field.
5. Load the prepared data into a local PostgreSQL table named `customer`.
6. Use SQL to explore spending, product ratings, discounts, shipping, subscriptions, purchase-history bands, and age groups.
7. Use Power BI to communicate the findings visually.

## Setup

### 1. Create an environment and install packages

Python 3.10 or later is recommended.

```bash
python -m venv .venv
```

Activate it, then install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure PostgreSQL securely

Create a PostgreSQL database named `customer_behavior`, then set the environment variables below in your local terminal or IDE. Do not put real passwords in a notebook or commit them to Git.

| Variable | Default / purpose |
|---|---|
| `POSTGRES_USER` | Database user; defaults to `postgres` |
| `POSTGRES_PASSWORD` | Required password, supplied through the environment |
| `POSTGRES_DB` | Database name; defaults to `customer_behavior` |
| `POSTGRES_HOST` | Host; defaults to `localhost` |
| `POSTGRES_PORT` | Port; defaults to `5432` |

Copy `.env.example` to `.env` only if you use a local environment-file loader, and keep `.env` untracked. The notebook reads environment variables directly; it does not automatically load a `.env` file.

### 3. Run the notebook

Open `code.ipynb` in Jupyter, run the analysis cells in order, and run the PostgreSQL loading cell only after configuring the database environment variables.

### 4. Run SQL analysis

After the notebook creates the `customer` table, execute `customer-database.sql` in your PostgreSQL client. Run `sql/data_quality_checks.sql` to inspect key data-quality conditions.

## Interpretation and limitations

- The current dataset has customer attributes and purchase-related fields, but it does not provide a transaction timestamp, reliable order identifier, customer acquisition date, product cost, or exact discount amount.
- As a result, this project cannot establish monthly sales trends, customer retention/churn over time, customer lifetime value, profit margin, or the causal effect of discounts.
- A row count represents customer records in this dataset; it should not be presented as a universal order-count metric.
- Purchase-history bands are descriptive groups, not verified lifecycle labels such as “new,” “returning,” or “loyal.”
- Differences between groups are observational associations. They do not by themselves prove that subscription status, discounts, or shipping choices caused higher spending.
- Review-rating imputation should be documented, and any dashboard conclusions should be checked against the imputed values.

## Suggested next improvements

- Add screenshots of the Power BI report to this README.
- Add automated tests for the cleaning and validation steps.
- Record the dataset source, license, refresh date, and a data dictionary.
- Add validated, reproducible summary tables and a concise findings section with exact values from the final analysis.

## Security note

Never commit credentials. If a database password was previously committed to a public repository, rotate it immediately. Removing it from the current file does not erase it from earlier Git history; history cleanup may also be required.
