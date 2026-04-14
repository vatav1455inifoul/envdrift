"""Tests for envdrift.snapshot_commands."""

import os
import pytest

from envdrift.snapshot_commands import cmd_snapshot_save, cmd_snapshot_diff, cmd_snapshot_info
from envdrift.snapshot import create_snapshot, save_snapshot


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


@pytest.fixture()
def saved_snap(tmp_path):
    snap = create_snapshot("base", {"APP": "v1", "DB": "localhost"})
    path = str(tmp_path / "base.json")
    save_snapshot(snap, path)
    return path


def test_save_creates_file(tmp_env, tmp_path):
    env = tmp_env("APP=hello\nDB=world\n")
    out = str(tmp_path / "out.json")
    code = cmd_snapshot_save(env, "dev", out)
    assert code == 0
    assert os.path.exists(out)


def test_save_missing_env_returns_1(tmp_path):
    out = str(tmp_path / "out.json")
    code = cmd_snapshot_save("/nonexistent/.env", "dev", out)
    assert code == 1


def test_diff_no_drift_returns_0(tmp_env, saved_snap):
    env = tmp_env("APP=v1\nDB=localhost\n")
    code = cmd_snapshot_diff(env, saved_snap)
    assert code == 0


def test_diff_with_drift_no_exit_flag_returns_0(tmp_env, saved_snap):
    env = tmp_env("APP=v2\nDB=localhost\n")
    code = cmd_snapshot_diff(env, saved_snap, use_exit_code=False)
    assert code == 0


def test_diff_with_drift_exit_flag_returns_1(tmp_env, saved_snap):
    env = tmp_env("APP=v2\n")
    code = cmd_snapshot_diff(env, saved_snap, use_exit_code=True)
    assert code == 1


def test_diff_missing_snapshot_returns_1(tmp_env, tmp_path):
    env = tmp_env("APP=v1\n")
    code = cmd_snapshot_diff(env, str(tmp_path / "ghost.json"))
    assert code == 1


def test_diff_missing_env_returns_1(saved_snap):
    code = cmd_snapshot_diff("/no/.env", saved_snap)
    assert code == 1


def test_info_prints_summary(saved_snap, capsys):
    code = cmd_snapshot_info(saved_snap)
    assert code == 0
    out = capsys.readouterr().out
    assert "base" in out
    assert "APP" in out


def test_info_missing_file_returns_1(tmp_path):
    code = cmd_snapshot_info(str(tmp_path / "nope.json"))
    assert code == 1
