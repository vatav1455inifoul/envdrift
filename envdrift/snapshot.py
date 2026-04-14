"""Snapshot management for envdrift — save and load env snapshots for later comparison."""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

SNAPSHOT_VERSION = 1


def create_snapshot(env_name: str, parsed_env: Dict[str, str], notes: Optional[str] = None) -> dict:
    """Create a snapshot dict from a parsed env."""
    return {
        "version": SNAPSHOT_VERSION,
        "env_name": env_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes or "",
        "values": parsed_env,
    }


def save_snapshot(snapshot: dict, path: str) -> None:
    """Write a snapshot to a JSON file."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)
        fh.write("\n")


def load_snapshot(path: str) -> dict:
    """Load a snapshot from a JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Snapshot file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    _validate_snapshot(data)
    return data


def _validate_snapshot(data: dict) -> None:
    """Raise ValueError if the snapshot is malformed."""
    required = {"version", "env_name", "created_at", "values"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Snapshot is missing required fields: {missing}")
    if not isinstance(data["values"], dict):
        raise ValueError("Snapshot 'values' must be a dict")


def snapshot_summary(snapshot: dict) -> str:
    """Return a human-readable one-liner summary of a snapshot."""
    name = snapshot["env_name"]
    created = snapshot["created_at"]
    count = len(snapshot["values"])
    notes = f" — {snapshot['notes']}" if snapshot.get("notes") else ""
    return f"[{name}] {count} keys, saved {created}{notes}"
