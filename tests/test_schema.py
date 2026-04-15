"""Tests for schema validation and reporter."""
import json
import pytest
from pathlib import Path

from envdrift.schema import load_schema, validate_env, SchemaResult
from envdrift.schema_reporter import format_schema_report


@pytest.fixture
def simple_schema(tmp_path):
    schema = {
        "DATABASE_URL": {"required": True, "pattern": r"postgres://.+"},
        "PORT": {"required": True, "min_length": 1, "max_length": 5},
        "DEBUG": {"required": False, "pattern": r"true|false", "severity": "warning"},
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return p, schema


def test_load_schema_returns_dict(simple_schema):
    path, expected = simple_schema
    loaded = load_schema(path)
    assert loaded == expected


def test_load_schema_missing_raises():
    with pytest.raises(FileNotFoundError):
        load_schema("/nonexistent/schema.json")


def test_valid_env_no_violations(simple_schema):
    _, schema = simple_schema
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432", "DEBUG": "true"}
    result = validate_env(env, schema, env_name="prod")
    assert not result.has_violations
    assert result.env_name == "prod"


def test_missing_required_key(simple_schema):
    _, schema = simple_schema
    env = {"PORT": "5432"}
    result = validate_env(env, schema)
    keys = [v.key for v in result.violations]
    assert "DATABASE_URL" in keys
    assert all(v.rule == "required" for v in result.violations if v.key == "DATABASE_URL")


def test_pattern_violation(simple_schema):
    _, schema = simple_schema
    env = {"DATABASE_URL": "mysql://localhost/db", "PORT": "5432"}
    result = validate_env(env, schema)
    pattern_violations = [v for v in result.violations if v.rule == "pattern"]
    assert len(pattern_violations) == 1
    assert pattern_violations[0].key == "DATABASE_URL"


def test_min_length_violation(simple_schema):
    _, schema = simple_schema
    env = {"DATABASE_URL": "postgres://x", "PORT": ""}
    result = validate_env(env, schema)
    ml = [v for v in result.violations if v.rule == "min_length"]
    assert any(v.key == "PORT" for v in ml)


def test_max_length_violation(simple_schema):
    _, schema = simple_schema
    env = {"DATABASE_URL": "postgres://x", "PORT": "123456"}
    result = validate_env(env, schema)
    ml = [v for v in result.violations if v.rule == "max_length"]
    assert any(v.key == "PORT" for v in ml)


def test_warning_severity(simple_schema):
    _, schema = simple_schema
    env = {"DATABASE_URL": "postgres://x", "PORT": "5432", "DEBUG": "yes"}
    result = validate_env(env, schema)
    warns = result.warnings
    assert any(v.key == "DEBUG" for v in warns)
    assert not any(v.key == "DEBUG" for v in result.errors)


def test_errors_and_warnings_properties(simple_schema):
    _, schema = simple_schema
    env = {"PORT": "5432", "DEBUG": "maybe"}  # missing DATABASE_URL (error) + bad DEBUG (warning)
    result = validate_env(env, schema)
    assert len(result.errors) >= 1
    assert len(result.warnings) >= 1


def test_reporter_no_violations():
    result = SchemaResult(env_name="staging")
    report = format_schema_report(result, color=False)
    assert "All checks passed" in report
    assert "staging" in report


def test_reporter_shows_errors_and_warnings(simple_schema):
    _, schema = simple_schema
    env = {"PORT": "5432", "DEBUG": "oops"}
    result = validate_env(env, schema, env_name="dev")
    report = format_schema_report(result, color=False)
    assert "Errors" in report
    assert "Warnings" in report
    assert "DATABASE_URL" in report
    assert "DEBUG" in report
