"""Tests for envdrift.digest_commands."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envdrift.digest_commands import cmd_digest


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"strict": False, "exit_code": False, "json": False, "no_color": True}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_returns_zero_single_file(tmp_env):
    path = tmp_env("a.env", "KEY=val\n")
    assert cmd_digest(_ns(files=[path])) == 0


def test_missing_file_returns_one(tmp_env):
    assert cmd_digest(_ns(files=["/no/such/file.env"])) == 1


def test_no_drift_returns_zero(tmp_env):
    p1 = tmp_env("a.env", "KEY=val\n")
    p2 = tmp_env("b.env", "KEY=val\n")
    assert cmd_digest(_ns(files=[p1, p2], exit_code=True)) == 0


def test_drift_exit_code_returns_one(tmp_env):
    p1 = tmp_env("a.env", "KEY=val\n")
    p2 = tmp_env("b.env", "KEY=other\n")
    assert cmd_digest(_ns(files=[p1, p2], exit_code=True)) == 1


def test_drift_without_exit_code_flag_returns_zero(tmp_env):
    p1 = tmp_env("a.env", "KEY=val\n")
    p2 = tmp_env("b.env", "KEY=other\n")
    assert cmd_digest(_ns(files=[p1, p2], exit_code=False)) == 0


def test_json_output_is_valid(tmp_env, capsys):
    path = tmp_env("a.env", "KEY=val\n")
    ret = cmd_digest(_ns(files=[path], json=True))
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["env_name"] == "a"


def test_strict_mode_detects_comment_diff(tmp_env):
    p1 = tmp_env("a.env", "KEY=val\n")
    p2 = tmp_env("b.env", "# note\nKEY=val\n")
    # without strict: same content → 0
    assert cmd_digest(_ns(files=[p1, p2], exit_code=True, strict=False)) == 0
    # with strict: bytes differ → 1
    assert cmd_digest(_ns(files=[p1, p2], exit_code=True, strict=True)) == 1
