"""Overlap analysis between two or more .env files.

Measures how many keys are shared vs unique across environments,
giving a quick sense of how aligned the configs are.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class OverlapResult:
    env_names: List[str]
    all_keys: Set[str]
    shared_keys: Set[str]          # present in ALL envs
    partial_keys: Set[str]         # present in SOME but not all
    unique_keys: Dict[str, Set[str]]  # env_name -> keys only in that env

    @property
    def total_keys(self) -> int:
        return len(self.all_keys)

    @property
    def overlap_rate(self) -> float:
        """Fraction of keys shared across all environments (0.0 – 1.0)."""
        if not self.all_keys:
            return 1.0
        return len(self.shared_keys) / len(self.all_keys)

    @property
    def overlap_percent(self) -> int:
        return round(self.overlap_rate * 100)


def analyse_overlap(envs: Dict[str, Dict[str, str]]) -> OverlapResult:
    """Compute key-overlap statistics across *envs*.

    Parameters
    ----------
    envs:
        Mapping of environment-name -> parsed key/value dict.
    """
    if len(envs) < 2:
        raise ValueError("analyse_overlap requires at least two environments")

    env_names = list(envs.keys())
    key_sets: List[Set[str]] = [set(v.keys()) for v in envs.values()]

    all_keys: Set[str] = set().union(*key_sets)
    shared_keys: Set[str] = key_sets[0].intersection(*key_sets[1:])
    partial_keys: Set[str] = all_keys - shared_keys

    unique_keys: Dict[str, Set[str]] = {}
    for name, ks in zip(env_names, key_sets):
        others = set().union(*(s for n, s in zip(env_names, key_sets) if n != name))
        unique_keys[name] = ks - others

    return OverlapResult(
        env_names=env_names,
        all_keys=all_keys,
        shared_keys=shared_keys,
        partial_keys=partial_keys,
        unique_keys=unique_keys,
    )
