"""Tests for differ_commands."""
from __future__ import annotations
import json
import pathlib
import pytest
from argparse import Namespace
from envdrift.differ_commands import cmd_multi_diff


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _ns(**kwargs):
    defaults = dict(
        envs=[],
        ignore_values=False,
        ignore_file=None,
        export_json=None,
        exit_code=False,
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_returns_zero_no_drift(tmp_env):
    a = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    b = tmp_env("b.env", "FOO=bar\nBAZ=qux\n")
    assert cmd_multi_diff(_ns(envs=[a, b])) == 0


def test_returns_zero_with_drift_no_flag(tmp_env):
    a = tmp_env("a.env", "FOO=bar\n")
    b = tmp_env("b.env", "BAZ=qux\n")
    assert cmd_multi_diff(_ns(envs=[a, b])) == 0


def test_returns_one_with_drift_and_flag(tmp_env):
    a = tmp_env("a.env", "FOO=bar\n")
    b = tmp_env("b.env", "BAZ=qux\n")
    assert cmd_multi_diff(_ns(envs=[a, b], exit_code=True)) == 1


def test_missing_file_returns_one(tmp_env):
    a = tmp_env("a.env", "FOO=bar\n")
    assert cmd_multi_diff(_ns(envs=[a, "/no/such/file.env"])) == 1


def test_single_file_returns_one(tmp_env):
    a = tmp_env("a.env", "FOO=bar\n")
    assert cmd_multi_diff(_ns(envs=[a])) == 1


def test_export_json_creates_file(tmp_env, tmp_path):
    a = tmp_env("a.env", "FOO=bar\n")
    b = tmp_env("b.env", "FOO=bar\n")
    out = str(tmp_path / "out.json")
    cmd_multi_diff(_ns(envs=[a, b], export_json=out))
    data = json.loads(pathlib.Path(out).read_text())
    assert "has_drift" in data


def test_ignore_values_flag(tmp_env):
    a = tmp_env("a.env", "FOO=bar\n")
    b = tmp_env("b.env", "FOO=different\n")
    assert cmd_multi_diff(_ns(envs=[a, b], ignore_values=True, exit_code=True)) == 0
