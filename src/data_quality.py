"""Data-quality checks for customer shopping datasets."""
from __future__ import annotations
import pandas as pd

ALIASES = {
    "customer_id": ["customer_id", "customer id", "customerid"],
    "age": ["age"],
    "purchase_amount": ["purchase_amount", "purchase amount (usd)", "purchase_amount_usd", "purchase amount"],
    "review_rating": ["review_rating", "review rating"],
    "previous_purchases": ["previous_purchases", "previous purchases"],
    "discount_applied": ["discount_applied", "discount applied"],
    "promo_code_used": ["promo_code_used", "promo code used"],
    "item_purchased": ["item_purchased", "item purchased"],
    "category": ["category"], "gender": ["gender"],
    "shipping_type": ["shipping_type", "shipping type"],
    "subscription_status": ["subscription_status", "subscription status"],
    "payment_method": ["payment_method", "payment method"],
    "purchase_frequency": ["purchase_frequency", "frequency of purchases", "purchase frequency"],
    "season": ["season"], "size": ["size"], "color": ["color"], "location": ["location"],
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized snake_case names and common aliases."""
    out = df.copy()
    out.columns = (pd.Index(out.columns).astype(str).str.strip().str.lower()
                   .str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_"))
    reverse = {}
    for canonical, names in ALIASES.items():
        for name in names:
            key = pd.Series([name]).str.replace(r"[^a-z0-9]+", "_", regex=True).iloc[0].strip("_")
            reverse[key] = canonical
    return out.rename(columns={c: reverse.get(c, c) for c in out.columns})

def run_quality_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Return a table of checks, counts, and pass/review status."""
    data = normalize_columns(df)
    checks = []
    def add(name: str, issue_count: int, detail: str) -> None:
        checks.append({"check": name, "issue_count": int(issue_count),
                       "status": "PASS" if issue_count == 0 else "REVIEW", "details": detail})
    add("Empty dataset", int(len(data) == 0), f"{len(data):,} rows")
    if "customer_id" in data:
        add("Missing customer IDs", data["customer_id"].isna().sum(), "Customer identifier should be present.")
        add("Duplicate customer IDs", data["customer_id"].duplicated(keep=False).sum(),
            "Counts rows participating in duplicated IDs.")
    else:
        add("Customer ID column", 1, "No recognized customer_id column was found.")
    for col in ["age", "purchase_amount", "review_rating", "previous_purchases", "item_purchased"]:
        if col not in data:
            add(f"Required field: {col}", 1, "Column was not found; check source schema.")
        else:
            add(f"Missing values: {col}", data[col].isna().sum(), "Missing values may need review.")
    for col in ["age", "purchase_amount", "review_rating", "previous_purchases"]:
        if col not in data:
            continue
        values = pd.to_numeric(data[col], errors="coerce")
        invalid = ((values.lt(1) | values.gt(5)).fillna(False) if col == "review_rating"
                   else values.lt(0).fillna(False))
        add(f"Invalid range: {col}", invalid.sum(),
            "Expected ratings from 1 to 5." if col == "review_rating" else "Expected non-negative values.")
    if {"discount_applied", "promo_code_used"}.issubset(data.columns):
        left = data["discount_applied"].astype("string").str.strip().str.casefold()
        right = data["promo_code_used"].astype("string").str.strip().str.casefold()
        mismatch = (left != right) & left.notna() & right.notna()
        add("Promotion field mismatches", mismatch.sum(),
            "Review before dropping either field; labels may have different meanings.")
    for col in ["gender", "category", "shipping_type", "subscription_status", "payment_method"]:
        if col in data:
            raw = data[col].dropna().astype(str)
            inconsistent = int(raw.str.strip().ne(raw).sum() + raw.str.lower().duplicated().sum())
            add(f"Category formatting: {col}", inconsistent,
                "Potential whitespace or case inconsistency; review before standardizing.")
    return pd.DataFrame(checks)
