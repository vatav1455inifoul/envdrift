"""Tests for envdrift.profiler."""
import pytest

from envdrift.profiler import profile_env, ProfileResult


@pytest.fixture
def tmp_env(tmp_path):
    def _write(content: str):
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def test_empty_file_gives_zero_keys(tmp_env):
    path = tmp_env("")
    r = profile_env(path)
    assert r.total_keys == 0
    assert r.fill_rate == 0.0


def test_fill_rate_all_filled(tmp_env):
    path = tmp_env("A=hello\nB=world\n")
    r = profile_env(path)
    assert r.fill_rate == 100.0
    assert r.empty_count == 0


def test_detects_empty_values(tmp_env):
    path = tmp_env("A=\nB=value\n")
    r = profile_env(path)
    assert "A" in r.empty_values
    assert "B" not in r.empty_values
    assert r.fill_rate == 50.0


def test_detects_numeric_values(tmp_env):
    path = tmp_env("PORT=8080\nNAME=app\nTIMEOUT=3.14\n")
    r = profile_env(path)
    assert "PORT" in r.numeric_values
    assert "TIMEOUT" in r.numeric_values
    assert "NAME" not in r.numeric_values


def test_detects_url_values(tmp_env):
    path = tmp_env("DB_URL=https://db.example.com\nNAME=app\n")
    r = profile_env(path)
    assert "DB_URL" in r.url_values
    assert "NAME" not in r.url_values


def test_detects_boolean_values(tmp_env):
    path = tmp_env("DEBUG=true\nVERBOSE=yes\nNAME=app\n")
    r = profile_env(path)
    assert "DEBUG" in r.boolean_values
    assert "VERBOSE" in r.boolean_values
    assert "NAME" not in r.boolean_values


def test_detects_long_values(tmp_env):
    long_val = "x" * 101
    path = tmp_env(f"SECRET={long_val}\nSHORT=hi\n")
    r = profile_env(path)
    assert "SECRET" in r.long_values
    assert "SHORT" not in r.long_values


def test_key_lengths_recorded(tmp_env):
    path = tmp_env("A=hello\nB=\n")
    r = profile_env(path)
    assert r.key_lengths["A"] == 5
    assert r.key_lengths["B"] == 0


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        profile_env(str(tmp_path / "nonexistent.env"))
