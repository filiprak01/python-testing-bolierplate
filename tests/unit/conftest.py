"""Fresh copies of the real default configuration for validation tests."""

from typing import Any

import pytest
import yaml

from project import DEFAULT_CONFIG_PATH


@pytest.fixture
def configuration_mapping() -> dict[str, Any]:
    return yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
