import pandas as pd
import streamlit as st
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Monthly Budget Dashboard", layout="wide")

st.title("📊 Monthly Budget & Tool Expense Dashboard")
st.markdown("Upload your Excel budget sheet to visualize expense and per-KM analysis interactively.")

# Upload Excel file
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file:
    # Read and clean data
    df = pd.read_excel(uploaded_file)

    # Clean numeric + duration
    df['Total Value'] = df['Total Value'].astype(str).str.replace(',', '').str.strip()
    df['Total Value'] = pd.to_numeric(df['Total Value'], errors='coerce')
    df['DURATION'] = df['DURATION'].str.upper().str.strip()

    df['Release Date Parsed'] = pd.to_datetime(df['Release Date'], errors='coerce', dayfirst=True)
    df['Delivery Date Parsed'] = pd.to_datetime(df['Delivery Date'], errors='coerce', dayfirst=True)
    df['Purchase Month'] = df['Release Date Parsed'].fillna(df['Delivery Date Parsed']).dt.to_period('M')
    df['Expense Month'] = df['Purchase Month'].astype(str)

    def allocate(row):
        if row['DURATION'] == 'MONTHLY':
            return row['Total Value']
        elif row['DURATION'] == 'YEARLY':
            return row['Total Value'] / 12
        else:
            return None

    df['Allocated Monthly Expense'] = df.apply(allocate, axis=1)
    df_cleaned = df.dropna(subset=['Allocated Monthly Expense'])

    all_months = sorted(df_cleaned['Expense Month'].unique())
    selected_months = st.multiselect("📅 Select Month(s) for Analysis", options=all_months)

    if selected_months:
        # Dynamic KM Inputs
        km_inputs = {}
        for month in selected_months:
            km_inputs[month] = st.number_input(f"🚌 Enter Bus KM for {month}", min_value=0.0, step=100.0)

        # Filter & Compute
        filtered_data = df_cleaned[df_cleaned['Expense Month'].isin(selected_months)].copy()
        filtered_totals = (
            filtered_data.groupby('Expense Month')['Allocated Monthly Expense']
            .sum()
            .rename('Total Monthly Expense')
            .reset_index()
        )

        filtered_totals['Bus KM'] = filtered_totals['Expense Month'].map(km_inputs)
        filtered_totals['Per KM Expense'] = filtered_totals.apply(
            lambda row: row['Total Monthly Expense'] / row['Bus KM'] if row['Bus KM'] else None,
            axis=1
        )

        st.subheader("📘 Summary Table")
        st.dataframe(filtered_totals.style.format({"Total Monthly Expense": "₹{:,.2f}", "Per KM Expense": "₹{:,.2f}"}))

        # Chart 1 – Bar: Total Expense
        st.subheader("💰 Monthly Expense")
        fig1 = px.bar(filtered_totals, x='Expense Month', y='Total Monthly Expense', text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2 – Line: Per-KM Expense
        st.subheader("🧮 Per-KM Expense")
        fig2 = px.line(filtered_totals, x='Expense Month', y='Per KM Expense', markers=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Table of tools
        st.subheader("🛠️ Tools Purchased in Selected Month(s)")
        tools_table = filtered_data[['Expense Month', 'Short Text', 'DURATION', 'Total Value', 'Allocated Monthly Expense']]
        st.dataframe(tools_table)

        # Download Visuals
        def fig_to_image(fig):
            buffer = BytesIO()
            fig.write_image(buffer, format="png")
            buffer.seek(0)
            return buffer

        st.markdown("### ⬇️ Download Visuals")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Download Expense Chart", fig_to_image(fig1), file_name="monthly_expense.png")
        with col2:
            st.download_button("📥 Download Per-KM Chart", fig_to_image(fig2), file_name="per_km_expense.png")

        # Export to Excel
        towrite = BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            filtered_totals.to_excel(writer, index=False, sheet_name='Summary')
            tools_table.to_excel(writer, index=False, sheet_name='Tools')
        towrite.seek(0)
        st.download_button("📥 Download Full Report (Excel)", data=towrite, file_name="budget_report.xlsx")
