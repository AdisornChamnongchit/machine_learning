import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- Configuration ---
PAGE_TITLE = "Income & Expense Tracker"
PAGE_ICON = "💰"
LAYOUT = "wide"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)

# --- Data Handling ---
DATA_FILE = "transactions.csv"

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])
    try:
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date  # Convert Date to date object
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

def save_data(date, trans_type, category, amount, note):
    new_data = pd.DataFrame({
        "Date": [date],
        "Type": [trans_type],
        "Category": [category],
        "Amount": [amount],
        "Note": [note]
    })
    
    if not os.path.exists(DATA_FILE):
        new_data.to_csv(DATA_FILE, index=False)
    else:
        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)

# --- Main App ---
def main():
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")

    # --- Sidebar: Add Transaction ---
    st.sidebar.header("Add New Transaction")
    
    with st.sidebar.form("transaction_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.today())
        trans_type = st.selectbox("Type", ["Income", "Expense"])
        category = st.text_input("Category (e.g., Food, Salary)", placeholder="Enter category...")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        note = st.text_area("Note", placeholder="Optional details...")
        
        submitted = st.form_submit_button("Start Tracking 🚀")
        
        if submitted:
            if category and amount > 0:
                save_data(date, trans_type, category, amount, note)
                st.sidebar.success("Transaction Saved!")
                st.rerun()  # Refresh to show new data
            else:
                st.sidebar.warning("Please fill in Category and Amount.")

    # --- Load Data ---
    df = load_data()

    if df.empty:
        st.info("No transactions yet. Start adding from the sidebar! 👈")
        return

    # --- Dashboard Metrics ---
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"฿{total_income:,.2f}", delta="Income")
    col2.metric("Total Expense", f"฿{total_expense:,.2f}", delta="-Expense", delta_color="inverse")
    col3.metric("Net Balance", f"฿{balance:,.2f}", delta_color="off")

    st.markdown("---")

    # --- Visualizations ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Expense Breakdown")
        expense_df = df[df["Type"] == "Expense"]
        if not expense_df.empty:
            fig_pie = px.pie(expense_df, values="Amount", names="Category", 
                             title="Expenses by Category (Donut Chart)", 
                             hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data to display.")

    with col_chart2:
        st.subheader("Income vs Expense Trend")
        # Preprocess for trend chart
        trend_df = df.groupby(["Date", "Type"])["Amount"].sum().reset_index()
        if not trend_df.empty:
            fig_bar = px.bar(trend_df, x="Date", y="Amount", color="Type", 
                             barmode="group", title="Daily Transaction Trend",
                             color_discrete_map={"Income": "green", "Expense": "red"})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No transaction data to display.")

    st.markdown("---")

    # --- Recent Transactions Table ---
    st.subheader("Recent Transactions")
    
    # Show dataframe with styling
    st.dataframe(
        df.sort_values(by="Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()