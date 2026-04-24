"""Tests for envdrift.digester."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from envdrift.digester import (
    DigestResult,
    changed_keys,
    digest_file,
    digest_to_dict,
    digests_match,
)


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_digest_file_returns_digest_result(tmp_env):
    path = tmp_env("a.env", "KEY=val\nFOO=bar\n")
    result = digest_file(path)
    assert isinstance(result, DigestResult)
    assert result.key_count == 2
    assert result.env_name == "a"


def test_file_hash_matches_sha256_of_bytes(tmp_env):
    content = "KEY=val\n"
    path = tmp_env("x.env", content)
    result = digest_file(path)
    expected = hashlib.sha256(content.encode()).hexdigest()
    assert result.file_hash == expected


def test_content_hash_ignores_comments_and_blanks(tmp_env):
    p1 = tmp_env("e1.env", "# comment\nKEY=val\n")
    p2 = tmp_env("e2.env", "KEY=val\n")
    d1 = digest_file(p1)
    d2 = digest_file(p2)
    assert d1.content_hash == d2.content_hash
    assert d1.file_hash != d2.file_hash


def test_content_hash_ignores_key_order(tmp_env):
    p1 = tmp_env("o1.env", "A=1\nB=2\n")
    p2 = tmp_env("o2.env", "B=2\nA=1\n")
    assert digest_file(p1).content_hash == digest_file(p2).content_hash


def test_digests_match_content_mode(tmp_env):
    p1 = tmp_env("m1.env", "KEY=val\n")
    p2 = tmp_env("m2.env", "# note\nKEY=val\n")
    d1, d2 = digest_file(p1), digest_file(p2)
    assert digests_match(d1, d2) is True
    assert digests_match(d1, d2, strict=True) is False


def test_digests_match_strict_identical_files(tmp_env):
    p1 = tmp_env("s1.env", "KEY=val\n")
    p2 = tmp_env("s2.env", "KEY=val\n")
    d1, d2 = digest_file(p1), digest_file(p2)
    assert digests_match(d1, d2, strict=True) is True


def test_changed_keys_detects_value_change(tmp_env):
    p1 = tmp_env("c1.env", "A=1\nB=same\n")
    p2 = tmp_env("c2.env", "A=2\nB=same\n")
    diff = changed_keys(digest_file(p1), digest_file(p2))
    assert "A" in diff
    assert "B" not in diff


def test_changed_keys_detects_missing_key(tmp_env):
    p1 = tmp_env("d1.env", "A=1\nB=2\n")
    p2 = tmp_env("d2.env", "A=1\n")
    diff = changed_keys(digest_file(p1), digest_file(p2))
    assert "B" in diff
    ha, hb = diff["B"]
    assert ha is not None
    assert hb is None


def test_digest_to_dict_keys(tmp_env):
    path = tmp_env("z.env", "X=1\n")
    d = digest_to_dict(digest_file(path))
    for key in ("env_name", "path", "file_hash", "content_hash", "key_count", "key_hashes"):
        assert key in d
