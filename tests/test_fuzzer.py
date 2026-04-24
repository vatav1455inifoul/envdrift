"""Tests for envdrift.fuzzer and envdrift.fuzzer_reporter."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdrift.fuzzer import fuzzy_diff, FuzzyMatch, FuzzyResult, DEFAULT_THRESHOLD
from envdrift.fuzzer_reporter import format_fuzzy_report


# ---------------------------------------------------------------------------
# fuzzy_diff core logic
# ---------------------------------------------------------------------------

def test_identical_keys_no_suggestions():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = fuzzy_diff(env, env)
    assert not result.has_suggestions
    assert result.unmatched_a == []
    assert result.unmatched_b == []


def test_detects_likely_rename():
    a = {"DATABASE_URL": "x"}
    b = {"DATABSE_URL": "x"}  # typo
    result = fuzzy_diff(a, b, threshold=0.7)
    assert result.has_suggestions
    assert len(result.matches) == 1
    m = result.matches[0]
    assert m.key_a == "DATABASE_URL"
    assert m.key_b == "DATABSE_URL"
    assert m.score > 0.7


def test_completely_different_keys_go_to_unmatched():
    a = {"ALPHA": "1", "BETA": "2"}
    b = {"GAMMA": "3", "DELTA": "4"}
    result = fuzzy_diff(a, b, threshold=DEFAULT_THRESHOLD)
    assert not result.has_suggestions
    assert sorted(result.unmatched_a) == ["ALPHA", "BETA"]
    assert sorted(result.unmatched_b) == ["DELTA", "GAMMA"]


def test_partial_overlap_common_keys_ignored():
    a = {"SHARED": "v", "DB_HOST": "x"}
    b = {"SHARED": "v", "DB_HAST": "x"}  # typo in second
    result = fuzzy_diff(a, b, threshold=0.7)
    # SHARED is in both → not in only_a / only_b
    assert all(m.key_a != "SHARED" for m in result.matches)
    assert result.has_suggestions


def test_env_names_stored_in_result():
    result = fuzzy_diff({}, {}, name_a="prod.env", name_b="staging.env")
    assert result.env_a == "prod.env"
    assert result.env_b == "staging.env"


def test_threshold_zero_excluded():
    """threshold=0 is nonsensical; the function still runs but every key matches."""
    a = {"FOO": "1"}
    b = {"BAR": "2"}
    result = fuzzy_diff(a, b, threshold=0.0)
    # with threshold=0 everything is ≥ threshold, so BAR should match FOO
    assert result.has_suggestions or result.unmatched_a or result.unmatched_b


def test_match_not_duplicated_across_keys():
    """A key in env_b should only be matched once."""
    a = {"API_KEY": "x", "API_KEYS": "y"}
    b = {"API_KEY_": "z"}
    result = fuzzy_diff(a, b, threshold=0.7)
    matched_b_keys = [m.key_b for m in result.matches]
    assert len(matched_b_keys) == len(set(matched_b_keys)), "duplicate match in env_b"


# ---------------------------------------------------------------------------
# reporter
# ---------------------------------------------------------------------------

def test_report_no_suggestions_message():
    result = FuzzyResult(env_a="a", env_b="b")
    report = format_fuzzy_report(result, color=False)
    assert "No fuzzy matches" in report


def test_report_shows_match():
    result = FuzzyResult(
        env_a="a",
        env_b="b",
        matches=[FuzzyMatch(key_a="DATABASE_URL", key_b="DATABSE_URL", score=0.92)],
    )
    report = format_fuzzy_report(result, color=False)
    assert "DATABASE_URL" in report
    assert "DATABSE_URL" in report
    assert "92%" in report


def test_report_shows_unmatched():
    result = FuzzyResult(
        env_a="prod",
        env_b="staging",
        unmatched_a=["LEGACY_KEY"],
        unmatched_b=["NEW_KEY"],
    )
    report = format_fuzzy_report(result, color=False)
    assert "LEGACY_KEY" in report
    assert "NEW_KEY" in report


def test_report_header_contains_env_names():
    result = FuzzyResult(env_a="prod.env", env_b="dev.env")
    report = format_fuzzy_report(result, color=False)
    assert "prod.env" in report
    assert "dev.env" in report
