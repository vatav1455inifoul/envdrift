"""Tests for envdrift.differ (multi-environment diff)."""

import pytest
from pathlib import Path

from envdrift.differ import multi_diff, MultiDiffResult


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_requires_at_least_two_envs(tmp_env):
    path = tmp_env(".env", "KEY=val\n")
    with pytest.raises(ValueError, match="at least two"):
        multi_diff({"prod": path})


def test_no_drift_identical_files(tmp_env):
    content = "KEY=value\nDB=postgres\n"
    a = tmp_env("a.env", content)
    b = tmp_env("b.env", content)
    result = multi_diff({"a": a, "b": b})
    assert not result.has_drift
    assert result.inconsistent_keys == set()
    assert result.missing_in_some == set()


def test_detects_missing_key(tmp_env):
    a = tmp_env("a.env", "KEY=value\nEXTRA=only_in_a\n")
    b = tmp_env("b.env", "KEY=value\n")
    result = multi_diff({"a": a, "b": b})
    assert result.has_drift
    assert "EXTRA" in result.missing_in_some


def test_detects_changed_value(tmp_env):
    a = tmp_env("a.env", "KEY=foo\n")
    b = tmp_env("b.env", "KEY=bar\n")
    result = multi_diff({"a": a, "b": b})
    assert result.has_drift
    assert "KEY" in result.inconsistent_keys


def test_matrix_contains_all_envs(tmp_env):
    a = tmp_env("a.env", "KEY=1\n")
    b = tmp_env("b.env", "KEY=2\n")
    c = tmp_env("c.env", "KEY=3\n")
    result = multi_diff({"a": a, "b": b, "c": c})
    assert set(result.matrix["KEY"].keys()) == {"a", "b", "c"}


def test_matrix_none_for_missing_key(tmp_env):
    a = tmp_env("a.env", "ONLY_A=yes\n")
    b = tmp_env("b.env", "OTHER=no\n")
    result = multi_diff({"a": a, "b": b})
    assert result.matrix["ONLY_A"]["b"] is None
    assert result.matrix["OTHER"]["a"] is None


def test_ignore_values_no_drift_on_value_change(tmp_env):
    a = tmp_env("a.env", "KEY=foo\n")
    b = tmp_env("b.env", "KEY=bar\n")
    result = multi_diff({"a": a, "b": b}, ignore_values=True)
    assert not result.has_drift


def test_pairwise_keyed_by_base_and_other(tmp_env):
    a = tmp_env("a.env", "KEY=1\n")
    b = tmp_env("b.env", "KEY=2\n")
    result = multi_diff({"a": a, "b": b})
    assert ("a", "b") in result.pairwise


def test_three_envs_pairwise_has_two_results(tmp_env):
    content = "KEY=val\n"
    a = tmp_env("a.env", content)
    b = tmp_env("b.env", content)
    c = tmp_env("c.env", content)
    result = multi_diff({"a": a, "b": b, "c": c})
    # base is 'a', compared against 'b' and 'c'
    assert len(result.pairwise) == 2
    assert ("a", "b") in result.pairwise
    assert ("a", "c") in result.pairwise
