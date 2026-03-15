## Phase 3 Implementation Summary

- **Filtering and discovery options**: Added `--exclude`, `--max-depth`, and `--include-hidden` flags in the CLI and wired them through `Config` into `discover_repos`, which now performs a controlled directory walk that respects these options.
- **Dirty repo handling**: Introduced a `--allow-dirty` flag; by default dirty repositories are detected via `git status --porcelain` and skipped with a `DIRTY_SKIPPED` status, with a clear message on how to override.
- **Verbosity controls**: Implemented `--quiet` (suppress per-repo output, keep summary) and `--verbose` (show full git stdout/stderr per repo) with corresponding fields in `Config` and behavior changes in `runner`.
- **Improved summary and status UX**: `runner` now shows a more detailed summary (updated, up-to-date, dirty skipped, failed) and uses color-coded prefixes, including a yellow `[SKIP]` for dirty-skipped repositories; `--version` support remains via the Typer option and `__version__` in the package.

