"""Tests for envdrift.auditor."""

import json
from pathlib import Path

import pytest

from envdrift.auditor import (
    audit_summary,
    list_audits,
    load_audit,
    record_audit,
)


@pytest.fixture()
def audit_dir(tmp_path: Path) -> str:
    return str(tmp_path / "audits")


def test_record_creates_file(audit_dir: str) -> None:
    path = record_audit(
        env_files=[".env.dev", ".env.prod"],
        drift_detected=True,
        summary="2 keys differ",
        audit_dir=audit_dir,
    )
    assert path.exists()
    assert path.suffix == ".json"


def test_record_content_is_valid(audit_dir: str) -> None:
    path = record_audit(
        env_files=[".env.dev"],
        drift_detected=False,
        summary="no drift",
        audit_dir=audit_dir,
        notes="nightly run",
    )
    data = json.loads(path.read_text())
    assert data["drift_detected"] is False
    assert data["summary"] == "no drift"
    assert data["notes"] == "nightly run"
    assert ".env.dev" in data["env_files"]
    assert "timestamp" in data


def test_load_audit_roundtrip(audit_dir: str) -> None:
    path = record_audit(
        env_files=[".env.staging"],
        drift_detected=True,
        summary="1 key missing",
        audit_dir=audit_dir,
    )
    entry = load_audit(path)
    assert entry["drift_detected"] is True
    assert entry["summary"] == "1 key missing"


def test_load_audit_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_audit(tmp_path / "nonexistent.json")


def test_list_audits_empty(audit_dir: str) -> None:
    assert list_audits(audit_dir) == []


def test_list_audits_sorted(audit_dir: str) -> None:
    for i in range(3):
        record_audit(
            env_files=[".env"],
            drift_detected=False,
            summary=f"run {i}",
            audit_dir=audit_dir,
        )
    entries = list_audits(audit_dir)
    assert len(entries) == 3
    names = [e.name for e in entries]
    assert names == sorted(names)


def test_audit_summary_ok() -> None:
    entry = {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "env_files": [".env.dev", ".env.prod"],
        "drift_detected": False,
        "summary": "all good",
    }
    result = audit_summary(entry)
    assert "OK" in result
    assert ".env.dev" in result
    assert "all good" in result


def test_audit_summary_drift() -> None:
    entry = {
        "timestamp": "2024-06-15T12:00:00+00:00",
        "env_files": [".env.prod"],
        "drift_detected": True,
        "summary": "3 keys differ",
    }
    result = audit_summary(entry)
    assert "DRIFT" in result
    assert "3 keys differ" in result
