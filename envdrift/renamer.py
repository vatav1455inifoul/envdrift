"""Suggest or apply key renames across .env files based on a rename map."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

from envdrift.parser import parse_env_file


@dataclass
class RenameResult:
    env_name: str
    applied: List[tuple] = field(default_factory=list)   # (old, new)
    skipped: List[tuple] = field(default_factory=list)   # (old, reason)

    @property
    def has_changes(self) -> bool:
        return bool(self.applied)


def load_rename_map(path: str) -> Dict[str, str]:
    """Load a rename map from a simple KEY_OLD=KEY_NEW file."""
    mapping: Dict[str, str] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            old, new = line.split("=", 1)
            mapping[old.strip()] = new.strip()
    return mapping


def suggest_renames(env_path: str, rename_map: Dict[str, str]) -> RenameResult:
    """Return a RenameResult showing what would change without writing."""
    keys = parse_env_file(env_path)
    result = RenameResult(env_name=env_path)
    for old, new in rename_map.items():
        if old in keys:
            if new in keys:
                result.skipped.append((old, f"target '{new}' already exists"))
            else:
                result.applied.append((old, new))
        else:
            result.skipped.append((old, "key not found"))
    return result


def apply_renames(env_path: str, rename_map: Dict[str, str], dry_run: bool = False) -> RenameResult:
    """Rewrite the .env file with keys renamed according to rename_map."""
    result = suggest_renames(env_path, rename_map)
    if dry_run or not result.has_changes:
        return result

    with open(env_path) as fh:
        lines = fh.readlines()

    out_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in rename_map and any(key == a[0] for a in result.applied):
                new_key = rename_map[key]
                line = line.replace(key, new_key, 1)
        out_lines.append(line)

    with open(env_path, "w") as fh:
        fh.writelines(out_lines)

    return result
