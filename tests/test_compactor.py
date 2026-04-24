"""Tests for envdrift.compactor."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdrift.compactor import compact_envs, render_compact_summary


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Factory: write a .env file and return its path."""
    counter = {"n": 0}

    def _write(content: str) -> str:
        counter["n"] += 1
        p = tmp_path / f"env{counter['n']}.env"
        p.write_text(content)
        return str(p)

    return _write


# ---------------------------------------------------------------------------
# basic cases
# ---------------------------------------------------------------------------

def test_requires_at_least_one_env():
    with pytest.raises(ValueError, match="at least one"):
        compact_envs([])


def test_single_layer_no_shadowed(tmp_env):
    p = tmp_env("FOO=1\nBAR=2\n")
    result = compact_envs([p])
    assert result.shadowed[p] == []
    assert not result.has_shadowed


def test_two_layers_override_detected(tmp_env):
    base = tmp_env("FOO=base\nBAR=base\n")
    override = tmp_env("FOO=new\n")
    result = compact_envs([base, override])
    # FOO in base is shadowed by override
    assert "FOO" in result.shadowed[base]
    # BAR is only in base, not shadowed
    assert "BAR" not in result.shadowed[base]
    # override layer itself has nothing shadowed
    assert result.shadowed[override] == []


def test_resolved_uses_last_layer(tmp_env):
    base = tmp_env("FOO=1\nBAR=old\n")
    top = tmp_env("BAR=new\nBAZ=3\n")
    result = compact_envs([base, top])
    assert result.resolved["FOO"] == "1"
    assert result.resolved["BAR"] == "new"
    assert result.resolved["BAZ"] == "3"


def test_three_layers_middle_also_shadowed(tmp_env):
    a = tmp_env("KEY=a\n")
    b = tmp_env("KEY=b\n")
    c = tmp_env("KEY=c\n")
    result = compact_envs([a, b, c])
    assert "KEY" in result.shadowed[a]
    assert "KEY" in result.shadowed[b]
    assert result.shadowed[c] == []


def test_total_shadowed_count(tmp_env):
    base = tmp_env("A=1\nB=2\nC=3\n")
    top = tmp_env("A=x\nB=y\n")
    result = compact_envs([base, top])
    assert result.total_shadowed == 2


def test_has_shadowed_false_when_no_overrides(tmp_env):
    a = tmp_env("UNIQUE_A=1\n")
    b = tmp_env("UNIQUE_B=2\n")
    result = compact_envs([a, b])
    assert not result.has_shadowed


# ---------------------------------------------------------------------------
# render_compact_summary
# ---------------------------------------------------------------------------

def test_render_summary_mentions_shadowed_keys(tmp_env):
    base = tmp_env("FOO=1\n")
    top = tmp_env("FOO=2\n")
    result = compact_envs([base, top])
    summary = render_compact_summary(result)
    assert "FOO" in summary
    assert "1 shadowed" in summary


def test_render_summary_no_shadow_message(tmp_env):
    p = tmp_env("ONLY=here\n")
    result = compact_envs([p])
    summary = render_compact_summary(result)
    assert "no shadowed keys" in summary
