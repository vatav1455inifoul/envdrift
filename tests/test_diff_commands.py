"""Tests for envdrift/diff_commands.py"""
import argparse
import pytest
from pathlib import Path
from envdrift.diff_commands import cmd_diff


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str):
    p.write_text(content)
    return p


def _ns(a, b, ignore_values=False, ignore_file=None, exit_code=False):
    return argparse.Namespace(
        env_a=str(a), env_b=str(b),
        ignore_values=ignore_values,
        ignore_file=ignore_file,
        exit_code=exit_code,
    )


def test_returns_zero_no_drift(tmp_env):
    a = _write(tmp_env / "a.env", "FOO=bar\nBAZ=qux\n")
    b = _write(tmp_env / "b.env", "FOO=bar\nBAZ=qux\n")
    assert cmd_diff(_ns(a, b)) == 0


def test_returns_zero_with_drift_no_flag(tmp_env):
    a = _write(tmp_env / "a.env", "FOO=bar\n")
    b = _write(tmp_env / "b.env", "FOO=different\n")
    assert cmd_diff(_ns(a, b)) == 0


def test_returns_one_with_drift_and_flag(tmp_env):
    a = _write(tmp_env / "a.env", "FOO=bar\n")
    b = _write(tmp_env / "b.env", "FOO=different\n")
    assert cmd_diff(_ns(a, b, exit_code=True)) == 1


def test_missing_file_a_returns_one(tmp_env):
    b = _write(tmp_env / "b.env", "FOO=bar\n")
    ns = _ns(tmp_env / "nope.env", b)
    assert cmd_diff(ns) == 1


def test_missing_file_b_returns_one(tmp_env):
    a = _write(tmp_env / "a.env", "FOO=bar\n")
    ns = _ns(a, tmp_env / "nope.env")
    assert cmd_diff(ns) == 1


def test_ignore_values_flag(tmp_env):
    a = _write(tmp_env / "a.env", "FOO=bar\n")
    b = _write(tmp_env / "b.env", "FOO=totally_different\n")
    # Same keys, different values — with ignore_values no drift
    assert cmd_diff(_ns(a, b, ignore_values=True, exit_code=True)) == 0


def test_ignore_file_filters_keys(tmp_env):
    a = _write(tmp_env / "a.env", "FOO=bar\nSECRET=abc\n")
    b = _write(tmp_env / "b.env", "FOO=bar\n")
    ig = _write(tmp_env / ".envdriftignore", "SECRET\n")
    # SECRET is ignored so no drift
    assert cmd_diff(_ns(a, b, ignore_file=str(ig), exit_code=True)) == 0
