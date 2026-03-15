from __future__ import annotations

from pathlib import Path

from .config import Config
from .discovery import discover_repos


def run(config: Config) -> int:
    """Core orchestration for Phase 1.

    Performs minimal discovery and a fake operation (no real git commands yet).
    """
    root: Path = config.root_path
    repos = discover_repos(root)

    if not repos:
        print(f"No git repositories found under {root}")
        return 0

    for repo in repos:
        if config.dry_run:
            print(f"[DRY RUN] Would process repo at {repo}")
        else:
            # Phase 1: fake operation only, no real git commands yet.
            print(f"Pretending to update repo at {repo}")

    return 0

