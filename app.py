import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sqlite3

# --- Page Configuration ---
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Data Analysis")
st.markdown("Explore and analyze your sales data with filters, visualizations, and SQL queries.")

# --- Sidebar File Upload ---
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")
use_db = st.sidebar.checkbox("Use local SQLite database if no file uploaded", value=True)
default_file = "sales data analysis.csv"

conn = None
file_used = ""

# --- Load Data ---
if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    file_used = uploaded_file.name
    st.sidebar.success("File loaded successfully.")
    conn = sqlite3.connect(":memory:")
    df.to_sql("sales", conn, index=False, if_exists="replace")

elif use_db and os.path.exists("sales.db"):
    try:
        conn = sqlite3.connect("sales.db")
        df = pd.read_sql_query("SELECT * FROM sales", conn)
        file_used = "sales.db"
        st.sidebar.success("Loaded data from local SQLite database.")
        
        # Show available columns
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(sales)")
        columns = [row[1] for row in cursor.fetchall()]
        st.sidebar.markdown("Available Columns:")
        st.sidebar.write(columns)

    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        st.stop()

elif os.path.exists(default_file):
    df = pd.read_csv(default_file, encoding='latin1')
    file_used = default_file
    conn = sqlite3.connect(":memory:")
    df.to_sql("sales", conn, index=False, if_exists="replace")
    st.sidebar.info("Loaded sample data from default file.")

else:
    st.error("No data source found. Please upload a CSV or ensure a valid database file exists.")
    st.stop()

st.sidebar.write(f"Using: `{file_used}`")

# --- Data Cleaning ---
df.columns = [col.strip() for col in df.columns]

# --- Data Preview ---
with st.expander("Preview Data"):
    st.dataframe(df.head(10))

# --- SQL Query Tool ---
if conn is not None:
    st.subheader("🧮 SQL Query Tool")
    query_input = st.text_area("Write a SQL query (table name: `sales`)", value="SELECT * FROM sales LIMIT 5")

    if st.button("Run Query"):
        try:
            result = pd.read_sql_query(query_input, conn)
            st.success("Query executed successfully.")
            st.dataframe(result)
        except Exception as e:
            st.error(f"SQL Error: {e}")

# --- Detect Revenue Column ---
revenue_col = next((col for col in df.columns if 'revenue' in col.lower() or 'sales' in col.lower()), None)

# --- KPIs ---
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    if revenue_col:
        st.metric("Total Revenue", f"${df[revenue_col].sum():,.2f}")
    else:
        st.metric("Total Revenue", "Not Available")

with col2:
    st.metric("Total Orders", df.shape[0])

with col3:
    if revenue_col:
        st.metric("Average Order Value", f"${df[revenue_col].mean():,.2f}")
    else:
        st.metric("Average Order Value", "Not Available")

# --- Date Filtering ---
st.sidebar.header("Filters")

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    min_date, max_date = df["Date"].min(), df["Date"].max()
    start_date = st.sidebar.date_input("Start Date", min_value=min_date, value=min_date)
    end_date = st.sidebar.date_input("End Date", max_value=max_date, value=max_date)

    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# --- Sales by Category ---
if "Category" in df.columns and revenue_col:
    st.subheader("Sales by Product Category")
    category_sales = df.groupby("Category")[revenue_col].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    category_sales.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_ylabel("Revenue")
    ax1.set_title("Revenue by Category")
    st.pyplot(fig1)

# --- Region-wise Sales ---
if "Region" in df.columns and revenue_col:
    st.subheader("Sales Distribution by Region")
    region_sales = df.groupby("Region")[revenue_col].sum()
    fig2, ax2 = plt.subplots()
    ax2.pie(region_sales, labels=region_sales.index, autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

# --- Correlation Heatmap ---
numeric_cols = df.select_dtypes(include=np.number)

if not numeric_cols.empty and numeric_cols.shape[1] >= 2:
    st.subheader("Correlation Heatmap")
    selected_cols = st.multiselect(
        "Choose numeric columns to visualize correlations:",
        numeric_cols.columns.tolist(),
        default=numeric_cols.columns.tolist()
    )

    if len(selected_cols) >= 2:
        corr = df[selected_cols].corr()
        if not corr.isnull().all().all():
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax3)
            st.pyplot(fig3)
        else:
            st.warning("Correlation matrix could not be generated from the selected columns.")
    else:
        st.info("Please select at least two numeric columns.")

else:
    st.info("Not enough numeric data to create a correlation heatmap.")

# --- Data Download ---
st.subheader("Download Data")
st.download_button(
    label="Download Processed CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="processed_sales_data.csv",
    mime="text/csv"
)

# --- Footer ---
st.caption("Built with ❤️ using Streamlit | By Gurleen Kaur")
