"""Tests for envdrift.merger."""

import os
import pytest

from envdrift.merger import merge_envs, render_template


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_merge_single_env(tmp_env):
    path = tmp_env("a.env", "FOO=1\nBAR=2\n")
    result = merge_envs({"a": path})
    assert result.keys == ["FOO", "BAR"]
    assert result.values["FOO"] == "1"
    assert result.missing_in["FOO"] == []


def test_merge_collects_all_keys(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=1\nBAZ=3\n")
    result = merge_envs({"a": a, "b": b})
    assert set(result.keys) == {"FOO", "BAR", "BAZ"}


def test_primary_values_take_precedence(tmp_env):
    a = tmp_env("a.env", "FOO=from_a\n")
    b = tmp_env("b.env", "FOO=from_b\n")
    result = merge_envs({"a": a, "b": b}, primary="b")
    assert result.values["FOO"] == "from_b"


def test_missing_in_populated_correctly(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=1\n")
    result = merge_envs({"a": a, "b": b})
    assert "b" in result.missing_in["BAR"]
    assert result.missing_in["FOO"] == []


def test_complete_and_partial_keys(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=1\n")
    result = merge_envs({"a": a, "b": b})
    assert "FOO" in result.complete_keys
    assert "BAR" in result.partial_keys


def test_primary_key_ordering(tmp_env):
    a = tmp_env("a.env", "ALPHA=1\nBETA=2\n")
    b = tmp_env("b.env", "GAMMA=3\nALPHA=1\n")
    result = merge_envs({"a": a, "b": b}, primary="a")
    # ALPHA and BETA come first (from primary), then GAMMA
    assert result.keys.index("ALPHA") < result.keys.index("GAMMA")


def test_sources_tracks_first_seen(tmp_env):
    a = tmp_env("a.env", "FOO=1\n")
    b = tmp_env("b.env", "FOO=1\nNEW=5\n")
    result = merge_envs({"a": a, "b": b})
    assert result.sources["FOO"] == "a"
    assert result.sources["NEW"] == "b"


def test_requires_at_least_one_env():
    with pytest.raises(ValueError, match="At least one"):
        merge_envs({})


def test_invalid_primary_raises(tmp_env):
    a = tmp_env("a.env", "FOO=1\n")
    with pytest.raises(ValueError, match="Primary env"):
        merge_envs({"a": a}, primary="nonexistent")


def test_render_template_all_keys(tmp_env):
    a = tmp_env("a.env", "FOO=hello\nBAR=world\n")
    b = tmp_env("b.env", "FOO=hello\nBAZ=extra\n")
    result = merge_envs({"a": a, "b": b})
    rendered = render_template(result)
    assert "FOO=hello" in rendered
    assert "BAZ=" in rendered


def test_render_template_placeholder(tmp_env):
    a = tmp_env("a.env", "FOO=1\n")
    b = tmp_env("b.env", "BAR=2\n")
    result = merge_envs({"a": a, "b": b})
    rendered = render_template(result, placeholder="CHANGE_ME")
    assert "BAR=CHANGE_ME" in rendered
    assert "FOO=1" in rendered
