"""End-to-end tests for the Expense Tracker app (localStorage-backed PWA)."""
from __future__ import annotations

import pytest

from .pages.expenses_page import ExpensesPage

pytestmark = pytest.mark.web


@pytest.fixture()
def expenses(page, base_url) -> ExpensesPage:
    ep = ExpensesPage(page, base_url)
    ep.load()
    page.evaluate("localStorage.clear()")
    ep.load()
    return ep


def test_empty_state_and_zero_total(expenses: ExpensesPage) -> None:
    assert expenses.is_empty_state_visible()
    assert expenses.total_text() == "$0.00"


def test_add_expense_updates_total(expenses: ExpensesPage) -> None:
    expenses.add("Groceries", "42.50")
    assert expenses.item_descriptions() == ["Groceries"]
    assert expenses.total_text() == "$42.50"


def test_add_multiple_expenses_sums_total(expenses: ExpensesPage) -> None:
    expenses.add("Groceries", "42.50")
    expenses.add("Coffee", "3.75")
    expenses.add("Gas", "28.00")
    assert expenses.total_text() == "$74.25"
    assert len(expenses.item_descriptions()) == 3


def test_delete_expense_updates_total(expenses: ExpensesPage) -> None:
    expenses.add("Groceries", "42.50")
    expenses.add("Coffee", "3.75")
    expenses.delete("Coffee")
    assert expenses.item_descriptions() == ["Groceries"]
    assert expenses.total_text() == "$42.50"


def test_rejects_empty_description(expenses: ExpensesPage) -> None:
    expenses.add("", "10.00")
    assert "description" in expenses.error_text().lower()
    assert expenses.is_empty_state_visible()


def test_rejects_invalid_amount(expenses: ExpensesPage) -> None:
    expenses.add("Snacks", "0")
    assert "valid amount" in expenses.error_text().lower()
    assert expenses.is_empty_state_visible()


def test_expenses_persist_across_reload(expenses: ExpensesPage) -> None:
    expenses.add("Rent", "1200.00")
    expenses.load()
    assert expenses.item_descriptions() == ["Rent"]
    assert expenses.total_text() == "$1200.00"
