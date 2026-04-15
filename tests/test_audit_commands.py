"""Tests for envdrift.audit_commands."""

import argparse
import json
from pathlib import Path

import pytest

from envdrift.audit_commands import cmd_audit_list, cmd_audit_record, cmd_audit_show
from envdrift.auditor import record_audit


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "env_files": [".env.dev"],
        "drift": False,
        "summary": "test run",
        "notes": "",
        "audit_dir": "",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def audit_dir(tmp_path: Path) -> str:
    return str(tmp_path / "audits")


def test_record_returns_zero(audit_dir: str) -> None:
    ns = _ns(audit_dir=audit_dir)
    assert cmd_audit_record(ns) == 0


def test_record_creates_file(audit_dir: str, capsys) -> None:
    ns = _ns(audit_dir=audit_dir, drift=True, summary="2 diffs")
    cmd_audit_record(ns)
    out = capsys.readouterr().out
    assert "Audit recorded" in out


def test_list_empty(audit_dir: str, capsys) -> None:
    ns = _ns(audit_dir=audit_dir)
    rc = cmd_audit_list(ns)
    assert rc == 0
    assert "No audit entries found" in capsys.readouterr().out


def test_list_shows_entries(audit_dir: str, capsys) -> None:
    record_audit(
        env_files=[".env.dev", ".env.prod"],
        drift_detected=True,
        summary="key mismatch",
        audit_dir=audit_dir,
    )
    ns = _ns(audit_dir=audit_dir)
    rc = cmd_audit_list(ns)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DRIFT" in out
    assert "key mismatch" in out


def test_show_valid_entry(audit_dir: str, capsys) -> None:
    path = record_audit(
        env_files=[".env"],
        drift_detected=False,
        summary="clean",
        audit_dir=audit_dir,
    )
    ns = argparse.Namespace(path=str(path))
    rc = cmd_audit_show(ns)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["summary"] == "clean"


def test_show_missing_returns_one(tmp_path: Path) -> None:
    ns = argparse.Namespace(path=str(tmp_path / "nope.json"))
    assert cmd_audit_show(ns) == 1
