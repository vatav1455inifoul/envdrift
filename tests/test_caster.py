import pytest
from envdrift.caster import cast_env, CastResult, _infer_type


def test_infer_int():
    assert _infer_type("42") == "int"


def test_infer_float():
    assert _infer_type("3.14") == "float"


def test_infer_bool_true():
    assert _infer_type("true") == "bool"


def test_infer_bool_yes():
    assert _infer_type("yes") == "bool"


def test_infer_str():
    assert _infer_type("hello") == "str"


def test_no_issues_when_types_match():
    env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
    schema = {"PORT": "int", "DEBUG": "bool", "NAME": "str"}
    result = cast_env(env, schema, env_file=".env")
    assert not result.has_issues()
    assert result.env_file == ".env"


def test_detects_wrong_type():
    env = {"PORT": "not_a_number"}
    schema = {"PORT": "int"}
    result = cast_env(env, schema)
    assert result.has_issues()
    assert result.issues[0].key == "PORT"
    assert result.issues[0].expected_type == "int"


def test_missing_schema_key_skipped():
    env = {"EXTRA": "something"}
    schema = {"PORT": "int"}
    result = cast_env(env, schema)
    assert not result.has_issues()


def test_key_in_schema_but_missing_from_env_skipped():
    env = {}
    schema = {"PORT": "int"}
    result = cast_env(env, schema)
    assert not result.has_issues()


def test_float_expected_but_int_given_passes():
    # 42 can be inferred as int, not float — should flag
    env = {"RATIO": "42"}
    schema = {"RATIO": "float"}
    result = cast_env(env, schema)
    assert result.has_issues()
    assert "float" in result.issues[0].message


def test_multiple_issues_collected():
    env = {"PORT": "abc", "TIMEOUT": "xyz"}
    schema = {"PORT": "int", "TIMEOUT": "float"}
    result = cast_env(env, schema)
    assert len(result.issues) == 2
