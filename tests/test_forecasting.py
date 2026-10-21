import pandas as pd
from src.forecasting import validate_forecasting_data

def test_forecasting_is_blocked_without_dates():
    ready, message = validate_forecasting_data(pd.DataFrame({"purchase_amount": [1, 2, 3]}))
    assert not ready and "transaction_date" in message

def test_forecasting_requires_distinct_dates():
    ready, message = validate_forecasting_data(pd.DataFrame({
        "transaction_date": ["2025-01-01"] * 3, "purchase_amount": [10, 20, 30]}))
    assert not ready and "distinct valid dates" in message
