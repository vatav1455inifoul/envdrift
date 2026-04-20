"""Statistical summary across multiple drift comparisons."""
from dataclasses import dataclass, field
from typing import List, Dict
from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult


@dataclass
class DriftStats:
    total_keys: int
    missing_count: int
    extra_count: int
    changed_count: int
    drift_score: float  # 0.0 = clean, 1.0 = fully drifted
    most_drifted_key: str | None
    key_drift_counts: Dict[str, int] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return self.drift_score == 0.0


def stats_from_pair(result: DriftResult) -> DriftStats:
    total = len(result.missing) + len(result.extra) + len(result.changed) + len(result.unchanged)
    drifted = len(result.missing) + len(result.extra) + len(result.changed)
    score = round(drifted / total, 4) if total else 0.0
    key_counts: Dict[str, int] = {}
    for k in list(result.missing) + list(result.extra) + list(result.changed):
        key_counts[k] = key_counts.get(k, 0) + 1
    most_drifted = max(key_counts, key=key_counts.get) if key_counts else None
    return DriftStats(
        total_keys=total,
        missing_count=len(result.missing),
        extra_count=len(result.extra),
        changed_count=len(result.changed),
        drift_score=score,
        most_drifted_key=most_drifted,
        key_drift_counts=key_counts,
    )


def stats_from_multi(result: MultiDiffResult) -> DriftStats:
    all_keys = result.all_keys
    total = len(all_keys)
    missing_keys = set(result.missing_in_some.keys())
    inconsistent = set(result.inconsistent_keys)
    drifted = len(missing_keys | inconsistent)
    score = round(drifted / total, 4) if total else 0.0
    key_counts: Dict[str, int] = {}
    for k in missing_keys | inconsistent:
        key_counts[k] = key_counts.get(k, 0) + 1
    most_drifted = max(key_counts, key=key_counts.get) if key_counts else None
    return DriftStats(
        total_keys=total,
        missing_count=len(missing_keys),
        extra_count=0,
        changed_count=len(inconsistent),
        drift_score=score,
        most_drifted_key=most_drifted,
        key_drift_counts=key_counts,
    )
