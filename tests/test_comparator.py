"""Tests for the env comparator / drift detection logic."""

import pytest
from envdrift.comparator import compare_envs, DriftResult


BASE = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "DB_URL": "postgres://localhost/dev",
    "SECRET_KEY": "dev-secret",
}

TARGET = {
    "APP_NAME": "myapp",
    "DEBUG": "true",           # changed
    "DB_URL": "postgres://prod/prod",  # changed
    "NEW_RELIC_KEY": "abc",   # extra
    # SECRET_KEY missing
}


def test_detects_missing_keys():
    result = compare_envs(BASE, TARGET)
    assert "SECRET_KEY" in result.missing_keys


def test_detects_extra_keys():
    result = compare_envs(BASE, TARGET)
    assert "NEW_RELIC_KEY" in result.extra_keys


def test_detects_changed_values():
    result = compare_envs(BASE, TARGET)
    assert "DEBUG" in result.changed_keys
    assert result.changed_keys["DEBUG"] == ("false", "true")
    assert "DB_URL" in result.changed_keys


def test_no_drift_identical():
    result = compare_envs(BASE, BASE)
    assert not result.has_drift
    assert result.summary == "no drift"


def test_ignore_values_flag():
    """With ignore_values=True, same keys but different values should not flag changes."""
    same_keys_diff_vals = {k: "x" for k in BASE}
    result = compare_envs(BASE, same_keys_diff_vals, ignore_values=True)
    assert not result.changed_keys
    assert not result.missing_keys
    assert not result.extra_keys


def test_summary_string():
    result = compare_envs(BASE, TARGET)
    assert "missing" in result.summary
    assert "extra" in result.summary
    assert "changed" in result.summary


def test_labels_preserved():
    result = compare_envs(BASE, TARGET, base_label=".env.example", target_label=".env.prod")
    assert result.base_label == ".env.example"
    assert result.target_label == ".env.prod"


def test_has_drift_property():
    result = compare_envs(BASE, TARGET)
    assert result.has_drift is True
