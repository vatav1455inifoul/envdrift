"""Aggregate drift statistics across multiple env comparisons."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence
from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult


@dataclass
class AggregateSummary:
    total_keys_checked: int
    total_missing: int
    total_extra: int
    total_changed: int
    drift_score: float  # 0.0 (clean) – 1.0 (fully drifted)
    env_pairs: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.drift_score == 0.0


def summarise_pair(result: DriftResult) -> AggregateSummary:
    total = (
        len(result.missing_keys)
        + len(result.extra_keys)
        + len(result.changed_keys)
        + len(result.matching_keys)
    )
    drifted = len(result.missing_keys) + len(result.extra_keys) + len(result.changed_keys)
    score = round(drifted / total, 4) if total else 0.0
    return AggregateSummary(
        total_keys_checked=total,
        total_missing=len(result.missing_keys),
        total_extra=len(result.extra_keys),
        total_changed=len(result.changed_keys),
        drift_score=score,
        env_pairs=[f"{result.env_a} vs {result.env_b}"],
    )


def summarise_multi(result: MultiDiffResult) -> AggregateSummary:
    all_keys: set[str] = set()
    for env_data in result.envs.values():
        all_keys.update(env_data.keys())
    total = len(all_keys)
    drifted = len(result.inconsistent_keys) + len(result.missing_in_some)
    score = round(drifted / total, 4) if total else 0.0
    return AggregateSummary(
        total_keys_checked=total,
        total_missing=len(result.missing_in_some),
        total_extra=0,
        total_changed=len(result.inconsistent_keys),
        drift_score=score,
        env_pairs=list(result.envs.keys()),
    )
