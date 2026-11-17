"""Configuration defaults and boundaries that protect project files."""

from pathlib import Path
from typing import Any

import pytest

from models.configuration import FrameworkConfig

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_optional_browser_and_evidence_values_have_real_defaults(
    configuration_mapping: dict[str, Any],
    tmp_path: Path,
) -> None:
    configuration_mapping["browser"] = {}
    configuration_mapping.pop("evidence")
    config = FrameworkConfig.from_mapping(configuration_mapping, tmp_path)
    assert config.browser.name == "chrome"
    assert config.browser.headless is False
    assert config.evidence.screenshots_enabled is True
    assert config.evidence.screenshot_after_steps is False
    assert config.paths.uploads == tmp_path / "data" / "uploads"


@pytest.mark.parametrize("value", [0, -1, True, "10", None])
def test_invalid_explicit_timeouts_are_rejected(
    configuration_mapping: dict[str, Any],
    tmp_path: Path,
    value: object,
) -> None:
    configuration_mapping["timeouts"]["explicit_seconds"] = value
    with pytest.raises(ValueError, match="positive integer"):
        FrameworkConfig.from_mapping(configuration_mapping, tmp_path)


@pytest.mark.parametrize("section", ["environment", "browser", "timeouts", "paths"])
def test_required_sections_must_be_mappings(
    configuration_mapping: dict[str, Any],
    tmp_path: Path,
    section: str,
) -> None:
    configuration_mapping[section] = []
    with pytest.raises(ValueError, match="must be a mapping"):
        FrameworkConfig.from_mapping(configuration_mapping, tmp_path)


@pytest.mark.parametrize(
    "path",
    [".", "..", "src", "src/generated", "tests", ".git", "data", "data/fixtures"],
)
def test_cleanup_paths_cannot_target_source_or_static_inputs(
    configuration_mapping: dict[str, Any],
    tmp_path: Path,
    path: str,
) -> None:
    configuration_mapping["paths"]["logs"] = path
    with pytest.raises(ValueError, match="Artifact directories"):
        FrameworkConfig.from_mapping(configuration_mapping, tmp_path)


def test_overlapping_generated_directories_are_rejected(
    configuration_mapping: dict[str, Any],
    tmp_path: Path,
) -> None:
    configuration_mapping["paths"]["screenshots"] = "logs/screenshots"
    with pytest.raises(ValueError, match="must not overlap each other"):
        FrameworkConfig.from_mapping(configuration_mapping, tmp_path)


def test_custom_artifact_directories_are_supported(
    configuration_mapping: dict[str, Any],
    tmp_path: Path,
) -> None:
    configuration_mapping["paths"]["logs"] = "output/logs"
    config = FrameworkConfig.from_mapping(configuration_mapping, tmp_path)
    assert config.paths.logs == tmp_path / "output" / "logs"
