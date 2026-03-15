from pathlib import Path
from typing import Any

from gitty_up.git_ops import RepoResult, RepoStatus, _is_dirty, pull_all


class DummyCompleted:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_is_dirty_true(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], **_: Any) -> DummyCompleted:  # type: ignore[override]
        calls.append(args)
        return DummyCompleted(returncode=0, stdout=" M file.py\n", stderr="")

    import subprocess  # noqa: WPS433

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert _is_dirty(tmp_path) is True
    assert calls and calls[0][:3] == ["git", "status", "--porcelain"]


def test_is_dirty_false(monkeypatch: Any, tmp_path: Path) -> None:
    def fake_run(*_: Any, **__: Any) -> DummyCompleted:  # type: ignore[override]
        return DummyCompleted(returncode=0, stdout="", stderr="")

    import subprocess  # noqa: WPS433

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert _is_dirty(tmp_path) is False


def test_pull_all_dry_run(tmp_path: Path) -> None:
    result = pull_all(tmp_path, dry_run=True, allow_dirty=False)

    assert isinstance(result, RepoResult)
    assert result.status is RepoStatus.UP_TO_DATE
    assert "dry run" in result.stdout
    assert result.exit_code == 0


def test_pull_all_skips_dirty_when_not_allowed(monkeypatch: Any, tmp_path: Path) -> None:
    def fake_is_dirty(_: Path) -> bool:
        return True

    monkeypatch.setattr("gitty_up.git_ops._is_dirty", fake_is_dirty)

    result = pull_all(tmp_path, dry_run=False, allow_dirty=False)

    assert result.status is RepoStatus.DIRTY_SKIPPED
    assert result.exit_code == 0
    assert "skipped" in result.stdout.lower()


def test_pull_all_invokes_git_pull(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_is_dirty(_: Path) -> bool:
        return False

    def fake_run(args: list[str], **_: Any) -> DummyCompleted:  # type: ignore[override]
        calls.append(args)
        return DummyCompleted(returncode=0, stdout="up to date", stderr="")

    monkeypatch.setattr("gitty_up.git_ops._is_dirty", fake_is_dirty)

    import subprocess  # noqa: WPS433

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = pull_all(tmp_path, dry_run=False, allow_dirty=True)

    assert calls and calls[0][:3] == ["git", "pull", "--all"]
    assert result.status is RepoStatus.UPDATED
    assert result.exit_code == 0

