import pytest
from envdrift.normalizer import (
    normalize_env,
    render_normalized,
    has_changes,
    NormalizeResult,
)


def test_no_changes_clean_env():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = normalize_env(env)
    assert result.normalized == env
    assert not has_changes(result)


def test_strips_whitespace():
    env = {"KEY": "  value  "}
    result = normalize_env(env)
    assert result.normalized["KEY"] == "value"
    assert has_changes(result)
    assert any("stripped whitespace" in c for c in result.changes)


def test_normalizes_bool_true_variants():
    for val in ["True", "TRUE", "yes", "YES", "1", "On"]:
        result = normalize_env({"FLAG": val})
        assert result.normalized["FLAG"] == "true", f"failed for {val!r}"


def test_normalizes_bool_false_variants():
    for val in ["False", "FALSE", "no", "NO", "0", "Off"]:
        result = normalize_env({"FLAG": val})
        assert result.normalized["FLAG"] == "false", f"failed for {val!r}"


def test_already_normalized_bool_no_change():
    result = normalize_env({"FLAG": "true"})
    assert not has_changes(result)
    result2 = normalize_env({"FLAG": "false"})
    assert not has_changes(result2)


def test_original_preserved():
    env = {"KEY": "YES"}
    result = normalize_env(env)
    assert result.original["KEY"] == "YES"
    assert result.normalized["KEY"] == "true"


def test_multiple_keys_changes_tracked():
    env = {"A": "YES", "B": "  hello  ", "C": "clean"}
    result = normalize_env(env)
    assert len(result.changes) == 2


def test_render_normalized_basic():
    env = {"HOST": "localhost", "DEBUG": "true"}
    result = normalize_env(env)
    rendered = render_normalized(result)
    assert "HOST=localhost" in rendered
    assert "DEBUG=true" in rendered


def test_render_normalized_quotes_values_with_spaces():
    env = {"MSG": "hello world"}
    result = normalize_env(env)
    rendered = render_normalized(result)
    assert 'MSG="hello world"' in rendered


def test_render_empty_env():
    result = normalize_env({})
    assert render_normalized(result) == ""
