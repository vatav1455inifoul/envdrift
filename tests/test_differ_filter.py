"""Tests for envdrift.differ_filter."""

import pytest

from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult
from envdrift.differ_filter import FilterOptions, filter_pair_drift, filter_multi_drift


def _pair(**kwargs) -> DriftResult:
    defaults = dict(env_a="a", env_b="b", missing_keys=[], extra_keys=[], changed_values={})
    defaults.update(kwargs)
    return DriftResult(**defaults)


def _multi(**kwargs) -> MultiDiffResult:
    defaults = dict(env_names=["a", "b"], missing_in_some={}, inconsistent_keys={})
    defaults.update(kwargs)
    return MultiDiffResult(**defaults)


def test_no_filter_returns_all_keys():
    r = _pair(missing_keys=["A", "B"], extra_keys=["C"], changed_values={"D": ("1", "2")})
    out = filter_pair_drift(r, FilterOptions())
    assert out.missing_keys == ["A", "B"]
    assert out.extra_keys == ["C"]
    assert "D" in out.changed_values


def test_include_pattern_limits_keys():
    r = _pair(missing_keys=["DB_HOST", "APP_NAME"], extra_keys=["DB_PORT"])
    out = filter_pair_drift(r, FilterOptions(include_patterns=["DB_*"]))
    assert out.missing_keys == ["DB_HOST"]
    assert out.extra_keys == ["DB_PORT"]


def test_exclude_pattern_removes_keys():
    r = _pair(missing_keys=["SECRET_KEY", "APP_NAME"], changed_values={"SECRET_TOKEN": ("a", "b")})
    out = filter_pair_drift(r, FilterOptions(exclude_patterns=["SECRET_*"]))
    assert out.missing_keys == ["APP_NAME"]
    assert "SECRET_TOKEN" not in out.changed_values


def test_only_missing_hides_extra_and_changed():
    r = _pair(missing_keys=["A"], extra_keys=["B"], changed_values={"C": ("1", "2")})
    out = filter_pair_drift(r, FilterOptions(only_missing=True))
    assert out.missing_keys == ["A"]
    assert out.extra_keys == []
    assert out.changed_values == {}


def test_only_extra_hides_missing_and_changed():
    r = _pair(missing_keys=["A"], extra_keys=["B"], changed_values={"C": ("1", "2")})
    out = filter_pair_drift(r, FilterOptions(only_extra=True))
    assert out.extra_keys == ["B"]
    assert out.missing_keys == []
    assert out.changed_values == {}


def test_only_changed_hides_missing_and_extra():
    r = _pair(missing_keys=["A"], extra_keys=["B"], changed_values={"C": ("1", "2")})
    out = filter_pair_drift(r, FilterOptions(only_changed=True))
    assert out.changed_values == {"C": ("1", "2")}
    assert out.missing_keys == []
    assert out.extra_keys == []


def test_filter_multi_include_pattern():
    r = _multi(
        missing_in_some={"DB_HOST": ["prod"], "APP_NAME": ["staging"]},
        inconsistent_keys={"DB_PORT": {"prod": "5432", "staging": "3306"}},
    )
    out = filter_multi_drift(r, FilterOptions(include_patterns=["DB_*"]))
    assert "DB_HOST" in out.missing_in_some
    assert "APP_NAME" not in out.missing_in_some
    assert "DB_PORT" in out.inconsistent_keys


def test_filter_multi_exclude_pattern():
    r = _multi(
        missing_in_some={"SECRET_KEY": ["prod"], "APP_NAME": ["staging"]},
    )
    out = filter_multi_drift(r, FilterOptions(exclude_patterns=["SECRET_*"]))
    assert "SECRET_KEY" not in out.missing_in_some
    assert "APP_NAME" in out.missing_in_some


def test_env_names_preserved_after_filter():
    r = _pair(missing_keys=["X"])
    out = filter_pair_drift(r, FilterOptions(include_patterns=["Y_*"]))
    assert out.env_a == "a"
    assert out.env_b == "b"
