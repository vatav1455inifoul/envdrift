"""Tests for envdrift.watcher."""

import os
import time
import pytest
from pathlib import Path

from envdrift.watcher import watch_envs, _get_mtimes


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str):
    path.write_text(content)


def test_get_mtimes_existing_files(tmp_env):
    a = tmp_env / "a.env"
    b = tmp_env / "b.env"
    _write(a, "X=1")
    _write(b, "X=2")
    mtimes = _get_mtimes([str(a), str(b)])
    assert str(a) in mtimes
    assert str(b) in mtimes
    assert mtimes[str(a)] > 0
    assert mtimes[str(b)] > 0


def test_get_mtimes_missing_file(tmp_env):
    missing = str(tmp_env / "ghost.env")
    mtimes = _get_mtimes([missing])
    assert mtimes[missing] == -1.0


def test_watch_detects_change(tmp_env):
    base = tmp_env / "base.env"
    cmp = tmp_env / "cmp.env"
    _write(base, "KEY=hello\nFOO=bar")
    _write(cmp, "KEY=hello\nFOO=bar")

    collected = []

    def on_change(report: str):
        collected.append(report)

    # Run one iteration with no change — nothing should fire
    watch_envs(
        str(base),
        str(cmp),
        interval=0.05,
        on_change=on_change,
        max_iterations=1,
    )
    assert collected == []

    # Modify cmp and run another iteration
    time.sleep(0.05)
    _write(cmp, "KEY=world\nFOO=bar")

    watch_envs(
        str(base),
        str(cmp),
        interval=0.05,
        on_change=on_change,
        max_iterations=1,
    )
    assert len(collected) == 1
    assert "KEY" in collected[0]


def test_watch_missing_file_reports_error(tmp_env):
    base = tmp_env / "base.env"
    cmp = tmp_env / "missing.env"
    _write(base, "KEY=1")
    # cmp does not exist — force a fake mtime change by using -1 sentinel

    collected = []

    # Patch _get_mtimes indirectly by just running; missing file => -1 stays -1
    # We need at least one change event; easiest: write base after watcher starts.
    # Instead, directly test that a FileNotFoundError path is handled gracefully.
    # We simulate by running with a non-existent compare path and touching base.
    time.sleep(0.05)
    base.touch()  # update mtime to trigger change detection

    watch_envs(
        str(base),
        str(cmp),
        interval=0.05,
        on_change=lambda r: collected.append(r),
        max_iterations=1,
    )
    # Should have caught FileNotFoundError and reported it
    assert any("not found" in m.lower() or "envdrift" in m.lower() for m in collected)
