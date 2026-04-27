"""Coverage analysis: how completely a set of envs covers a shared key universe."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from envdrift.parser import parse_env_file


@dataclass
class CoverageEntry:
    env_name: str
    present_keys: List[str]
    missing_keys: List[str]
    total_keys: int

    @property
    def coverage_rate(self) -> float:
        if self.total_keys == 0:
            return 1.0
        return len(self.present_keys) / self.total_keys

    @property
    def coverage_percent(self) -> float:
        return round(self.coverage_rate * 100, 1)

    @property
    def is_complete(self) -> bool:
        return len(self.missing_keys) == 0

    def __str__(self) -> str:
        return f"{self.env_name}: {self.coverage_percent}% ({len(self.present_keys)}/{self.total_keys})"


@dataclass
class CoverageResult:
    entries: List[CoverageEntry]
    universe: List[str]

    @property
    def total_keys(self) -> int:
        return len(self.universe)

    @property
    def fully_covered(self) -> List[str]:
        """Keys present in every env."""
        if not self.entries:
            return []
        sets = [set(e.present_keys) for e in self.entries]
        shared = sets[0].intersection(*sets[1:])
        return sorted(shared)

    @property
    def partially_covered(self) -> List[str]:
        """Keys present in some but not all envs."""
        full = set(self.fully_covered)
        return [k for k in self.universe if k not in full]

    @property
    def average_coverage(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.coverage_rate for e in self.entries) / len(self.entries)


def analyse_coverage(
    env_paths: Dict[str, str],
    universe: Sequence[str] | None = None,
) -> CoverageResult:
    """Compute per-env coverage against a shared key universe.

    If *universe* is not provided it is derived as the union of all keys.
    """
    if len(env_paths) < 1:
        raise ValueError("analyse_coverage requires at least one environment.")

    parsed: Dict[str, Dict[str, str]] = {
        name: parse_env_file(path) for name, path in env_paths.items()
    }

    if universe is None:
        all_keys: set[str] = set()
        for kv in parsed.values():
            all_keys.update(kv.keys())
        key_universe = sorted(all_keys)
    else:
        key_universe = list(universe)

    entries: List[CoverageEntry] = []
    for name, kv in parsed.items():
        present = [k for k in key_universe if k in kv]
        missing = [k for k in key_universe if k not in kv]
        entries.append(
            CoverageEntry(
                env_name=name,
                present_keys=present,
                missing_keys=missing,
                total_keys=len(key_universe),
            )
        )

    return CoverageResult(entries=entries, universe=key_universe)
