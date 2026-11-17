"""Load YAML configuration into framework dataclasses."""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from models.configuration import FrameworkConfig
from project import DEFAULT_CONFIG_PATH, PROJECT_ROOT


def load_config(config_path: Path | None = None) -> FrameworkConfig:
    """Load a YAML configuration file after loading local environment variables."""
    load_dotenv(PROJECT_ROOT / ".env")
    selected_path = config_path or Path(os.environ.get("TEST_CONFIG_FILE", DEFAULT_CONFIG_PATH))
    if not selected_path.is_absolute():
        selected_path = PROJECT_ROOT / selected_path

    with selected_path.open(encoding="utf-8") as config_file:
        raw_values = yaml.safe_load(config_file) or {}

    if not isinstance(raw_values, dict):
        raise ValueError("The root of the YAML configuration must be a mapping.")

    values = _expand_environment_variables(raw_values)
    overrides = (
        ("TEST_BASE_URL", "environment", "base_url"),
        ("TEST_BROWSER", "browser", "name"),
        ("TEST_HEADLESS", "browser", "headless"),
    )
    for variable, section_name, key in overrides:
        value = os.environ.get(variable)
        if not value:
            continue
        section = values.setdefault(section_name, {})
        if not isinstance(section, dict):
            raise ValueError(f"Configuration section '{section_name}' must be a mapping.")
        if variable == "TEST_HEADLESS":
            value = value.strip().lower()
            if value not in {"true", "false"}:
                raise ValueError("TEST_HEADLESS must be true or false.")
            section[key] = value == "true"
        else:
            section[key] = value
    return FrameworkConfig.from_mapping(values, PROJECT_ROOT)


def _expand_environment_variables(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {key: _expand_environment_variables(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_environment_variables(item) for item in value]
    return value
