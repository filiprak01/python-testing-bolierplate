"""Opt-in Selenium integration against a real, local, deterministic application."""

from collections.abc import Generator
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from assertions.page_assertions import assert_element_text, assert_page_title
from clients.ui_client import UIClient
from models.configuration import FrameworkConfig
from pages.base_page import BasePage
from project import FIXTURES_PATH

pytestmark = [pytest.mark.framework, pytest.mark.integration, pytest.mark.ui]


class SandboxPage(BasePage):
    """Actions and assertions for the committed local fixture."""

    def greet(self, name: str) -> None:
        self.fill((By.ID, "name"), name)
        self.click((By.ID, "greet"))

    def assert_greeting(self, name: str) -> None:
        assert_page_title(self.driver, "Local testing sandbox")
        assert_element_text(self.driver, (By.ID, "greeting"), f"Hello, {name}!")

    def download_sample(self) -> None:
        self.click((By.ID, "download"))


@pytest.fixture(scope="module")
def sandbox_url() -> Generator[str, None, None]:
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(SimpleHTTPRequestHandler, directory=str(FIXTURES_PATH)),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/ui_sandbox.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.functional
def test_browser_form_and_screenshot(ui_client: UIClient, sandbox_url: str) -> None:
    with ui_client.step("Open the local application"):
        ui_client.open(sandbox_url)
    page = ui_client.page(SandboxPage)
    with ui_client.step("Enter a synthetic test name"):
        page.greet("Test User")
    with ui_client.step("Verify the updated greeting"):
        page.assert_greeting("Test User")
    directory = ui_client.screenshot_directory
    assert directory is not None
    before = set(directory.glob("*.png"))
    ui_client.capture_screenshot_step("Local greeting evidence")
    screenshots = set(directory.glob("*.png")) - before
    assert len(screenshots) == 1
    assert screenshots.pop().read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


@pytest.mark.functional
def test_browser_download_matches_the_committed_fixture(
    ui_client: UIClient,
    sandbox_url: str,
    config: FrameworkConfig,
    driver: WebDriver,
) -> None:
    ui_client.open(sandbox_url)
    with ui_client.step("Download the local sample"):
        ui_client.page(SandboxPage).download_sample()
    target: Path = config.paths.downloads / "sample.txt"
    WebDriverWait(driver, 10).until(lambda _driver: target.is_file())
    assert target.read_text(encoding="utf-8") == (FIXTURES_PATH / "sample.txt").read_text(
        encoding="utf-8",
    )


def test_missing_element_keeps_a_useful_assertion_failure(
    ui_client: UIClient,
    sandbox_url: str,
    driver: WebDriver,
) -> None:
    ui_client.open(sandbox_url)
    with pytest.raises(AssertionError, match="element missing or stale") as raised:
        assert_element_text(driver, (By.ID, "missing-status"), "Complete", timeout=0.1)
    assert isinstance(raised.value.__cause__, TimeoutException)
