"""Tests for envdrift.differ_heatmap."""
from __future__ import annotations

import pytest

from envdrift.comparator import compare_envs
from envdrift.differ import multi_diff
from envdrift.differ_heatmap import (
    HeatmapEntry,
    heatmap_from_multi,
    heatmap_from_pairs,
)


def _pair(base: dict, other: dict, bn: str = "base", on: str = "other"):
    return compare_envs(base, other, bn, on)


def _multi(named: dict):
    return multi_diff(named)


# --- heatmap_from_pairs ---

def test_no_pairs_returns_empty_heatmap():
    result = heatmap_from_pairs([])
    assert result.entries == []
    assert result.total_comparisons == 0


def test_single_pair_no_drift():
    env = {"A": "1", "B": "2"}
    result = heatmap_from_pairs([_pair(env, env)])
    assert result.total_comparisons == 1
    assert len(result.drifting_keys) == 0
    assert len(result.stable_keys) == 2


def test_single_pair_with_drift():
    base = {"A": "1", "B": "2"}
    other = {"A": "99", "B": "2"}
    result = heatmap_from_pairs([_pair(base, other)])
    drifting = {e.key for e in result.drifting_keys}
    assert "A" in drifting
    assert "B" not in drifting


def test_multiple_pairs_accumulate_drift():
    base = {"X": "1", "Y": "hello"}
    other1 = {"X": "2", "Y": "hello"}
    other2 = {"X": "3", "Y": "hello"}
    result = heatmap_from_pairs([_pair(base, other1), _pair(base, other2)])
    x_entry = next(e for e in result.entries if e.key == "X")
    assert x_entry.drift_count == 2
    assert x_entry.total_comparisons == 2
    assert x_entry.drift_rate == 1.0


def test_missing_key_counted_as_drift():
    base = {"A": "1", "B": "2"}
    other = {"A": "1"}
    result = heatmap_from_pairs([_pair(base, other)])
    b_entry = next(e for e in result.entries if e.key == "B")
    assert b_entry.drift_count >= 1


def test_hottest_returns_sorted_descending():
    base = {"A": "1", "B": "2", "C": "3"}
    other = {"A": "99", "B": "2", "C": "77"}
    result = heatmap_from_pairs([_pair(base, other)])
    rates = [e.drift_rate for e in result.hottest]
    assert rates == sorted(rates, reverse=True)


# --- heatmap_from_multi ---

def test_multi_no_drift():
    envs = {"dev": {"A": "1"}, "prod": {"A": "1"}}
    result = heatmap_from_multi(_multi(envs))
    assert len(result.drifting_keys) == 0


def test_multi_detects_inconsistent_key():
    envs = {"dev": {"A": "1", "B": "x"}, "prod": {"A": "1", "B": "y"}}
    result = heatmap_from_multi(_multi(envs))
    drifting = {e.key for e in result.drifting_keys}
    assert "B" in drifting


def test_heatmap_entry_str():
    entry = HeatmapEntry(key="FOO", drift_count=3, total_comparisons=5)
    s = str(entry)
    assert "FOO" in s
    assert "3/5" in s
    assert "60%" in s


def test_drift_rate_zero_comparisons():
    entry = HeatmapEntry(key="K", drift_count=0, total_comparisons=0)
    assert entry.drift_rate == 0.0
