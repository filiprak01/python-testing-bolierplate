"""Client ownership, pool cleanup, and evidence failure behavior."""

import logging
from pathlib import Path
from unittest.mock import Mock

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from clients.client_pool import UIClientPool
from clients.ui_client import UIClient

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_client_context_closes_browser_after_test_error() -> None:
    driver = Mock(spec=WebDriver)
    with pytest.raises(ValueError, match="original failure"), UIClient(driver=driver):
        raise ValueError("original failure")
    driver.quit.assert_called_once()


def test_pool_rejects_duplicates_without_leaking_the_original_client() -> None:
    driver = Mock(spec=WebDriver)
    with UIClientPool() as pool:
        original = pool.acquire(" primary ", driver=driver)
        with pytest.raises(ValueError, match="already registered"):
            pool.acquire("primary", driver=Mock(spec=WebDriver))
        assert pool.get("primary") is original
    driver.quit.assert_called_once()


def test_pool_attempts_every_close_when_one_browser_quit_fails() -> None:
    first, second = Mock(spec=WebDriver), Mock(spec=WebDriver)
    first.quit.side_effect = RuntimeError("browser already gone")
    pool = UIClientPool()
    pool.acquire("first", driver=first)
    pool.acquire("second", driver=second)
    with pytest.raises(ExceptionGroup, match="Unable to close") as raised:
        pool.close_all()
    second.quit.assert_called_once()
    assert len(raised.value.exceptions) == 1
    assert len(pool) == 0


@pytest.mark.parametrize("client_id", ["", " "])
def test_pool_rejects_empty_client_names(client_id: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        UIClientPool().acquire(client_id, driver=Mock(spec=WebDriver))


def test_open_resolves_relative_urls_and_logs_page_load_timeout(
    caplog: pytest.LogCaptureFixture,
) -> None:
    driver = Mock(spec=WebDriver)
    driver.get.side_effect = TimeoutException("page load")
    client = UIClient(driver=driver, base_url="https://example.test/")
    with caplog.at_level(logging.WARNING):
        client.open("/products")
    driver.get.assert_called_once_with("https://example.test/products")
    assert "PAGE LOAD TIMEOUT" in caplog.text


def test_screenshot_failure_does_not_replace_the_original_step_error() -> None:
    driver = Mock(spec=WebDriver)
    driver.get_screenshot_as_png.side_effect = RuntimeError("browser disconnected")
    client = UIClient(driver=driver, screenshot_after_steps=True)
    with pytest.raises(ValueError, match="business assertion"), client.step("Check item"):
        raise ValueError("business assertion")


def test_disabled_screenshot_capability_does_not_touch_browser(tmp_path: Path) -> None:
    driver = Mock(spec=WebDriver)
    client = UIClient(driver=driver, screenshots_enabled=False, screenshot_directory=tmp_path)
    client.capture_screenshot_step("Evidence disabled")
    driver.get_screenshot_as_png.assert_not_called()
    assert list(tmp_path.iterdir()) == []
