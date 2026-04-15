"""Tests for envdrift.ignorer."""

import pytest
from pathlib import Path

from envdrift.ignorer import (
    load_ignore_patterns,
    should_ignore,
    filter_keys,
    _pattern_matches,
)


@pytest.fixture
def tmp_ignore(tmp_path):
    def _write(content: str) -> Path:
        p = tmp_path / ".envdriftignore"
        p.write_text(content)
        return p
    return _write


def test_load_ignore_patterns_basic(tmp_ignore):
    p = tmp_ignore("SECRET_KEY\nDATABASE_URL\n")
    patterns = load_ignore_patterns(p)
    assert patterns == ["SECRET_KEY", "DATABASE_URL"]


def test_load_ignore_patterns_skips_comments_and_blanks(tmp_ignore):
    p = tmp_ignore("# this is a comment\n\nAPI_KEY\n")
    patterns = load_ignore_patterns(p)
    assert patterns == ["API_KEY"]


def test_load_ignore_patterns_missing_file(tmp_path):
    patterns = load_ignore_patterns(tmp_path / "nonexistent")
    assert patterns == []


def test_load_ignore_patterns_default_missing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    patterns = load_ignore_patterns()
    assert patterns == []


def test_pattern_matches_exact():
    assert _pattern_matches("SECRET_KEY", "SECRET_KEY")
    assert not _pattern_matches("SECRET_KEY", "OTHER_KEY")


def test_pattern_matches_wildcard_suffix():
    assert _pattern_matches("AWS_*", "AWS_ACCESS_KEY")
    assert _pattern_matches("AWS_*", "AWS_SECRET")
    assert not _pattern_matches("AWS_*", "GCP_SECRET")


def test_pattern_matches_wildcard_prefix():
    assert _pattern_matches("*_SECRET", "DB_SECRET")
    assert not _pattern_matches("*_SECRET", "DB_KEY")


def test_pattern_matches_case_insensitive():
    assert _pattern_matches("secret_key", "SECRET_KEY")


def test_should_ignore_true():
    assert should_ignore("SECRET_KEY", ["SECRET_KEY", "API_TOKEN"])


def test_should_ignore_false():
    assert not should_ignore("PORT", ["SECRET_KEY", "API_TOKEN"])


def test_should_ignore_empty_patterns():
    assert not should_ignore("ANYTHING", [])


def test_filter_keys_removes_matched():
    env = {"SECRET_KEY": "abc", "PORT": "8080", "AWS_ID": "id123"}
    result = filter_keys(env, ["SECRET_KEY", "AWS_*"])
    assert result == {"PORT": "8080"}


def test_filter_keys_no_patterns():
    env = {"A": "1", "B": "2"}
    assert filter_keys(env, []) == env


def test_filter_keys_all_ignored():
    env = {"SECRET": "x", "TOKEN": "y"}
    result = filter_keys(env, ["SECRET", "TOKEN"])
    assert result == {}
