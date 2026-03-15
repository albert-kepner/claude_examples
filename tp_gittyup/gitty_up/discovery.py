from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


def discover_repos(root: Path) -> List[Path]:
    """Minimal repo discovery for Phase 1.

    A directory is considered a git repo if it contains a `.git` entry.
    """
    root = root.resolve()
    repos: set[Path] = set()

    for path in root.rglob(".git"):
        if path.is_dir() or path.is_file():
            repos.add(path.parent)

    return sorted(repos)

