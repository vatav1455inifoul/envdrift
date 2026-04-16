"""Tests for envdrift.tagger."""
import pytest
from pathlib import Path
from envdrift import tagger as T


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Redirect _TAGS_DIR to a temp directory."""
    tags_dir = tmp_path / ".envdrift" / "tags"
    monkeypatch.setattr(T, "_TAGS_DIR", tags_dir)
    yield tags_dir


def test_save_creates_file(isolated):
    dest = T.save_tag("staging", ["staging.env"])
    assert dest.exists()


def test_save_and_load_roundtrip(isolated):
    T.save_tag("prod", ["prod.env", "prod.secrets.env"], notes="production")
    tag = T.load_tag("prod")
    assert tag["label"] == "prod"
    assert "prod.env" in tag["paths"]
    assert tag["notes"] == "production"


def test_load_missing_raises(isolated):
    with pytest.raises(FileNotFoundError, match="nope"):
        T.load_tag("nope")


def test_list_tags_empty(isolated):
    assert T.list_tags() == []


def test_list_tags_returns_labels(isolated):
    T.save_tag("alpha", ["a.env"])
    T.save_tag("beta", ["b.env"])
    labels = T.list_tags()
    assert labels == ["alpha", "beta"]


def test_delete_existing_tag(isolated):
    T.save_tag("temp", ["t.env"])
    result = T.delete_tag("temp")
    assert result is True
    assert T.list_tags() == []


def test_delete_missing_tag(isolated):
    assert T.delete_tag("ghost") is False


def test_tag_summary_format(isolated):
    T.save_tag("dev", ["dev.env", "local.env"], notes="local dev")
    tag = T.load_tag("dev")
    summary = T.tag_summary(tag)
    assert "dev" in summary
    assert "dev.env" in summary
    assert "local dev" in summary
    assert "Files : 2" in summary


def test_tag_summary_no_notes(isolated):
    T.save_tag("ci", ["ci.env"])
    tag = T.load_tag("ci")
    summary = T.tag_summary(tag)
    assert "Notes" not in summary
