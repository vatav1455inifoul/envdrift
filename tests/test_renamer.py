import pytest
from pathlib import Path
from envdrift.renamer import load_rename_map, suggest_renames, apply_renames


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_load_rename_map(tmp_env):
    path = tmp_env("rename.map", "DB_HOST=DATABASE_HOST\nDB_PORT=DATABASE_PORT\n")
    m = load_rename_map(path)
    assert m == {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}


def test_load_rename_map_skips_comments(tmp_env):
    path = tmp_env("rename.map", "# comment\nOLD=NEW\n")
    m = load_rename_map(path)
    assert "OLD" in m and len(m) == 1


def test_suggest_renames_applied(tmp_env):
    env = tmp_env(".env", "DB_HOST=localhost\nSECRET=abc\n")
    result = suggest_renames(env, {"DB_HOST": "DATABASE_HOST"})
    assert ("DB_HOST", "DATABASE_HOST") in result.applied
    assert result.has_changes


def test_suggest_renames_key_not_found(tmp_env):
    env = tmp_env(".env", "SECRET=abc\n")
    result = suggest_renames(env, {"MISSING": "NEW_MISSING"})
    assert not result.has_changes
    assert result.skipped[0][0] == "MISSING"


def test_suggest_renames_target_exists(tmp_env):
    env = tmp_env(".env", "OLD=1\nNEW=2\n")
    result = suggest_renames(env, {"OLD": "NEW"})
    assert not result.has_changes
    assert any("already exists" in r[1] for r in result.skipped)


def test_apply_renames_rewrites_file(tmp_env):
    env = tmp_env(".env", "DB_HOST=localhost\nPORT=5432\n")
    result = apply_renames(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.has_changes
    content = Path(env).read_text()
    assert "DATABASE_HOST=localhost" in content
    assert "DB_HOST" not in content


def test_apply_renames_dry_run_does_not_write(tmp_env):
    env = tmp_env(".env", "DB_HOST=localhost\n")
    original = Path(env).read_text()
    result = apply_renames(env, {"DB_HOST": "DATABASE_HOST"}, dry_run=True)
    assert result.has_changes
    assert Path(env).read_text() == original


def test_apply_renames_no_changes_leaves_file(tmp_env):
    env = tmp_env(".env", "SECRET=abc\n")
    original = Path(env).read_text()
    apply_renames(env, {"MISSING": "NEW"})
    assert Path(env).read_text() == original
