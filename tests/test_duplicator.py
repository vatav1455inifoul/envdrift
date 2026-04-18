import pytest
from envdrift.duplicator import find_duplicate_values, DuplicateValueResult


def _env(**kwargs):
    return dict(kwargs)


def test_no_duplicates_all_unique():
    env = _env(A="foo", B="bar", C="baz")
    result = find_duplicate_values(env, env_name="test")
    assert not result.has_duplicates
    assert result.duplicate_groups == {}
    assert result.total_duplicate_keys == 0


def test_detects_shared_value():
    env = _env(A="secret", B="secret", C="other")
    result = find_duplicate_values(env, env_name="prod")
    assert result.has_duplicates
    assert "secret" in result.duplicate_groups
    assert set(result.duplicate_groups["secret"]) == {"A", "B"}


def test_multiple_duplicate_groups():
    env = _env(A="x", B="x", C="y", D="y", E="z")
    result = find_duplicate_values(env)
    groups = result.duplicate_groups
    assert len(groups) == 2
    assert result.total_duplicate_keys == 4


def test_blank_values_ignored_by_default():
    env = _env(A="", B="", C="real")
    result = find_duplicate_values(env)
    assert not result.has_duplicates


def test_blank_values_included_when_flag_off():
    env = _env(A="", B="", C="real")
    result = find_duplicate_values(env, ignore_blank=False)
    assert result.has_duplicates
    assert "" in result.duplicate_groups
    assert set(result.duplicate_groups[""]) == {"A", "B"}


def test_env_name_stored():
    result = find_duplicate_values({}, env_name="staging")
    assert result.env_name == "staging"


def test_single_key_env():
    env = _env(ONLY="value")
    result = find_duplicate_values(env)
    assert not result.has_duplicates
