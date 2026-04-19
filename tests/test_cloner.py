"""Tests for envdrift.cloner."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdrift.cloner import clone_env
from envdrift.parser import parse_env_file


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_basic_clone(tmp_env, tmp_path):
    src = tmp_env("source.env", "FOO=bar\nBAZ=qux\n")
    dst = str(tmp_path / "target.env")
    result = clone_env(src, dst)
    assert set(result.keys_written) == {"FOO", "BAZ"}
    assert result.keys_skipped == []
    parsed = parse_env_file(dst)
    assert parsed == {"FOO": "bar", "BAZ": "qux"}


def test_clone_with_include(tmp_env, tmp_path):
    src = tmp_env("source.env", "FOO=1\nBAR=2\nBAZ=3\n")
    dst = str(tmp_path / "out.env")
    result = clone_env(src, dst, include=["FOO", "BAZ"])
    assert result.keys_written == ["FOO", "BAZ"]
    assert "BAR" in result.keys_skipped
    parsed = parse_env_file(dst)
    assert "BAR" not in parsed


def test_clone_with_exclude(tmp_env, tmp_path):
    src = tmp_env("source.env", "FOO=1\nSECRET=hunter2\n")
    dst = str(tmp_path / "out.env")
    result = clone_env(src, dst, exclude=["SECRET"])
    assert "SECRET" in result.keys_skipped
    assert "FOO" in result.keys_written
    parsed = parse_env_file(dst)
    assert "SECRET" not in parsed


def test_clone_redacts_sensitive(tmp_env, tmp_path):
    src = tmp_env("source.env", "API_KEY=supersecret\nHOST=localhost\n")
    dst = str(tmp_path / "out.env")
    result = clone_env(src, dst, redact=True)
    parsed = parse_env_file(dst)
    assert parsed["API_KEY"] == "***"
    assert parsed["HOST"] == "localhost"
    assert "API_KEY" in result.redacted_keys


def test_clone_creates_parent_dirs(tmp_env, tmp_path):
    src = tmp_env("source.env", "X=1\n")
    dst = str(tmp_path / "nested" / "deep" / "out.env")
    clone_env(src, dst)
    assert Path(dst).exists()


def test_clone_missing_source_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        clone_env(str(tmp_path / "nope.env"), str(tmp_path / "out.env"))
