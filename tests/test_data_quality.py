import pandas as pd
from src.data_quality import normalize_columns, run_quality_checks

def test_column_normalization():
    df = normalize_columns(pd.DataFrame({"Purchase Amount (USD)": [10], "Customer ID": [1]}))
    assert "purchase_amount" in df.columns and "customer_id" in df.columns

def test_quality_checks_flag_duplicate_ids_and_invalid_values():
    df = pd.DataFrame({"Customer ID": [1, 1], "Age": [25, 30],
        "Purchase Amount (USD)": [10, -3], "Review Rating": [4, 7],
        "Previous Purchases": [1, 2], "Item Purchased": ["Hat", "Coat"]})
    result = run_quality_checks(df).set_index("check")
    assert result.loc["Duplicate customer IDs", "issue_count"] == 2
    assert result.loc["Invalid range: purchase_amount", "issue_count"] == 1
    assert result.loc["Invalid range: review_rating", "issue_count"] == 1
