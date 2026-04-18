import pytest
from pathlib import Path
from envdrift.sorter import sort_env, render_sorted, write_sorted, SortResult


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_already_sorted(tmp_env):
    p = tmp_env("a.env", "ALPHA=1\nBETA=2\nGAMMA=3\n")
    result = sort_env(p)
    assert result.is_sorted
    assert result.moved_keys == []


def test_unsorted_detected(tmp_env):
    p = tmp_env("b.env", "ZEBRA=1\nAPPLE=2\nMIDDLE=3\n")
    result = sort_env(p)
    assert not result.is_sorted
    assert result.sorted_order == ["APPLE", "MIDDLE", "ZEBRA"]


def test_moved_keys(tmp_env):
    p = tmp_env("c.env", "ZEBRA=1\nAPPLE=2\n")
    result = sort_env(p)
    assert set(result.moved_keys) == {"ZEBRA", "APPLE"}


def test_env_name_override(tmp_env):
    p = tmp_env("d.env", "A=1\n")
    result = sort_env(p, env_name="production")
    assert result.env_name == "production"


def test_render_sorted_output(tmp_env):
    p = tmp_env("e.env", "ZEBRA=z\nAPPLE=a\n")
    result = sort_env(p)
    rendered = render_sorted(result)
    lines = rendered.strip().splitlines()
    assert lines[0].startswith("APPLE")
    assert lines[1].startswith("ZEBRA")


def test_render_quotes_values_with_spaces(tmp_env):
    p = tmp_env("f.env", 'KEY=hello world\n')
    result = sort_env(p)
    rendered = render_sorted(result)
    assert 'KEY="hello world"' in rendered


def test_write_sorted_creates_file(tmp_env, tmp_path):
    p = tmp_env("g.env", "ZEBRA=1\nAPPLE=2\n")
    result = sort_env(p)
    out = str(tmp_path / "sorted.env")
    write_sorted(result, out)
    content = Path(out).read_text()
    assert content.startswith("APPLE")


def test_single_key_is_sorted(tmp_env):
    p = tmp_env("h.env", "ONLY=value\n")
    result = sort_env(p)
    assert result.is_sorted
    assert result.moved_keys == []
