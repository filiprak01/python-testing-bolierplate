"""Browser option construction and useful assertion failures."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from assertions import page_assertions
from webdriver import factory
from webdriver.chrome_options import build_chrome_options

pytestmark = pytest.mark.unit


def test_chrome_options_configure_headless_and_absolute_download_paths(tmp_path: Path) -> None:
    options = build_chrome_options(
        headless=True,
        download_directory=tmp_path,
        extra_arguments=("--window-size=1280,800",),
    )
    assert "--headless=new" in options.arguments
    assert "--window-size=1280,800" in options.arguments
    assert options.experimental_options["prefs"]["download.default_directory"] == str(tmp_path)


@pytest.mark.parametrize("browser", ["firefox", "edge", ""])
def test_factory_rejects_unsupported_browsers_before_starting_a_process(browser: str) -> None:
    with pytest.raises(ValueError, match="Unsupported browser"):
        factory.create_webdriver(browser)


def test_factory_passes_an_explicit_driver_service(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    constructor = Mock(return_value=Mock(spec=WebDriver))
    monkeypatch.setattr(factory.webdriver, "Chrome", constructor)
    path = tmp_path / "chromedriver.exe"
    result = factory.create_webdriver(driver_path=path, headless=True)
    assert result is constructor.return_value
    assert constructor.call_args.kwargs["service"].path == str(path)


def test_missing_element_after_timeout_retains_assertion_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wait = Mock(side_effect=TimeoutException("wait expired"))
    monkeypatch.setattr(page_assertions, "_wait", wait)
    driver = Mock(spec=WebDriver)
    driver.find_element.side_effect = NoSuchElementException("element removed")
    with pytest.raises(AssertionError, match="element missing or stale") as raised:
        page_assertions.assert_element_text(driver, (By.ID, "status"), "Complete")
    assert isinstance(raised.value.__cause__, TimeoutException)
