import pytest
from envdrift.redactor import (
    load_redact_patterns,
    redact_env,
    redact_keys,
    DEFAULT_PATTERNS,
    REDACTED,
)


@pytest.fixture
def tmp_patterns(tmp_path):
    def _write(content):
        p = tmp_path / ".envdriftredact"
        p.write_text(content)
        return str(p)
    return _write


def test_load_defaults_when_no_file():
    patterns = load_redact_patterns(None)
    assert patterns == DEFAULT_PATTERNS


def test_load_defaults_when_missing_file():
    patterns = load_redact_patterns("/nonexistent/path")
    assert patterns == DEFAULT_PATTERNS


def test_load_custom_patterns(tmp_patterns):
    path = tmp_patterns("# comment\nMY_SECRET.*\nFOO_TOKEN\n")
    patterns = load_redact_patterns(path)
    assert patterns == ["MY_SECRET.*", "FOO_TOKEN"]


def test_redact_env_sensitive_keys():
    env = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp", "API_KEY": "abc123"}
    result = redact_env(env)
    assert result["DB_PASSWORD"] == REDACTED
    assert result["API_KEY"] == REDACTED
    assert result["APP_NAME"] == "myapp"


def test_redact_env_preserves_non_sensitive():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env)
    assert result == env


def test_redact_env_custom_patterns():
    env = {"MY_CUSTOM": "value", "SAFE": "ok"}
    result = redact_env(env, patterns=[r"MY_CUSTOM"])
    assert result["MY_CUSTOM"] == REDACTED
    assert result["SAFE"] == "ok"


def test_redact_keys_identifies_sensitive():
    keys = ["SECRET_KEY", "HOST", "TOKEN", "DEBUG"]
    result = redact_keys(keys)
    assert result["SECRET_KEY"] is True
    assert result["TOKEN"] is True
    assert result["HOST"] is False
    assert result["DEBUG"] is False


def test_redact_env_case_insensitive_match():
    env = {"db_password": "secret"}
    result = redact_env(env)
    assert result["db_password"] == REDACTED
