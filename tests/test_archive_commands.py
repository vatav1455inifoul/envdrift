"""Tests for envdrift.archive_commands."""

import types
import pytest
from pathlib import Path
from envdrift import archiver
from envdrift.archive_commands import (
    cmd_archive_save,
    cmd_archive_extract,
    cmd_archive_list,
    cmd_archive_info,
)


@pytest.fixture(autouse=True)
def _patch_archive_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(archiver, "ARCHIVE_DIR", tmp_path / "archives")


@pytest.fixture()
def tmp_env(tmp_path):
    p = tmp_path / "test.env"
    p.write_text("FOO=bar\nBAZ=1\n")
    return str(p)


def _ns(**kwargs):
    return types.SimpleNamespace(**kwargs)


def test_save_returns_zero(tmp_env):
    args = _ns(envfiles=[tmp_env], name="cmd-test", notes="")
    assert cmd_archive_save(args) == 0


def test_save_missing_file_returns_one(tmp_path):
    args = _ns(envfiles=[str(tmp_path / "ghost.env")], name="", notes="")
    assert cmd_archive_save(args) == 1


def test_list_empty(capsys):
    assert cmd_archive_list(_ns()) == 0
    out = capsys.readouterr().out
    assert "No archives" in out


def test_list_shows_names(tmp_env):
    cmd_archive_save(_ns(envfiles=[tmp_env], name="listed-arc", notes=""))
    assert cmd_archive_list(_ns()) == 0


def test_info_returns_zero(tmp_env):
    cmd_archive_save(_ns(envfiles=[tmp_env], name="info-arc", notes="my note"))
    assert cmd_archive_info(_ns(name="info-arc")) == 0


def test_info_shows_notes(tmp_env, capsys):
    cmd_archive_save(_ns(envfiles=[tmp_env], name="noted", notes="important"))
    cmd_archive_info(_ns(name="noted"))
    out = capsys.readouterr().out
    assert "important" in out


def test_info_missing_returns_one():
    assert cmd_archive_info(_ns(name="nope")) == 1


def test_extract_returns_zero(tmp_env, tmp_path):
    cmd_archive_save(_ns(envfiles=[tmp_env], name="ext-arc", notes=""))
    dest = str(tmp_path / "out")
    assert cmd_archive_extract(_ns(name="ext-arc", dest=dest)) == 0


def test_extract_missing_returns_one(tmp_path):
    assert cmd_archive_extract(_ns(name="missing", dest=str(tmp_path))) == 1
