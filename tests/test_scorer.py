"""Tests for envdrift.scorer."""
import pytest
from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult
from envdrift.scorer import score_drift, ScoreResult


def _pair(missing=None, extra=None, changed=None):
    return DriftResult(
        env_a="dev",
        env_b="prod",
        missing_keys=missing or [],
        extra_keys=extra or [],
        changed_values=changed or {},
    )


def _multi(inconsistent=None, missing_some=None):
    return MultiDiffResult(
        env_names=["dev", "staging", "prod"],
        all_keys=set(),
        inconsistent_keys=inconsistent or {},
        missing_in_some=missing_some or {},
    )


def test_perfect_score_no_drift():
    r = score_drift(_pair())
    assert r.score == 100
    assert r.grade == "A"
    assert r.details == []


def test_missing_keys_reduce_score():
    r = score_drift(_pair(missing=["A", "B"]))
    assert r.score == 80
    assert r.missing_count == 2
    assert r.grade == "B"


def test_extra_keys_reduce_score():
    r = score_drift(_pair(extra=["X"]))
    assert r.score == 95
    assert r.extra_count == 1


def test_changed_values_reduce_score():
    r = score_drift(_pair(changed={"DB_URL": ("a", "b"), "SECRET": ("x", "y")}))
    assert r.score == 84
    assert r.changed_count == 2


def test_score_floor_is_zero():
    r = score_drift(_pair(
        missing=[f"K{i}" for i in range(20)],
        changed={f"C{i}": ("a", "b") for i in range(10)},
    ))
    assert r.score == 0
    assert r.grade == "F"


def test_details_populated():
    r = score_drift(_pair(missing=["A"], extra=["B"], changed={"C": ("1", "2")}))
    assert any("missing" in d for d in r.details)
    assert any("extra" in d for d in r.details)
    assert any("changed" in d for d in r.details)


def test_multi_diff_perfect():
    r = score_drift(_multi())
    assert r.score == 100
    assert r.grade == "A"


def test_multi_diff_inconsistent():
    r = score_drift(_multi(inconsistent={"KEY": {}}))
    assert r.score == 92
    assert r.changed_count == 1


def test_multi_diff_missing_some():
    r = score_drift(_multi(missing_some={"FOO": ["prod"]}))
    assert r.score == 90
    assert r.missing_count == 1


def test_returns_score_result_instance():
    r = score_drift(_pair())
    assert isinstance(r, ScoreResult)
