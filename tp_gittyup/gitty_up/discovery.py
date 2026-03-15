from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

from .config import Config


def _should_skip_dir(
    path: Path,
    *,
    depth: int,
    config: Config,
) -> bool:
    name = path.name

    if not config.include_hidden and name.startswith("."):
        return True

    for pattern in config.exclude:
        if pattern and pattern in name:
            return True

    if config.max_depth is not None and depth > config.max_depth:
        return True

    return False


def discover_repos(root: Path, config: Config) -> List[Path]:
    """Discover git repositories under ``root`` honoring Phase 3 options.

    A directory is considered a git repo if it contains a `.git` entry.
    We continue descending into repositories to allow nested repos.
    """
    root = root.resolve()
    repos: set[Path] = set()

    stack: list[tuple[Path, int]] = [(root, 0)]

    while stack:
        current, depth = stack.pop()

        git_entry = current / ".git"
        if git_entry.exists():
            repos.add(current)

        try:
            for child in current.iterdir():
                if not child.is_dir():
                    continue
                if _should_skip_dir(child, depth=depth + 1, config=config):
                    continue
                stack.append((child, depth + 1))
        except PermissionError:
            # Skip directories we cannot access.
            continue

    return sorted(repos)

