import pytest
from pathlib import Path
from envdrift.grouper import group_env, compare_groups, _extract_prefix


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_underscore():
    assert _extract_prefix("PORT") is None


def test_extract_prefix_leading_underscore():
    assert _extract_prefix("_SECRET") is None


def test_group_env_basic(tmp_env):
    p = tmp_env("basic.env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\nPORT=8080\n")
    result = group_env(p, env_name="basic")
    assert result.env_name == "basic"
    assert "DB" in result.groups
    assert "APP" in result.groups
    assert sorted(result.groups["DB"]) == ["DB_HOST", "DB_PORT"]
    assert result.groups["APP"] == ["APP_NAME"]
    assert "PORT" in result.ungrouped


def test_group_env_all_ungrouped(tmp_env):
    p = tmp_env("flat.env", "PORT=80\nHOST=localhost\n")
    result = group_env(p)
    assert result.groups == {}
    assert set(result.ungrouped) == {"PORT", "HOST"}


def test_total_keys(tmp_env):
    p = tmp_env("mixed.env", "DB_HOST=x\nDB_PORT=y\nPORT=80\n")
    result = group_env(p)
    assert result.total_keys == 3


def test_group_names_sorted(tmp_env):
    p = tmp_env("sorted.env", "Z_KEY=1\nA_KEY=2\nM_KEY=3\n")
    result = group_env(p)
    assert result.group_names == ["A", "M", "Z"]


def test_compare_groups_presence(tmp_env):
    p1 = tmp_env("a.env", "DB_HOST=x\nREDIS_URL=y\n")
    p2 = tmp_env("b.env", "DB_HOST=x\nAPP_NAME=z\n")
    r1 = group_env(p1, env_name="a")
    r2 = group_env(p2, env_name="b")
    presence = compare_groups([r1, r2])
    assert set(presence["DB"]) == {"a", "b"}
    assert presence["REDIS"] == ["a"]
    assert presence["APP"] == ["b"]


def test_group_env_empty_file(tmp_env):
    p = tmp_env("empty.env", "")
    result = group_env(p)
    assert result.total_keys == 0
    assert result.ungrouped == []
    assert result.groups == {}
