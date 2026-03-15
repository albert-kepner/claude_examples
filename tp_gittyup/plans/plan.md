## High-level goals

- **Deliverable**: A professional-grade, shareable CLI app `gitty-up` that recursively finds git repos and runs `git pull --all` in each, with good UX, reliability, and safety.
- **Constraints**: Plan only in this phase (no code), but detailed enough that we can implement step-by-step next.

---

## 1. Product Definition

- **Primary user**: Developers with multiple projects and/or multiple machines who want to quickly sync all repos under a directory.
- **Core use case**: From a root folder (e.g., `~/dev`), run `gitty-up` to:
  - Discover all nested git repos.
  - For each repo, run `git pull --all`.
  - Show clear, colored status for each repo (success, up-to-date, error, skipped).
- **Non-goals (for v1)**:
  - No interactive conflict resolution wizard.
  - No GUI.
  - No git operations beyond safe “update” operations (`pull`, maybe `fetch`, configurable, include pull and fetch as defaults).

---

## 2. Scope for v1

- **Feature set v1**:
  - **CLI entry point** (`gitty-up` command).
  - **Recursive repo discovery** starting at current working directory or a provided path.
  - **Git status checks** (optional optimization: detect if anything to pull).
  - **Run `git pull --all`** per repo, capturing output and exit codes.
  - **Colored, concise summary** using `colorama` (e.g., green = updated/ok, yellow = skipped, red = error).
  - **Dry-run mode** (show what would be run, but don’t actually run git commands).
  - **Basic configuration**:
    - CLI flags (e.g., `--path`, `--max-depth`, `--exclude`, `--include-hidden`, `--dry-run`, `--concurrent N`).
  - **Robust logging** (to console; optional file logging).
  - **Graceful error handling** (bad repos, missing remotes, permission issues).
- **Out-of-scope for v1 (future)**:
  - Config files (YAML/JSON) for per-project rules.
  - Multi-remote policies (e.g., only pull origin).
  - Git credential management.
  - Parallel execution with advanced scheduling (we may still add simple concurrency if easy).

---

## 3. Technology & Architecture

- **Language**: Python 3.10+ (assumption; we can adjust).
- **Packaging / distribution**:
  - Standard Python package (e.g. `gitty_up`).
  - Installable via `pip` with console script entry point (`gitty-up`).
  - Include `colorama` dependency.
- **Architecture layers**:
  - **CLI layer**:
    - Argument parsing (likely `argparse` or `typer/click` if we want a nicer UX).
    - Translates CLI flags to internal config/options object.
  - **Core service layer**:
    - Repo discovery.
    - Execution orchestration (loop through repos, run commands).
    - Status aggregation.
  - **Git integration layer**:
    - Abstractions for running git commands.
    - Handles shell invocation, timeouts, exit codes, and output.
  - **Output / UI layer**:
    - Colorized log lines.
    - Structured summary at end.
- **Key design decisions**:
  - **File system traversal**:
    - Walk directories starting at root.
    - Identify git repos by the presence of `.git` directory.
    - Allow depth limiting and exclusions (patterns like `node_modules`, `.venv`).
  - **Execution model**:
    - Default: sequential per repo (simpler, safer).
    - Optional: simple concurrency (e.g., `--concurrent 4`) using threads or processes.
  - **Safety**:
    - Default: require clean working tree? (maybe warn if dirty; configurable `--allow-dirty`).
    - Dry-run to preview repos that will be touched and commands to be run.

---

## 4. Detailed Feature Breakdown

### 4.1 CLI interface

- **Command**: `gitty-up [options]`
- **Arguments / options**:
  - **Path selection**:
    - `--path PATH` (default = current working directory).
    - `--max-depth N` to limit recursion (0 = only root, 1 = root + children, etc).
  - **Filtering**:
    - `--exclude PATTERN` (can be repeated; glob-style or substring).
    - `--include-hidden` (include directories starting with `.`).
  - **Execution behavior**:
    - `--dry-run` (don’t execute git commands, just show plan).
    - `--no-color` (disable color output).
    - `--concurrent N` (advanced/v1.1).
    - `--allow-dirty` (don’t skip/warn about repos with uncommitted changes).
    - `--pull-args "..."` (additional arguments to `git pull`, e.g. `--rebase`).
  - **Output / verbosity**:
    - `-q/--quiet` (only show summary).
    - `-v/--verbose` (show full git output).
    - `--version`.
    - `--summary-style {table,list,json}` (JSON useful for scripting; maybe v1.1).
- **Behavior**:
  - Parse args, build a `Config` object (path, depth, flags).
  - Hand off to core orchestration function.

### 4.2 Repo discovery

- **Responsibility**: From a root path, find all directories that are git repos.
- **Rules**:
  - A directory is a repo if it contains `.git` (folder or file, to handle worktrees).
  - Once we find a repo at a path, decision:
    - **Default**: still scan its subdirectories because monorepos may contain nested repos (e.g., submodules or separate packages).
    - Option `--stop-at-repo` to stop descending into that repo’s subdirectories.
  - Respect `--exclude` patterns and `--max-depth`.
- **Outputs**:
  - A list of repo descriptors, each including:
    - Absolute path.
    - Relative path from root (for display).
    - Maybe repo name (folder name).
    - Flags (e.g., hidden, excluded but included by override, etc.).

### 4.3 Git operations per repo

- **Core function**:
  - Given a repo path and global config, perform:
    - Optional pre-checks:
      - `git status --porcelain` to detect dirty working trees.
      - Skip or warn if dirty (depending on `--allow-dirty`).
    - Execution:
      - Standard command: `git pull --all` (plus any `--pull-args`).
      - Capture stdout/stderr and exit code.
  - Wrap in try/except and OS error handling (e.g., git not installed).
- **Result model**:
  - For each repo, produce a `RepoResult` object:
    - `path`.
    - `status` enum: `UPDATED`, `UP_TO_DATE`, `DIRTY_SKIPPED`, `ERROR`, `SKIPPED_BY_FILTER`, etc.
    - `stdout` (optional, or truncated).
    - `stderr`.
    - `exit_code`.
    - `duration`.

### 4.4 Orchestration & concurrency

- **Sequential mode**:
  - Iterate through repos.
  - For each, call git operation and immediately print/log result with color.
- **Optional concurrent mode (if included)**:
  - Use thread pool or process pool.
  - Bound concurrency by `--concurrent N`.
  - Collect `RepoResult`s and print results as they complete.
- **Failure handling**:
  - Never abort all remaining repos on single failure by default.
  - Option `--fail-fast` to stop after first error.

### 4.5 Output and UX

- **Per-repo live output (non-quiet)**:
  - Prefix each line with a colored status symbol and repo name, e.g.:
    - Green `[OK] repo-name` for success/up-to-date.
    - Yellow `[SKIP] repo-name` for skipped (dirty, excluded, dry-run).
    - Red `[ERR] repo-name` for failures.
- **Final summary**:
  - Counts:
    - Total repos found.
    - Updated.
    - Up-to-date.
    - Skipped (dirty, excluded, other).
    - Failed.
  - If `--summary-style json`, print a JSON object (v1.1 task).
- **Color handling**:
  - Use `colorama` for cross-platform colors.
  - Fallback to plain text if `--no-color` or non-TTY.

---

## 5. Configuration & Extensibility

- **Internal configuration object**:
  - Encapsulate all options from CLI.
  - Makes it easy to call core functionality programmatically (e.g., from tests or other tools).
- **Future configuration file**:
  - Support `.gitty-up.yml` at project or user home (~/.gitty-up.yml).
  - Allow global defaults (e.g., default exclude patterns).
- **Plugin / extension points (later)**:
  - Option to run arbitrary commands before or after pulls.
  - Different strategies for each repo type (e.g., `npm install` after pull).

---

## 6. Quality, Testing, and Tooling

- **Project structure (conceptual)**:
  - `gitty_up/` package:
    - `cli.py` – entry point & argument parsing.
    - `config.py` – config models and defaults.
    - `discovery.py` – repo discovery logic.
    - `git_ops.py` – git command wrappers.
    - `runner.py` – orchestration and result aggregation.
    - `output.py` – color and formatting helpers.
    - `__init__.py`.
  - `tests/` – unit tests & some integration tests.
  - `pyproject.toml` or `setup.py` – packaging and dependencies.
  - `README.md`, `LICENSE`, `CHANGELOG.md`.
- **Testing strategy**:
  - **Unit tests**:
    - Repo discovery with mocked directory structure.
    - Config parsing from CLI args.
    - Git command wrapper using mocks (no real git in unit tests).
  - **Integration tests**:
    - Use a temp directory with small git repos initialized during tests.
    - Run the CLI with `--dry-run` and with real `git pull` against dummy remotes.
  - **Static checks**:
    - `flake8` or `ruff` for linting.
    - `black` or `ruff format` for formatting.
    - `mypy` (optional) for type checking.
- **CI/CD**:
  - GitHub Actions (or similar) to:
    - Run tests on push/PR.
    - Lint/type-check.
    - Optionally publish to PyPI on tag.

---

## 7. Safety & Edge Cases

- **Edge cases to handle**:
  - No git repos found (graceful message, exit code 0 or 1? Probably 0 with explanation).
  - Git not installed or not on PATH.
  - Repos with:
    - Missing `origin` or any remote.
    - Shallow clones.
    - Submodules.
    - Worktrees (where `.git` is a file).
  - Permission errors when traversing directories.
- **Data safety**:
  - Avoid destructive operations: we only run `git pull --all` by default.
  - Warn clearly when working in dirty repos (and default to skip or require `--allow-dirty`).
  - Avoid rewriting history (no `--force`, no `reset`, etc.).

---

## 8. Milestones / Implementation Phases

- **Phase 1: Skeleton & core CLI**
  - Set up Python project structure and packaging.
  - Implement CLI stub with `--version` and basic `--path` and `--dry-run`.
  - Implement minimal discovery and a fake operation (no git yet).
- **Phase 2: Basic functionality**
  - Implement real repo discovery.
  - Implement git wrapper that runs `git pull --all` sequentially.
  - Add `colorama`-based colored output.
  - Add basic error handling and summary.
- **Phase 3: UX polish & options**
  - Add filtering (`--exclude`, `--max-depth`, `--include-hidden`).
  - Add dirty-repo handling and `--allow-dirty`.
  - Add verbosity flags (`--quiet`, `--verbose`).
  - Improve summary formatting.
- **Phase 4: Testing, docs, and packaging**
  - Write comprehensive unit and basic integration tests.
  - Polish README with examples and screenshots/asciinema.
  - Add license and contribution guidelines.
  - Prepare for PyPI release (metadata, versioning).
- **Phase 5: Optional enhancements**
  - Simple concurrency (`--concurrent`).
  - JSON summary output.
  - Config file support.

---

## 9. Next steps

- Confirmed preferences:
  - **CLI framework**: use `typer`/`click`.
  - **Packaging approach**: modern `pyproject.toml`
- After confirmation, begin **Phase 1** implementation based on this plan.

