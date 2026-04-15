"""Tests for envdrift.profile_commands."""
import argparse
import pytest

from envdrift.profile_commands import cmd_profile, register_profile_subcommand


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"no_color": True}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_profile_returns_zero(tmp_env):
    path = tmp_env(".env", "A=1\nB=hello\n")
    code = cmd_profile(_ns(envfiles=[path]))
    assert code == 0


def test_missing_file_returns_one(tmp_path):
    code = cmd_profile(_ns(envfiles=[str(tmp_path / "missing.env")]))
    assert code == 1


def test_multiple_files_all_missing_returns_one(tmp_path):
    paths = [str(tmp_path / f"e{i}.env") for i in range(3)]
    code = cmd_profile(_ns(envfiles=paths))
    assert code == 1


def test_mixed_files_returns_one(tmp_env, tmp_path):
    good = tmp_env("good.env", "X=1\n")
    bad = str(tmp_path / "bad.env")
    code = cmd_profile(_ns(envfiles=[good, bad]))
    assert code == 1


def test_register_adds_profile_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_profile_subcommand(sub)
    args = parser.parse_args(["profile", "some.env"])
    assert args.envfiles == ["some.env"]
    assert hasattr(args, "func")
