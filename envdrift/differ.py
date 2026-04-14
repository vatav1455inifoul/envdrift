"""Multi-environment diff: compare more than two .env files at once."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from envdrift.parser import parse_env_file
from envdrift.comparator import compare_envs, DriftResult


@dataclass
class MultiDiffResult:
    """Aggregated drift results across N environments."""

    env_names: List[str]
    # all keys seen across every env file
    all_keys: Set[str] = field(default_factory=set)
    # key -> {env_name -> value or None if missing}
    matrix: Dict[str, Dict[str, str | None]] = field(default_factory=dict)
    # pairwise drift results keyed by (base, other)
    pairwise: Dict[tuple, DriftResult] = field(default_factory=dict)

    @property
    def has_drift(self) -> bool:
        return any(r.has_drift for r in self.pairwise.values())

    @property
    def inconsistent_keys(self) -> Set[str]:
        """Keys whose values differ across at least two environments."""
        inconsistent: Set[str] = set()
        for key in self.all_keys:
            values = {
                v for v in self.matrix[key].values() if v is not None
            }
            if len(values) > 1:
                inconsistent.add(key)
        return inconsistent

    @property
    def missing_in_some(self) -> Set[str]:
        """Keys present in at least one env but absent in at least one other."""
        return {
            key
            for key, env_map in self.matrix.items()
            if None in env_map.values()
        }


def multi_diff(
    env_paths: Dict[str, str],
    ignore_values: bool = False,
) -> MultiDiffResult:
    """Compare multiple env files.

    Args:
        env_paths: mapping of environment name -> path to .env file.
        ignore_values: if True only check key presence, not values.

    Returns:
        A MultiDiffResult summarising drift across all environments.
    """
    if len(env_paths) < 2:
        raise ValueError("multi_diff requires at least two environments")

    parsed: Dict[str, Dict[str, str]] = {
        name: parse_env_file(path) for name, path in env_paths.items()
    }

    all_keys: Set[str] = set()
    for env_data in parsed.values():
        all_keys.update(env_data.keys())

    env_names = list(env_paths.keys())

    matrix: Dict[str, Dict[str, str | None]] = {
        key: {name: parsed[name].get(key) for name in env_names}
        for key in all_keys
    }

    pairwise: Dict[tuple, DriftResult] = {}
    base_name = env_names[0]
    for other_name in env_names[1:]:
        result = compare_envs(
            parsed[base_name],
            parsed[other_name],
            base_name,
            other_name,
            ignore_values=ignore_values,
        )
        pairwise[(base_name, other_name)] = result

    return MultiDiffResult(
        env_names=env_names,
        all_keys=all_keys,
        matrix=matrix,
        pairwise=pairwise,
    )
