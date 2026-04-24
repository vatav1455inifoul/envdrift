"""Tests for envdrift.referencer."""

import pytest
from envdrift.referencer import _extract_refs, analyse_references


# ---------------------------------------------------------------------------
# _extract_refs
# ---------------------------------------------------------------------------

def test_extract_refs_dollar_brace():
    assert _extract_refs("${FOO}/bar") == ["FOO"]


def test_extract_refs_plain_dollar():
    assert _extract_refs("$FOO/bar") == ["FOO"]


def test_extract_refs_multiple():
    refs = _extract_refs("${HOST}:${PORT}")
    assert refs == ["HOST", "PORT"]


def test_extract_refs_none():
    assert _extract_refs("plain-value") == []


def test_extract_refs_mixed_styles():
    refs = _extract_refs("$SCHEME://${HOST}")
    assert refs == ["SCHEME", "HOST"]


# ---------------------------------------------------------------------------
# analyse_references
# ---------------------------------------------------------------------------

def test_no_references_returns_empty_consumers():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = analyse_references(env, env_name="test")
    assert result.consumers == {}
    assert result.providers == {}
    assert not result.has_dangling


def test_consumer_recorded_correctly():
    env = {"BASE": "https://x.com", "URL": "${BASE}/api"}
    result = analyse_references(env, env_name="test")
    assert "URL" in result.consumers
    assert result.consumers["URL"] == ["BASE"]


def test_provider_recorded_correctly():
    env = {"HOST": "localhost", "DSN": "${HOST}:5432"}
    result = analyse_references(env, env_name="test")
    assert "HOST" in result.providers
    assert result.providers["HOST"] == ["DSN"]


def test_no_dangling_when_all_keys_present():
    env = {"HOST": "localhost", "URL": "http://${HOST}"}
    result = analyse_references(env, env_name="test")
    assert not result.has_dangling
    assert result.dangling == {}


def test_dangling_when_referenced_key_missing():
    env = {"URL": "http://${HOST}"}
    result = analyse_references(env, env_name="test")
    assert result.has_dangling
    assert "URL" in result.dangling
    assert "HOST" in result.dangling["URL"]


def test_all_referenced_keys_aggregated():
    env = {
        "A": "${X}",
        "B": "${X}/${Y}",
        "X": "val",
        "Y": "val2",
    }
    result = analyse_references(env, env_name="test")
    assert result.all_referenced_keys == {"X", "Y"}


def test_env_name_stored():
    result = analyse_references({}, env_name="production")
    assert result.env_name == "production"


def test_multiple_consumers_for_same_provider():
    env = {
        "HOST": "localhost",
        "URL1": "${HOST}:8080",
        "URL2": "${HOST}:9090",
    }
    result = analyse_references(env, env_name="test")
    assert set(result.providers["HOST"]) == {"URL1", "URL2"}
