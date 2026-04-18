"""Group env keys by prefix and report structural organization."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdrift.parser import parse_env_file


@dataclass
class GroupResult:
    env_name: str
    groups: Dict[str, List[str]] = field(default_factory=dict)  # prefix -> keys
    ungrouped: List[str] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self.groups.values()) + len(self.ungrouped)

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())


def _extract_prefix(key: str, sep: str = "_") -> str | None:
    """Return the first segment before sep, or None if no sep found."""
    parts = key.split(sep, 1)
    if len(parts) == 2 and parts[0]:
        return parts[0]
    return None


def group_env(path: str, env_name: str | None = None, sep: str = "_") -> GroupResult:
    """Parse an env file and group keys by prefix."""
    name = env_name or path
    data = parse_env_file(path)
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for key in sorted(data.keys()):
        prefix = _extract_prefix(key, sep)
        if prefix:
            groups.setdefault(prefix, []).append(key)
        else:
            ungrouped.append(key)

    return GroupResult(env_name=name, groups=groups, ungrouped=ungrouped)


def compare_groups(results: List[GroupResult]) -> Dict[str, List[str]]:
    """Return mapping of prefix -> which envs contain it."""
    presence: Dict[str, List[str]] = {}
    for r in results:
        for prefix in r.group_names:
            presence.setdefault(prefix, []).append(r.env_name)
    return presence
