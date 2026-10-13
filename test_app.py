import tempfile
import unittest
from pathlib import Path
from app import ExpenseStore

class ExpenseStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.tmp.close(); self.store = ExpenseStore(Path(self.tmp.name))
    def tearDown(self): self.store.close(); Path(self.tmp.name).unlink(missing_ok=True)
    def test_add_and_totals(self):
        self.store.add('Income', 10000, 'Salary', 'Bank Transfer', '2026-10-01', 'Monthly salary')
        self.store.add('Expense', 250, 'Food', 'UPI', '2026-10-01', 'Lunch')
        self.assertEqual(self.store.totals(), (10000.0, 250.0))
    def test_filter_and_delete(self):
        self.store.add('Expense', 100, 'Travel', 'Cash', '2026-10-02', 'Bus')
        self.store.add('Expense', 200, 'Food', 'UPI', '2026-10-03', 'Dinner')
        self.assertEqual(len(self.store.list_rows(category='Food')), 1)
        row=self.store.list_rows()[0]; self.store.delete(row['id']); self.assertEqual(len(self.store.list_rows()),1)

if __name__ == '__main__': unittest.main()
