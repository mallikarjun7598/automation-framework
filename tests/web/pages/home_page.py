"""Home / product-listing page object."""
from __future__ import annotations

from playwright.sync_api import Locator

from .base_page import BasePage


class HomePage(BasePage):
    def load(self) -> None:
        self.page.goto(f"{self.base_url}/")

    def product_cards(self) -> Locator:
        return self.page.get_by_test_id("product-card")

    def product_names(self) -> list[str]:
        return self.page.get_by_test_id("product-name").all_inner_texts()

    def add_product_to_cart_by_name(self, name: str) -> None:
        card = self.page.get_by_test_id("product-card").filter(has_text=name)
        card.get_by_test_id("add-to-cart").click()

    def has_no_results(self) -> bool:
        return self.page.get_by_test_id("no-results").is_visible()
