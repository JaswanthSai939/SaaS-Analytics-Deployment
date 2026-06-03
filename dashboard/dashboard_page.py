import os
import sys

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT  = os.path.dirname(DASHBOARD_DIR)
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import plotly.express as px
import streamlit as st

from auth.session_manager import logout
from src.filter_data import load_filtered_data
from src.forecasting import sales_forecast
from src.customer_analysis import customer_metrics
from src.geographic_analysis import sales_by_country, sales_by_city
from src.product_analysis import (
    top_products,
    bottom_products,
    product_profit,
    product_discount
)

# Fix OpenBLAS memory issue
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"]      = "1"
os.environ["MKL_NUM_THREADS"]      = "1"

# Hide sidebar
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

# Guard: redirect to login if not authenticated
if not st.session_state.get("logged_in"):
    st.switch_page(os.path.join(DASHBOARD_DIR, "login_page.py"))

# ==========================
# TOP BAR  —  user info + logout
# ==========================

top_left, top_right = st.columns([4, 1])

with top_left:
    st.title("SaaS Business Analytics & Prediction Platform")
    st.write(f"Hello, **{st.session_state.user_name}** ({st.session_state.user_email})")

with top_right:
    if "user_picture" in st.session_state:
        st.image(st.session_state.user_picture, width=60)
    if st.button("🔍 Insights", width="stretch"):
        st.switch_page(os.path.join(DASHBOARD_DIR, "insights_page.py"))
    if st.button("Logout", width="stretch"):
        logout()
        st.rerun()

st.markdown("---")

# ==========================
# INLINE FILTERS
# ==========================

st.subheader("Filters")

f_col1, f_col2, f_col3 = st.columns([2, 2, 1])

with f_col1:
    region = st.selectbox(
        "Select Region",
        ["All", "AMER", "APJ", "EMEA"]
    )

with f_col2:
    segment = st.selectbox(
        "Select Segment",
        ["All", "Enterprise", "SMB", "Strategic"]
    )

filtered_df = load_filtered_data(region, segment).copy()
filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"])

with f_col3:
    st.markdown("<br>", unsafe_allow_html=True)
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇ Download Report",
        data=csv,
        file_name="saas_report.csv",
        mime="text/csv",
        width="stretch"
    )

st.markdown("---")

# ======================
# KPI METRICS
# ======================

st.subheader("Dashboard Home")

try:
    sales     = filtered_df["Sales"].sum()
    profit    = filtered_df["Profit"].sum()
    orders    = len(filtered_df)
    customers = filtered_df["Customer ID"].nunique()
except Exception as e:
    st.error(f"Dashboard Error: {e}")
    sales = profit = orders = customers = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sales",     f"${sales:,.2f}")
with col2:
    st.metric("Total Profit",    f"${profit:,.2f}")
with col3:
    st.metric("Total Orders",    f"{orders:,}")
with col4:
    st.metric("Total Customers", f"{customers:,}")

# ======================
# CUSTOMER ANALYTICS
# ======================

st.markdown("---")
st.subheader("Customer Analytics")

total_cust, repeat_cust, retention = customer_metrics(filtered_df)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Customers",        total_cust)
with c2:
    st.metric("Repeat Customers", repeat_cust)
with c3:
    st.metric("Retention Rate",   f"{retention:.2f}%")

customer_sales = (
    filtered_df.groupby("Customer")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(customer_sales)

# ======================
# SALES FORECAST
# ======================

st.markdown("---")
st.subheader("Sales Forecast")

forecast = sales_forecast()
predicted_sales = round(forecast["yhat"].iloc[-1], 2)

st.metric("Predicted Future Sales", f"${predicted_sales:,.2f}")

forecast_chart = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].set_index("ds")
st.line_chart(forecast_chart)

# ======================
# MONTHLY SALES TREND
# ======================

st.markdown("---")
st.subheader("Monthly Sales Trend")

sales_df = (
    filtered_df
    .set_index("Order Date")
    .resample("ME")["Sales"]
    .sum()
    .reset_index()
)

st.line_chart(sales_df.set_index("Order Date")["Sales"])

# ======================
# PROFIT TREND
# ======================

st.markdown("---")
st.subheader("Profit Trend")

profit_df = (
    filtered_df
    .set_index("Order Date")
    .resample("ME")["Profit"]
    .sum()
    .reset_index()
)

st.line_chart(profit_df.set_index("Order Date")["Profit"])

# ======================
# SALES BY SEGMENT
# ======================

st.markdown("---")
st.subheader("Sales By Segment")

segment_df = (
    filtered_df.groupby("Segment")["Sales"]
    .sum()
    .reset_index()
)

st.bar_chart(segment_df.set_index("Segment")["Sales"])

# ======================
# REGIONAL SALES
# ======================

st.markdown("---")
st.subheader("Regional Sales")

region_df = (
    filtered_df.groupby("Region")["Sales"]
    .sum()
    .reset_index()
)

st.bar_chart(region_df.set_index("Region")["Sales"])

# ======================
# GEOGRAPHIC ANALYTICS
# ======================

st.markdown("---")
st.subheader("Geographic Analytics")

country_df = sales_by_country()

country_codes = {
    "United States": "USA", "Canada": "CAN", "United Kingdom": "GBR",
    "Germany": "DEU", "France": "FRA", "India": "IND",
    "Australia": "AUS", "Japan": "JPN", "Brazil": "BRA"
}

country_df["ISO"] = country_df["Country"].map(country_codes)

fig = px.choropleth(
    country_df,
    locations="ISO",
    locationmode="ISO-3",
    color="Sales",
    hover_name="Country"
)

st.plotly_chart(fig, width="stretch")

city_df = sales_by_city()
st.subheader("Top Cities")
st.dataframe(city_df, width="stretch")

# ======================
# PRODUCT ANALYTICS
# ======================

st.markdown("---")
st.header("Product Analytics")

st.subheader("Top Selling Products")
st.bar_chart(top_products().set_index("Product")["Sales"])

st.subheader("Lowest Selling Products")
st.bar_chart(bottom_products().set_index("Product")["Sales"])

st.subheader("Most Profitable Products")
st.bar_chart(product_profit().set_index("Product")["Profit"])

st.subheader("Most Discounted Products")
st.bar_chart(product_discount().set_index("Product")["Discount"])

# ======================
# TOP 10 PRODUCTS
# ======================

st.markdown("---")
st.subheader("Top 10 Products")

product_df = (
    filtered_df.groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

st.bar_chart(product_df.set_index("Product")["Sales"])

# ======================
# TOP 10 CUSTOMERS
# ======================

st.markdown("---")
st.subheader("Top 10 Customers")

customer_df = (
    filtered_df.groupby("Customer")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

st.dataframe(customer_df, width="stretch")

# ======================
# DISCOUNT ANALYTICS
# ======================

st.markdown("---")
st.header("Discount Analytics")

avg_discount = round(filtered_df["Discount"].mean() * 100, 2)
correlation  = round(filtered_df["Discount"].corr(filtered_df["Profit"]), 4)

col1, col2 = st.columns(2)

with col1:
    st.metric("Average Discount",            f"{avg_discount}%")
with col2:
    st.metric("Discount-Profit Correlation", f"{correlation}")

st.subheader("Discount Distribution")

fig = px.histogram(filtered_df, x="Discount", nbins=20, title="Discount Distribution")
st.plotly_chart(fig, width="stretch")

st.subheader("Discount vs Profit Correlation")

fig = px.scatter(filtered_df, x="Discount", y="Profit", title="Discount vs Profit")
st.plotly_chart(fig, width="stretch")

st.subheader("High Discount Risk Products")

risk_df = (
    filtered_df.groupby("Product")
    .agg({"Discount": "mean", "Profit": "sum", "Sales": "sum"})
    .reset_index()
    .sort_values(by="Discount", ascending=False)
    .head(10)
)

st.dataframe(risk_df, width="stretch")

st.subheader("Top Discounted Products")

fig = px.bar(risk_df, x="Product", y="Discount", title="Products Receiving Highest Discounts")
st.plotly_chart(fig, width="stretch")

# ======================
# EXECUTIVE INSIGHTS
# ======================

st.markdown("---")
st.header("Executive Insights & Recommendations")

region_sales      = filtered_df.groupby("Region")["Sales"].sum()
best_region       = region_sales.idxmax()
best_region_sales = region_sales.max()
st.success(f"🏆 Best Performing Region: {best_region} (${best_region_sales:,.2f})")

product_profit_df   = filtered_df.groupby("Product")["Profit"].sum()
best_product        = product_profit_df.idxmax()
best_product_profit = product_profit_df.max()
st.success(f"💰 Most Profitable Product: {best_product} (${best_product_profit:,.2f})")

monthly_sales_exec   = filtered_df.set_index("Order Date").resample("ME")["Sales"].sum()
growth               = monthly_sales_exec.pct_change()
highest_growth_month = growth.idxmax()
highest_growth_value = growth.max() * 100
st.success(f"📈 Highest Growth Month: {highest_growth_month.strftime('%B %Y')} ({highest_growth_value:.2f}%)")

risk_products_exec = (
    filtered_df.groupby("Product")
    .agg({"Discount": "mean", "Profit": "sum"})
    .reset_index()
)

risk_products_exec = risk_products_exec[
    (risk_products_exec["Discount"] > 0.20) &
    (risk_products_exec["Profit"] < 1000)
]

st.subheader("Risk Products")
st.dataframe(risk_products_exec, width="stretch")

st.subheader("Business Recommendations")

recommendations = []

if correlation < 0:
    recommendations.append("High discounts are reducing profitability. Consider discount optimization.")

if avg_discount > 20:
    recommendations.append("Average discount exceeds 20%. Review discount policies.")

if retention < 70:
    recommendations.append("Customer retention is low. Focus on loyalty programs.")

if len(risk_products_exec) > 0:
    recommendations.append("Review pricing strategy for high-risk products.")

if best_region == "EMEA":
    recommendations.append("EMEA is the strongest market. Increase marketing investment.")

if best_product:
    recommendations.append(f"Promote {best_product} aggressively because it generates the highest profit.")

if not recommendations:
    recommendations.append("Business performance is healthy.")

for rec in recommendations:
    st.info(rec)

# ======================
# NAVIGATE TO INSIGHTS
# ======================

st.markdown("---")
st.markdown("### Want deeper intelligence?")
st.write("Upload your SaaS CSV or use the sample dataset to get AI-powered insights on churn, revenue, and customer retention.")

if st.button("🔍 Go to AI Insights →", type="primary"):
    st.switch_page(os.path.join(DASHBOARD_DIR, "insights_page.py"))