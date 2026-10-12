"""Page Object for the Expense Tracker app."""
from __future__ import annotations

from playwright.sync_api import Locator

from .base_page import BasePage


class ExpensesPage(BasePage):
    def load(self) -> None:
        self.page.goto(f"{self.base_url}/apps/expenses")

    def add(self, description: str, amount: str) -> None:
        self.page.get_by_test_id("expense-desc").fill(description)
        self.page.get_by_test_id("expense-amount").fill(amount)
        self.page.get_by_test_id("expense-add").click()

    def items(self) -> Locator:
        return self.page.get_by_test_id("expense-item")

    def item_descriptions(self) -> list[str]:
        return self.page.get_by_test_id("expense-item-desc").all_inner_texts()

    def delete(self, description: str) -> None:
        row = self.items().filter(has_text=description)
        row.get_by_test_id("expense-delete").click()

    def total_text(self) -> str:
        return self.page.get_by_test_id("expense-total").inner_text()

    def error_text(self) -> str:
        return self.page.get_by_test_id("expense-error").inner_text()

    def is_empty_state_visible(self) -> bool:
        return self.page.get_by_test_id("expense-empty").is_visible()
