"""Tests for differ_chain and chain_reporter."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdrift.differ_chain import chain_diff, ChainResult, ChainLink
from envdrift.chain_reporter import format_chain_report


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# chain_diff
# ---------------------------------------------------------------------------

def test_requires_at_least_two_envs(tmp_env):
    f = _write(tmp_env / "a.env", "KEY=1\n")
    with pytest.raises(ValueError, match="at least two"):
        chain_diff([("a", str(f))])


def test_no_drift_identical_chain(tmp_env):
    content = "KEY=value\nOTHER=123\n"
    f1 = _write(tmp_env / "a.env", content)
    f2 = _write(tmp_env / "b.env", content)
    f3 = _write(tmp_env / "c.env", content)

    result = chain_diff([("a", str(f1)), ("b", str(f2)), ("c", str(f3))])

    assert isinstance(result, ChainResult)
    assert len(result.links) == 2
    assert not result.has_drift
    assert result.stable_links == result.links
    assert result.drifting_links == []


def test_detects_missing_key_in_chain(tmp_env):
    f1 = _write(tmp_env / "a.env", "KEY=1\nEXTRA=yes\n")
    f2 = _write(tmp_env / "b.env", "KEY=1\n")

    result = chain_diff([("a", str(f1)), ("b", str(f2))])

    assert result.has_drift
    assert len(result.drifting_links) == 1
    link = result.links[0]
    assert "EXTRA" in link.result.missing_keys


def test_detects_changed_value(tmp_env):
    f1 = _write(tmp_env / "a.env", "KEY=old\n")
    f2 = _write(tmp_env / "b.env", "KEY=new\n")

    result = chain_diff([("a", str(f1)), ("b", str(f2))])

    assert result.has_drift
    assert "KEY" in result.links[0].result.changed_values


def test_ignore_values_skips_value_changes(tmp_env):
    f1 = _write(tmp_env / "a.env", "KEY=old\n")
    f2 = _write(tmp_env / "b.env", "KEY=new\n")

    result = chain_diff([("a", str(f1)), ("b", str(f2))], ignore_values=True)

    assert not result.has_drift


def test_summary_counts(tmp_env):
    f1 = _write(tmp_env / "a.env", "A=1\nB=2\n")
    f2 = _write(tmp_env / "b.env", "A=changed\n")
    f3 = _write(tmp_env / "c.env", "A=changed\nC=3\n")

    result = chain_diff([("a", str(f1)), ("b", str(f2)), ("c", str(f3))])
    s = result.summary()

    assert s["links"] == 2
    assert s["total_missing"] >= 1   # B missing in b
    assert s["total_extra"] >= 1     # C extra in c


# ---------------------------------------------------------------------------
# chain_reporter
# ---------------------------------------------------------------------------

def test_format_report_no_drift(tmp_env):
    content = "KEY=1\n"
    f1 = _write(tmp_env / "a.env", content)
    f2 = _write(tmp_env / "b.env", content)

    result = chain_diff([("dev", str(f1)), ("prod", str(f2))])
    report = format_chain_report(result)

    assert "dev" in report
    assert "prod" in report
    assert "no drift" in report


def test_format_report_shows_drift(tmp_env):
    f1 = _write(tmp_env / "a.env", "KEY=old\nEXTRA=yes\n")
    f2 = _write(tmp_env / "b.env", "KEY=new\n")

    result = chain_diff([("staging", str(f1)), ("prod", str(f2))])
    report = format_chain_report(result)

    assert "KEY" in report
    assert "EXTRA" in report
    assert "drifting" in report
