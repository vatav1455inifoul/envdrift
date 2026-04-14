"""Tests for envdrift.multi_reporter."""

from __future__ import annotations

import io
import pytest

from envdrift.differ import MultiDiffResult
from envdrift.multi_reporter import format_multi_report, print_multi_report


@pytest.fixture()
def no_drift() -> MultiDiffResult:
    envs = {"prod": {"KEY": "val"}, "staging": {"KEY": "val"}}
    return MultiDiffResult(
        env_names=["prod", "staging"],
        all_keys={"KEY"},
        missing_in_some={},
        inconsistent_keys={},
    )


@pytest.fixture()
def full_drift() -> MultiDiffResult:
    return MultiDiffResult(
        env_names=["prod", "staging", "dev"],
        all_keys={"DB_URL", "SECRET", "ONLY_PROD"},
        missing_in_some={
            "ONLY_PROD": ["prod"],
        },
        inconsistent_keys={
            "DB_URL": {"prod": "postgres://prod", "staging": "postgres://staging", "dev": "postgres://dev"},
            "SECRET": {"prod": "abc", "staging": "abc", "dev": "xyz"},
        },
    )


def test_no_drift_message(no_drift: MultiDiffResult) -> None:
    report = format_multi_report(no_drift, use_color=False)
    assert "No drift detected" in report


def test_header_contains_all_env_names(full_drift: MultiDiffResult) -> None:
    report = format_multi_report(full_drift, use_color=False)
    assert "prod" in report
    assert "staging" in report
    assert "dev" in report


def test_missing_keys_section(full_drift: MultiDiffResult) -> None:
    report = format_multi_report(full_drift, use_color=False)
    assert "ONLY_PROD" in report
    assert "absent in" in report


def test_inconsistent_keys_section(full_drift: MultiDiffResult) -> None:
    report = format_multi_report(full_drift, use_color=False)
    assert "DB_URL" in report
    assert "SECRET" in report
    assert "postgres://prod" in report


def test_no_drift_does_not_show_sections(no_drift: MultiDiffResult) -> None:
    report = format_multi_report(no_drift, use_color=False)
    assert "missing" not in report.lower() or "No drift" in report
    assert "inconsistent" not in report.lower()


def test_print_multi_report_writes_to_file(full_drift: MultiDiffResult) -> None:
    buf = io.StringIO()
    print_multi_report(full_drift, use_color=False, file=buf)
    output = buf.getvalue()
    assert "DB_URL" in output


def test_format_no_color_vs_color_differ(full_drift: MultiDiffResult) -> None:
    plain = format_multi_report(full_drift, use_color=False)
    colored = format_multi_report(full_drift, use_color=True)
    # colored output should contain ANSI escape codes
    assert "\033[" in colored
    # plain should not
    assert "\033[" not in plain
