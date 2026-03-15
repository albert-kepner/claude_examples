from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from .config import Config
from .runner import run as run_pipeline

app = typer.Typer(help="Recursively discover git repositories and prepare to update them.")


def _version_callback(value: bool) -> None:
    if value:
        # We keep this simple for Phase 1 and align with pyproject.toml
        typer.echo("gitty-up version 0.1.0")
        raise typer.Exit()


@app.command()
def main(
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        resolve_path=True,
        help="Root directory to scan for git repositories (defaults to current directory).",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be done without performing any git operations.",
    ),
    exclude: List[str] = typer.Option(
        [],
        "--exclude",
        "-e",
        help="Exclude directories whose names contain this string (can be repeated).",
    ),
    max_depth: Optional[int] = typer.Option(
        None,
        "--max-depth",
        min=0,
        help="Maximum directory recursion depth (0 = only root, 1 = root + children, etc).",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        help="Include directories starting with '.'.",
    ),
    allow_dirty: bool = typer.Option(
        False,
        "--allow-dirty",
        help="Allow git operations in repositories with uncommitted changes.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Only print the final summary.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print git command output for each repository.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the gitty-up version and exit.",
    ),
) -> None:
    """Entry point command used by the console script."""
    root = path or Path.cwd()
    config = Config(
        root_path=root,
        dry_run=dry_run,
        exclude=exclude,
        max_depth=max_depth,
        include_hidden=include_hidden,
        allow_dirty=allow_dirty,
        quiet=quiet,
        verbose=verbose,
    )
    exit_code = run_pipeline(config)
    raise typer.Exit(code=exit_code)


def cli() -> None:
    """Invoke the Typer application (for manual use if needed)."""
    app()

