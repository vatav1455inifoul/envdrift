"""Tests for envdrift.differ_coverage."""
from __future__ import annotations

import pytest

from envdrift.differ_coverage import analyse_coverage, CoverageEntry, CoverageResult


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_requires_at_least_one_env(tmp_env):
    with pytest.raises(ValueError, match="at least one"):
        analyse_coverage({})


def test_single_env_full_coverage(tmp_env):
    p = tmp_env("a.env", "FOO=1\nBAR=2\n")
    result = analyse_coverage({"a": p})
    assert result.total_keys == 2
    assert len(result.entries) == 1
    assert result.entries[0].is_complete
    assert result.entries[0].coverage_percent == 100.0


def test_two_envs_partial_coverage(tmp_env):
    p1 = tmp_env("a.env", "FOO=1\nBAR=2\n")
    p2 = tmp_env("b.env", "FOO=1\n")
    result = analyse_coverage({"a": p1, "b": p2})
    assert result.total_keys == 2
    b_entry = next(e for e in result.entries if e.env_name == "b")
    assert "BAR" in b_entry.missing_keys
    assert b_entry.coverage_percent == 50.0


def test_fully_covered_keys(tmp_env):
    p1 = tmp_env("a.env", "FOO=1\nBAR=2\n")
    p2 = tmp_env("b.env", "FOO=1\nBAR=2\nBAZ=3\n")
    result = analyse_coverage({"a": p1, "b": p2})
    # FOO and BAR are in both; BAZ is only in b
    assert set(result.fully_covered) == {"FOO", "BAR"}
    assert "BAZ" in result.partially_covered


def test_custom_universe(tmp_env):
    p = tmp_env("a.env", "FOO=1\n")
    result = analyse_coverage({"a": p}, universe=["FOO", "BAR", "BAZ"])
    assert result.total_keys == 3
    entry = result.entries[0]
    assert entry.missing_keys == ["BAR", "BAZ"]
    assert round(entry.coverage_rate, 4) == round(1 / 3, 4)


def test_average_coverage_all_complete(tmp_env):
    p1 = tmp_env("a.env", "FOO=1\n")
    p2 = tmp_env("b.env", "FOO=2\n")
    result = analyse_coverage({"a": p1, "b": p2})
    assert result.average_coverage == 1.0


def test_average_coverage_mixed(tmp_env):
    p1 = tmp_env("a.env", "FOO=1\nBAR=2\n")
    p2 = tmp_env("b.env", "FOO=1\n")
    result = analyse_coverage({"a": p1, "b": p2})
    # a=100%, b=50% -> avg=75%
    assert result.average_coverage == 0.75


def test_empty_envs_empty_universe(tmp_env):
    p1 = tmp_env("a.env", "")
    p2 = tmp_env("b.env", "")
    result = analyse_coverage({"a": p1, "b": p2})
    assert result.total_keys == 0
    assert result.fully_covered == []
    assert result.average_coverage == 1.0


def test_coverage_entry_str(tmp_env):
    p = tmp_env("prod.env", "A=1\nB=2\n")
    result = analyse_coverage({"prod": p})
    s = str(result.entries[0])
    assert "prod" in s
    assert "100.0%" in s
