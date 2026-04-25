"""Tests for envdrift.differ_variance and envdrift.variance_reporter."""
from __future__ import annotations
import pytest
from pathlib import Path
from envdrift.differ_variance import analyse_variance, VarianceEntry, VarianceResult
from envdrift.variance_reporter import format_variance_report


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_requires_at_least_two_envs(tmp_env):
    f = tmp_env("a.env", "KEY=1\n")
    with pytest.raises(ValueError, match="at least two"):
        analyse_variance({"a": f})


def test_no_variance_identical_files(tmp_env):
    content = "KEY=hello\nOTHER=world\n"
    a = tmp_env("a.env", content)
    b = tmp_env("b.env", content)
    result = analyse_variance({"a": a, "b": b})
    assert result.is_uniform
    assert len(result.divergent_keys) == 0
    assert len(result.partial_keys) == 0


def test_detects_divergent_value(tmp_env):
    a = tmp_env("a.env", "KEY=hello\n")
    b = tmp_env("b.env", "KEY=world\n")
    result = analyse_variance({"a": a, "b": b})
    assert not result.is_uniform
    assert len(result.divergent_keys) == 1
    entry = result.divergent_keys[0]
    assert entry.key == "KEY"
    assert entry.unique_values == 2


def test_detects_partial_key(tmp_env):
    a = tmp_env("a.env", "KEY=hello\nEXTRA=only_in_a\n")
    b = tmp_env("b.env", "KEY=hello\n")
    result = analyse_variance({"a": a, "b": b})
    assert len(result.partial_keys) == 1
    assert result.partial_keys[0].key == "EXTRA"
    assert "b" in result.partial_keys[0].missing_in


def test_variance_ratio_two_envs(tmp_env):
    a = tmp_env("a.env", "K=1\n")
    b = tmp_env("b.env", "K=2\n")
    result = analyse_variance({"a": a, "b": b})
    entry = result.entries[0]
    assert entry.variance_ratio == pytest.approx(0.5)


def test_three_envs_two_same_one_different(tmp_env):
    a = tmp_env("a.env", "K=same\n")
    b = tmp_env("b.env", "K=same\n")
    c = tmp_env("c.env", "K=other\n")
    result = analyse_variance({"a": a, "b": b, "c": c})
    assert not result.is_uniform
    entry = result.divergent_keys[0]
    # 1 out of 3 diverges
    assert entry.variance_ratio == pytest.approx(1 / 3)


def test_env_names_stored_in_result(tmp_env):
    a = tmp_env("a.env", "K=1\n")
    b = tmp_env("b.env", "K=1\n")
    result = analyse_variance({"staging": a, "prod": b})
    assert "staging" in result.env_names
    assert "prod" in result.env_names


def test_format_report_no_variance(tmp_env):
    a = tmp_env("a.env", "K=1\n")
    b = tmp_env("b.env", "K=1\n")
    result = analyse_variance({"a": a, "b": b})
    report = format_variance_report(result, color=False)
    assert "uniform" in report.lower()
    assert "✔" in report


def test_format_report_shows_divergent_key(tmp_env):
    a = tmp_env("a.env", "DB=postgres\n")
    b = tmp_env("b.env", "DB=sqlite\n")
    result = analyse_variance({"a": a, "b": b})
    report = format_variance_report(result, color=False)
    assert "DB" in report
    assert "postgres" in report
    assert "sqlite" in report


def test_format_report_shows_partial_key(tmp_env):
    a = tmp_env("a.env", "KEY=1\nONLY_A=x\n")
    b = tmp_env("b.env", "KEY=1\n")
    result = analyse_variance({"a": a, "b": b})
    report = format_variance_report(result, color=False)
    assert "ONLY_A" in report
    assert "missing" in report.lower()
