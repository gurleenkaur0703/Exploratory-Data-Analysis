import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sqlite3

# --- Page setup ---
st.set_page_config(page_title="Christmas Sales EDA", layout="wide")
st.title("🎄 Christmas Sales Data Analysis Dashboard")
st.markdown("Analyze your Christmas sales data using interactive filters, visualizations, and SQL queries.")

# --- File loading logic ---
uploaded_file = st.sidebar.file_uploader("📤 Upload your CSV file", type="csv")
use_db = st.sidebar.checkbox("Use SQLite database if no file uploaded", value=True)
default_file = "Christmas sales data analysis.csv"

conn = None
file_used = ""

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    file_used = uploaded_file.name
    st.sidebar.success("✅ Custom CSV file loaded")

    # ✅ Create in-memory SQLite DB for querying
    conn = sqlite3.connect(":memory:")
    df.to_sql("sales", conn, index=False, if_exists="replace")

    # SQL query input
    default_query = "SELECT * FROM sales LIMIT 5"
    custom_query = st.sidebar.text_area("Write a custom SQL query", value=default_query)
    df = pd.read_sql_query(custom_query, conn)

elif use_db and os.path.exists("sales.db"):
    try:
        conn = sqlite3.connect("sales.db")
        default_query = "SELECT * FROM sales"
        custom_query = st.sidebar.text_area("Write a custom SQL query", value=default_query)
        df = pd.read_sql_query(custom_query, conn)
        file_used = "sales.db (SQLite)"
        st.sidebar.success("✅ Loaded from SQLite database")

        # ✅ Show table columns
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(sales)")
            columns = [row[1] for row in cursor.fetchall()]
            st.sidebar.markdown("### 📋 Available Columns")
            st.sidebar.write(columns)
        except Exception as e:
            st.sidebar.error(f"Could not fetch column info: {e}")

    except Exception as e:
        st.error(f"❌ Failed to read from database: {e}")
        st.stop()

elif os.path.exists(default_file):
    df = pd.read_csv(default_file, encoding='latin1')
    file_used = default_file
    st.sidebar.info("✅ Sample CSV file loaded")

else:
    st.error("⚠️ No data available. Upload a CSV, or ensure `sales.db` or sample file exists.")
    st.stop()

st.sidebar.write(f"📁 Using file: `{file_used}`")

# --- Preprocessing ---
df.columns = [col.strip() for col in df.columns]

# --- Preview ---
with st.expander("📄 Preview Dataset"):
    st.dataframe(df.head(10))  # Show first 10 records

# --- Detect revenue/sales column ---
revenue_col = None
for col in df.columns:
    if 'revenue' in col.lower() or 'sales' in col.lower():
        revenue_col = col
        break

# --- KPIs ---
st.subheader("📊 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

with col1:
    if revenue_col:
        total_sales = df[revenue_col].sum()
        st.metric("💰 Total Revenue", f"${total_sales:,.2f}")
    else:
        st.metric("💰 Total Revenue", "N/A")

with col2:
    total_orders = df.shape[0]
    st.metric("📦 Total Orders", total_orders)

with col3:
    if revenue_col:
        avg_value = df[revenue_col].mean()
        st.metric("💳 Avg Order Value", f"${avg_value:,.2f}")
    else:
        st.metric("💳 Avg Order Value", "N/A")

# --- Filters ---
st.sidebar.header("🔍 Filters")

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    start_date = st.sidebar.date_input("Start Date", df["Date"].min())
    end_date = st.sidebar.date_input("End Date", df["Date"].max())
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# --- Category Analysis ---
if "Category" in df.columns and revenue_col:
    st.subheader("📦 Sales by Product Category")
    category_sales = df.groupby("Category")[revenue_col].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    category_sales.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_ylabel("Revenue")
    ax1.set_title("Revenue by Category")
    st.pyplot(fig1)

# --- Region Analysis ---
if "Region" in df.columns and revenue_col:
    st.subheader("🌍 Sales Distribution by Region")
    region_sales = df.groupby("Region")[revenue_col].sum()
    fig2, ax2 = plt.subplots()
    ax2.pie(region_sales, labels=region_sales.index, autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

# --- Correlation Heatmap ---
numeric_cols = df.select_dtypes(include=np.number)

if not numeric_cols.empty and numeric_cols.shape[1] >= 2:
    st.subheader("🧠 Correlation Heatmap")
    selected_cols = st.multiselect(
        "Select numeric columns to include in heatmap:",
        numeric_cols.columns.tolist(),
        default=numeric_cols.columns.tolist()
    )

    if selected_cols and len(selected_cols) >= 2:
        corr_matrix = df[selected_cols].corr()
        if corr_matrix.isnull().all().all():
            st.warning("⚠️ Correlation matrix is empty or invalid. Please check your column selection.")
        else:
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax3)
            st.pyplot(fig3)
    else:
        st.info("ℹ️ Select at least two numeric columns to generate a heatmap.")
else:
    st.info("ℹ️ Not enough numeric data to generate a correlation heatmap.")
    if uploaded_file:
        st.info("📌 Tip: For meaningful correlations, upload a CSV with multiple numeric columns like revenue, age, discount, etc.")

# --- Download ---
st.subheader("📥 Download Processed Data")
st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="processed_sales_data.csv",
    mime="text/csv"
)

# --- Footer ---
st.caption("Built with ❤️ using Streamlit | By Gurleen Kaur")
