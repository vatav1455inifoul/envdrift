"""Drift heatmap: rank keys by how often they differ across many env pairs."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Sequence

from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult


@dataclass
class HeatmapEntry:
    key: str
    drift_count: int
    total_comparisons: int

    @property
    def drift_rate(self) -> float:
        if self.total_comparisons == 0:
            return 0.0
        return self.drift_count / self.total_comparisons

    def __str__(self) -> str:
        pct = self.drift_rate * 100
        return f"{self.key}: {self.drift_count}/{self.total_comparisons} ({pct:.0f}%)"


@dataclass
class HeatmapResult:
    entries: List[HeatmapEntry] = field(default_factory=list)
    total_comparisons: int = 0

    @property
    def hottest(self) -> List[HeatmapEntry]:
        return sorted(self.entries, key=lambda e: e.drift_rate, reverse=True)

    @property
    def stable_keys(self) -> List[HeatmapEntry]:
        return [e for e in self.entries if e.drift_count == 0]

    @property
    def drifting_keys(self) -> List[HeatmapEntry]:
        return [e for e in self.hottest if e.drift_count > 0]


def heatmap_from_pairs(results: Sequence[DriftResult]) -> HeatmapResult:
    """Build a heatmap from multiple pairwise DriftResults."""
    drift_counts: Counter = Counter()
    seen_counts: Counter = Counter()

    for result in results:
        all_keys = (
            set(result.missing_keys)
            | set(result.extra_keys)
            | set(result.changed_keys)
            | set(result.base.keys())
            | set(result.other.keys())
        )
        for key in all_keys:
            seen_counts[key] += 1
        for key in result.missing_keys:
            drift_counts[key] += 1
        for key in result.extra_keys:
            drift_counts[key] += 1
        for key in result.changed_keys:
            drift_counts[key] += 1

    entries = [
        HeatmapEntry(key=k, drift_count=drift_counts[k], total_comparisons=seen_counts[k])
        for k in seen_counts
    ]
    return HeatmapResult(entries=entries, total_comparisons=len(results))


def heatmap_from_multi(result: MultiDiffResult) -> HeatmapResult:
    """Build a heatmap from a MultiDiffResult."""
    drift_counts: Counter = Counter()
    seen_counts: Counter = Counter()
    n = len(result.env_names)

    all_keys = set(result.all_keys)
    for key in all_keys:
        present_in = sum(1 for env in result.values.values() if key in env)
        seen_counts[key] = present_in
        if key in result.inconsistent_keys() or key in result.missing_in_some():
            drift_counts[key] = present_in

    entries = [
        HeatmapEntry(key=k, drift_count=drift_counts[k], total_comparisons=n)
        for k in all_keys
    ]
    return HeatmapResult(entries=entries, total_comparisons=n)
