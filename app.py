import streamlit as st
import pandas as pd

# Cache so it only loads once unless the file changes
@st.cache_data
def load_data():
    # Load CSV file
    df = pd.read_csv('data/sales_data.csv')

    # Convert 'Date' to datetime format
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

    # Drop any rows with missing required values (optional)
    df = df.dropna(subset=['Order ID', 'Order Date', 'Sales'])

    # Add a new column for month (helps with trend grouping later)
    df['Month'] = df['Order Date'].dt.to_period('M')

    return df

# Actually call the function so your data is available in memory
sales = load_data()

# Quick sanity check — show a small preview
st.write("Preview of Sales Data:")
st.dataframe(sales.head())
