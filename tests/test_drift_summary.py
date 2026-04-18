"""Tests for drift_summary."""
from __future__ import annotations
import pytest
from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult
from envdrift.drift_summary import summarise_pair, summarise_multi


def _pair(**kwargs) -> DriftResult:
    defaults = dict(
        env_a="a.env",
        env_b="b.env",
        missing_keys=[],
        extra_keys=[],
        changed_keys={},
        matching_keys=[],
    )
    defaults.update(kwargs)
    return DriftResult(**defaults)


def _multi(**kwargs) -> MultiDiffResult:
    defaults = dict(
        envs={"a": {"FOO": "1"}, "b": {"FOO": "1"}},
        inconsistent_keys={},
        missing_in_some={},
    )
    defaults.update(kwargs)
    return MultiDiffResult(**defaults)


def test_pair_clean():
    r = _pair(matching_keys=["A", "B"])
    s = summarise_pair(r)
    assert s.is_clean
    assert s.drift_score == 0.0
    assert s.total_keys_checked == 2


def test_pair_full_drift():
    r = _pair(missing_keys=["A"], extra_keys=["B"], changed_keys={"C": ("x", "y")})
    s = summarise_pair(r)
    assert s.drift_score == 1.0
    assert not s.is_clean


def test_pair_partial_drift():
    r = _pair(missing_keys=["A"], matching_keys=["B", "C", "D"])
    s = summarise_pair(r)
    assert 0.0 < s.drift_score < 1.0


def test_multi_clean():
    r = _multi()
    s = summarise_multi(r)
    assert s.is_clean
    assert s.total_keys_checked == 1


def test_multi_with_drift():
    r = _multi(
        envs={"a": {"FOO": "1", "BAR": "x"}, "b": {"FOO": "2", "BAR": "x"}},
        inconsistent_keys={"FOO": {"a": "1", "b": "2"}},
        missing_in_some={},
    )
    s = summarise_multi(r)
    assert s.total_changed == 1
    assert s.drift_score == 0.5


def test_empty_env_zero_score():
    r = _multi(envs={"a": {}, "b": {}}, inconsistent_keys={}, missing_in_some={})
    s = summarise_multi(r)
    assert s.drift_score == 0.0
