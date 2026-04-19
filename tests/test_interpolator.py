"""Tests for envdrift.interpolator."""
import pytest
from envdrift.interpolator import _extract_refs, check_interpolation


def test_extract_refs_dollar_brace():
    assert _extract_refs("${FOO}") == ["FOO"]


def test_extract_refs_plain_dollar():
    assert _extract_refs("$BAR") == ["BAR"]


def test_extract_refs_multiple():
    refs = _extract_refs("${HOST}:${PORT}")
    assert refs == ["HOST", "PORT"]


def test_extract_refs_none():
    assert _extract_refs("plain_value") == []


def test_no_references():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = check_interpolation(env, "test")
    assert not result.references
    assert not result.has_unresolved
    assert result.all_referenced_keys == set()


def test_resolved_reference():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = check_interpolation(env, "test")
    assert "URL" in result.references
    assert result.references["URL"] == ["HOST"]
    assert not result.has_unresolved


def test_unresolved_reference():
    env = {"URL": "http://${HOST}/api"}
    result = check_interpolation(env, "test")
    assert result.has_unresolved
    assert "URL" in result.unresolved
    assert "HOST" in result.unresolved["URL"]


def test_partial_resolution():
    env = {"HOST": "localhost", "URL": "http://${HOST}:${PORT}/"}
    result = check_interpolation(env, "test")
    assert result.has_unresolved
    assert result.unresolved["URL"] == ["PORT"]
    assert "HOST" not in result.unresolved.get("URL", [])


def test_all_referenced_keys():
    env = {"A": "${B}", "C": "${D}"}
    result = check_interpolation(env, "test")
    assert result.all_referenced_keys == {"B", "D"}


def test_env_name_stored():
    result = check_interpolation({}, "staging")
    assert result.env_name == "staging"
