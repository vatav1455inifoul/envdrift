"""Tests for envdrift.reporter."""

import io
import pytest
from envdrift.comparator import DriftResult
from envdrift.reporter import format_report, print_report


@pytest.fixture
def no_drift():
    return DriftResult(missing_keys=set(), extra_keys=set(), changed_values={})


@pytest.fixture
def full_drift():
    return DriftResult(
        missing_keys={"SECRET_KEY"},
        extra_keys={"NEW_FLAG"},
        changed_values={"DATABASE_URL": ("postgres://old", "postgres://new")},
    )


def test_no_drift_message(no_drift):
    report = format_report(no_drift, ".env", ".env.prod", use_color=False)
    assert "No drift detected" in report
    assert "Missing" not in report
    assert "Extra" not in report


def test_header_contains_env_names(full_drift):
    report = format_report(full_drift, ".env", ".env.staging", use_color=False)
    assert ".env" in report
    assert ".env.staging" in report


def test_missing_keys_shown(full_drift):
    report = format_report(full_drift, "a", "b", use_color=False)
    assert "SECRET_KEY" in report
    assert "Missing" in report


def test_extra_keys_shown(full_drift):
    report = format_report(full_drift, "a", "b", use_color=False)
    assert "NEW_FLAG" in report
    assert "Extra" in report


def test_changed_values_shown(full_drift):
    report = format_report(full_drift, "a", "b", use_color=False)
    assert "DATABASE_URL" in report
    assert "postgres://old" in report
    assert "postgres://new" in report


def test_summary_line_present(full_drift):
    report = format_report(full_drift, "a", "b", use_color=False)
    # summary() from DriftResult should appear at the end
    assert full_drift.summary() in report


def test_print_report_writes_to_buffer(full_drift):
    buf = io.StringIO()
    print_report(full_drift, "a", "b", use_color=False, output=buf)
    output = buf.getvalue()
    assert "DATABASE_URL" in output
    assert "SECRET_KEY" in output


def test_color_codes_absent_when_disabled(full_drift):
    report = format_report(full_drift, "a", "b", use_color=False)
    assert "\033[" not in report


def test_color_codes_present_when_enabled(full_drift):
    report = format_report(full_drift, "a", "b", use_color=True)
    assert "\033[" in report
