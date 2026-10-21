import pandas as pd
from src.analytics import answer_question, kmeans_segments, prepare_data, product_discovery

def sample_data():
    return pd.DataFrame({
        "Customer ID": [1, 2, 3, 4, 5, 6],
        "Age": [22, 25, 41, 52, 33, 60],
        "Purchase Amount (USD)": [20, 30, 50, 70, 40, 80],
        "Review Rating": [4.0, 4.5, 3.5, 5.0, 4.0, 4.2],
        "Previous Purchases": [1, 2, 5, 7, 3, 9],
        "Item Purchased": ["Hat", "Hat", "Coat", "Coat", "Shoes", "Shoes"],
        "Category": ["Accessories", "Accessories", "Clothing", "Clothing", "Footwear", "Footwear"],
        "Discount Applied": ["Yes", "No", "Yes", "No", "Yes", "No"],
        "Subscription Status": ["Yes", "No", "Yes", "No", "Yes", "No"],
        "Shipping Type": ["Express", "Standard", "Express", "Standard", "Express", "Standard"],
    })

def test_prepare_data_normalizes_columns():
    data = prepare_data(sample_data())
    assert "purchase_amount" in data.columns and "item_purchased" in data.columns

def test_question_router_returns_category_summary():
    message, result = answer_question(sample_data(), "Which categories have highest purchase amount?")
    assert "Category summaries" in message and result is not None
    assert "category" in result.columns

def test_question_router_does_not_execute_arbitrary_sql():
    message, result = answer_question(sample_data(), "DROP TABLE customer")
    assert result is None and "I can answer questions" in message

def test_kmeans_adds_segment_labels():
    result, score = kmeans_segments(sample_data(), 3)
    assert "segment" in result.columns and result["segment"].nunique() == 3

def test_product_discovery_has_popularity_order():
    result = product_discovery(sample_data())
    assert len(result) > 0
    assert result.iloc[0]["records"] >= result.iloc[-1]["records"]
