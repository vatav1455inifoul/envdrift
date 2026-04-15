"""Tests for envdrift.baseline module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdrift.baseline import (
    save_baseline,
    load_baseline,
    list_baselines,
    diff_against_baseline,
    baseline_has_drift,
    baseline_path,
)
from envdrift.snapshot import save_snapshot, create_snapshot


@pytest.fixture()
def tmp_snap(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n")
    snap = create_snapshot(env_file, env_name="test")
    snap_path = tmp_path / "snap.json"
    save_snapshot(snap, snap_path)
    return snap_path, snap


def test_save_baseline_creates_file(tmp_path, tmp_snap):
    snap_path, _ = tmp_snap
    dest = save_baseline(snap_path, "prod", directory=tmp_path / "bl")
    assert dest.exists()
    assert dest.name == "prod.baseline.json"


def test_load_baseline_roundtrip(tmp_path, tmp_snap):
    snap_path, snap = tmp_snap
    save_baseline(snap_path, "staging", directory=tmp_path / "bl")
    loaded = load_baseline("staging", directory=tmp_path / "bl")
    assert loaded["variables"] == snap["variables"]


def test_load_baseline_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="No baseline named"):
        load_baseline("nonexistent", directory=tmp_path)


def test_list_baselines_empty(tmp_path):
    assert list_baselines(directory=tmp_path / "empty") == []


def test_list_baselines_multiple(tmp_path, tmp_snap):
    snap_path, _ = tmp_snap
    bl_dir = tmp_path / "bl"
    save_baseline(snap_path, "prod", directory=bl_dir)
    save_baseline(snap_path, "staging", directory=bl_dir)
    names = list_baselines(directory=bl_dir)
    assert names == ["prod", "staging"]


def test_diff_no_drift():
    snap = {"variables": {"A": "1", "B": "2"}}
    diff = diff_against_baseline(snap, snap)
    assert not baseline_has_drift(diff)


def test_diff_detects_added():
    base = {"variables": {"A": "1"}}
    curr = {"variables": {"A": "1", "B": "2"}}
    diff = diff_against_baseline(curr, base)
    assert "B" in diff["added"]
    assert baseline_has_drift(diff)


def test_diff_detects_removed():
    base = {"variables": {"A": "1", "B": "2"}}
    curr = {"variables": {"A": "1"}}
    diff = diff_against_baseline(curr, base)
    assert "B" in diff["removed"]


def test_diff_detects_changed():
    base = {"variables": {"A": "old"}}
    curr = {"variables": {"A": "new"}}
    diff = diff_against_baseline(curr, base)
    assert diff["changed"]["A"] == ("old", "new")
