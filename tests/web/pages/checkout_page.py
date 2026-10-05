"""Checkout + confirmation page object."""
from __future__ import annotations

from .base_page import BasePage


class CheckoutPage(BasePage):
    def load(self) -> None:
        self.page.goto(f"{self.base_url}/checkout")

    def place_order(self, name: str) -> None:
        self.page.get_by_test_id("checkout-name").fill(name)
        self.page.get_by_test_id("place-order").click()

    def error_text(self) -> str:
        return self.page.get_by_test_id("checkout-error").inner_text()

    # --- confirmation page (shown after a successful order) ---
    def confirmation_visible(self) -> bool:
        return self.page.get_by_test_id("order-confirmation").is_visible()

    def order_id(self) -> str:
        return self.page.get_by_test_id("order-id").inner_text()
