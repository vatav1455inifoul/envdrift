"""Tests for the CLI layer (envdrift/cli.py)."""

import pytest
from pathlib import Path

from envdrift.cli import run


@pytest.fixture
def tmp_env(tmp_path):
    """Helper that writes a .env file and returns its path."""
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


def test_no_drift_exits_zero(tmp_env):
    base = tmp_env(".env.base", "KEY=value\nFOO=bar\n")
    target = tmp_env(".env.target", "KEY=value\nFOO=bar\n")
    assert run([str(base), str(target)]) == 0


def test_drift_exits_zero_without_exit_code_flag(tmp_env):
    base = tmp_env(".env.base", "KEY=value\n")
    target = tmp_env(".env.target", "KEY=different\n")
    # drift present but --exit-code not set, should still return 0
    assert run([str(base), str(target)]) == 0


def test_drift_exits_one_with_exit_code_flag(tmp_env):
    base = tmp_env(".env.base", "KEY=value\n")
    target = tmp_env(".env.target", "KEY=different\n")
    assert run([str(base), str(target), "--exit-code"]) == 1


def test_missing_file_exits_two(tmp_env):
    base = tmp_env(".env.base", "KEY=value\n")
    assert run([str(base), "/nonexistent/.env.target"]) == 2


def test_ignore_values_flag_no_drift(tmp_env):
    base = tmp_env(".env.base", "KEY=value1\n")
    target = tmp_env(".env.target", "KEY=value2\n")
    # values differ but --ignore-values means no drift
    assert run([str(base), str(target), "--ignore-values", "--exit-code"]) == 0


def test_no_color_flag_accepted(tmp_env, capsys):
    base = tmp_env(".env.base", "KEY=value\n")
    target = tmp_env(".env.target", "KEY=value\n")
    code = run([str(base), str(target), "--no-color"])
    assert code == 0
    captured = capsys.readouterr()
    # ANSI escape codes should not appear
    assert "\033[" not in captured.out


def test_env_names_in_output(tmp_env, capsys):
    base = tmp_env(".env.staging", "KEY=value\n")
    target = tmp_env(".env.production", "KEY=value\n")
    run([str(base), str(target), "--no-color"])
    captured = capsys.readouterr()
    assert ".env.staging" in captured.out
    assert ".env.production" in captured.out


def test_missing_key_shown_in_output(tmp_env, capsys):
    base = tmp_env(".env.base", "ONLY_IN_BASE=x\nSHARED=y\n")
    target = tmp_env(".env.target", "SHARED=y\n")
    run([str(base), str(target), "--no-color"])
    captured = capsys.readouterr()
    assert "ONLY_IN_BASE" in captured.out
