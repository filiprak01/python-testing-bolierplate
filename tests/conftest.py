"""Shared configuration, opt-in browser fixtures, and Allure failure evidence."""

import logging
from collections.abc import Generator
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from clients.ui_client import UIClient
from config.loader import load_config
from evidence.artifacts import clean_artifact_directory
from evidence.pytest_logging import attach_browser_evidence, attach_execution_log
from models.configuration import FrameworkConfig
from webdriver.factory import create_webdriver


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register explicit browser execution and headless-mode switches."""

    parser.addoption("--run-ui", action="store_true", help="Run tests marked ui; requires Chrome.")
    parser.addoption("--headless", action="store_true", help="Run browser tests without a window.")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Keep the default suite independent of browser installations and public sites."""

    if config.getoption("--run-ui"):
        return
    skip = pytest.mark.skip(reason="Browser tests require --run-ui and an installed Chrome.")
    for item in items:
        if "ui" in item.keywords:
            item.add_marker(skip)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Clean only validated generated directories, leaving collection non-destructive."""

    if session.config.option.collectonly:
        return
    paths = load_config().paths
    for directory in (
        paths.downloads,
        paths.screenshots,
        paths.logs,
        paths.allure_results,
        paths.reports,
    ):
        clean_artifact_directory(directory)


@pytest.fixture(scope="session")
def config() -> FrameworkConfig:
    """Load the framework configuration once per test session."""

    return load_config()


@pytest.fixture(scope="session", autouse=True)
def execution_log_path(config: FrameworkConfig) -> Generator[Path, None, None]:
    """Expose a session log while restoring the caller's root logging level afterward."""

    config.paths.logs.mkdir(parents=True, exist_ok=True)
    log_path = config.paths.logs / "test-execution.log"
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger = logging.getLogger()
    original_level = logger.level
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    try:
        yield log_path
    finally:
        logger.removeHandler(handler)
        logger.setLevel(original_level)
        handler.close()


@pytest.fixture
def driver(
    request: pytest.FixtureRequest, config: FrameworkConfig
) -> Generator[WebDriver, None, None]:
    """Own one configured browser and close it even if timeout setup fails."""

    if not request.config.getoption("--run-ui"):
        pytest.skip("The driver fixture requires --run-ui.")
    browser = create_webdriver(
        config.browser.name,
        headless=bool(request.config.getoption("--headless")) or config.browser.headless,
        download_directory=config.paths.downloads,
    )
    try:
        browser.implicitly_wait(config.timeouts.implicit_seconds)
        browser.set_page_load_timeout(config.timeouts.page_load_seconds)
        browser.set_script_timeout(config.timeouts.script_seconds)
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def ui_client(driver: WebDriver, config: FrameworkConfig) -> UIClient:
    """Wrap the fixture-owned browser with page access and evidence steps."""

    return UIClient(
        driver=driver,
        base_url=config.environment.base_url,
        screenshot_directory=config.paths.screenshots,
        timeout=config.timeouts.explicit_seconds,
        screenshots_enabled=config.evidence.screenshots_enabled,
        screenshot_after_steps=config.evidence.screenshot_after_steps,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[object],
) -> Generator[None, None, None]:
    """Attach available evidence for a failed test body."""

    del call
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    log_path = item.funcargs.get("execution_log_path")
    if isinstance(log_path, Path):
        attach_execution_log(log_path)
    browser = item.funcargs.get("driver")
    if isinstance(browser, WebDriver):
        attach_browser_evidence(browser)
