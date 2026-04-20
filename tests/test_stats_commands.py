import argparse
import pytest
from pathlib import Path
from envdrift.stats_commands import cmd_stats


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _ns(**kwargs):
    defaults = dict(envs=[])
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_returns_zero_no_drift(tmp_env):
    a = tmp_env("a.env", "KEY=val\nFOO=bar\n")
    b = tmp_env("b.env", "KEY=val\nFOO=bar\n")
    assert cmd_stats(_ns(envs=[a, b])) == 0


def test_returns_zero_with_drift(tmp_env):
    a = tmp_env("a.env", "KEY=val\n")
    b = tmp_env("b.env", "KEY=other\nEXTRA=1\n")
    assert cmd_stats(_ns(envs=[a, b])) == 0


def test_missing_file_returns_one(tmp_env):
    a = tmp_env("a.env", "KEY=val\n")
    assert cmd_stats(_ns(envs=[a, "/no/such/file.env"])) == 1


def test_too_few_args_returns_one():
    assert cmd_stats(_ns(envs=["only_one.env"])) == 1


def test_multi_env_returns_zero(tmp_env):
    a = tmp_env("a.env", "KEY=val\n")
    b = tmp_env("b.env", "KEY=val\n")
    c = tmp_env("c.env", "KEY=val\n")
    assert cmd_stats(_ns(envs=[a, b, c])) == 0
