"""Customer Intelligence Platform — multi-page Power BI-style analytics and AI chat."""
from pathlib import Path
import io
import pandas as pd
import streamlit as st
import plotly.express as px

from src.analytics import deterministic_insights, kmeans_segments, prepare_data, product_discovery
from src.chatbot import answer_chat
from src.data_quality import run_quality_checks
from src.forecasting import validate_forecasting_data
from src.llm_insights import generate_insights

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "customer_shopping_behavior.csv"
st.set_page_config(page_title="Customer Intelligence | Analytics", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

# Consistent, simpler visual hierarchy.
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2.5rem; max-width: 1500px;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.22);}
[data-testid="stMetric"] {background: rgba(128,128,128,.07); border: 1px solid rgba(128,128,128,.18); padding: 14px 16px; border-radius: 12px;}
.hero {padding: 1.25rem 1.5rem; border-radius: 16px; border: 1px solid rgba(128,128,128,.22); margin-bottom: 1rem;}
.small-note {font-size: .88rem; opacity: .8;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes | None, path_string: str) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes)) if file_bytes is not None else pd.read_csv(path_string)

with st.sidebar:
    st.markdown("## 📊 Customer Intelligence")
    st.caption("Shopping behaviour · BI dashboards")
    uploaded = st.file_uploader("Use another CSV", type=["csv"], help="Optional. Leave empty to use the project dataset.")
    st.divider()
    pages = {
        "🏠 Executive Overview": "overview",
        "👥 Customer Demographics": "customers",
        "🛍️ Product & Category": "products",
        "💳 Purchase & Promotions": "purchases",
        "🚚 Shipping & Payments": "operations",
        "🧩 Customer Segments": "segments",
        "🤖 AI Chatbot": "chat",
        "🧹 Data Quality": "quality",
        "📄 Reports & Downloads": "reports",
    }
    page_label = st.radio("MENU", list(pages), label_visibility="visible")
    page = pages[page_label]
    st.divider()
    st.caption("Use the menu to open a focused dashboard page.")

try:
    if uploaded is not None:
        raw = load_csv(uploaded.getvalue(), str(DEFAULT_CSV))
    elif DEFAULT_CSV.exists():
        raw = load_csv(None, str(DEFAULT_CSV))
    else:
        st.info("Upload a CSV file from the sidebar to get started.")
        st.stop()
    data = prepare_data(raw)
except Exception as exc:
    st.error(f"Unable to load the dataset: {exc}")
    st.stop()

def has(*cols):
    return set(cols).issubset(data.columns)

def chart_bar(frame, x, y, title, horizontal=False):
    if frame.empty or x not in frame or y not in frame:
        st.info(f"Not enough data to draw **{title}**.")
        return
    fig = px.bar(frame, x=y if horizontal else x, y=x if horizontal else y,
                 orientation="h" if horizontal else "v", title=title, template="plotly_white")
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=360)
    st.plotly_chart(fig, use_container_width=True)

def grouped(column, metric="count"):
    if column not in data:
        return pd.DataFrame()
    if metric == "count":
        return data[column].fillna("Missing").astype(str).value_counts().rename_axis(column).reset_index(name="records")
    if metric == "mean" and "purchase_amount" in data:
        return data.groupby(column, dropna=False)["purchase_amount"].mean().reset_index(name="average_purchase_amount").sort_values("average_purchase_amount", ascending=False)
    if metric == "sum" and "purchase_amount" in data:
        return data.groupby(column, dropna=False)["purchase_amount"].sum().reset_index(name="purchase_amount_sum").sort_values("purchase_amount_sum", ascending=False)
    return pd.DataFrame()

def show_kpis():
    cols = st.columns(4)
    cols[0].metric("Dataset records", f"{len(data):,}")
    if "purchase_amount" in data:
        cols[1].metric("Average purchase amount", f"{data['purchase_amount'].mean():,.2f}")
        cols[2].metric("Purchase amount sum*", f"{data['purchase_amount'].sum():,.2f}")
    if "review_rating" in data:
        cols[3].metric("Average review rating", f"{data['review_rating'].mean():.2f} / 5")
    st.caption("*Sum of the values in dataset rows; not verified transaction revenue.")

if page == "overview":
    st.markdown('<div class="hero"><h1>Executive Overview</h1><p>One place to understand the key patterns in your customer-shopping dataset.</p></div>', unsafe_allow_html=True)
    show_kpis()
    left, right = st.columns(2)
    with left:
        if has("category", "purchase_amount"):
            chart_bar(grouped("category", "sum"), "category", "purchase_amount_sum", "Purchase amount by category", True)
        if "season" in data:
            chart_bar(grouped("season"), "season", "records", "Records by season")
    with right:
        if "item_purchased" in data:
            chart_bar(grouped("item_purchased").head(10), "item_purchased", "records", "Top 10 products by record count", True)
        if "review_rating" in data:
            rating = data["review_rating"].dropna().round(0).astype(int).value_counts().sort_index().rename_axis("rating").reset_index(name="records")
            chart_bar(rating, "rating", "records", "Review rating distribution")
    st.subheader("Key findings")
    for item in deterministic_insights(data):
        st.write("• " + item)

elif page == "customers":
    st.title("Customer Demographics")
    st.caption("Explore the customer mix and how observed purchasing varies across available groups.")
    show_kpis()
    a, b = st.columns(2)
    with a:
        for col, title in [("age_group", "Records by age group"), ("gender", "Records by gender")]:
            if col in data: chart_bar(grouped(col), col, "records", title)
    with b:
        for col, title in [("subscription_status", "Subscription status"), ("frequency_of_purchases", "Purchase frequency")]:
            if col in data: chart_bar(grouped(col), col, "records", title, True)
    if has("age_group", "purchase_amount"):
        st.subheader("Average purchase amount by age group")
        chart_bar(grouped("age_group", "mean"), "age_group", "average_purchase_amount", "Average purchase amount by age group")

elif page == "products":
    st.title("Product & Category Dashboard")
    st.caption("Popularity, category mix, and available review ratings.")
    show_kpis()
    if "category" in data:
        opts = ["All"] + sorted(data["category"].dropna().astype(str).unique().tolist())
        selected = st.selectbox("Filter category", opts)
    else:
        selected = "All"
    result = product_discovery(data, selected)
    a, b = st.columns(2)
    with a:
        if not result.empty: chart_bar(result.head(12), "item_purchased", "records", "Top products by record count", True)
    with b:
        if not result.empty and "average_rating" in result:
            rated = result.dropna(subset=["average_rating"]).head(12)
            chart_bar(rated, "item_purchased", "average_rating", "Average product rating", True)
    if has("category", "purchase_amount"):
        chart_bar(grouped("category", "sum"), "category", "purchase_amount_sum", "Purchase amount sum by category", True)
    st.dataframe(result, use_container_width=True, hide_index=True)
    st.download_button("Download product analysis CSV", result.to_csv(index=False).encode("utf-8"), "product_analysis.csv", "text/csv")

elif page == "purchases":
    st.title("Purchase & Promotions Dashboard")
    st.caption("Compare observed purchase amounts; these comparisons do not establish cause and effect.")
    show_kpis()
    a, b = st.columns(2)
    with a:
        if "season" in data: chart_bar(grouped("season", "mean"), "season", "average_purchase_amount", "Average purchase amount by season")
        if "discount_applied" in data: chart_bar(grouped("discount_applied"), "discount_applied", "records", "Records by discount flag")
    with b:
        if "discount_applied" in data: chart_bar(grouped("discount_applied", "mean"), "discount_applied", "average_purchase_amount", "Average purchase amount by discount flag")
        if "payment_method" in data: chart_bar(grouped("payment_method"), "payment_method", "records", "Payment method mix", True)
    if has("category", "discount_applied", "purchase_amount"):
        st.subheader("Category × discount summary")
        summary = data.groupby(["category", "discount_applied"], dropna=False).agg(records=("purchase_amount", "size"), average_purchase_amount=("purchase_amount", "mean")).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)
    st.warning("The dataset is observational. It does not establish that discounts caused higher spending or increased profit.")

elif page == "operations":
    st.title("Shipping & Payments Dashboard")
    st.caption("Understand delivery options, payment preferences, and their observed purchase amounts.")
    show_kpis()
    a, b = st.columns(2)
    with a:
        if "shipping_type" in data: chart_bar(grouped("shipping_type"), "shipping_type", "records", "Shipping option mix", True)
        if "payment_method" in data: chart_bar(grouped("payment_method"), "payment_method", "records", "Payment method mix", True)
    with b:
        if "shipping_type" in data: chart_bar(grouped("shipping_type", "mean"), "shipping_type", "average_purchase_amount", "Average purchase amount by shipping")
        if "location" in data: chart_bar(grouped("location").head(12), "location", "records", "Top 12 locations by record count", True)
    if has("shipping_type", "payment_method"):
        st.subheader("Shipping × payment method")
        st.dataframe(pd.crosstab(data["shipping_type"], data["payment_method"]), use_container_width=True)

elif page == "segments":
    st.title("Customer Segmentation Dashboard")
    st.caption("Exploratory groups built from the available numeric attributes; not validated customer personas.")
    k = st.slider("Number of segments", 2, 8, 3)
    try:
        segmented, score = kmeans_segments(data, k)
        if score is not None: st.metric("Silhouette score", f"{score:.3f}")
        summary_cols = [c for c in ["age", "purchase_amount", "review_rating", "previous_purchases"] if c in segmented]
        agg = {"records": ("segment", "size")}
        agg.update({c: (c, "mean") for c in summary_cols})
        summary = segmented.groupby("segment").agg(**agg).reset_index()
        a, b = st.columns(2)
        with a: chart_bar(summary, "segment", "records", "Records per segment")
        with b:
            if "purchase_amount" in summary: chart_bar(summary, "segment", "purchase_amount", "Average purchase amount by segment")
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.download_button("Download segmented records", segmented.to_csv(index=False).encode("utf-8"), "customer_segments.csv", "text/csv")
    except ValueError as exc:
        st.warning(str(exc))

elif page == "chat":
    st.title("AI Chatbot")
    st.caption("Ask general questions or ask about this dataset. With an API key, the assistant can answer broad questions; dataset answers are grounded in available data summaries.")
    with st.expander("Example questions", expanded=False):
        st.markdown("- Explain this dataset in simple words.\n- Which categories have the highest purchase amounts?\n- What are the limitations of this analysis?\n- Explain customer segmentation.\n- Help me write a Python function.\n- What is the difference between revenue and profit?")
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask me anything…")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        history = st.session_state.chat_messages[:-1]
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                answer, mode = answer_chat(data, prompt, history)
            st.markdown(answer)
            st.caption(mode)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    if st.session_state.chat_messages and st.button("Clear conversation"):
        st.session_state.chat_messages = []
        st.rerun()

elif page == "quality":
    st.title("Data Quality Dashboard")
    checks = run_quality_checks(data)
    a, b, c = st.columns(3)
    a.metric("Rows", f"{len(data):,}")
    b.metric("Columns", f"{len(data.columns):,}")
    c.metric("Missing cells", f"{int(data.isna().sum().sum()):,}")
    left, right = st.columns(2)
    with left: chart_bar(data.isna().sum().rename_axis("column").reset_index(name="missing_cells").sort_values("missing_cells", ascending=False).head(15), "column", "missing_cells", "Missing values by column", True)
    with right:
        dup = pd.DataFrame({"record_type": ["Unique rows", "Duplicate rows"], "records": [int((~data.duplicated()).sum()), int(data.duplicated().sum())]})
        chart_bar(dup, "record_type", "records", "Duplicate-row check")
    st.dataframe(checks, use_container_width=True, hide_index=True)
    st.download_button("Download quality checks", checks.to_csv(index=False).encode("utf-8"), "data_quality_checks.csv", "text/csv")

elif page == "reports":
    st.title("Reports & Downloads")
    st.caption("Export the current dataset and reusable analysis snapshots.")
    insights, mode = generate_insights(data)
    st.info(mode)
    st.subheader("Executive summary")
    for item in insights: st.write("• " + item)
    report = "# Customer Shopping Analysis\n\n" + "\n".join("- " + str(item) for item in insights)
    report += "\n\n## Limitations\n- Descriptive analysis only; observational comparisons are not causal.\n- The dataset does not support dated trends, verified profit, or order-level metrics.\n"
    a, b = st.columns(2)
    with a: st.download_button("Download Markdown report", report.encode("utf-8"), "customer_analysis_report.md", "text/markdown")
    with b: st.download_button("Download prepared data", data.to_csv(index=False).encode("utf-8"), "prepared_customer_data.csv", "text/csv")
    st.subheader("Forecast readiness")
    ready, message = validate_forecasting_data(data)
    st.write(message)
    if not ready: st.caption("A dated transaction history is needed before time-series forecasting can be performed responsibly.")
