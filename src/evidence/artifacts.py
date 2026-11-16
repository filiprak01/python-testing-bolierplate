"""Cleanup of generated files within a validated project artifact directory."""

import shutil
from pathlib import Path


def clean_artifact_directory(directory: Path) -> None:
    """Remove generated contents, retaining the directory and its .gitkeep file.

    Callers must validate configured paths before invoking this function.
    Directory symlinks are unlinked rather than followed.
    """

    directory.mkdir(parents=True, exist_ok=True)
    for path in directory.iterdir():
        if path.name == ".gitkeep":
            continue
        if path.is_symlink():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
