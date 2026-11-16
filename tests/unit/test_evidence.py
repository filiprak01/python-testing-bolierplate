"""Failure diagnostics remain best-effort when the browser or report sink fails."""

from unittest.mock import Mock

import pytest
from selenium.webdriver.chrome.webdriver import WebDriver

from evidence import pytest_logging

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_screenshot_error_does_not_discard_page_source_or_browser_logs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    driver = Mock(spec=WebDriver)
    driver.get_screenshot_as_png.side_effect = RuntimeError("disconnected screenshot channel")
    driver.page_source = "<p>Useful page state</p>"
    driver.get_log.return_value = [{"level": "WARNING", "message": "fixture diagnostic"}]
    attach = Mock()
    monkeypatch.setattr(pytest_logging.allure, "attach", attach)
    pytest_logging.attach_browser_evidence(driver)
    assert [call.kwargs["name"] for call in attach.call_args_list] == [
        "failure-page-source",
        "failure-browser-logs",
    ]
    assert attach.call_args_list[0].args[0] == driver.page_source
    assert "fixture diagnostic" in attach.call_args_list[1].args[0]


def test_attachment_sink_errors_do_not_escape_the_evidence_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    driver = Mock(spec=WebDriver)
    driver.get_screenshot_as_png.return_value = b"fixture-image"
    driver.page_source = "<p>Useful page state</p>"
    driver.get_log.return_value = []
    attach = Mock(side_effect=OSError("report destination unavailable"))
    monkeypatch.setattr(pytest_logging.allure, "attach", attach)
    pytest_logging.attach_browser_evidence(driver)
    assert attach.call_count == 3
    driver.get_log.assert_called_once_with("browser")
