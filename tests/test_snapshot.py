"""Tests for envdrift.snapshot module."""

import json
import os
import pytest

from envdrift.snapshot import (
    create_snapshot,
    load_snapshot,
    save_snapshot,
    snapshot_summary,
    _validate_snapshot,
)

SAMPLE_ENV = {"APP_ENV": "production", "DB_HOST": "db.prod.example.com", "DEBUG": "false"}


def test_create_snapshot_structure():
    snap = create_snapshot("prod", SAMPLE_ENV)
    assert snap["env_name"] == "prod"
    assert snap["values"] == SAMPLE_ENV
    assert snap["version"] == 1
    assert "created_at" in snap
    assert snap["notes"] == ""


def test_create_snapshot_with_notes():
    snap = create_snapshot("staging", SAMPLE_ENV, notes="before deploy")
    assert snap["notes"] == "before deploy"


def test_save_and_load_roundtrip(tmp_path):
    snap = create_snapshot("prod", SAMPLE_ENV)
    path = str(tmp_path / "prod.snapshot.json")
    save_snapshot(snap, path)
    assert os.path.exists(path)
    loaded = load_snapshot(path)
    assert loaded["env_name"] == "prod"
    assert loaded["values"] == SAMPLE_ENV


def test_save_creates_parent_dirs(tmp_path):
    snap = create_snapshot("prod", SAMPLE_ENV)
    path = str(tmp_path / "snapshots" / "prod.json")
    save_snapshot(snap, path)
    assert os.path.exists(path)


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_snapshot(str(tmp_path / "nope.json"))


def test_validate_snapshot_missing_fields():
    with pytest.raises(ValueError, match="missing required fields"):
        _validate_snapshot({"env_name": "x", "values": {}})


def test_validate_snapshot_bad_values_type():
    with pytest.raises(ValueError, match="must be a dict"):
        _validate_snapshot(
            {"version": 1, "env_name": "x", "created_at": "now", "values": ["oops"]}
        )


def test_snapshot_summary_no_notes():
    snap = create_snapshot("dev", {"KEY": "val"})
    summary = snapshot_summary(snap)
    assert "[dev]" in summary
    assert "1 keys" in summary


def test_snapshot_summary_with_notes():
    snap = create_snapshot("dev", {"A": "1", "B": "2"}, notes="hotfix")
    summary = snapshot_summary(snap)
    assert "hotfix" in summary
    assert "2 keys" in summary


def test_saved_file_is_valid_json(tmp_path):
    snap = create_snapshot("ci", {"CI": "true"})
    path = str(tmp_path / "ci.json")
    save_snapshot(snap, path)
    with open(path) as fh:
        data = json.load(fh)
    assert data["env_name"] == "ci"
