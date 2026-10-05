"""Cart page object."""
from __future__ import annotations

from .base_page import BasePage


class CartPage(BasePage):
    def load(self) -> None:
        self.page.goto(f"{self.base_url}/cart")

    def is_empty(self) -> bool:
        return self.page.get_by_test_id("empty-cart").is_visible()

    def row_names(self) -> list[str]:
        return self.page.get_by_test_id("cart-item-name").all_inner_texts()

    def total_text(self) -> str:
        return self.page.get_by_test_id("cart-total").inner_text()

    def clear(self) -> None:
        self.page.get_by_test_id("clear-cart").click()

    def go_to_checkout(self) -> None:
        self.page.get_by_test_id("go-to-checkout").click()
