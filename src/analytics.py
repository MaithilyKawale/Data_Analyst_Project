"""Reusable analytics for the Customer Intelligence Platform."""
from __future__ import annotations
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from src.data_quality import normalize_columns

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    data = normalize_columns(df)
    for col in ["purchase_amount", "review_rating", "age", "previous_purchases"]:
        if col in data:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    if "age" in data and "age_group" not in data:
        bins = [0, 24, 34, 44, 54, float("inf")]
        labels = ["18-24", "25-34", "35-44", "45-54", "55+"]
        data["age_group"] = pd.cut(data["age"], bins=bins, labels=labels, include_lowest=True)
    return data

def kmeans_segments(df: pd.DataFrame, n_clusters: int = 3) -> tuple[pd.DataFrame, float | None]:
    data = prepare_data(df)
    candidates = ["age", "purchase_amount", "review_rating", "previous_purchases"]
    features = [c for c in candidates if c in data and data[c].notna().sum() > 1]
    if len(features) < 2:
        raise ValueError("At least two usable numeric features are required for segmentation.")
    matrix = data[features].fillna(data[features].median()).fillna(0)
    if len(matrix) < 3:
        raise ValueError("At least three rows are required for segmentation.")
    k = max(2, min(int(n_clusters), len(matrix) - 1))
    scaled = StandardScaler().fit_transform(matrix)
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(scaled)
    out = data.copy()
    out["segment"] = labels.astype(int)
    score = float(silhouette_score(scaled, labels)) if 1 < len(set(labels)) < len(labels) else None
    return out, score

def product_discovery(df: pd.DataFrame, category: str | None = None) -> pd.DataFrame:
    data = prepare_data(df)
    if "item_purchased" not in data:
        return pd.DataFrame(columns=["item_purchased", "records", "average_rating", "average_purchase_amount"])
    if category and category != "All" and "category" in data:
        data = data[data["category"].astype(str) == category]
    aggs = {"records": ("item_purchased", "size")}
    if "review_rating" in data:
        aggs["average_rating"] = ("review_rating", "mean")
    if "purchase_amount" in data:
        aggs["average_purchase_amount"] = ("purchase_amount", "mean")
    out = data.groupby("item_purchased", dropna=False).agg(**aggs).reset_index()
    for col in ["average_rating", "average_purchase_amount"]:
        if col not in out:
            out[col] = float("nan")
    return out.sort_values(["records", "average_rating"], ascending=False, na_position="last")

def answer_question(df: pd.DataFrame, question: str) -> tuple[str, pd.DataFrame | None]:
    """Map plain-English questions to approved local analyses; never execute arbitrary SQL."""
    data, q = prepare_data(df), question.casefold()
    if any(k in q for k in ["top product", "popular product", "best selling", "most popular"]):
        return "Products ranked by record count; records may not represent order-level sales.", product_discovery(data).head(10)
    if "rating" in q or "review" in q:
        if not {"item_purchased", "review_rating"}.issubset(data.columns):
            return "The data needs item_purchased and review_rating columns.", None
        result = data.groupby("item_purchased").agg(records=("review_rating", "count"), average_rating=("review_rating", "mean")).reset_index()
        return "Average product ratings with sample sizes; ratings may include imputed values.", result.sort_values("average_rating", ascending=False).head(10)
    if any(k in q for k in ["discount", "promo"]):
        if not {"discount_applied", "purchase_amount"}.issubset(data.columns):
            return "The data needs discount_applied and purchase_amount columns.", None
        result = data.groupby("discount_applied", dropna=False).agg(records=("purchase_amount", "size"), average_purchase_amount=("purchase_amount", "mean"), total_purchase_amount=("purchase_amount", "sum")).reset_index()
        return "Observed purchase amounts by discount flag. This comparison is not causal.", result
    if any(k in q for k in ["subscription", "subscriber"]):
        if not {"subscription_status", "purchase_amount"}.issubset(data.columns):
            return "The data needs subscription_status and purchase_amount columns.", None
        result = data.groupby("subscription_status", dropna=False).agg(records=("purchase_amount", "size"), average_purchase_amount=("purchase_amount", "mean"), total_purchase_amount=("purchase_amount", "sum")).reset_index()
        return "Observed purchase amounts by subscription status; this does not establish causation.", result
    if any(k in q for k in ["category", "categories"]):
        if not {"category", "purchase_amount"}.issubset(data.columns):
            return "The data needs category and purchase_amount columns.", None
        result = data.groupby("category", dropna=False).agg(records=("purchase_amount", "size"), total_purchase_amount=("purchase_amount", "sum"), average_purchase_amount=("purchase_amount", "mean")).reset_index().sort_values("total_purchase_amount", ascending=False)
        return "Category summaries based on records in the supplied dataset.", result
    if any(k in q for k in ["shipping", "delivery"]):
        if not {"shipping_type", "purchase_amount"}.issubset(data.columns):
            return "The data needs shipping_type and purchase_amount columns.", None
        result = data.groupby("shipping_type", dropna=False).agg(records=("purchase_amount", "size"), average_purchase_amount=("purchase_amount", "mean")).reset_index().sort_values("average_purchase_amount", ascending=False)
        return "Average purchase amount by shipping type; differences may reflect customer mix.", result
    if any(k in q for k in ["average", "mean", "spend", "purchase amount", "revenue", "total"]):
        if "purchase_amount" not in data:
            return "The data needs a purchase_amount column.", None
        result = pd.DataFrame([{"records": len(data), "total_purchase_amount": data["purchase_amount"].sum(), "average_purchase_amount": data["purchase_amount"].mean(), "median_purchase_amount": data["purchase_amount"].median()}])
        return "Overall purchase-amount summary. Total is a sum over dataset records, not verified transaction revenue.", result
    return ("I can answer questions about spending, categories, popular products, ratings, discounts, subscriptions, and shipping. Try: Which categories have the highest purchase amount?", None)

def deterministic_insights(df: pd.DataFrame) -> list[str]:
    data = prepare_data(df)
    insights = [f"The dataset contains {len(data):,} records."]
    if "purchase_amount" in data:
        values = data["purchase_amount"].dropna()
        if not values.empty:
            insights.append(f"Average purchase amount is {values.mean():.2f}; median is {values.median():.2f}.")
    if {"category", "purchase_amount"}.issubset(data.columns):
        grouped = data.groupby("category")["purchase_amount"].sum().sort_values(ascending=False)
        if not grouped.empty:
            insights.append(f"Highest total purchase-amount category by record sum: {grouped.index[0]} ({grouped.iloc[0]:.2f}).")
    if "review_rating" in data:
        rating = data["review_rating"].dropna()
        if not rating.empty:
            insights.append(f"Average available review rating is {rating.mean():.2f}; check whether missing values were imputed.")
    insights.append("These are descriptive associations, not causal claims; no dated trend is inferred.")
    return insights
