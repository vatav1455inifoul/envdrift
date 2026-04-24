"""Symmetry analysis: checks how symmetric the drift is between two envs.

A perfectly symmetric diff means every key missing in A is extra in B and
vice-versa (i.e. a pure rename/shuffle situation with no value-only changes).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult


@dataclass
class SymmetryResult:
    env_a: str
    env_b: str
    missing_keys: List[str]          # in A but not B
    extra_keys: List[str]            # in B but not A
    changed_keys: List[str]          # present in both, value differs
    symmetry_score: float            # 0.0 (fully asymmetric) – 1.0 (perfect)
    is_symmetric: bool
    notes: List[str] = field(default_factory=list)


def _score(missing: List[str], extra: List[str], changed: List[str]) -> float:
    """Heuristic symmetry score.

    Perfect symmetry: missing == extra (same count), no changed keys.
    Changed keys break symmetry entirely.
    """
    total = len(missing) + len(extra) + len(changed)
    if total == 0:
        return 1.0
    balanced = min(len(missing), len(extra)) * 2
    penalty = abs(len(missing) - len(extra)) + len(changed) * 2
    raw = max(0.0, balanced - penalty)
    return round(raw / (total + 1e-9), 4)


def analyse_symmetry(
    result: DriftResult,
    threshold: float = 0.8,
) -> SymmetryResult:
    """Derive a symmetry report from a pairwise DriftResult."""
    missing = sorted(result.missing_keys)
    extra = sorted(result.extra_keys)
    changed = sorted(result.changed_keys.keys())

    score = _score(missing, extra, changed)
    symmetric = score >= threshold

    notes: List[str] = []
    if changed:
        notes.append(f"{len(changed)} key(s) changed value — reduces symmetry")
    if len(missing) != len(extra):
        notes.append(
            f"key count imbalance: {len(missing)} missing vs {len(extra)} extra"
        )
    if symmetric and not changed and len(missing) == len(extra):
        notes.append("envs look like a symmetric rename or reorder")

    return SymmetryResult(
        env_a=result.env_a,
        env_b=result.env_b,
        missing_keys=missing,
        extra_keys=extra,
        changed_keys=changed,
        symmetry_score=score,
        is_symmetric=symmetric,
        notes=notes,
    )


def symmetry_from_multi(
    result: MultiDiffResult,
    threshold: float = 0.8,
) -> Dict[str, SymmetryResult]:
    """Run symmetry analysis over every pair produced by multi_diff."""
    from envdrift.comparator import compare_envs

    out: Dict[str, SymmetryResult] = {}
    names = result.env_names
    for i, name_a in enumerate(names):
        for name_b in names[i + 1 :]:
            pair_key = f"{name_a}↔{name_b}"
            env_a_data = result.envs[name_a]
            env_b_data = result.envs[name_b]
            drift = compare_envs(env_a_data, env_b_data, name_a, name_b)
            out[pair_key] = analyse_symmetry(drift, threshold=threshold)
    return out
