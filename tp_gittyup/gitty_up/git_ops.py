from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional

import subprocess


class RepoStatus(Enum):
    UPDATED = auto()
    UP_TO_DATE = auto()
    DIRTY_SKIPPED = auto()
    ERROR = auto()


@dataclass(slots=True)
class RepoResult:
    path: Path
    status: RepoStatus
    stdout: str
    stderr: str
    exit_code: int


def _is_dirty(repo_path: Path) -> bool:
    """Return True if the repository has uncommitted changes."""
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        # If we cannot run git at all, treat as not-dirty here and let
        # the pull step surface the underlying problem.
        return False

    return bool(completed.stdout.strip())


def pull_all(
    repo_path: Path,
    *,
    dry_run: bool = False,
    allow_dirty: bool = False,
) -> RepoResult:
    """Run `git pull --all` inside the given repository with Phase 3 rules."""
    if dry_run:
        # In dry-run mode, we never invoke git; we just report what
        # would have happened.
        return RepoResult(
            path=repo_path,
            status=RepoStatus.UP_TO_DATE,
            stdout="(dry run) git pull --all",
            stderr="",
            exit_code=0,
        )

    if not allow_dirty and _is_dirty(repo_path):
        # Skip dirty repositories unless explicitly allowed.
        return RepoResult(
            path=repo_path,
            status=RepoStatus.DIRTY_SKIPPED,
            stdout="Working tree has uncommitted changes; skipped. Use --allow-dirty to override.",
            stderr="",
            exit_code=0,
        )

    try:
        completed = subprocess.run(
            ["git", "pull", "--all"],
            cwd=repo_path,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        # Git is not installed or not on PATH.
        return RepoResult(
            path=repo_path,
            status=RepoStatus.ERROR,
            stdout="",
            stderr=str(exc),
            exit_code=127,
        )
    except OSError as exc:
        # Generic OS-level failure.
        return RepoResult(
            path=repo_path,
            status=RepoStatus.ERROR,
            stdout="",
            stderr=str(exc),
            exit_code=1,
        )

    status = RepoStatus.UPDATED if completed.returncode == 0 else RepoStatus.ERROR

    return RepoResult(
        path=repo_path,
        status=status,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
    )

