from backend import db_helper
import datetime

def test_fetch_expences_for_date():
    expenses = db_helper.fetch_by_date('2025-09-18')

    assert len(expenses) == 2
    assert expenses[0]['expense_date'] == datetime.date(2025, 9, 18)
    assert expenses[1]['expense_date'] == datetime.date(2025, 9, 18)
    assert expenses[0]['amount'] == 120
    assert expenses[1]['amount'] == 36

def test_fetch_expenses_for_date_invalid():
    expenses = db_helper.fetch_by_date('9898-09-18')
    assert len(expenses) == 0

def test_expense_summary_for_date():
    summary = db_helper.fetch_expenses_summary('9000-09-09', '9898-09-18')
    assert len(summary) == 0
