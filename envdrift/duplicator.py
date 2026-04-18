"""Detect duplicate values across keys in an env file."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List


@dataclass
class DuplicateValueResult:
    env_name: str
    value_map: Dict[str, List[str]]  # value -> list of keys sharing it

    @property
    def has_duplicates(self) -> bool:
        return any(len(keys) > 1 for keys in self.value_map.values())

    @property
    def duplicate_groups(self) -> Dict[str, List[str]]:
        return {v: ks for v, ks in self.value_map.items() if len(ks) > 1}

    @property
    def total_duplicate_keys(self) -> int:
        return sum(len(ks) for ks in self.duplicate_groups.values())


def find_duplicate_values(
    env: Dict[str, str],
    env_name: str = "env",
    ignore_blank: bool = True,
) -> DuplicateValueResult:
    """Find keys that share the same value."""
    grouped: Dict[str, List[str]] = defaultdict(list)
    for key, value in env.items():
        if ignore_blank and value == "":
            continue
        grouped[value].append(key)
    return DuplicateValueResult(env_name=env_name, value_map=dict(grouped))
