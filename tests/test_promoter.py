import os
import pytest
from pathlib import Path
from envdrift.promoter import promote_env, PromoteResult
from envdrift.parser import parse_env_file


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_promotes_missing_keys(tmp_env):
    src = tmp_env("src.env", "FOO=bar\nNEW=value\n")
    tgt = tmp_env("tgt.env", "FOO=bar\n")
    result = promote_env(src, tgt)
    assert "NEW" in result.promoted
    assert result.total_promoted() == 1
    assert parse_env_file(tgt)["NEW"] == "value"


def test_skips_existing_keys_without_force(tmp_env):
    src = tmp_env("src.env", "FOO=new\n")
    tgt = tmp_env("tgt.env", "FOO=old\n")
    result = promote_env(src, tgt)
    assert "FOO" in result.skipped
    assert result.total_promoted() == 0
    assert parse_env_file(tgt)["FOO"] == "old"


def test_force_overwrites_existing(tmp_env):
    src = tmp_env("src.env", "FOO=new\n")
    tgt = tmp_env("tgt.env", "FOO=old\n")
    result = promote_env(src, tgt, force=True)
    assert "FOO" in result.promoted
    assert parse_env_file(tgt)["FOO"] == "new"


def test_conflict_detected(tmp_env):
    src = tmp_env("src.env", "FOO=new\n")
    tgt = tmp_env("tgt.env", "FOO=old\n")
    result = promote_env(src, tgt)
    assert result.has_conflicts()
    assert result.conflicts["FOO"] == ("new", "old")


def test_no_conflict_same_value(tmp_env):
    src = tmp_env("src.env", "FOO=same\n")
    tgt = tmp_env("tgt.env", "FOO=same\n")
    result = promote_env(src, tgt)
    assert not result.has_conflicts()


def test_dry_run_does_not_write(tmp_env):
    src = tmp_env("src.env", "NEW=val\n")
    tgt = tmp_env("tgt.env", "")
    promote_env(src, tgt, dry_run=True)
    assert parse_env_file(tgt) == {}


def test_selective_keys(tmp_env):
    src = tmp_env("src.env", "A=1\nB=2\nC=3\n")
    tgt = tmp_env("tgt.env", "")
    result = promote_env(src, tgt, keys=["A", "C"])
    data = parse_env_file(tgt)
    assert "A" in data and "C" in data
    assert "B" not in data
    assert result.total_promoted() == 2


def test_labels_stored(tmp_env):
    src = tmp_env("src.env", "X=1\n")
    tgt = tmp_env("tgt.env", "")
    result = promote_env(src, tgt, source_name="staging", target_name="prod")
    assert result.source_name == "staging"
    assert result.target_name == "prod"
