"""Base Page Object for mobile-web automation.

The mobile suite automates the SAME storefront, but inside a real mobile
browser (Safari on an iOS Simulator, or Chrome on an Android emulator) driven
by Appium. Because the markup is identical, we reuse the same `data-testid`
hooks — only the driver differs (Appium WebDriver vs Playwright).

Appium's WebDriver is Selenium-compatible, so we use Selenium's By/locators.
"""
from __future__ import annotations

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def testid(value: str) -> tuple[str, str]:
    """CSS selector for a data-testid attribute."""
    return (By.CSS_SELECTOR, f'[data-testid="{value}"]')


class MobileBasePage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10.0) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def _find(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def _find_all(self, locator: tuple[str, str]) -> list[WebElement]:
        self.wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def _texts(self, locator: tuple[str, str]) -> list[str]:
        """Read .text from all matches, retrying if the DOM mutates underneath.

        After a navigation (e.g. search), element references captured a moment
        earlier can go stale. Re-fetch and read in one shot; retry on staleness.
        """
        for _ in range(3):
            try:
                self.wait.until(EC.presence_of_element_located(locator))
                return [el.text for el in self.driver.find_elements(*locator)]
            except StaleElementReferenceException:
                continue
        # Final attempt (let any exception propagate for a clear failure).
        return [el.text for el in self.driver.find_elements(*locator)]

    # --- shared header actions ---
    def search(self, term: str) -> None:
        box = self._find(testid("search-input"))
        box.clear()
        box.send_keys(term)
        self._find(testid("search-button")).click()
        # Wait for the results page to settle: either a product grid or a
        # no-results message must be present before the test reads anything.
        self.wait.until(
            lambda d: d.find_elements(*testid("product-grid"))
            or d.find_elements(*testid("no-results"))
        )

    def open_cart(self) -> None:
        self._find(testid("cart-link")).click()

    def cart_count(self) -> int:
        return int(self._find(testid("cart-count")).text)


class MobileHomePage(MobileBasePage):
    def load(self) -> None:
        self.driver.get(f"{self.base_url}/")

    def product_names(self) -> list[str]:
        return self._texts(testid("product-name"))

    def add_product_to_cart_by_name(self, name: str) -> None:
        cards = self._find_all(testid("product-card"))
        for card in cards:
            if name in card.text:
                card.find_element(*testid("add-to-cart")).click()
                return
        raise AssertionError(f"Product not found on page: {name}")
