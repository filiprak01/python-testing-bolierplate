"""Filesystem cleanup preserves committed markers and unrelated data."""

from pathlib import Path

import pytest

from evidence.artifacts import clean_artifact_directory

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_cleanup_removes_generated_contents_but_preserves_marker_and_siblings(
    tmp_path: Path,
) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / ".gitkeep").touch()
    (artifacts / "old.log").write_text("generated", encoding="utf-8")
    nested = artifacts / "previous"
    nested.mkdir()
    (nested / "result.json").write_text("{}", encoding="utf-8")
    static = tmp_path / "fixture.txt"
    static.write_text("keep", encoding="utf-8")
    clean_artifact_directory(artifacts)
    assert [path.name for path in artifacts.iterdir()] == [".gitkeep"]
    assert static.read_text(encoding="utf-8") == "keep"
