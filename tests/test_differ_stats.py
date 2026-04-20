import pytest
from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult
from envdrift.differ_stats import stats_from_pair, stats_from_multi, DriftStats


def _pair(**kwargs) -> DriftResult:
    defaults = dict(missing=set(), extra=set(), changed=set(), unchanged=set(),
                    env_a="a", env_b="b", ignore_values=False)
    defaults.update(kwargs)
    return DriftResult(**defaults)


def _multi(**kwargs) -> MultiDiffResult:
    defaults = dict(env_names=["a", "b"], all_keys=set(),
                    inconsistent_keys=[], missing_in_some={},
                    value_map={})
    defaults.update(kwargs)
    return MultiDiffResult(**defaults)


def test_pair_no_drift():
    r = _pair(unchanged={"A", "B", "C"})
    s = stats_from_pair(r)
    assert s.is_clean
    assert s.drift_score == 0.0
    assert s.total_keys == 3


def test_pair_full_drift():
    r = _pair(missing={"X"}, extra={"Y"}, changed={"Z"})
    s = stats_from_pair(r)
    assert s.missing_count == 1
    assert s.extra_count == 1
    assert s.changed_count == 1
    assert s.drift_score == 1.0
    assert not s.is_clean


def test_pair_partial_drift():
    r = _pair(missing={"A"}, unchanged={"B", "C", "D"})
    s = stats_from_pair(r)
    assert s.drift_score == pytest.approx(0.2)


def test_pair_most_drifted_key():
    r = _pair(missing={"KEY"}, changed={"KEY"})
    s = stats_from_pair(r)
    assert s.most_drifted_key == "KEY"


def test_multi_no_drift():
    r = _multi(all_keys={"A", "B"})
    s = stats_from_multi(r)
    assert s.is_clean
    assert s.total_keys == 2


def test_multi_with_inconsistent():
    r = _multi(all_keys={"A", "B", "C"}, inconsistent_keys=["B"],
               missing_in_some={"C": ["b"]})
    s = stats_from_multi(r)
    assert s.changed_count == 1
    assert s.missing_count == 1
    assert not s.is_clean


def test_empty_env_zero_score():
    r = _pair()
    s = stats_from_pair(r)
    assert s.drift_score == 0.0
    assert s.most_drifted_key is None
