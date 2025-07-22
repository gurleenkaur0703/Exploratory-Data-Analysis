import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Christmas Sales EDA", layout="wide")
st.title("🎄 Christmas Sales Data Analysis Dashboard")
st.markdown("Analyze your Christmas sales data with interactive charts, filters, KPIs, and visualizations. "
            "Upload your own dataset or use the sample provided.")

# Upload or load default
uploaded_file = st.sidebar.file_uploader("📤 Upload your CSV file", type="csv")
default_file = "Christmas sales data analysis.csv"

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    file_used = uploaded_file.name
    st.sidebar.success("✅ Custom file loaded")
elif os.path.exists(default_file):
    df = pd.read_csv(default_file, encoding='latin1')
    file_used = default_file
    st.sidebar.info("✅ Sample dataset loaded")
else:
    st.warning("⚠️ No file uploaded or sample file found.")
    st.stop()

# Show which file is being used
st.sidebar.write(f"📁 Using file: `{file_used}`")

# Clean column names
df.columns = [col.strip() for col in df.columns]

# Preview dataset
with st.expander("📄 Preview Dataset"):
    st.dataframe(df.head())

# 🔍 Try to auto-detect the revenue column
revenue_col = None
for col in df.columns:
    if 'revenue' in col.lower() or 'sales' in col.lower():
        revenue_col = col
        break

# KPIs
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

# Sidebar filters
st.sidebar.header("🔍 Filters")

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    start_date = st.sidebar.date_input("Start Date", df["Date"].min())
    end_date = st.sidebar.date_input("End Date", df["Date"].max())
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# 📦 Sales by Category
if "Category" in df.columns and revenue_col:
    st.subheader("📦 Sales by Product Category")
    category_sales = df.groupby("Category")[revenue_col].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    category_sales.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_ylabel("Revenue")
    ax1.set_title("Revenue by Category")
    st.pyplot(fig1)

# 🌍 Sales by Region
if "Region" in df.columns and revenue_col:
    st.subheader("🌍 Sales Distribution by Region")
    region_sales = df.groupby("Region")[revenue_col].sum()
    fig2, ax2 = plt.subplots()
    ax2.pie(region_sales, labels=region_sales.index, autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

# 🧠 Correlation Heatmap
numeric_cols = df.select_dtypes(include=np.number)

if not numeric_cols.empty:
    st.subheader("🧠 Correlation Heatmap")
    selected_cols = st.multiselect(
        "Select numeric columns to include in heatmap:",
        numeric_cols.columns.tolist(),
        default=numeric_cols.columns.tolist()
    )
    if selected_cols:
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        sns.heatmap(df[selected_cols].corr(), annot=True, cmap="coolwarm", ax=ax3)
        st.pyplot(fig3)

# 📥 Download filtered/processed data
st.subheader("📥 Download Processed Data")
st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="processed_sales_data.csv",
    mime="text/csv"
)

# Footer
st.caption("Built with ❤️ using Streamlit | By Gurleen Kaur")
