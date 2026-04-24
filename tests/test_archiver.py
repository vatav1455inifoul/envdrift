"""Tests for envdrift.archiver."""

import pytest
from pathlib import Path
from envdrift import archiver


@pytest.fixture(autouse=True)
def _patch_archive_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(archiver, "ARCHIVE_DIR", tmp_path / "archives")


@pytest.fixture()
def two_envs(tmp_path):
    a = tmp_path / "dev.env"
    b = tmp_path / "prod.env"
    a.write_text("KEY=dev\nDB=sqlite\n")
    b.write_text("KEY=prod\nDB=postgres\n")
    return str(a), str(b)


def test_create_archive_returns_path(two_envs):
    dest = archiver.create_archive(list(two_envs), name="test-arc")
    assert dest.exists()
    assert dest.suffix == ".gz"


def test_create_archive_auto_name(two_envs):
    dest = archiver.create_archive(list(two_envs))
    assert dest.exists()


def test_list_archives_empty():
    assert archiver.list_archives() == []


def test_list_archives_after_save(two_envs):
    archiver.create_archive(list(two_envs), name="arc1")
    archiver.create_archive(list(two_envs), name="arc2")
    names = archiver.list_archives()
    assert names == ["arc1", "arc2"]


def test_load_archive_meta(two_envs):
    archiver.create_archive(list(two_envs), name="meta-test", notes="hello")
    meta = archiver.load_archive_meta("meta-test")
    assert meta["name"] == "meta-test"
    assert meta["notes"] == "hello"
    assert len(meta["files"]) == 2


def test_load_archive_meta_missing_raises():
    with pytest.raises(FileNotFoundError):
        archiver.load_archive_meta("does-not-exist")


def test_extract_archive_restores_files(two_envs, tmp_path):
    archiver.create_archive(list(two_envs), name="restore-test")
    out = tmp_path / "restored"
    files = archiver.extract_archive("restore-test", str(out))
    assert len(files) == 2
    names = {Path(f).name for f in files}
    assert "dev.env" in names
    assert "prod.env" in names


def test_extract_archive_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        archiver.extract_archive("ghost", str(tmp_path))


def test_extracted_content_is_correct(two_envs, tmp_path):
    archiver.create_archive(list(two_envs), name="content-check")
    out = tmp_path / "out"
    archiver.extract_archive("content-check", str(out))
    assert (out / "dev.env").read_text() == "KEY=dev\nDB=sqlite\n"
