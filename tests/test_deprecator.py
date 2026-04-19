"""Tests for envdrift.deprecator."""
import json
import pytest
from pathlib import Path
from envdrift.deprecator import (
    load_deprecation_map,
    check_deprecations,
    DeprecationResult,
)


@pytest.fixture()
def tmp_map(tmp_path):
    def _write(data: dict) -> Path:
        p = tmp_path / "deprecations.json"
        p.write_text(json.dumps(data))
        return p
    return _write


def test_load_deprecation_map_basic(tmp_map):
    p = tmp_map({"OLD_KEY": {"message": "Use NEW_KEY", "replacement": "NEW_KEY"}})
    dm = load_deprecation_map(p)
    assert "OLD_KEY" in dm
    assert dm["OLD_KEY"]["replacement"] == "NEW_KEY"


def test_load_deprecation_map_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_deprecation_map(tmp_path / "nope.json")


def test_load_deprecation_map_invalid_raises(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("[1, 2, 3]")
    with pytest.raises(ValueError):
        load_deprecation_map(p)


def test_no_warnings_when_no_deprecated_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    dm = {"OLD_HOST": {"message": "use HOST"}}
    result = check_deprecations(env, dm, env_name="prod")
    assert not result.has_warnings()
    assert result.keys() == []


def test_detects_deprecated_key():
    env = {"OLD_HOST": "localhost", "PORT": "5432"}
    dm = {"OLD_HOST": {"message": "Use HOST instead", "replacement": "HOST"}}
    result = check_deprecations(env, dm, env_name="staging")
    assert result.has_warnings()
    assert "OLD_HOST" in result.keys()


def test_warning_carries_message_and_replacement():
    env = {"LEGACY_DB": "postgres://old"}
    dm = {"LEGACY_DB": {"message": "Use DATABASE_URL", "replacement": "DATABASE_URL"}}
    result = check_deprecations(env, dm)
    w = result.warnings[0]
    assert w.message == "Use DATABASE_URL"
    assert w.replacement == "DATABASE_URL"


def test_warning_without_replacement():
    env = {"DEAD_KEY": "value"}
    dm = {"DEAD_KEY": {"message": "No longer used"}}
    result = check_deprecations(env, dm)
    assert result.warnings[0].replacement is None


def test_multiple_deprecated_keys():
    env = {"OLD_A": "1", "OLD_B": "2", "GOOD": "3"}
    dm = {
        "OLD_A": {"message": "use A"},
        "OLD_B": {"message": "use B"},
    }
    result = check_deprecations(env, dm)
    assert len(result.warnings) == 2
    assert set(result.keys()) == {"OLD_A", "OLD_B"}


def test_env_name_stored_on_result():
    result = check_deprecations({}, {}, env_name="production")
    assert result.env_name == "production"
