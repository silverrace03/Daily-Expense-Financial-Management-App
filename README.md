# Daily Expense Financial Management Application

An offline personal-finance desktop application for recording income and daily expenses. It is built with Python, Tkinter and SQLite, so no server or internet connection is required.

## Features

- Add income and expense transactions
- Categories, payment methods, dates and descriptions
- Automatic income, expense and balance calculations
- Search, type and category filters
- Transaction deletion with confirmation
- Category-wise expense report
- CSV export of filtered records
- SQLite persistence in `expenses.db`

## Requirements

- Python 3.9 or newer
- Tkinter (included with the standard Python installer on macOS and Windows)

## Run

```bash
cd daily_expense_financial_app
python3 app.py
```

The first run creates `expenses.db` in the same folder. Use positive amounts. Dates must use `YYYY-MM-DD`.

## Test

```bash
python3 -m unittest -v test_app.py
```

## Project design

The interface has three tabs: Add Transaction, Transaction History and Reports. The SQLite table stores `kind`, `amount`, `category`, `payment_method`, `transaction_date`, `description` and timestamps. The balance is calculated as total income minus total expenses.
