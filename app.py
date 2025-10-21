import pandas as pd
import streamlit as st
import altair as alt

@st.cache_data
def load_data():
    # Load CSV file
    df = pd.read_csv("data/sales_data.csv")

    # --- Detect column names dynamically ---
    # Possible variations for key fields
    date_cols = ['Order Date', 'Date', 'Order_Date', 'OrderDate']
    ship_cols = ['Ship Date', 'Shipping Date', 'Ship_Date']
    sales_cols = ['Sales', 'Total', 'Revenue', 'Amount']

    # Detect existing columns
    order_date_col = next((col for col in date_cols if col in df.columns), None)
    ship_date_col = next((col for col in ship_cols if col in df.columns), None)
    sales_col = next((col for col in sales_cols if col in df.columns), None)

    # --- Handle missing columns gracefully ---
    missing = []
    if not order_date_col:
        missing.append("Order Date")
    if not sales_col:
        missing.append("Sales / Total / Revenue")

    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}. Please check your dataset.")
        st.stop()

    # --- Clean and standardize data ---
    df[order_date_col] = pd.to_datetime(df[order_date_col], errors='coerce')
    if ship_date_col:
        df[ship_date_col] = pd.to_datetime(df[ship_date_col], errors='coerce')

    df = df.dropna(subset=[order_date_col, sales_col])

    # Rename to standardized internal column names for easy use later
    df = df.rename(columns={
        order_date_col: "Order Date",
        sales_col: "Sales"
    })

    return df

st.set_page_config(page_title="Sales & Customer Insights Dashboard", layout="wide")

# Actually call the function so your data is available in memory
sales = load_data()

"""
# Quick sanity check — show a small preview
st.write("Preview of Sales Data:")
st.dataframe(sales.head())
"""

st.title("📊 Sales & Customer Insights Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

# Date filter
min_date = sales["Order Date"].min()
max_date = sales["Order Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Apply date filter
mask = (sales["Order Date"].dt.date >= date_range[0]) & (sales["Order Date"].dt.date <= date_range[1])
filtered = sales.loc[mask]

# Detect optional categorical columns (e.g., Region, Category)
region_col = next((col for col in ['Region', 'Market', 'Territory'] if col in sales.columns), None)
category_col = next((col for col in ['Category', 'Product Category', 'Segment'] if col in sales.columns), None)

if region_col:
    selected_region = st.sidebar.multiselect(
        "Select Region(s)", options=sales[region_col].unique(), default=sales[region_col].unique()
    )
    filtered = filtered[filtered[region_col].isin(selected_region)]

if category_col:
    selected_category = st.sidebar.multiselect(
        "Select Category", options=sales[category_col].unique(), default=sales[category_col].unique()
    )
    filtered = filtered[filtered[category_col].isin(selected_category)]

# KPIs
total_sales = filtered["Sales"].sum()
avg_sales = filtered["Sales"].mean()
num_orders = len(filtered)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📈 Average Order Value", f"${avg_sales:,.2f}")
col3.metric("🧾 Total Orders", f"{num_orders:,}")

st.markdown("---")

# --- Charts ---

# 1️⃣ Sales Over Time
sales_over_time = (
    filtered.groupby(filtered["Order Date"].dt.to_period("M"))["Sales"].sum().reset_index()
)
sales_over_time["Order Date"] = sales_over_time["Order Date"].dt.to_timestamp()

chart1 = (
    alt.Chart(sales_over_time)
    .mark_line(point=True)
    .encode(
        x="Order Date:T",
        y="Sales:Q",
        tooltip=["Order Date:T", "Sales:Q"]
    )
    .properties(title="Sales Over Time", height=400)
)

st.altair_chart(chart1, use_container_width=True)

# 2️⃣ Top 10 Products
product_col = next((col for col in ['Product Name', 'Item', 'SKU'] if col in sales.columns), None)

if product_col:
    top_products = (
        filtered.groupby(product_col)["Sales"].sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    chart2 = (
        alt.Chart(top_products)
        .mark_bar()
        .encode(
            x="Sales:Q",
            y=alt.Y(f"{product_col}:N", sort="-x"),
            tooltip=[product_col, "Sales:Q"]
        )
        .properties(title="Top 10 Products by Sales", height=400)
    )

    st.altair_chart(chart2, use_container_width=True)

# 3️⃣ Regional Sales Breakdown (if available)
if region_col:
    region_sales = (
        filtered.groupby(region_col)["Sales"].sum().reset_index()
    )

    chart3 = (
        alt.Chart(region_sales)
        .mark_arc(innerRadius=50)
        .encode(
            theta="Sales:Q",
            color=region_col,
            tooltip=[region_col, "Sales:Q"]
        )
        .properties(title="Sales by Region", height=400)
    )

    st.altair_chart(chart3, use_container_width=True)


