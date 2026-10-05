"""Base Page Object.

Page Objects wrap a page's structure so tests read like user intent
("search for X", "add to cart") instead of raw selectors. If the markup
changes, you fix the selector here once rather than in every test.
"""
from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- shared header elements (present on every page) ---
    def search(self, term: str) -> None:
        self.page.get_by_test_id("search-input").fill(term)
        self.page.get_by_test_id("search-button").click()

    def open_cart(self) -> None:
        self.page.get_by_test_id("cart-link").click()

    def cart_count(self) -> int:
        return int(self.page.get_by_test_id("cart-count").inner_text())
