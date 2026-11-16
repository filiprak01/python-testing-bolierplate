"""Real YAML, environment, filesystem, and client integration without a browser."""

import logging
from logging.handlers import MemoryHandler
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml
from selenium.webdriver.remote.webdriver import WebDriver

from clients.ui_client import UIClient
from config import loader
from evidence.artifacts import clean_artifact_directory
from evidence.pytest_logging import attach_execution_log
from project import DEFAULT_CONFIG_PATH

pytestmark = [pytest.mark.framework, pytest.mark.integration]


@pytest.fixture
def runtime_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for variable in ("TEST_CONFIG_FILE", "TEST_BASE_URL", "TEST_BROWSER", "TEST_HEADLESS"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setattr(loader, "load_dotenv", Mock())
    monkeypatch.setattr(loader, "PROJECT_ROOT", tmp_path)
    config_file = tmp_path / "runtime.yaml"
    config_file.write_text(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setenv("TEST_CONFIG_FILE", "runtime.yaml")
    return config_file


def test_yaml_and_environment_control_navigation_and_persisted_evidence(
    runtime_config: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_BASE_URL", "https://example.test/")
    monkeypatch.setenv("TEST_HEADLESS", "true")
    config = loader.load_config()
    driver = Mock(spec=WebDriver)
    driver.get_screenshot_as_png.return_value = b"fixture-image"
    with UIClient(
        driver=driver,
        base_url=config.environment.base_url,
        screenshot_directory=config.paths.screenshots,
    ) as client:
        client.open("/items")
        client.capture_screenshot_step("Item details")
    driver.get.assert_called_once_with("https://example.test/items")
    driver.quit.assert_called_once()
    screenshots = list(config.paths.screenshots.glob("*.png"))
    assert len(screenshots) == 1
    assert screenshots[0].read_bytes() == b"fixture-image"
    assert config.browser.headless is True
    assert runtime_config.is_file()


def test_yaml_placeholders_expand_before_validation(
    runtime_config: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mapping = yaml.safe_load(runtime_config.read_text(encoding="utf-8"))
    mapping["environment"]["base_url"] = "${SANDBOX_URL}"
    runtime_config.write_text(yaml.safe_dump(mapping), encoding="utf-8")
    monkeypatch.setenv("SANDBOX_URL", "https://fixture.test/")
    assert loader.load_config().environment.base_url == "https://fixture.test/"


@pytest.mark.parametrize("value", ["yes", "0"])
def test_invalid_boolean_override_has_an_actionable_error(
    runtime_config: Path,
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("TEST_HEADLESS", value)
    with pytest.raises(ValueError, match="TEST_HEADLESS must be true or false"):
        loader.load_config(runtime_config)


def test_cleanup_of_configured_outputs_preserves_uploaded_and_static_files(
    runtime_config: Path,
) -> None:
    config = loader.load_config(runtime_config)
    for directory in (config.paths.uploads, config.paths.fixtures, config.paths.logs):
        directory.mkdir(parents=True)
        (directory / "example.txt").write_text("fixture", encoding="utf-8")
    clean_artifact_directory(config.paths.logs)
    assert list(config.paths.logs.iterdir()) == []
    assert (config.paths.uploads / "example.txt").read_text(encoding="utf-8") == "fixture"
    assert (config.paths.fixtures / "example.txt").read_text(encoding="utf-8") == "fixture"


def test_explicit_config_path_takes_precedence_over_environment(
    runtime_config: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_CONFIG_FILE", "missing.yaml")
    assert loader.load_config(runtime_config).browser.name == "chrome"


def test_execution_log_flushes_buffered_records_before_attachment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    log_path = tmp_path / "buffered.log"
    destination = logging.FileHandler(log_path, encoding="utf-8")
    buffer = MemoryHandler(capacity=100, flushLevel=logging.CRITICAL, target=destination)
    root = logging.getLogger()
    root.addHandler(buffer)
    attached_text: list[str] = []

    def record_file(path: str, **_metadata: object) -> None:
        attached_text.append(Path(path).read_text(encoding="utf-8"))

    monkeypatch.setattr("evidence.pytest_logging.allure.attach.file", record_file)
    try:
        logging.getLogger("framework.evidence.test").info("Buffered fixture diagnostic")
        assert log_path.read_text(encoding="utf-8") == ""
        attach_execution_log(log_path)
        assert len(attached_text) == 1
        assert "Buffered fixture diagnostic" in attached_text[0]
    finally:
        root.removeHandler(buffer)
        buffer.close()
        destination.close()
