"""Tests for the .env file parser."""

import pytest
from pathlib import Path
from textwrap import dedent

from envdrift.parser import parse_env_file, _clean_value


@pytest.fixture
def tmp_env(tmp_path):
    """Helper that writes a .env file and returns its path."""
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(dedent(content), encoding="utf-8")
        return p
    return _write


def test_basic_key_value(tmp_env):
    p = tmp_env("""
        APP_NAME=envdrift
        DEBUG=true
    """)
    result = parse_env_file(p)
    assert result["APP_NAME"] == "envdrift"
    assert result["DEBUG"] == "true"


def test_quoted_values(tmp_env):
    p = tmp_env("""
        SECRET="hello world"
        TOKEN='abc123'
    """)
    result = parse_env_file(p)
    assert result["SECRET"] == "hello world"
    assert result["TOKEN"] == "abc123"


def test_skips_comments_and_blanks(tmp_env):
    p = tmp_env("""
        # this is a comment
        APP=test

        # another comment
        PORT=8080
    """)
    result = parse_env_file(p)
    assert list(result.keys()) == ["APP", "PORT"]


def test_inline_comment_stripped(tmp_env):
    p = tmp_env("DB_HOST=localhost # primary db\n")
    result = parse_env_file(p)
    assert result["DB_HOST"] == "localhost"


def test_empty_value(tmp_env):
    p = tmp_env("EMPTY=\n")
    result = parse_env_file(p)
    assert result["EMPTY"] == ""


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_clean_value_double_quoted():
    assert _clean_value('"hello"') == "hello"


def test_clean_value_single_quoted():
    assert _clean_value("'world'") == "world"


def test_clean_value_empty():
    assert _clean_value("") == ""
