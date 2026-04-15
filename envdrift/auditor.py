"""Audit trail: record when and how drift was detected."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_AUDIT_DIR = ".envdrift/audits"


def _audit_path(audit_dir: str = DEFAULT_AUDIT_DIR) -> Path:
    return Path(audit_dir)


def record_audit(
    env_files: list[str],
    drift_detected: bool,
    summary: str,
    audit_dir: str = DEFAULT_AUDIT_DIR,
    notes: str = "",
) -> Path:
    """Write a single audit entry as a JSON file and return its path."""
    audit_dir_path = _audit_path(audit_dir)
    audit_dir_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    slug = timestamp.replace(":", "-").replace("+", "Z").split(".")[0]
    filename = audit_dir_path / f"audit_{slug}.json"

    entry: dict[str, Any] = {
        "timestamp": timestamp,
        "env_files": env_files,
        "drift_detected": drift_detected,
        "summary": summary,
        "notes": notes,
    }

    filename.write_text(json.dumps(entry, indent=2))
    return filename


def load_audit(path: str | Path) -> dict[str, Any]:
    """Load a single audit entry from disk."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Audit file not found: {p}")
    return json.loads(p.read_text())


def list_audits(audit_dir: str = DEFAULT_AUDIT_DIR) -> list[Path]:
    """Return all audit files sorted oldest-first."""
    d = _audit_path(audit_dir)
    if not d.exists():
        return []
    return sorted(d.glob("audit_*.json"))


def audit_summary(entry: dict[str, Any]) -> str:
    """Return a one-line human-readable summary of an audit entry."""
    status = "DRIFT" if entry["drift_detected"] else "OK"
    files = ", ".join(entry["env_files"])
    return f"[{entry['timestamp']}] {status} | {files} | {entry['summary']}"
