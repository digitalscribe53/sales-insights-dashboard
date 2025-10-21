import pandas as pd
import streamlit as st

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


# Actually call the function so your data is available in memory
sales = load_data()

# Quick sanity check — show a small preview
st.write("Preview of Sales Data:")
st.dataframe(sales.head())
