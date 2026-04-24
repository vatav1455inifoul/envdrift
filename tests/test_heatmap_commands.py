"""Tests for envdrift.heatmap_commands."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envdrift.heatmap_commands import cmd_heatmap, register_heatmap_subcommand


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"mode": "multi", "top": 0}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_returns_zero_no_drift(tmp_env, capsys):
    a = tmp_env("a.env", "A=1\nB=2\n")
    b = tmp_env("b.env", "A=1\nB=2\n")
    rc = cmd_heatmap(_ns(envs=[str(a), str(b)]))
    assert rc == 0


def test_returns_zero_with_drift(tmp_env, capsys):
    a = tmp_env("a.env", "A=1\nB=hello\n")
    b = tmp_env("b.env", "A=99\nB=hello\n")
    rc = cmd_heatmap(_ns(envs=[str(a), str(b)]))
    assert rc == 0


def test_missing_file_returns_one(tmp_env, capsys):
    a = tmp_env("a.env", "A=1\n")
    rc = cmd_heatmap(_ns(envs=[str(a), "/no/such/file.env"]))
    assert rc == 1


def test_single_file_returns_one(tmp_env, capsys):
    a = tmp_env("a.env", "A=1\n")
    rc = cmd_heatmap(_ns(envs=[str(a)]))
    assert rc == 1


def test_pair_mode_works(tmp_env, capsys):
    a = tmp_env("a.env", "A=1\nB=2\n")
    b = tmp_env("b.env", "A=9\nB=2\n")
    c = tmp_env("c.env", "A=7\nB=2\n")
    rc = cmd_heatmap(_ns(envs=[str(a), str(b), str(c)], mode="pair"))
    assert rc == 0


def test_top_flag_limits_output(tmp_env, capsys):
    a = tmp_env("a.env", "A=1\nB=2\nC=3\nD=4\n")
    b = tmp_env("b.env", "A=9\nB=8\nC=7\nD=6\n")
    rc = cmd_heatmap(_ns(envs=[str(a), str(b)], top=2))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Heatmap" in out


def test_register_creates_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_heatmap_subcommand(sub)
    args = parser.parse_args(["heatmap", "a.env", "b.env"])
    assert hasattr(args, "func")
