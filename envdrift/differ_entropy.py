"""Entropy analysis: measure value diversity and randomness across env files."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import parse_env_file


@dataclass
class EntropyEntry:
    key: str
    values: List[str]
    unique_count: int
    shannon_entropy: float

    @property
    def is_uniform(self) -> bool:
        """All envs share the same value."""
        return self.unique_count == 1

    @property
    def is_fully_diverse(self) -> bool:
        """Every env has a distinct value."""
        return self.unique_count == len(self.values)

    def __str__(self) -> str:
        return f"{self.key}: entropy={self.shannon_entropy:.3f} unique={self.unique_count}/{len(self.values)}"


@dataclass
class EntropyResult:
    env_names: List[str]
    entries: List[EntropyEntry] = field(default_factory=list)

    @property
    def high_entropy_keys(self) -> List[EntropyEntry]:
        """Keys whose Shannon entropy is above 1.0 (meaningfully diverse)."""
        return [e for e in self.entries if e.shannon_entropy > 1.0]

    @property
    def uniform_keys(self) -> List[EntropyEntry]:
        return [e for e in self.entries if e.is_uniform]

    @property
    def average_entropy(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.shannon_entropy for e in self.entries) / len(self.entries)


def _shannon(values: List[str]) -> float:
    """Compute Shannon entropy over a list of string values."""
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def analyse_entropy(
    env_paths: Dict[str, str],
    ignore_empty: bool = True,
) -> EntropyResult:
    """Analyse value entropy across multiple env files.

    Args:
        env_paths: mapping of env_name -> file path.
        ignore_empty: skip keys whose value is empty in all envs.

    Returns:
        EntropyResult with per-key entropy data.
    """
    if len(env_paths) < 2:
        raise ValueError("analyse_entropy requires at least two environments")

    parsed = {name: parse_env_file(path) for name, path in env_paths.items()}
    env_names = list(env_paths.keys())

    all_keys: set = set()
    for env in parsed.values():
        all_keys.update(env.keys())

    entries: List[EntropyEntry] = []
    for key in sorted(all_keys):
        values = [parsed[name].get(key, "") for name in env_names]
        if ignore_empty and all(v == "" for v in values):
            continue
        entries.append(
            EntropyEntry(
                key=key,
                values=values,
                unique_count=len(set(values)),
                shannon_entropy=_shannon(values),
            )
        )

    return EntropyResult(env_names=env_names, entries=entries)
