"""Tests for envdrift.differ_consensus."""
import pytest
from pathlib import Path
from envdrift.differ_consensus import analyse_consensus, ConsensusResult


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> str:
    path.write_text(content)
    return str(path)


def test_requires_at_least_two_envs(tmp_env):
    f = _write(tmp_env / "a.env", "KEY=1\n")
    with pytest.raises(ValueError, match="at least two"):
        analyse_consensus({"a": f})


def test_unanimous_all_agree(tmp_env):
    f1 = _write(tmp_env / "a.env", "HOST=localhost\nPORT=5432\n")
    f2 = _write(tmp_env / "b.env", "HOST=localhost\nPORT=5432\n")
    f3 = _write(tmp_env / "c.env", "HOST=localhost\nPORT=5432\n")
    result = analyse_consensus({"a": f1, "b": f2, "c": f3})
    assert len(result.unanimous) == 2
    assert result.majority == []
    assert result.contested == []
    assert result.consensus_rate == 1.0


def test_majority_above_threshold(tmp_env):
    f1 = _write(tmp_env / "a.env", "HOST=localhost\n")
    f2 = _write(tmp_env / "b.env", "HOST=localhost\n")
    f3 = _write(tmp_env / "c.env", "HOST=remotehost\n")
    result = analyse_consensus({"a": f1, "b": f2, "c": f3}, threshold=0.6)
    assert len(result.majority) == 1
    entry = result.majority[0]
    assert entry.key == "HOST"
    assert entry.majority_value == "localhost"
    assert "a" in entry.agreeing_envs and "b" in entry.agreeing_envs
    assert "c" in entry.dissenting_envs


def test_contested_below_threshold(tmp_env):
    f1 = _write(tmp_env / "a.env", "MODE=debug\n")
    f2 = _write(tmp_env / "b.env", "MODE=release\n")
    f3 = _write(tmp_env / "c.env", "MODE=staging\n")
    result = analyse_consensus({"a": f1, "b": f2, "c": f3}, threshold=0.6)
    assert len(result.contested) == 1
    assert result.contested[0].key == "MODE"


def test_absent_key_missing_in_majority(tmp_env):
    f1 = _write(tmp_env / "a.env", "RARE=yes\n")
    f2 = _write(tmp_env / "b.env", "OTHER=1\n")
    f3 = _write(tmp_env / "c.env", "OTHER=2\n")
    result = analyse_consensus({"a": f1, "b": f2, "c": f3})
    assert "RARE" in result.absent


def test_agreement_rate_on_entry(tmp_env):
    f1 = _write(tmp_env / "a.env", "X=1\n")
    f2 = _write(tmp_env / "b.env", "X=1\n")
    f3 = _write(tmp_env / "c.env", "X=1\n")
    f4 = _write(tmp_env / "d.env", "X=2\n")
    result = analyse_consensus({"a": f1, "b": f2, "c": f3, "d": f4}, threshold=0.6)
    assert result.majority
    entry = result.majority[0]
    assert abs(entry.agreement_rate - 0.75) < 0.01


def test_total_keys_counts_all_categories(tmp_env):
    f1 = _write(tmp_env / "a.env", "A=1\nB=x\nC=foo\n")
    f2 = _write(tmp_env / "b.env", "A=1\nB=y\n")
    f3 = _write(tmp_env / "c.env", "A=1\nB=z\n")
    result = analyse_consensus({"a": f1, "b": f2, "c": f3}, threshold=0.6)
    # A: unanimous, B: contested, C: absent (only in 1 of 3)
    assert result.total_keys == 3


def test_env_names_stored(tmp_env):
    f1 = _write(tmp_env / "dev.env", "X=1\n")
    f2 = _write(tmp_env / "prod.env", "X=1\n")
    result = analyse_consensus({"dev": f1, "prod": f2})
    assert "dev" in result.env_names
    assert "prod" in result.env_names


def test_unanimous_entry_is_unanimous_property(tmp_env):
    f1 = _write(tmp_env / "a.env", "K=v\n")
    f2 = _write(tmp_env / "b.env", "K=v\n")
    result = analyse_consensus({"a": f1, "b": f2})
    assert result.unanimous[0].is_unanimous is True
