"""Page Object for the To-Do app."""
from __future__ import annotations

from playwright.sync_api import Locator

from .base_page import BasePage


class TodoPage(BasePage):
    def load(self) -> None:
        self.page.goto(f"{self.base_url}/apps/todo")

    def add(self, text: str) -> None:
        self.page.get_by_test_id("todo-input").fill(text)
        self.page.get_by_test_id("todo-add").click()

    def items(self) -> Locator:
        return self.page.get_by_test_id("todo-item")

    def item_texts(self) -> list[str]:
        return self.page.get_by_test_id("todo-text").all_inner_texts()

    def toggle(self, text: str) -> None:
        row = self.items().filter(has_text=text)
        row.get_by_test_id("todo-toggle").click()

    def is_done(self, text: str) -> bool:
        row = self.items().filter(has_text=text)
        return "done" in (row.get_attribute("class") or "")

    def delete(self, text: str) -> None:
        row = self.items().filter(has_text=text)
        row.get_by_test_id("todo-delete").click()

    def summary_text(self) -> str:
        return self.page.get_by_test_id("todo-summary").inner_text()

    def is_empty_state_visible(self) -> bool:
        return self.page.get_by_test_id("todo-empty").is_visible()
