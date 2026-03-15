from pathlib import Path

from gitty_up.config import Config
from gitty_up.discovery import discover_repos


def _make_repo(path: Path) -> None:
    (path / ".git").mkdir(parents=True, exist_ok=True)


def test_discover_repos_finds_single_repo(tmp_path: Path) -> None:
    repo_dir = tmp_path / "project"
    repo_dir.mkdir()
    _make_repo(repo_dir)

    config = Config(root_path=tmp_path)
    repos = discover_repos(tmp_path, config)

    assert repos == [repo_dir.resolve()]


def test_discover_repos_respects_exclude(tmp_path: Path) -> None:
    good = tmp_path / "keep"
    bad = tmp_path / "skip_me"
    good.mkdir()
    bad.mkdir()
    _make_repo(good)
    _make_repo(bad)

    config = Config(root_path=tmp_path, exclude=["skip"])
    repos = discover_repos(tmp_path, config)

    assert good.resolve() in repos
    assert bad.resolve() not in repos


def test_discover_repos_respects_max_depth(tmp_path: Path) -> None:
    level0 = tmp_path
    level1 = tmp_path / "level1"
    level2 = level1 / "level2"
    level1.mkdir()
    level2.mkdir(parents=True, exist_ok=True)
    _make_repo(level0)
    _make_repo(level1)
    _make_repo(level2)

    config = Config(root_path=tmp_path, max_depth=1)
    repos = discover_repos(tmp_path, config)

    assert level0.resolve() in repos
    assert level1.resolve() in repos
    assert level2.resolve() not in repos

