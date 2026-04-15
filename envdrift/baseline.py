"""Baseline management: mark a snapshot as the accepted baseline and diff against it."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envdrift.snapshot import load_snapshot, _validate_snapshot

DEFAULT_BASELINE_DIR = Path(".envdrift/baselines")


def baseline_path(name: str, directory: Path = DEFAULT_BASELINE_DIR) -> Path:
    """Return the path for a named baseline file."""
    return directory / f"{name}.baseline.json"


def save_baseline(snapshot_path: Path, name: str, directory: Path = DEFAULT_BASELINE_DIR) -> Path:
    """Copy a snapshot to the baseline store under *name*.

    Returns the path where the baseline was written.
    """
    snap = load_snapshot(snapshot_path)  # validates on load
    directory.mkdir(parents=True, exist_ok=True)
    dest = baseline_path(name, directory)
    dest.write_text(json.dumps(snap, indent=2))
    return dest


def load_baseline(name: str, directory: Path = DEFAULT_BASELINE_DIR) -> dict:
    """Load a previously saved baseline by name.

    Raises FileNotFoundError if no baseline with that name exists.
    """
    path = baseline_path(name, directory)
    if not path.exists():
        raise FileNotFoundError(f"No baseline named '{name}' found at {path}")
    data = json.loads(path.read_text())
    _validate_snapshot(data)
    return data


def list_baselines(directory: Path = DEFAULT_BASELINE_DIR) -> list[str]:
    """Return names of all saved baselines (without extension)."""
    if not directory.exists():
        return []
    return sorted(
        p.name.replace(".baseline.json", "")
        for p in directory.glob("*.baseline.json")
    )


def diff_against_baseline(current: dict, baseline: dict) -> dict:
    """Compare *current* snapshot values against *baseline*.

    Returns a dict with keys: added, removed, changed.
    Each value is a dict of {key: value} or {key: (baseline_val, current_val)}.
    """
    base_vars: dict = baseline.get("variables", {})
    curr_vars: dict = current.get("variables", {})

    added = {k: v for k, v in curr_vars.items() if k not in base_vars}
    removed = {k: v for k, v in base_vars.items() if k not in curr_vars}
    changed = {
        k: (base_vars[k], curr_vars[k])
        for k in base_vars
        if k in curr_vars and base_vars[k] != curr_vars[k]
    }
    return {"added": added, "removed": removed, "changed": changed}


def baseline_has_drift(diff: dict) -> bool:
    """Return True if the diff contains any changes."""
    return any(diff[k] for k in ("added", "removed", "changed"))
