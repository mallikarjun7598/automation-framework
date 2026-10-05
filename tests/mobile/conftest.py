"""Pytest fixtures for the mobile-web (Appium) suite.

This suite is a working scaffold. It runs for real when an Appium server and a
device/emulator are available; otherwise every mobile test SKIPS (rather than
fails) so the overall pipeline stays green on machines without a mobile setup.

To run mobile tests for real:
  1. Install Appium:            npm i -g appium
  2. Install a driver:
       iOS:     appium driver install xcuitest   (requires Xcode + Simulator)
       Android: appium driver install uiautomator2 (requires Android SDK + emulator)
  3. Start the server:          appium
  4. Start the app:             PORT=5001 python -m app.server   (or set BASE_URL)
  5. Run:                       pytest tests/mobile -m mobile \
                                  --appium --platform ios

Environment variables:
  APPIUM_URL     default http://127.0.0.1:4723
  MOBILE_PLATFORM  ios | android  (default ios)
  BASE_URL       URL the mobile browser should hit. On Android emulator this
                 must be reachable from the emulator (e.g. http://10.0.2.2:5001).
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_APPIUM_URL = "http://127.0.0.1:4723"


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--appium",
        action="store_true",
        default=False,
        help="Actually attempt to connect to Appium (otherwise mobile tests skip).",
    )
    parser.addoption(
        "--platform",
        action="store",
        default=os.environ.get("MOBILE_PLATFORM", "ios"),
        choices=["ios", "android"],
        help="Mobile platform to target.",
    )


def _appium_is_up(url: str) -> bool:
    """Return True if an Appium server answers at <url>/status."""
    try:
        with urllib.request.urlopen(f"{url}/status", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def appium_url() -> str:
    return os.environ.get("APPIUM_URL", DEFAULT_APPIUM_URL)


@pytest.fixture(scope="session")
def mobile_base_url() -> str:
    """URL the mobile browser hits. Defaults differ per platform."""
    if os.environ.get("BASE_URL"):
        return os.environ["BASE_URL"].rstrip("/")
    # Android emulator reaches the host via 10.0.2.2; iOS Simulator shares host net.
    platform = os.environ.get("MOBILE_PLATFORM", "ios")
    host = "10.0.2.2" if platform == "android" else "127.0.0.1"
    return f"http://{host}:5001"


@pytest.fixture()
def mobile_driver(request, appium_url, mobile_base_url):
    """Create an Appium WebDriver for a mobile browser session.

    Skips the test (does not fail) when --appium is not passed or no Appium
    server is reachable, keeping the suite green without a device.
    """
    if not request.config.getoption("--appium"):
        pytest.skip("Mobile tests require --appium (and a running Appium server).")

    if not _appium_is_up(appium_url):
        pytest.skip(f"No Appium server reachable at {appium_url}.")

    # Imported lazily so the module import never fails when Appium isn't used.
    from appium import webdriver
    from appium.options.ios import XCUITestOptions
    from appium.options.android import UiAutomator2Options

    platform = request.config.getoption("--platform")
    if platform == "ios":
        options = XCUITestOptions()
        options.browser_name = "Safari"
        # Defaults match a modern Simulator; override via env for your machine.
        options.platform_version = os.environ.get("IOS_VERSION", "17.0")
        options.device_name = os.environ.get("IOS_DEVICE", "iPhone 15")
        # Safari's remote web inspector can be slow to expose the page on a
        # freshly booted sim. Give it more time and let WDA start Safari itself.
        options.set_capability("appium:webviewConnectTimeout", 30000)
        options.set_capability("appium:safariInitialUrl", mobile_base_url)
        options.set_capability("appium:newCommandTimeout", 120)
    else:
        options = UiAutomator2Options()
        options.browser_name = "Chrome"
        options.device_name = os.environ.get("ANDROID_DEVICE", "emulator-5554")
        options.set_capability("appium:newCommandTimeout", 120)

    driver = webdriver.Remote(appium_url, options=options)
    driver.implicitly_wait(5)
    try:
        yield driver
    finally:
        driver.quit()
