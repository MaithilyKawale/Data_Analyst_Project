"""Streamlit entry point for Customer Intelligence Platform."""
from pathlib import Path
import pandas as pd
import streamlit as st
from src.analytics import answer_question, deterministic_insights, kmeans_segments, prepare_data, product_discovery
from src.data_quality import run_quality_checks
from src.forecasting import validate_forecasting_data
from src.llm_insights import generate_insights

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "customer_shopping_behavior.csv"
st.set_page_config(page_title="Customer Intelligence Platform", page_icon="📊", layout="wide")
st.title("Customer Intelligence Platform")
st.caption("Customer shopping analytics · Python · SQL · Power BI · Optional AI")

@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes | None, path_string: str) -> pd.DataFrame:
    if file_bytes is not None:
        import io
        return pd.read_csv(io.BytesIO(file_bytes))
    return pd.read_csv(path_string)

uploaded = st.sidebar.file_uploader("Upload customer CSV (optional)", type=["csv"])
try:
    if uploaded is not None:
        raw = load_csv(uploaded.getvalue(), str(DEFAULT_CSV))
    elif DEFAULT_CSV.exists():
        raw = load_csv(None, str(DEFAULT_CSV))
    else:
        st.info("Upload a CSV to begin. The default file is customer_shopping_behavior.csv.")
        st.stop()
except Exception as exc:
    st.error(f"Could not read the CSV: {exc}")
    st.stop()

data = prepare_data(raw)
pages = ["Overview", "Data quality", "Customer segments", "Discount analysis", "Ask the data", "Product discovery", "Reports"]
page = st.sidebar.radio("Navigate", pages)

if page == "Overview":
    st.subheader("Executive overview")
    a, b, c, d = st.columns(4)
    a.metric("Records", f"{len(data):,}")
    if "purchase_amount" in data:
        b.metric("Total purchase amount*", f"{data['purchase_amount'].sum(skipna=True):,.2f}")
        c.metric("Average purchase amount", f"{data['purchase_amount'].mean():,.2f}")
    if "review_rating" in data:
        d.metric("Average rating", f"{data['review_rating'].mean():.2f}/5")
    st.caption("*Sum across dataset records; not necessarily transaction-level revenue.")
    if "category" in data:
        categories = ["All"] + sorted(data["category"].dropna().astype(str).unique().tolist())
        selected = st.selectbox("Category filter", categories)
        view = data if selected == "All" else data[data["category"].astype(str) == selected]
    else:
        view = data
    st.write(f"Showing {len(view):,} records.")
    if {"category", "purchase_amount"}.issubset(view.columns):
        st.bar_chart(view.groupby("category")["purchase_amount"].sum().sort_values(ascending=False))
    if "item_purchased" in view:
        st.subheader("Most frequent product records")
        st.dataframe(view["item_purchased"].value_counts().head(10).rename_axis("item").reset_index(name="records"), use_container_width=True)
    st.subheader("Computed insights")
    for insight in deterministic_insights(view):
        st.write("• " + insight)

elif page == "Data quality":
    st.subheader("Data-quality review")
    checks = run_quality_checks(data)
    st.dataframe(checks, use_container_width=True, hide_index=True)
    st.caption("REVIEW indicates a condition to inspect, not automatically a confirmed error.")
    st.download_button("Download quality checks", checks.to_csv(index=False).encode("utf-8"), "data_quality_checks.csv", "text/csv")

elif page == "Customer segments":
    st.subheader("Exploratory K-Means segmentation")
    k = st.slider("Number of segments", min_value=2, max_value=8, value=3)
    try:
        segmented, score = kmeans_segments(data, k)
        st.metric("Silhouette score", f"{score:.3f}" if score is not None else "Not available")
        st.caption("Clusters are exploratory groups based on available numeric fields. Validate stability and business usefulness before acting.")
        fields = {col: (col, "mean") for col in ["age", "purchase_amount", "review_rating", "previous_purchases"] if col in segmented}
        summary = segmented.groupby("segment").agg(records=("segment", "size"), **fields).reset_index()
        st.dataframe(summary, use_container_width=True)
        st.download_button("Download segmented records", segmented.to_csv(index=False).encode("utf-8"), "customer_segments.csv", "text/csv")
    except ValueError as exc:
        st.warning(str(exc))

elif page == "Discount analysis":
    st.subheader("Observed discount comparisons")
    if {"discount_applied", "purchase_amount"}.issubset(data.columns):
        summary = data.groupby("discount_applied", dropna=False).agg(records=("purchase_amount", "size"), average_purchase_amount=("purchase_amount", "mean"), median_purchase_amount=("purchase_amount", "median"), total_purchase_amount=("purchase_amount", "sum")).reset_index()
        st.dataframe(summary, use_container_width=True)
        st.bar_chart(summary.set_index("discount_applied")["average_purchase_amount"])
        st.warning("Observational data only: differences may reflect customer or product mix and do not establish that discounts caused higher spending.")
    else:
        st.info("Columns discount_applied and purchase_amount are required.")

elif page == "Ask the data":
    st.subheader("Ask a business question")
    st.write("Questions are routed to approved local analyses; arbitrary SQL is not generated or executed.")
    question = st.text_input("Example: Which categories have the highest purchase amount?")
    if st.button("Analyze question", type="primary") and question.strip():
        message, result = answer_question(data, question)
        st.info(message)
        if result is not None:
            st.dataframe(result, use_container_width=True)
            st.download_button("Download answer as CSV", result.to_csv(index=False).encode("utf-8"), "question_result.csv", "text/csv")

elif page == "Product discovery":
    st.subheader("Product popularity and rating baseline")
    categories = ["All"] + sorted(data["category"].dropna().astype(str).unique().tolist()) if "category" in data else ["All"]
    selected = st.selectbox("Category", categories)
    result = product_discovery(data, selected)
    st.dataframe(result.head(25), use_container_width=True)
    st.caption("Ranks products by record count and rating. It is not personalized because complete customer-item baskets are not available.")
    st.download_button("Download product summary", result.to_csv(index=False).encode("utf-8"), "product_discovery.csv", "text/csv")
    _, message = validate_forecasting_data(data)
    st.write("Forecast readiness:", message)

elif page == "Reports":
    st.subheader("Download an analysis snapshot")
    insights, mode = generate_insights(data)
    st.caption(mode)
    report = "# Customer Shopping Analysis Snapshot\n\n" + "\n".join("- " + line for line in insights)
    report += "\n\nCaveat: descriptive analysis only; no causal or dated-trend claims.\n"
    st.markdown(report)
    st.download_button("Download Markdown report", report.encode("utf-8"), "customer_analysis_report.md", "text/markdown")
    st.download_button("Download prepared data", data.to_csv(index=False).encode("utf-8"), "prepared_customer_data.csv", "text/csv")
