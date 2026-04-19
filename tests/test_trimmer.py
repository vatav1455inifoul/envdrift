"""Tests for envdrift.trimmer and envdrift.trim_reporter."""
import os
import pytest
from envdrift.trimmer import trim_env, has_unused, render_trimmed
from envdrift.trim_reporter import format_trim_report


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content):
    path.write_text(content)
    return str(path)


def test_no_unused_when_identical(tmp_env):
    env = _write(tmp_env / "app.env", "A=1\nB=2\n")
    ref = _write(tmp_env / "ref.env", "A=x\nB=y\n")
    result = trim_env(env, ref)
    assert not has_unused(result)
    assert result.unused_keys == []
    assert set(result.kept_env) == {"A", "B"}


def test_detects_unused_keys(tmp_env):
    env = _write(tmp_env / "app.env", "A=1\nB=2\nC=3\n")
    ref = _write(tmp_env / "ref.env", "A=x\n")
    result = trim_env(env, ref)
    assert has_unused(result)
    assert set(result.unused_keys) == {"B", "C"}
    assert set(result.kept_env) == {"A"}


def test_all_unused_when_no_overlap(tmp_env):
    env = _write(tmp_env / "app.env", "X=1\nY=2\n")
    ref = _write(tmp_env / "ref.env", "A=x\n")
    result = trim_env(env, ref)
    assert set(result.unused_keys) == {"X", "Y"}
    assert result.kept_env == {}


def test_render_trimmed_only_kept_keys(tmp_env):
    env = _write(tmp_env / "app.env", "A=1\nB=2\nC=3\n")
    ref = _write(tmp_env / "ref.env", "A=x\nC=y\n")
    result = trim_env(env, ref)
    rendered = render_trimmed(result)
    assert "A=1" in rendered
    assert "C=3" in rendered
    assert "B" not in rendered


def test_render_trimmed_empty_when_nothing_kept(tmp_env):
    env = _write(tmp_env / "app.env", "X=1\n")
    ref = _write(tmp_env / "ref.env", "A=x\n")
    result = trim_env(env, ref)
    assert render_trimmed(result) == ""


def test_env_names_default_to_paths(tmp_env):
    env = _write(tmp_env / "app.env", "A=1\n")
    ref = _write(tmp_env / "ref.env", "A=x\n")
    result = trim_env(env, ref)
    assert result.env_name == env
    assert result.reference_name == ref


def test_custom_names(tmp_env):
    env = _write(tmp_env / "app.env", "A=1\n")
    ref = _write(tmp_env / "ref.env", "A=x\n")
    result = trim_env(env, ref, env_name="prod", reference_name="staging")
    assert result.env_name == "prod"
    assert result.reference_name == "staging"


def test_report_no_unused_message(tmp_env):
    env = _write(tmp_env / "app.env", "A=1\n")
    ref = _write(tmp_env / "ref.env", "A=x\n")
    result = trim_env(env, ref)
    report = format_trim_report(result, color=False)
    assert "No unused keys" in report


def test_report_lists_unused_keys(tmp_env):
    env = _write(tmp_env / "app.env", "A=1\nB=2\n")
    ref = _write(tmp_env / "ref.env", "A=x\n")
    result = trim_env(env, ref)
    report = format_trim_report(result, color=False)
    assert "B" in report
    assert "Unused keys" in report
