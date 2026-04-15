"""Tests for envdrift.linter and envdrift.lint_commands."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import pytest

from envdrift.linter import lint_env_file
from envdrift.lint_commands import cmd_lint


@pytest.fixture
def tmp_env(tmp_path: Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content))
        return str(p)
    return _write


def test_clean_file_has_no_issues(tmp_env):
    path = tmp_env(".env", """
        DB_HOST=localhost
        DB_PORT=5432
        APP_NAME="my app"
    """)
    result = lint_env_file(path)
    assert not result.has_issues


def test_detects_duplicate_key(tmp_env):
    path = tmp_env(".env", """
        KEY=first
        KEY=second
    """)
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_detects_empty_value(tmp_env):
    path = tmp_env(".env", """
        EMPTY_KEY=
    """)
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_detects_unquoted_whitespace(tmp_env):
    path = tmp_env(".env", """
        GREETING=hello world
    """)
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_quoted_whitespace_is_ok(tmp_env):
    path = tmp_env(".env", """
        GREETING="hello world"
    """)
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W003" not in codes


def test_invalid_syntax_no_equals(tmp_env):
    path = tmp_env(".env", """
        BADLINE
    """)
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_missing_file_returns_error():
    result = lint_env_file("/nonexistent/.env")
    assert result.has_issues
    assert result.errors[0].code == "E001"


def test_comments_and_blanks_ignored(tmp_env):
    path = tmp_env(".env", """
        # this is a comment

        KEY=value
    """)
    result = lint_env_file(path)
    assert not result.has_issues


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"envfiles": [], "strict": False, "no_color": True}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_lint_clean_file_exits_zero(tmp_env):
    path = tmp_env(".env", "KEY=value\n")
    assert cmd_lint(_ns(envfiles=[path])) == 0


def test_cmd_lint_error_exits_one(tmp_env):
    path = tmp_env(".env", "BADLINE\n")
    assert cmd_lint(_ns(envfiles=[path])) == 1


def test_cmd_lint_strict_warning_exits_one(tmp_env):
    path = tmp_env(".env", "EMPTY=\n")
    assert cmd_lint(_ns(envfiles=[path], strict=True)) == 1


def test_cmd_lint_no_files_exits_one():
    assert cmd_lint(_ns(envfiles=[])) == 1
