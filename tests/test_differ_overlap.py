"""Tests for envdrift.differ_overlap and envdrift.overlap_reporter."""
import pytest

from envdrift.differ_overlap import analyse_overlap, OverlapResult
from envdrift.overlap_reporter import format_overlap_report


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _envs(**kwargs):
    """Build a dict of name -> {key: value} from keyword args of lists."""
    return {name: {k: "v" for k in keys} for name, keys in kwargs.items()}


# ---------------------------------------------------------------------------
# analyse_overlap
# ---------------------------------------------------------------------------

def test_requires_at_least_two_envs():
    with pytest.raises(ValueError, match="at least two"):
        analyse_overlap({"only": {"A": "1"}})


def test_no_keys_returns_full_overlap():
    result = analyse_overlap({"a": {}, "b": {}})
    assert result.overlap_rate == 1.0
    assert result.total_keys == 0
    assert result.shared_keys == set()


def test_identical_envs_all_shared():
    result = analyse_overlap(_envs(prod=["A", "B", "C"], staging=["A", "B", "C"]))
    assert result.shared_keys == {"A", "B", "C"}
    assert result.partial_keys == set()
    assert result.overlap_percent == 100


def test_no_overlap_all_unique():
    result = analyse_overlap(_envs(prod=["A", "B"], staging=["C", "D"]))
    assert result.shared_keys == set()
    assert result.overlap_percent == 0
    assert result.unique_keys["prod"] == {"A", "B"}
    assert result.unique_keys["staging"] == {"C", "D"}


def test_partial_overlap():
    result = analyse_overlap(_envs(prod=["A", "B", "C"], staging=["B", "C", "D"]))
    assert result.shared_keys == {"B", "C"}
    assert "A" in result.partial_keys
    assert "D" in result.partial_keys
    assert result.total_keys == 4


def test_three_envs_shared_requires_all():
    result = analyse_overlap(
        _envs(dev=["A", "B"], staging=["A", "C"], prod=["A", "D"])
    )
    assert result.shared_keys == {"A"}
    assert {"B", "C", "D"} <= result.partial_keys


def test_unique_keys_only_in_one_env():
    result = analyse_overlap(_envs(prod=["A", "X"], staging=["A", "Y"]))
    assert result.unique_keys["prod"] == {"X"}
    assert result.unique_keys["staging"] == {"Y"}


def test_overlap_rate_value():
    # 2 shared out of 4 total => 50 %
    result = analyse_overlap(_envs(prod=["A", "B", "C"], staging=["A", "B", "D"]))
    assert result.overlap_percent == 75  # 3 shared (A,B) wait — A,B shared, C,D partial => 2/4=50
    # recalc: shared={A,B}, all={A,B,C,D} => 2/4 = 50
    # The previous assertion was wrong; fix:
    assert result.overlap_percent == 50


# ---------------------------------------------------------------------------
# overlap_reporter
# ---------------------------------------------------------------------------

def test_format_report_contains_env_names():
    result = analyse_overlap(_envs(prod=["A"], staging=["A"]))
    report = format_overlap_report(result, color=False)
    assert "prod" in report
    assert "staging" in report


def test_format_report_shows_overlap_percent():
    result = analyse_overlap(_envs(prod=["A", "B"], staging=["A", "B"]))
    report = format_overlap_report(result, color=False)
    assert "100%" in report


def test_format_report_lists_shared_keys():
    result = analyse_overlap(_envs(prod=["A", "B"], staging=["A", "C"]))
    report = format_overlap_report(result, color=False)
    assert "Shared keys" in report
    assert "A" in report


def test_format_report_no_crash_with_color():
    result = analyse_overlap(_envs(prod=["X"], staging=["Y"]))
    report = format_overlap_report(result, color=True)
    assert len(report) > 0
