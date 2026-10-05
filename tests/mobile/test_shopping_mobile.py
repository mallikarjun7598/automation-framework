"""Mobile-web automation tests (Appium + pytest).

Same shopping journey as the web suite, but driven through a real mobile
browser via Appium. These SKIP automatically unless you pass --appium and have
an Appium server + device/emulator running (see conftest.py).
"""
from __future__ import annotations

import pytest

from .pages.mobile_home_page import MobileHomePage

pytestmark = pytest.mark.mobile


@pytest.fixture()
def home(mobile_driver, mobile_base_url) -> MobileHomePage:
    hp = MobileHomePage(mobile_driver, mobile_base_url)
    hp.load()
    return hp


def test_mobile_homepage_lists_products(home: MobileHomePage) -> None:
    assert "Echo Dot (5th Gen)" in home.product_names()


def test_mobile_search_filters_products(home: MobileHomePage) -> None:
    home.search("kindle")
    assert home.product_names() == ["Kindle Paperwhite"]


def test_mobile_add_to_cart_updates_count(home: MobileHomePage) -> None:
    assert home.cart_count() == 0
    home.add_product_to_cart_by_name("Fire TV Stick 4K")
    assert home.cart_count() == 1
