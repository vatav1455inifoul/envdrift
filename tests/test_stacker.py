"""Tests for envdrift.stacker."""
from __future__ import annotations

import pytest

from envdrift.stacker import StackResult, stack_envs, winning_layer


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


# ---------------------------------------------------------------------------
# stack_envs
# ---------------------------------------------------------------------------

def test_single_file_returns_its_keys(tmp_env):
    p = tmp_env("base.env", "FOO=bar\nBAZ=qux\n")
    result = stack_envs([p])
    assert result.merged == {"FOO": "bar", "BAZ": "qux"}
    assert result.total_keys == 2


def test_later_file_overrides_earlier(tmp_env):
    base = tmp_env("base.env", "FOO=base\nSHARED=base\n")
    override = tmp_env("prod.env", "SHARED=prod\nEXTRA=yes\n")
    result = stack_envs([base, override])
    assert result.merged["SHARED"] == "prod"
    assert result.merged["FOO"] == "base"
    assert result.merged["EXTRA"] == "yes"


def test_three_layers_last_wins(tmp_env):
    a = tmp_env("a.env", "KEY=a\n")
    b = tmp_env("b.env", "KEY=b\n")
    c = tmp_env("c.env", "KEY=c\n")
    result = stack_envs([a, b, c])
    assert result.merged["KEY"] == "c"


def test_overridden_keys_detected(tmp_env):
    base = tmp_env("base.env", "A=1\nB=2\n")
    over = tmp_env("over.env", "B=99\n")
    result = stack_envs([base, over])
    assert "B" in result.overridden_keys
    assert "A" not in result.overridden_keys


def test_unique_keys_detected(tmp_env):
    base = tmp_env("base.env", "ONLY_BASE=x\nSHARED=1\n")
    over = tmp_env("over.env", "SHARED=2\n")
    result = stack_envs([base, over])
    assert "ONLY_BASE" in result.unique_keys
    assert "SHARED" not in result.unique_keys


def test_custom_names_stored(tmp_env):
    p = tmp_env("x.env", "K=v\n")
    result = stack_envs([p], names=["my-layer"])
    assert result.env_names == ["my-layer"]


def test_provenance_records_all_layers(tmp_env):
    a = tmp_env("a.env", "KEY=first\n")
    b = tmp_env("b.env", "KEY=second\n")
    result = stack_envs([a, b], names=["a", "b"])
    layers = result.provenance["KEY"]
    assert len(layers) == 2
    assert layers[0] == ("a", "first")
    assert layers[1] == ("b", "second")


def test_empty_file_is_valid(tmp_env):
    p = tmp_env("empty.env", "")
    result = stack_envs([p])
    assert result.merged == {}
    assert result.total_keys == 0


def test_raises_with_no_files():
    with pytest.raises(ValueError, match="at least one"):
        stack_envs([])


# ---------------------------------------------------------------------------
# winning_layer
# ---------------------------------------------------------------------------

def test_winning_layer_returns_last(tmp_env):
    a = tmp_env("a.env", "X=1\n")
    b = tmp_env("b.env", "X=2\n")
    result = stack_envs([a, b], names=["base", "local"])
    assert winning_layer(result, "X") == "local"


def test_winning_layer_missing_key_returns_none(tmp_env):
    p = tmp_env("a.env", "A=1\n")
    result = stack_envs([p])
    assert winning_layer(result, "NONEXISTENT") is None
