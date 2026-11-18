"""Report installed tools and packages without downloads or service changes."""

import importlib.metadata
import json
import platform
import shutil
import sys


def package_version(name: str) -> str | None:
    """Read distribution metadata without importing package application code."""
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "python": sys.version.split()[0],
                "python_312_or_later": sys.version_info >= (3, 12),
                "platform": platform.system(),
                "executable": sys.executable,
                "packages": {
                    name: package_version(name)
                    for name in (
                        "pip",
                        "setuptools",
                        "wheel",
                        "selenium",
                        "pytest",
                        "allure-pytest",
                        "PyYAML",
                        "python-dotenv",
                        "pytest-xdist",
                        "paramiko",
                        "asyncssh",
                        "playwright",
                    )
                },
                "commands": {
                    name: shutil.which(name)
                    for name in (
                        "node",
                        "npm",
                        "google-chrome",
                        "chromium",
                        "chromedriver",
                        "playwright",
                        "ssh",
                        "sftp",
                        "sshd",
                        "psql",
                        "pg_isready",
                        "mariadb",
                        "mysql",
                        "redis-cli",
                    )
                },
                "note": (
                    "Optional tools are not installed automatically. "
                    "Check mirror and endpoint availability in the real environment."
                ),
            },
            indent=2,
        )
    )
