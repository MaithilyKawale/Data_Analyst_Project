"""Guardrails for forecasting readiness."""
import pandas as pd

def validate_forecasting_data(df: pd.DataFrame, date_column: str = "transaction_date") -> tuple[bool, str]:
    if date_column not in df.columns:
        return False, f"Forecasting is unavailable: '{date_column}' is missing. Add reliable transaction-level dates and an appropriate numeric target first."
    dates = pd.to_datetime(df[date_column], errors="coerce")
    if dates.notna().sum() < 3 or dates.nunique() < 3:
        return False, "Forecasting needs at least three distinct valid dates."
    if "purchase_amount" not in df.columns:
        return False, "Forecasting needs a numeric purchase_amount target or another clearly defined target."
    target = pd.to_numeric(df["purchase_amount"], errors="coerce")
    if (dates.notna() & target.notna()).sum() < 3:
        return False, "Forecasting needs at least three rows with both a valid date and target."
    return True, "Basic date/target readiness passed; validate frequency, coverage, and holdout performance before forecasting."
