"""Variance analysis: measures how much a key's value diverges across environments."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envdrift.parser import parse_env_file


@dataclass
class VarianceEntry:
    key: str
    values: Dict[str, Optional[str]]   # env_name -> value
    unique_values: int = 0
    is_uniform: bool = True

    def __post_init__(self) -> None:
        non_none = [v for v in self.values.values() if v is not None]
        self.unique_values = len(set(non_none))
        self.is_uniform = self.unique_values <= 1

    @property
    def missing_in(self) -> List[str]:
        return [env for env, val in self.values.items() if val is None]

    @property
    def variance_ratio(self) -> float:
        """Fraction of envs that differ from the most common value (0 = uniform)."""
        non_none = [v for v in self.values.values() if v is not None]
        if not non_none:
            return 0.0
        counts: Dict[str, int] = {}
        for v in non_none:
            counts[v] = counts.get(v, 0) + 1
        most_common = max(counts.values())
        diverging = len(non_none) - most_common
        return diverging / len(self.values)


@dataclass
class VarianceResult:
    env_names: List[str]
    entries: List[VarianceEntry] = field(default_factory=list)

    @property
    def uniform_keys(self) -> List[VarianceEntry]:
        return [e for e in self.entries if e.is_uniform and not e.missing_in]

    @property
    def divergent_keys(self) -> List[VarianceEntry]:
        return [e for e in self.entries if not e.is_uniform]

    @property
    def partial_keys(self) -> List[VarianceEntry]:
        """Keys present in some but not all envs."""
        return [e for e in self.entries if e.missing_in]

    @property
    def is_uniform(self) -> bool:
        return len(self.divergent_keys) == 0 and len(self.partial_keys) == 0


def analyse_variance(env_files: Dict[str, str]) -> VarianceResult:
    """Analyse value variance across multiple env files.

    Args:
        env_files: mapping of env_name -> file path
    """
    if len(env_files) < 2:
        raise ValueError("analyse_variance requires at least two environments")

    parsed: Dict[str, Dict[str, str]] = {
        name: parse_env_file(path) for name, path in env_files.items()
    }
    env_names = list(env_files.keys())
    all_keys: set = set()
    for env in parsed.values():
        all_keys.update(env.keys())

    entries: List[VarianceEntry] = []
    for key in sorted(all_keys):
        values = {name: parsed[name].get(key) for name in env_names}
        entries.append(VarianceEntry(key=key, values=values))

    return VarianceResult(env_names=env_names, entries=entries)
