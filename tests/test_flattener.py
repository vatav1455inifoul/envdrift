import pytest
from envdrift.flattener import (
    flatten_env,
    has_overrides,
    override_keys,
    FlattenResult,
)


def test_basic_flatten_no_prefix():
    result = flatten_env({"DB_HOST": "localhost", "DB_PORT": "5432"}, env_name="prod")
    assert result.env_name == "prod"
    assert "db_host" in result.flat
    assert result.flat["db_port"] == "5432"


def test_strip_prefix_removes_leading_segment():
    env = {"APP_HOST": "localhost", "APP_PORT": "8080", "OTHER": "x"}
    result = flatten_env(env, strip_prefix="APP")
    assert "host" in result.flat
    assert "port" in result.flat
    assert "other" in result.flat


def test_strip_prefix_case_insensitive():
    env = {"app_debug": "true"}
    result = flatten_env(env, strip_prefix="APP")
    assert "debug" in result.flat


def test_lowercase_false_preserves_case():
    env = {"DB_HOST": "localhost"}
    result = flatten_env(env, lowercase=False)
    assert "DB_HOST" in result.flat
    assert "db_host" not in result.flat


def test_no_overrides_unique_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = flatten_env(env)
    assert not has_overrides(result)
    assert override_keys(result) == []


def test_detects_collision_after_prefix_strip():
    # APP_HOST and HOST both collapse to 'host' after stripping APP prefix
    env = {"APP_HOST": "prod", "HOST": "dev"}
    result = flatten_env(env, strip_prefix="APP")
    assert has_overrides(result)
    assert "host" in override_keys(result)


def test_last_value_wins_on_collision():
    env = {"APP_PORT": "9000", "PORT": "8000"}
    result = flatten_env(env, strip_prefix="APP")
    # dict ordering: APP_PORT first -> flat[port]=9000, then PORT -> flat[port]=8000
    assert result.flat["port"] == "8000"


def test_keys_list_matches_flat():
    env = {"X": "1", "Y": "2"}
    result = flatten_env(env)
    assert set(result.keys) == set(result.flat.keys())


def test_empty_env():
    result = flatten_env({})
    assert result.flat == {}
    assert result.keys == []
    assert not has_overrides(result)
