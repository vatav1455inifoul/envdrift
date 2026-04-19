"""Tests for envdrift.validator."""
import pytest
from envdrift.validator import validate_env, load_rules, ValidationResult


ENV = {
    "APP_URL": "https://example.com",
    "PORT": "8080",
    "DEBUG": "true",
    "ADMIN_EMAIL": "admin@example.com",
    "VERSION": "1.2.3",
    "BAD_URL": "not-a-url",
    "BAD_PORT": "abc",
    "BAD_EMAIL": "notanemail",
}


def test_valid_url_passes():
    result = validate_env({"APP_URL": "https://example.com"}, {"APP_URL": "url"})
    assert not result.has_issues()


def test_invalid_url_raises_issue():
    result = validate_env({"BAD_URL": "not-a-url"}, {"BAD_URL": "url"})
    assert result.has_issues()
    assert result.issues[0].key == "BAD_URL"
    assert result.issues[0].rule_name == "url"


def test_valid_port_passes():
    result = validate_env({"PORT": "8080"}, {"PORT": "port"})
    assert not result.has_issues()


def test_invalid_port_raises_issue():
    result = validate_env({"PORT": "abc"}, {"PORT": "port"})
    assert result.has_issues()


def test_bool_rule():
    result = validate_env({"DEBUG": "true"}, {"DEBUG": "bool"})
    assert not result.has_issues()
    result2 = validate_env({"DEBUG": "maybe"}, {"DEBUG": "bool"})
    assert result2.has_issues()


def test_email_rule_valid():
    result = validate_env({"ADMIN_EMAIL": "admin@example.com"}, {"ADMIN_EMAIL": "email"})
    assert not result.has_issues()


def test_email_rule_invalid():
    result = validate_env({"ADMIN_EMAIL": "notanemail"}, {"ADMIN_EMAIL": "email"})
    assert result.has_issues()


def test_custom_regex_rule():
    result = validate_env({"CODE": "ABC-123"}, {"CODE": r"^[A-Z]+-\d+$"})
    assert not result.has_issues()
    result2 = validate_env({"CODE": "abc"}, {"CODE": r"^[A-Z]+-\d+$"})
    assert result2.has_issues()
    assert result2.issues[0].rule_name == r"^[A-Z]+-\d+$"


def test_missing_key_skipped():
    """Keys in rules but absent from env should not raise issues."""
    result = validate_env({}, {"PORT": "port"})
    assert not result.has_issues()


def test_env_name_stored():
    result = validate_env({}, {}, env_name="production")
    assert result.env_name == "production"


def test_errors_and_warnings_split():
    result = validate_env({"PORT": "bad", "DEBUG": "maybe"}, {"PORT": "port", "DEBUG": "bool"})
    assert len(result.errors()) == 2
    assert result.warnings() == []
