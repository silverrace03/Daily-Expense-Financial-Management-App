"""Daily Expense Financial Management Application.

Offline desktop app using Tkinter and SQLite. Run with: python3 app.py
"""
from __future__ import annotations

import csv
import sqlite3
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "expenses.db"

CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Health", "Education", "Entertainment", "Rent", "Salary", "Other"]
PAYMENT_METHODS = ["Cash", "UPI", "Card", "Bank Transfer", "Other"]


class ExpenseStore:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL CHECK(kind IN ('Income','Expense')),
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )"""
        )
        self.conn.commit()

    def add(self, kind, amount, category, payment_method, transaction_date, description):
        self.conn.execute(
            "INSERT INTO transactions(kind,amount,category,payment_method,transaction_date,description,created_at) VALUES (?,?,?,?,?,?,?)",
            (kind, amount, category, payment_method, transaction_date, description, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def delete(self, transaction_id):
        self.conn.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        self.conn.commit()

    def list_rows(self, query="", kind="All", category="All", start="", end=""):
        clauses, args = ["1=1"], []
        if query:
            clauses.append("(description LIKE ? OR category LIKE ? OR payment_method LIKE ?)")
            args += [f"%{query}%"] * 3
        if kind != "All": clauses.append("kind=?"); args.append(kind)
        if category != "All": clauses.append("category=?"); args.append(category)
        if start: clauses.append("transaction_date>=?"); args.append(start)
        if end: clauses.append("transaction_date<=?"); args.append(end)
        return self.conn.execute(f"SELECT * FROM transactions WHERE {' AND '.join(clauses)} ORDER BY transaction_date DESC, id DESC", args).fetchall()

    def totals(self):
        row = self.conn.execute("SELECT COALESCE(SUM(CASE WHEN kind='Income' THEN amount END),0) income, COALESCE(SUM(CASE WHEN kind='Expense' THEN amount END),0) expenses FROM transactions").fetchone()
        return float(row["income"]), float(row["expenses"])

    def category_totals(self):
        return self.conn.execute("SELECT category, SUM(amount) total FROM transactions WHERE kind='Expense' GROUP BY category ORDER BY total DESC").fetchall()

    def close(self): self.conn.close()


class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daily Expense Financial Manager")
        self.geometry("1100x700")
        self.minsize(950, 620)
        self.store = ExpenseStore()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._style()
        self._build()
        self.refresh()

    def _style(self):
        style = ttk.Style(self)
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("Title.TLabel", font=("Arial", 22, "bold"), foreground="#17365D")
        style.configure("Card.TFrame", background="#F2F6FA")
        style.configure("CardTitle.TLabel", background="#F2F6FA", foreground="#5A6B7B", font=("Arial", 10))
        style.configure("CardValue.TLabel", background="#F2F6FA", foreground="#17365D", font=("Arial", 17, "bold"))
        style.configure("Treeview", rowheight=28, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def _build(self):
        head = ttk.Frame(self, padding=(22, 18, 22, 8)); head.pack(fill="x")
        ttk.Label(head, text="Daily Expense Financial Manager", style="Title.TLabel").pack(side="left")
        ttk.Button(head, text="Export CSV", command=self.export_csv).pack(side="right", padx=4)
        ttk.Button(head, text="Add Transaction", command=self.focus_amount).pack(side="right", padx=4)

        cards = ttk.Frame(self, padding=(22, 5, 22, 12)); cards.pack(fill="x")
        self.card_vars = {}
        for key, label, color in [("income", "Total Income", "#2F866A"), ("expenses", "Total Expenses", "#C75146"), ("balance", "Current Balance", "#2E6F95")]:
            f = ttk.Frame(cards, style="Card.TFrame", padding=14); f.pack(side="left", fill="x", expand=True, padx=5)
            ttk.Label(f, text=label, style="CardTitle.TLabel").pack(anchor="w")
            v = tk.StringVar(value="₹0.00"); self.card_vars[key] = v
            lab = ttk.Label(f, textvariable=v, style="CardValue.TLabel"); lab.pack(anchor="w", pady=(4,0)); lab.configure(foreground=color)

        notebook = ttk.Notebook(self); notebook.pack(fill="both", expand=True, padx=22, pady=(0, 15))
        self.entry_tab = ttk.Frame(notebook, padding=18); self.history_tab = ttk.Frame(notebook, padding=18); self.report_tab = ttk.Frame(notebook, padding=18)
        notebook.add(self.entry_tab, text="Add Transaction"); notebook.add(self.history_tab, text="Transaction History"); notebook.add(self.report_tab, text="Reports")
        self._build_entry(); self._build_history(); self._build_reports()

    def _build_entry(self):
        f = self.entry_tab
        ttk.Label(f, text="Record income or expense", font=("Arial", 16, "bold")).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,18))
        labels = ["Type", "Amount (₹)", "Category", "Payment method", "Date (YYYY-MM-DD)", "Description"]
        for i, label in enumerate(labels): ttk.Label(f,text=label).grid(row=i+1,column=0,sticky="w",pady=7)
        self.kind = ttk.Combobox(f, values=["Expense","Income"], state="readonly", width=29); self.kind.set("Expense"); self.kind.grid(row=1,column=1,sticky="w",pady=7)
        self.amount = ttk.Entry(f,width=32); self.amount.grid(row=2,column=1,sticky="w",pady=7)
        self.category = ttk.Combobox(f,values=CATEGORIES,state="readonly",width=29); self.category.set("Food"); self.category.grid(row=3,column=1,sticky="w",pady=7)
        self.payment = ttk.Combobox(f,values=PAYMENT_METHODS,state="readonly",width=29); self.payment.set("UPI"); self.payment.grid(row=4,column=1,sticky="w",pady=7)
        self.tx_date = ttk.Entry(f,width=32); self.tx_date.insert(0,date.today().isoformat()); self.tx_date.grid(row=5,column=1,sticky="w",pady=7)
        self.description = ttk.Entry(f,width=65); self.description.grid(row=6,column=1,sticky="w",pady=7)
        ttk.Button(f,text="Save Transaction",command=self.save).grid(row=7,column=1,sticky="w",pady=18)
        ttk.Button(f,text="Clear",command=self.clear_form).grid(row=7,column=1,sticky="w",padx=(145,0),pady=18)
        ttk.Label(f,text="Tip: use positive amounts; expenses reduce the current balance.",foreground="#5A6B7B").grid(row=9,column=0,columnspan=2,sticky="w",pady=(20,0))

    def _build_history(self):
        f=self.history_tab
        filters=ttk.Frame(f); filters.pack(fill="x",pady=(0,10))
        ttk.Label(filters,text="Search").pack(side="left"); self.search=tk.StringVar(); ttk.Entry(filters,textvariable=self.search,width=18).pack(side="left",padx=5)
        ttk.Label(filters,text="Type").pack(side="left",padx=(12,0)); self.filter_kind=ttk.Combobox(filters,values=["All","Expense","Income"],state="readonly",width=10); self.filter_kind.set("All"); self.filter_kind.pack(side="left",padx=5)
        ttk.Label(filters,text="Category").pack(side="left",padx=(12,0)); self.filter_category=ttk.Combobox(filters,values=["All"]+CATEGORIES,state="readonly",width=14); self.filter_category.set("All"); self.filter_category.pack(side="left",padx=5)
        ttk.Button(filters,text="Apply Filters",command=self.refresh).pack(side="left",padx=8); ttk.Button(filters,text="Delete Selected",command=self.delete_selected).pack(side="right")
        cols=("id","date","type","category","amount","payment","description")
        self.tree=ttk.Treeview(f,columns=cols,show="headings",selectmode="browse")
        widths={"id":55,"date":110,"type":90,"category":120,"amount":100,"payment":120,"description":350}
        heads={"id":"ID","date":"Date","type":"Type","category":"Category","amount":"Amount (₹)","payment":"Payment","description":"Description"}
        for c in cols: self.tree.heading(c,text=heads[c]); self.tree.column(c,width=widths[c],anchor="w")
        self.tree.pack(fill="both",expand=True); self.tree.tag_configure("Expense",foreground="#C75146"); self.tree.tag_configure("Income",foreground="#2F866A")

    def _build_reports(self):
        f=self.report_tab; ttk.Label(f,text="Expense report by category",font=("Arial",16,"bold")).pack(anchor="w",pady=(0,12))
        self.report_tree=ttk.Treeview(f,columns=("category","total","share"),show="headings",height=10)
        for c,h in [("category","Category"),("total","Total (₹)"),("share","Share of expenses")]: self.report_tree.heading(c,text=h); self.report_tree.column(c,width=230,anchor="w")
        self.report_tree.pack(fill="x")
        self.report_text=tk.StringVar(); ttk.Label(f,textvariable=self.report_text,foreground="#5A6B7B").pack(anchor="w",pady=18)

    def focus_amount(self): self.amount.focus_set()
    def clear_form(self):
        self.amount.delete(0,"end"); self.description.delete(0,"end"); self.tx_date.delete(0,"end"); self.tx_date.insert(0,date.today().isoformat()); self.kind.set("Expense"); self.category.set("Food"); self.payment.set("UPI")
    def save(self):
        try: amount=float(self.amount.get().replace(",",""))
        except ValueError: messagebox.showerror("Invalid amount","Enter a positive numeric amount."); return
        if amount<=0: messagebox.showerror("Invalid amount","Amount must be greater than zero."); return
        try: datetime.strptime(self.tx_date.get().strip(),"%Y-%m-%d")
        except ValueError: messagebox.showerror("Invalid date","Use the format YYYY-MM-DD."); return
        self.store.add(self.kind.get(),amount,self.category.get(),self.payment.get(),self.tx_date.get().strip(),self.description.get().strip())
        self.clear_form(); self.refresh(); messagebox.showinfo("Saved","Transaction saved successfully.")
    def refresh(self):
        if not hasattr(self,"tree"): return
        for x in self.tree.get_children(): self.tree.delete(x)
        rows=self.store.list_rows(self.search.get() if hasattr(self,"search") else "",self.filter_kind.get() if hasattr(self,"filter_kind") else "All",self.filter_category.get() if hasattr(self,"filter_category") else "All")
        for r in rows: self.tree.insert("","end",iid=str(r["id"]),values=(r["id"],r["transaction_date"],r["kind"],r["category"],f"₹{r['amount']:,.2f}",r["payment_method"],r["description"]),tags=(r["kind"],))
        income,expenses=self.store.totals(); self.card_vars["income"].set(f"₹{income:,.2f}"); self.card_vars["expenses"].set(f"₹{expenses:,.2f}"); self.card_vars["balance"].set(f"₹{income-expenses:,.2f}")
        for x in self.report_tree.get_children(): self.report_tree.delete(x)
        cats=self.store.category_totals(); total=sum(float(r["total"]) for r in cats)
        for r in cats: self.report_tree.insert("","end",values=(r["category"],f"₹{r['total']:,.2f}",f"{(float(r['total'])/total*100 if total else 0):.1f}%"))
        self.report_text.set(f"Total expense categories: {len(cats)} | Total expenses: ₹{total:,.2f}")
    def delete_selected(self):
        sel=self.tree.selection()
        if not sel: messagebox.showwarning("Nothing selected","Select a transaction first."); return
        if messagebox.askyesno("Confirm deletion","Delete the selected transaction?"): self.store.delete(int(sel[0])); self.refresh()
    def export_csv(self):
        rows=self.store.list_rows(self.search.get(),self.filter_kind.get(),self.filter_category.get())
        if not rows: messagebox.showinfo("No data","There are no transactions to export."); return
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV files","*.csv")],initialfile="expense_report.csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["ID","Type","Amount","Category","Payment method","Date","Description"])
            for r in rows: w.writerow([r["id"],r["kind"],r["amount"],r["category"],r["payment_method"],r["transaction_date"],r["description"]])
        messagebox.showinfo("Export complete",f"Saved {len(rows)} records to:\n{path}")
    def close(self): self.store.close(); self.destroy()

if __name__ == "__main__": ExpenseApp().mainloop()
