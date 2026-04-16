"""Drift scorer — assigns a numeric health score to an env comparison."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult


@dataclass
class ScoreResult:
    score: int          # 0-100, higher is healthier
    grade: str          # A/B/C/D/F
    total_keys: int
    missing_count: int
    extra_count: int
    changed_count: int
    details: list[str]


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def score_drift(result: Union[DriftResult, MultiDiffResult]) -> ScoreResult:
    """Compute a health score from a DriftResult or MultiDiffResult."""
    if isinstance(result, DriftResult):
        missing = len(result.missing_keys)
        extra = len(result.extra_keys)
        changed = len(result.changed_values)
        all_keys = set(result.missing_keys) | set(result.extra_keys) | set(result.changed_values)
        # union of both envs
        total = missing + extra + changed
        # base: treat each unique key as 1 slot
        universe = max(total, 1)
        deductions = (missing * 3 + extra * 1 + changed * 2)
        raw = max(0, 100 - int(deductions / universe * 100 * 0.5))
        # simpler linear: start 100, subtract per issue
        penalty = missing * 10 + extra * 5 + changed * 8
        score = max(0, 100 - penalty)
        details = []
        if missing:
            details.append(f"{missing} missing key(s) (-{missing*10} pts)")
        if extra:
            details.append(f"{extra} extra key(s) (-{extra*5} pts)")
        if changed:
            details.append(f"{changed} changed value(s) (-{changed*8} pts)")
        return ScoreResult(
            score=score,
            grade=_grade(score),
            total_keys=total,
            missing_count=missing,
            extra_count=extra,
            changed_count=changed,
            details=details,
        )
    else:  # MultiDiffResult
        inconsistent = len(result.inconsistent_keys)
        missing_some = len(result.missing_in_some)
        penalty = inconsistent * 8 + missing_some * 10
        score = max(0, 100 - penalty)
        details = []
        if inconsistent:
            details.append(f"{inconsistent} inconsistent key(s) (-{inconsistent*8} pts)")
        if missing_some:
            details.append(f"{missing_some} key(s) missing in some envs (-{missing_some*10} pts)")
        return ScoreResult(
            score=score,
            grade=_grade(score),
            total_keys=inconsistent + missing_some,
            missing_count=missing_some,
            extra_count=0,
            changed_count=inconsistent,
            details=details,
        )
