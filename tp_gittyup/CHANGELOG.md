## Changelog

### 0.1.0

- Initial public version of `gitty-up`.
- Recursive discovery of git repositories under a root directory.
- Sequential `git pull --all` execution per repository with colorized output.
- CLI options for `--path`, `--dry-run`, `--exclude`, `--max-depth`, `--include-hidden`, `--allow-dirty`, `--quiet`, `--verbose`, and `--version`.
- Basic safety around dirty working trees and missing git installations.
- Test suite using `pytest` covering discovery, git operations, and CLI/runner integration.

