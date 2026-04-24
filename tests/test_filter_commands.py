"""Tests for envdrift.filter_commands."""

import argparse
import os
import pytest

from envdrift.filter_commands import cmd_filter_diff, cmd_filter_multi


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content):
    path.write_text(content)
    return str(path)


def _ns(**kwargs):
    defaults = dict(
        include=None,
        exclude=None,
        only_missing=False,
        only_extra=False,
        only_changed=False,
        exit_code=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_filter_diff_no_drift_returns_zero(tmp_env):
    a = _write(tmp_env / "a.env", "KEY=val\n")
    b = _write(tmp_env / "b.env", "KEY=val\n")
    assert cmd_filter_diff(_ns(env_a=a, env_b=b)) == 0


def test_filter_diff_drift_no_flag_returns_zero(tmp_env):
    a = _write(tmp_env / "a.env", "KEY=val\n")
    b = _write(tmp_env / "b.env", "OTHER=val\n")
    assert cmd_filter_diff(_ns(env_a=a, env_b=b)) == 0


def test_filter_diff_drift_with_flag_returns_one(tmp_env):
    a = _write(tmp_env / "a.env", "KEY=val\n")
    b = _write(tmp_env / "b.env", "OTHER=val\n")
    assert cmd_filter_diff(_ns(env_a=a, env_b=b, exit_code=True)) == 1


def test_filter_diff_missing_file_returns_one(tmp_env):
    a = _write(tmp_env / "a.env", "KEY=val\n")
    assert cmd_filter_diff(_ns(env_a=a, env_b="/no/such.env")) == 1


def test_filter_diff_include_pattern_limits_drift(tmp_env):
    a = _write(tmp_env / "a.env", "DB_HOST=x\nAPP_NAME=foo\n")
    b = _write(tmp_env / "b.env", "DB_HOST=y\nAPP_NAME=foo\n")
    # only-changed + include DB_* should show drift
    ns = _ns(env_a=a, env_b=b, include=["DB_*"], only_changed=True, exit_code=True)
    assert cmd_filter_diff(ns) == 1


def test_filter_multi_no_drift_returns_zero(tmp_env):
    a = _write(tmp_env / "a.env", "KEY=val\n")
    b = _write(tmp_env / "b.env", "KEY=val\n")
    assert cmd_filter_multi(_ns(envs=[a, b])) == 0


def test_filter_multi_missing_file_returns_one(tmp_env):
    a = _write(tmp_env / "a.env", "KEY=val\n")
    assert cmd_filter_multi(_ns(envs=[a, "/no/such.env"])) == 1


def test_filter_multi_exit_code_on_drift(tmp_env):
    a = _write(tmp_env / "a.env", "KEY=val\n")
    b = _write(tmp_env / "b.env", "OTHER=val\n")
    assert cmd_filter_multi(_ns(envs=[a, b], exit_code=True)) == 1
