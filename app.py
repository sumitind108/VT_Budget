# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from io import BytesIO

# st.set_page_config(page_title="Monthly Budget Dashboard", layout="wide")

# st.title("📊 Monthly Budget & Tool Expense Dashboard")
# st.markdown("Upload your Excel budget sheet to visualize expense and per-KM analysis interactively.")

# # Upload Excel file
# uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

# if uploaded_file:
#     # Read and clean data
#     df = pd.read_excel(uploaded_file)

#     # Clean numeric + duration
#     df['Total Value'] = df['Total Value'].astype(str).str.replace(',', '').str.strip()
#     df['Total Value'] = pd.to_numeric(df['Total Value'], errors='coerce')
#     df['DURATION'] = df['DURATION'].str.upper().str.strip()

#     df['Release Date Parsed'] = pd.to_datetime(df['Release Date'], errors='coerce', dayfirst=True)
#     df['Delivery Date Parsed'] = pd.to_datetime(df['Delivery Date'], errors='coerce', dayfirst=True)
#     df['Purchase Month'] = df['Release Date Parsed'].fillna(df['Delivery Date Parsed']).dt.to_period('M')
#     df['Expense Month'] = df['Purchase Month'].astype(str)

#     def allocate(row):
#         if row['DURATION'] == 'MONTHLY':
#             return row['Total Value']
#         elif row['DURATION'] == 'YEARLY':
#             return row['Total Value'] / 12
#         else:
#             return None

#     df['Allocated Monthly Expense'] = df.apply(allocate, axis=1)
#     df_cleaned = df.dropna(subset=['Allocated Monthly Expense'])

#     all_months = sorted(df_cleaned['Expense Month'].unique())
#     selected_months = st.multiselect("📅 Select Month(s) for Analysis", options=all_months)

#     if selected_months:
#         # Dynamic KM Inputs
#         km_inputs = {}
#         for month in selected_months:
#             km_inputs[month] = st.number_input(f"🚌 Enter Bus KM for {month}", min_value=0.0, step=100.0)

#         # Filter & Compute
#         filtered_data = df_cleaned[df_cleaned['Expense Month'].isin(selected_months)].copy()
#         filtered_totals = (
#             filtered_data.groupby('Expense Month')['Allocated Monthly Expense']
#             .sum()
#             .rename('Total Monthly Expense')
#             .reset_index()
#         )

#         filtered_totals['Bus KM'] = filtered_totals['Expense Month'].map(km_inputs)
#         filtered_totals['Per KM Expense'] = filtered_totals.apply(
#             lambda row: row['Total Monthly Expense'] / row['Bus KM'] if row['Bus KM'] else None,
#             axis=1
#         )

#         st.subheader("📘 Summary Table")
#         st.dataframe(filtered_totals.style.format({"Total Monthly Expense": "₹{:,.2f}", "Per KM Expense": "₹{:,.2f}"}))

#         # Chart 1 – Bar: Total Expense
#         st.subheader("💰 Monthly Expense")
#         fig1 = px.bar(filtered_totals, x='Expense Month', y='Total Monthly Expense', text_auto=True)
#         st.plotly_chart(fig1, use_container_width=True)

#         # Chart 2 – Line: Per-KM Expense
#         st.subheader("🧮 Per-KM Expense")
#         fig2 = px.line(filtered_totals, x='Expense Month', y='Per KM Expense', markers=True)
#         st.plotly_chart(fig2, use_container_width=True)

#         # Table of tools
#         st.subheader("🛠️ Tools Purchased in Selected Month(s)")
#         tools_table = filtered_data[['Expense Month', 'Short Text', 'DURATION', 'Total Value', 'Allocated Monthly Expense']]
#         st.dataframe(tools_table)

#         # Download Visuals
#         def fig_to_image(fig):
#             buffer = BytesIO()
#             fig.write_image(buffer, format="png")
#             buffer.seek(0)
#             return buffer

#         st.markdown("### ⬇️ Download Visuals")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.download_button("📥 Download Expense Chart", fig_to_image(fig1), file_name="monthly_expense.png")
#         with col2:
#             st.download_button("📥 Download Per-KM Chart", fig_to_image(fig2), file_name="per_km_expense.png")

#         # Export to Excel
#         towrite = BytesIO()
#         with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
#             filtered_totals.to_excel(writer, index=False, sheet_name='Summary')
#             tools_table.to_excel(writer, index=False, sheet_name='Tools')
#         towrite.seek(0)
#         st.download_button("📥 Download Full Report (Excel)", data=towrite, file_name="budget_report.xlsx")

# ----------------------------------------------------



import pandas as pd
import streamlit as st
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="💰 Premium Budget Dashboard", layout="wide")

# --- Title Section ---
st.title("📊 Monthly Budget & Tool Expense Dashboard")
st.markdown("A premium view of monthly purchases, expenses, and per-KM analytics. Designed for leadership decisions.")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Upload & Filter")
    uploaded_file = st.file_uploader("Upload Excel Budget File", type=["xlsx"])
    st.markdown("👉 Supports `.xlsx` only. Must include `Total Value`, `Release Date`, `DURATION`, `Short Text`, etc.")

# --- Load and Process Data ---
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean & enrich
    df['Total Value'] = pd.to_numeric(df['Total Value'].astype(str).str.replace(',', ''), errors='coerce')
    df['DURATION'] = df['DURATION'].str.upper().str.strip()
    df['Release Date Parsed'] = pd.to_datetime(df['Release Date'], errors='coerce', dayfirst=True)
    df['Delivery Date Parsed'] = pd.to_datetime(df['Delivery Date'], errors='coerce', dayfirst=True)
    df['Expense Month'] = df['Release Date Parsed'].fillna(df['Delivery Date Parsed']).dt.to_period('M').astype(str)

    def allocate(row):
        if row['DURATION'] == 'MONTHLY':
            return row['Total Value']
        elif row['DURATION'] == 'YEARLY':
            return row['Total Value'] / 12
        return None

    df['Monthly Expense'] = df.apply(allocate, axis=1)
    df.dropna(subset=['Monthly Expense'], inplace=True)

    # --- Month Selector ---
    all_months = sorted(df['Expense Month'].unique())
    selected_months = st.multiselect("📅 Select Month(s) to Analyze", options=all_months, default=all_months[-3:])

    if selected_months:
        # KM inputs
        st.markdown("### 🚌 Bus KM Data")
        km_inputs = {}
        cols = st.columns(len(selected_months))
        for i, month in enumerate(selected_months):
            with cols[i]:
                km_inputs[month] = st.number_input(f"KM for {month}", min_value=0.0, step=100.0)

        # Filter data
        data = df[df['Expense Month'].isin(selected_months)].copy()

        # Compute summary
        summary = (
            data.groupby('Expense Month')['Monthly Expense']
            .sum()
            .reset_index()
            .rename(columns={'Monthly Expense': 'Total Expense'})
        )
        summary['Bus KM'] = summary['Expense Month'].map(km_inputs)
        summary['Per KM Expense'] = summary.apply(
            lambda r: r['Total Expense'] / r['Bus KM'] if r['Bus KM'] else None, axis=1
        )

        # --- Top KPIs ---
        st.markdown("### 📌 Key Metrics (Across Selected Months)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📅 Months Selected", len(selected_months))
        with col2:
            st.metric("💰 Total Expense", f"₹{summary['Total Expense'].sum():,.2f}")
        with col3:
            avg_per_km = summary['Per KM Expense'].mean()
            st.metric("🧮 Avg Per-KM Expense", f"₹{avg_per_km:,.2f}" if not pd.isna(avg_per_km) else "N/A")
        with col4:
            max_month = summary.loc[summary['Total Expense'].idxmax(), 'Expense Month']
            st.metric("📈 Max Expense Month", max_month)

        # --- Visuals ---
        st.markdown("### 📊 Visual Reports")

        # Bar Chart
        fig_exp = px.bar(
            summary, x='Expense Month', y='Total Expense',
            text_auto=True, color='Total Expense', color_continuous_scale='blues',
            title="Monthly Total Expense"
        )
        st.plotly_chart(fig_exp, use_container_width=True)

        # Line Chart
        fig_km = px.line(
            summary, x='Expense Month', y='Per KM Expense',
            markers=True, title="Per KM Expense Trend", line_shape='linear'
        )
        st.plotly_chart(fig_km, use_container_width=True)

        # Pie Chart: Tool Share
        st.markdown("### 🛠️ Tools Purchased Breakdown")
        tool_summary = data.groupby('Short Text')['Monthly Expense'].sum().reset_index()
        tool_summary = tool_summary.sort_values(by='Monthly Expense', ascending=False).head(10)
        fig_pie = px.pie(tool_summary, values='Monthly Expense', names='Short Text', title="Top 10 Tools by Expense")
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- Tables ---
        st.markdown("### 📋 Data Tables")
        st.dataframe(summary.style.format({"Total Expense": "₹{:,.2f}", "Per KM Expense": "₹{:,.2f}"}))
        st.markdown("**Full Tool Details**")
        st.dataframe(data[['Expense Month', 'Short Text', 'DURATION', 'Total Value', 'Monthly Expense']])

        # --- Export Buttons ---
        st.markdown("### ⬇️ Download Reports")

        # Excel Export
        towrite = BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            summary.to_excel(writer, sheet_name='Summary', index=False)
            data.to_excel(writer, sheet_name='Full Data', index=False)
        towrite.seek(0)
        st.download_button("📥 Export Excel Report", towrite, file_name="budget_summary.xlsx")
