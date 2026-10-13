"""Browser-based Streamlit version of the Daily Expense Financial Manager."""
from datetime import date, datetime
from pathlib import Path
import io
import sqlite3
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "expenses.db"
CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Health", "Education", "Entertainment", "Rent", "Salary", "Other"]
PAYMENT_METHODS = ["Cash", "UPI", "Card", "Bank Transfer", "Other"]

@st.cache_resource
def connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, amount REAL NOT NULL,
        category TEXT NOT NULL, payment_method TEXT NOT NULL, transaction_date TEXT NOT NULL,
        description TEXT DEFAULT '', created_at TEXT NOT NULL)""")
    conn.commit()
    return conn

def rows(query="", kind="All", category="All"):
    clauses, args = ["1=1"], []
    if query:
        clauses.append("(description LIKE ? OR category LIKE ? OR payment_method LIKE ?)")
        args.extend([f"%{query}%"] * 3)
    if kind != "All": clauses.append("kind=?"); args.append(kind)
    if category != "All": clauses.append("category=?"); args.append(category)
    return connection().execute(f"SELECT * FROM transactions WHERE {' AND '.join(clauses)} ORDER BY transaction_date DESC, id DESC", args).fetchall()

def add_transaction(kind, amount, category, payment, tx_date, description):
    connection().execute("INSERT INTO transactions(kind,amount,category,payment_method,transaction_date,description,created_at) VALUES (?,?,?,?,?,?,?)",
        (kind, amount, category, payment, tx_date, description, datetime.now().isoformat(timespec="seconds")))
    connection().commit()

st.set_page_config(page_title="Daily Expense Financial Manager", page_icon="💰", layout="wide")
st.title("💰 Daily Expense Financial Manager")
st.caption("Track income, daily expenses, balance and category-wise spending in your browser.")
all_rows = rows()
income = sum(r["amount"] for r in all_rows if r["kind"] == "Income")
expenses = sum(r["amount"] for r in all_rows if r["kind"] == "Expense")
c1, c2, c3 = st.columns(3)
c1.metric("Total Income", f"₹{income:,.2f}")
c2.metric("Total Expenses", f"₹{expenses:,.2f}")
c3.metric("Current Balance", f"₹{income-expenses:,.2f}")

tab_add, tab_history, tab_report = st.tabs(["Add Transaction", "Transaction History", "Reports"])
with tab_add:
    with st.form("transaction_form", clear_on_submit=True):
        kind = st.selectbox("Type", ["Expense", "Income"])
        amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0, format="%.2f")
        category = st.selectbox("Category", CATEGORIES)
        payment = st.selectbox("Payment method", PAYMENT_METHODS)
        tx_date = st.date_input("Date", value=date.today())
        description = st.text_input("Description")
        submitted = st.form_submit_button("Save Transaction", type="primary")
    if submitted:
        add_transaction(kind, float(amount), category, payment, tx_date.isoformat(), description.strip())
        st.success("Transaction saved successfully.")
        st.rerun()

with tab_history:
    f1, f2, f3 = st.columns([2, 1, 1])
    search = f1.text_input("Search")
    filter_kind = f2.selectbox("Type", ["All", "Expense", "Income"])
    filter_category = f3.selectbox("Category", ["All"] + CATEGORIES)
    filtered = rows(search, filter_kind, filter_category)
    data = [{"ID": r["id"], "Date": r["transaction_date"], "Type": r["kind"], "Category": r["category"], "Amount (₹)": r["amount"], "Payment": r["payment_method"], "Description": r["description"]} for r in filtered]
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    if data:
        selected = st.selectbox("Select transaction to delete", [f"{r['ID']} — {r['Date']} — ₹{r['Amount (₹)']:,.2f}" for r in data])
        if st.button("Delete Selected"):
            connection().execute("DELETE FROM transactions WHERE id=?", (int(selected.split(" — ")[0]),)); connection().commit(); st.rerun()
    csv_buffer = io.StringIO(); pd.DataFrame(data).to_csv(csv_buffer, index=False)
    st.download_button("⬇️ Export filtered CSV", csv_buffer.getvalue(), "expense_report.csv", "text/csv")

with tab_report:
    st.subheader("Expense report by category")
    report = pd.DataFrame([{"Category": r["category"], "Total (₹)": r["total"]} for r in connection().execute("SELECT category, SUM(amount) total FROM transactions WHERE kind='Expense' GROUP BY category ORDER BY total DESC")])
    if report.empty:
        st.info("No expense data yet.")
    else:
        report["Share"] = (report["Total (₹)"] / report["Total (₹)"].sum() * 100).round(1).astype(str) + "%"
        st.dataframe(report, use_container_width=True, hide_index=True)
        st.bar_chart(report.set_index("Category")["Total (₹)"])
