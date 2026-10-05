"""End-to-end web automation tests (Playwright + pytest).

These exercise the core shopping journey of the mini storefront:
browse -> search -> add to cart -> checkout.

The `page` fixture is provided by pytest-playwright. `base_url` is provided by
conftest.py (which also starts the app).
"""
from __future__ import annotations

import pytest

from .pages.cart_page import CartPage
from .pages.checkout_page import CheckoutPage
from .pages.home_page import HomePage

pytestmark = pytest.mark.web


@pytest.fixture()
def home(page, base_url) -> HomePage:
    hp = HomePage(page, base_url)
    hp.load()
    return hp


def test_homepage_lists_products(home: HomePage) -> None:
    assert home.product_cards().count() == 6
    assert "Echo Dot (5th Gen)" in home.product_names()


def test_search_filters_products(home: HomePage) -> None:
    home.search("kindle")
    names = home.product_names()
    assert names == ["Kindle Paperwhite"]


def test_search_no_results(home: HomePage) -> None:
    home.search("nonexistent-product-xyz")
    assert home.has_no_results()


def test_add_to_cart_updates_count(home: HomePage) -> None:
    assert home.cart_count() == 0
    home.add_product_to_cart_by_name("Fire TV Stick 4K")
    assert home.cart_count() == 1


def test_full_checkout_journey(page, base_url, home: HomePage) -> None:
    # 1. Add two different products.
    home.add_product_to_cart_by_name("Echo Dot (5th Gen)")
    home.add_product_to_cart_by_name("Wireless Mouse")

    # 2. Review the cart.
    cart = CartPage(page, base_url)
    cart.load()
    assert sorted(cart.row_names()) == ["Echo Dot (5th Gen)", "Wireless Mouse"]
    assert cart.total_text() == "$74.98"  # 49.99 + 24.99

    # 3. Check out.
    cart.go_to_checkout()
    checkout = CheckoutPage(page, base_url)
    checkout.place_order("Jordan Shopper")

    # 4. Confirmation shown with an order id.
    assert checkout.confirmation_visible()
    assert checkout.order_id().startswith("ORD-")


def test_checkout_requires_name(page, base_url, home: HomePage) -> None:
    home.add_product_to_cart_by_name("Kindle Paperwhite")
    checkout = CheckoutPage(page, base_url)
    checkout.load()
    checkout.place_order("")  # empty name
    assert "Name is required" in checkout.error_text()


def test_clear_cart_empties_it(page, base_url, home: HomePage) -> None:
    home.add_product_to_cart_by_name("USB-C Charging Cable")
    cart = CartPage(page, base_url)
    cart.load()
    assert not cart.is_empty()
    cart.clear()
    assert cart.is_empty()
