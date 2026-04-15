"""Tests for envdrift.baseline_commands."""

from __future__ import annotations

from pathlib import Path
import argparse

import pytest

from envdrift.baseline_commands import cmd_baseline_save, cmd_baseline_diff, cmd_baseline_list
from envdrift.snapshot import create_snapshot, save_snapshot


@pytest.fixture()
def tmp_env(tmp_path):
    env = tmp_path / ".env"
    env.write_text("HOST=localhost\nPORT=5432\n")
    return env


@pytest.fixture()
def saved_snap(tmp_path, tmp_env):
    snap = create_snapshot(tmp_env, env_name="base")
    snap_path = tmp_path / "snap.json"
    save_snapshot(snap, snap_path)
    return snap_path


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


def test_save_creates_baseline(tmp_path, saved_snap):
    bl_dir = tmp_path / "bl"
    args = _ns(snapshot=str(saved_snap), name="prod")
    # patch default dir by monkeypatching not needed; test via return code
    # We rely on the default dir but can't easily override; use integration style
    import envdrift.baseline as bl_mod
    orig = bl_mod.DEFAULT_BASELINE_DIR
    bl_mod.DEFAULT_BASELINE_DIR = bl_dir
    try:
        rc = cmd_baseline_save(args)
        assert rc == 0
        assert (bl_dir / "prod.baseline.json").exists()
    finally:
        bl_mod.DEFAULT_BASELINE_DIR = orig


def test_save_missing_snapshot_returns_1(tmp_path):
    args = _ns(snapshot=str(tmp_path / "nope.json"), name="x")
    assert cmd_baseline_save(args) == 1


def test_diff_no_drift_returns_0(tmp_path, tmp_env, saved_snap):
    import envdrift.baseline as bl_mod
    bl_dir = tmp_path / "bl"
    bl_mod.DEFAULT_BASELINE_DIR = bl_dir
    try:
        cmd_baseline_save(_ns(snapshot=str(saved_snap), name="base"))
        args = _ns(env_file=str(tmp_env), name="base", exit_code=True)
        assert cmd_baseline_diff(args) == 0
    finally:
        bl_mod.DEFAULT_BASELINE_DIR = bl_mod.Path(".envdrift/baselines")


def test_diff_missing_baseline_returns_1(tmp_path, tmp_env):
    import envdrift.baseline as bl_mod
    bl_mod.DEFAULT_BASELINE_DIR = tmp_path / "empty_bl"
    try:
        args = _ns(env_file=str(tmp_env), name="ghost", exit_code=False)
        assert cmd_baseline_diff(args) == 1
    finally:
        bl_mod.DEFAULT_BASELINE_DIR = bl_mod.Path(".envdrift/baselines")


def test_list_empty(tmp_path, capsys):
    import envdrift.baseline as bl_mod
    bl_mod.DEFAULT_BASELINE_DIR = tmp_path / "none"
    try:
        rc = cmd_baseline_list(_ns())
        assert rc == 0
        assert "No baselines" in capsys.readouterr().out
    finally:
        bl_mod.DEFAULT_BASELINE_DIR = bl_mod.Path(".envdrift/baselines")
