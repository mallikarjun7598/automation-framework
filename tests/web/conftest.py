"""Pytest fixtures for the web suite.

Key idea: the suite is self-contained. It starts the Flask app in a background
process before the tests run and shuts it down afterwards, so you don't have to
start the server manually. Set BASE_URL to point tests at an already-running
instance instead (useful in CI).
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOST = "127.0.0.1"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((DEFAULT_HOST, 0))
        return s.getsockname()[1]


def _wait_for_health(url: str, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 - we retry until healthy
            last_err = exc
            time.sleep(0.3)
    raise RuntimeError(f"App did not become healthy at {url}: {last_err}")


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL of the app under test.

    If BASE_URL is set in the environment, use it (assume app already running).
    Otherwise start a fresh Flask process on a free port for the whole session.
    """
    external = os.environ.get("BASE_URL")
    if external:
        _wait_for_health(f"{external.rstrip('/')}/health")
        yield external.rstrip("/")
        return

    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "app.server"],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PORT": str(port), "HOST": DEFAULT_HOST},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://{DEFAULT_HOST}:{port}"
    try:
        _wait_for_health(f"{url}/health")
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
