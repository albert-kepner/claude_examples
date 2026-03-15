## Gitty Up

`gitty-up` is a small CLI tool for developers who work across many local git repositories.  
Run it once at the root of your source tree and it will recursively find git repos and run `git pull --all` in each one, with clear colorized output and a concise summary.

### Features

- **Recursive discovery**: Walks a directory tree and detects git repositories by the presence of a `.git` entry.
- **Safe updates**: Runs `git pull --all` in each repository, with clear success and error reporting.
- **Dry-run mode**: Preview what would be updated without touching any repos.
- **Filtering & depth control**: Exclude directories, control maximum depth, and choose whether to include hidden directories.
- **Dirty-repo handling**: Skip repositories with uncommitted changes unless explicitly allowed.
- **Colorful UX**: Uses `colorama` to highlight success, skips, and errors.

### Installation

Once published to PyPI you will be able to install `gitty-up` with:

```bash
pip install gitty-up
```

For local development from this repository:

```bash
pip install -e .
```

### Usage

From the directory that contains your projects (for example, `~/dev`):

```bash
gitty-up
```

Common options:

- `--path PATH` – root directory to scan (defaults to the current working directory).
- `--dry-run` – show which repositories would be updated without running git.
- `--exclude PATTERN` – exclude directories whose names contain `PATTERN` (can be repeated).
- `--max-depth N` – limit recursion depth (`0` = only root, `1` = root + children, etc).
- `--include-hidden` – include directories starting with `.`.
- `--allow-dirty` – allow git operations in repositories with uncommitted changes.
- `--quiet` / `--verbose` – control how much output is shown.
- `--version` – print the `gitty-up` version and exit.

Example:

```bash
gitty-up --path ~/dev --exclude .venv --exclude node_modules --dry-run
```

### Development

- **Tests**: This project uses `pytest`. From the project root:

  ```bash
  pytest
  ```

- **Code style**: The project targets Python 3.14+ and is structured as a standard `pyproject.toml`-based package.

### License

`gitty-up` is released under the MIT License. See `LICENSE` for details.
