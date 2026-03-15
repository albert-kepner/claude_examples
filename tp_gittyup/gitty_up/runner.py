from __future__ import annotations

from pathlib import Path

from colorama import Fore, Style, init as colorama_init

from .config import Config
from .discovery import discover_repos
from .git_ops import RepoResult, RepoStatus, pull_all


def _format_repo_line(result: RepoResult) -> str:
    repo_name = result.path.name

    if result.status == RepoStatus.UPDATED:
        prefix = f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
    elif result.status == RepoStatus.UP_TO_DATE:
        prefix = f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
    else:
        prefix = f"{Fore.RED}[ERR]{Style.RESET_ALL}"

    return f"{prefix} {repo_name} ({result.path})"


def run(config: Config) -> int:
    """Core orchestration for Phase 2.

    - Discovers git repositories under the configured root.
    - Runs `git pull --all` sequentially in each repo.
    - Prints colored, per-repo status lines and a final summary.
    """
    colorama_init()

    root: Path = config.root_path
    repos = discover_repos(root)

    if not repos:
        print(f"No git repositories found under {root}")
        return 0

    results: list[RepoResult] = []

    for repo in repos:
        if config.dry_run:
            print(f"[DRY RUN] Would run `git pull --all` in {repo}")
            # For consistency, still record a synthetic result.
            results.append(
                RepoResult(
                    path=repo,
                    status=RepoStatus.UP_TO_DATE,
                    stdout="(dry run) git pull --all",
                    stderr="",
                    exit_code=0,
                )
            )
            continue

        result = pull_all(repo, dry_run=False)
        results.append(result)

        print(_format_repo_line(result))
        if result.exit_code != 0 and result.stderr:
            print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")

    total = len(results)
    updated = sum(1 for r in results if r.status == RepoStatus.UPDATED)
    up_to_date = sum(1 for r in results if r.status == RepoStatus.UP_TO_DATE)
    errors = sum(1 for r in results if r.status == RepoStatus.ERROR)

    print()
    print("Summary:")
    print(f"  Total repos:   {total}")
    print(f"  Updated/OK:    {updated + up_to_date}")
    print(f"  Failed:        {errors}")

    return 1 if errors else 0

