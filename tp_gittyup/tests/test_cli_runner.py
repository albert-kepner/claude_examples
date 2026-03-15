from pathlib import Path

from typer.testing import CliRunner

from gitty_up.cli import app
from gitty_up.config import Config
from gitty_up.discovery import discover_repos
from gitty_up.runner import run as run_pipeline


runner = CliRunner()


def test_runner_returns_zero_when_no_repos(tmp_path: Path) -> None:
    config = Config(root_path=tmp_path, dry_run=False)
    exit_code = run_pipeline(config)

    assert exit_code == 0


def test_discovery_and_runner_integration(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()

    config = Config(root_path=tmp_path, dry_run=True)
    repos = discover_repos(tmp_path, config)

    assert repo_dir.resolve() in repos

    exit_code = run_pipeline(config)
    assert exit_code == 0


def test_cli_dry_run_option(tmp_path: Path, monkeypatch: object) -> None:
    def fake_cwd() -> Path:
        return tmp_path

    from pathlib import Path as _Path  # noqa: N812

    monkeypatch.setattr(_Path, "cwd", staticmethod(fake_cwd))

    result = runner.invoke(app, ["--dry-run"])

    assert result.exit_code == 0

