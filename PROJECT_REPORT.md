# Daily Expense Financial Management Application

## 1. Project details

**Project title:** Daily Expense Financial Management Application  
**Author:** Prakhar Kumar Singh  
**Registration number:** 22MIP10083  
**Repository:** https://github.com/silverrace03/Daily-Expense-Financial-Management-App  
**Technology:** Python, Streamlit, SQLite, Pandas

## 2. Abstract

The Daily Expense Financial Management Application is a lightweight personal-finance system for recording income and daily expenses. It stores transactions in SQLite and presents a browser interface through Streamlit. Users can add transactions, view totals and balance, filter transaction history, delete incorrect records, export filtered data as CSV, and inspect category-wise expense reports. The application is intentionally simple, offline-compatible at the data layer, and suitable for academic demonstration.

## 3. Problem statement and motivation

People often record expenses in notebooks or scattered notes, making it difficult to know how much was spent, which categories consume the most money, and whether the current balance is accurate. A structured application is required to centralise daily transactions, calculate financial summaries automatically, and present useful reports without manual calculations.

## 4. Objectives

1. Record income and expense transactions with date, category, payment method and description.
2. Persist transaction data reliably in an SQLite database.
3. Calculate total income, total expenses and current balance.
4. Provide search and filtering for transaction history.
5. Generate category-wise expense summaries and a chart.
6. Allow filtered transactions to be downloaded as a CSV file.
7. Provide a simple browser interface that can be deployed on Streamlit Community Cloud.

## 5. Functional requirements

| ID | Requirement |
|---|---|
| FR1 | Add an income or expense with amount, category, payment method, date and description. |
| FR2 | Reject invalid or non-positive amounts through the input control. |
| FR3 | Store records in the `transactions` SQLite table. |
| FR4 | Display income, expense and balance metrics. |
| FR5 | Search and filter records by text, type and category. |
| FR6 | Delete a selected transaction. |
| FR7 | Display category totals and a bar chart. |
| FR8 | Export the filtered table to CSV. |

## 6. Non-functional requirements

- Usable in a modern web browser.
- Simple interface requiring no external database server.
- Persistent storage across application reruns.
- Clear labels and readable financial summaries.
- Python 3.9+ compatibility.

## 7. System design

### Architecture

```text
Browser
   |
Streamlit interface (streamlit_app.py)
   |
Application logic: validation, totals, filters, reports
   |
SQLite database (expenses.db)
   |
CSV download generated from filtered records
```

### Database design

The `transactions` table contains: `id`, `kind`, `amount`, `category`, `payment_method`, `transaction_date`, `description`, and `created_at`. The `kind` field identifies Income or Expense. Monetary values are stored as positive numbers; the transaction type determines whether they increase income or expenses.

### Core algorithm

```text
START
  Initialise SQLite connection and create transactions table if needed
  Read all transactions
  income = sum(amount where kind = Income)
  expenses = sum(amount where kind = Expense)
  balance = income - expenses
  Display metrics

  IF user submits a transaction:
      validate amount and date
      insert transaction into SQLite
      refresh page

  IF user applies filters:
      build SQL conditions for search, type and category
      retrieve matching rows
      display table and CSV download

  Group expense rows by category
  Display totals and bar chart
END
```

### User-flow diagram

```text
[Open web app]
       |
       v
[Add transaction] ---> [Validate input] --invalid--> [Show error]
       |                     |
       | valid               v
       +--------------> [Save in SQLite]
                              |
                              v
                    [Refresh metrics and reports]
                              |
                 +------------+-------------+
                 v                          v
       [Filter transaction history]   [View category report]
                 |
                 v
          [Export CSV / Delete]
```

## 8. Implementation details

The desktop prototype is implemented in `app.py` using Tkinter. The browser version is implemented in `streamlit_app.py`. Streamlit reruns the script after each interaction, while `st.cache_resource` keeps a reusable SQLite connection. Pandas converts database rows into tables and CSV output. SQLite parameterized queries are used for filters and inserts, avoiding unsafe string interpolation for user values.

## 9. Testing and validation

Automated tests in `test_app.py` verify adding transactions, income/expense totals, filtering and deletion. Manual testing was performed in the deployed Streamlit application.

| Test case | Input/action | Expected result |
|---|---|---|
| TC01 | Add income ₹50,000 | Income metric increases by ₹50,000. |
| TC02 | Add Food expense ₹250 | Expense metric increases and balance decreases by ₹250. |
| TC03 | Search `Food` | Only matching records are displayed. |
| TC04 | Select type `Income` | Only income records are displayed. |
| TC05 | Open Reports | Category totals and chart are displayed. |
| TC06 | Export filtered CSV | A CSV file downloads with the visible records. |
| TC07 | Delete a selected record | The record disappears and metrics refresh. |
| TC08 | Enter amount below minimum | The form prevents an invalid amount. |

## 10. Sample output

The deployed page displays three summary cards: Total Income, Total Expenses and Current Balance. The Transaction History tab displays ID, date, type, category, amount, payment method and description. The Reports tab displays category totals, percentage share and a bar chart.

## 11. Challenges and solutions

- **Desktop-to-browser conversion:** Tkinter windows do not run inside a web browser, so a Streamlit interface was created while retaining the SQLite data model.
- **Persistent data:** SQLite was selected because it requires no server and preserves records between reruns.
- **Interactive filtering:** SQL conditions are assembled from optional filters and values are passed as parameters.
- **User-friendly reporting:** Pandas tables and Streamlit charts provide readable summaries without requiring a separate frontend framework.

## 12. Conclusion

The application meets the core requirements of a daily expense manager. It provides persistent transaction storage, automatic calculations, filtering, deletion, CSV export and category reporting through a browser-accessible interface. The project demonstrates Python programming, database operations, validation, data processing and basic visual analytics.

## 13. Future enhancements

- User authentication and separate accounts.
- Monthly budgets and overspending alerts.
- Recurring transactions.
- Date-range filtering and monthly trend charts.
- Cloud database for multi-device access.
- PDF report generation and downloadable dashboard snapshots.
