"""Tests for envdrift.differ_entropy."""
import pytest

from envdrift.differ_entropy import (
    EntropyEntry,
    EntropyResult,
    _shannon,
    analyse_entropy,
)


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


# --- unit tests for _shannon ---

def test_shannon_all_same():
    assert _shannon(["a", "a", "a"]) == pytest.approx(0.0)


def test_shannon_all_different():
    # 4 unique values, uniform distribution -> log2(4) = 2.0
    assert _shannon(["a", "b", "c", "d"]) == pytest.approx(2.0)


def test_shannon_empty_list():
    assert _shannon([]) == 0.0


def test_shannon_two_equal_halves():
    assert _shannon(["x", "x", "y", "y"]) == pytest.approx(1.0)


# --- analyse_entropy ---

def test_requires_at_least_two_envs(tmp_env):
    p = tmp_env("a.env", "KEY=1\n")
    with pytest.raises(ValueError, match="at least two"):
        analyse_entropy({"a": p})


def test_no_drift_identical_files(tmp_env):
    content = "KEY=hello\nDB=postgres\n"
    a = tmp_env("a.env", content)
    b = tmp_env("b.env", content)
    result = analyse_entropy({"a": a, "b": b})
    assert isinstance(result, EntropyResult)
    assert all(e.is_uniform for e in result.entries)
    assert result.average_entropy == pytest.approx(0.0)


def test_fully_diverse_values(tmp_env):
    a = tmp_env("a.env", "SECRET=aaa\n")
    b = tmp_env("b.env", "SECRET=bbb\n")
    result = analyse_entropy({"a": a, "b": b})
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.key == "SECRET"
    assert entry.is_fully_diverse
    assert entry.shannon_entropy == pytest.approx(1.0)


def test_missing_key_treated_as_empty(tmp_env):
    a = tmp_env("a.env", "KEY=val\n")
    b = tmp_env("b.env", "OTHER=x\n")
    result = analyse_entropy({"a": a, "b": b}, ignore_empty=False)
    keys = {e.key for e in result.entries}
    assert "KEY" in keys
    assert "OTHER" in keys


def test_ignore_empty_skips_all_blank_keys(tmp_env):
    a = tmp_env("a.env", "EMPTY=\n")
    b = tmp_env("b.env", "EMPTY=\n")
    result = analyse_entropy({"a": a, "b": b}, ignore_empty=True)
    assert result.entries == []


def test_high_entropy_keys_filtered(tmp_env):
    a = tmp_env("a.env", "A=1\nB=x\n")
    b = tmp_env("b.env", "A=2\nB=x\n")
    c = tmp_env("c.env", "A=3\nB=x\n")
    result = analyse_entropy({"a": a, "b": b, "c": c})
    high = result.high_entropy_keys
    assert all(e.key == "A" for e in high)


def test_uniform_keys_filtered(tmp_env):
    a = tmp_env("a.env", "SHARED=same\nDIFF=1\n")
    b = tmp_env("b.env", "SHARED=same\nDIFF=2\n")
    result = analyse_entropy({"a": a, "b": b})
    uniform = {e.key for e in result.uniform_keys}
    assert "SHARED" in uniform
    assert "DIFF" not in uniform


def test_env_names_stored(tmp_env):
    a = tmp_env("a.env", "K=1\n")
    b = tmp_env("b.env", "K=2\n")
    result = analyse_entropy({"dev": a, "prod": b})
    assert result.env_names == ["dev", "prod"]


def test_entry_str_representation(tmp_env):
    a = tmp_env("a.env", "FOO=a\n")
    b = tmp_env("b.env", "FOO=b\n")
    result = analyse_entropy({"a": a, "b": b})
    s = str(result.entries[0])
    assert "FOO" in s
    assert "entropy=" in s
