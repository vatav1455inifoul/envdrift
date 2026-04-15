"""Tests for envdrift.exporter."""

import json
import csv
import io

import pytest

from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult
from envdrift.exporter import export_json, export_csv


@pytest.fixture
def no_drift():
    return DriftResult(
        has_drift=False,
        missing_keys=set(),
        extra_keys=set(),
        changed_values={},
    )


@pytest.fixture
def pair_drift():
    return DriftResult(
        has_drift=True,
        missing_keys={"SECRET"},
        extra_keys={"DEBUG"},
        changed_values={"PORT": ("8080", "9090")},
    )


@pytest.fixture
def multi_drift():
    return MultiDiffResult(
        has_drift=True,
        inconsistent_keys={"PORT": {"prod": "80", "staging": "8080"}},
        missing_in_some={"SECRET": {"staging"}},
    )


def test_export_json_no_drift(no_drift):
    out = export_json(no_drift, env_names=["local", "prod"])
    data = json.loads(out)
    assert data["has_drift"] is False
    assert data["missing_keys"] == []
    assert data["extra_keys"] == []
    assert data["changed_values"] == {}


def test_export_json_pair_drift_env_names(pair_drift):
    out = export_json(pair_drift, env_names=["dev", "prod"])
    data = json.loads(out)
    assert data["env_a"] == "dev"
    assert data["env_b"] == "prod"
    assert "SECRET" in data["missing_keys"]
    assert "DEBUG" in data["extra_keys"]
    assert data["changed_values"]["PORT"] == {"env_a": "8080", "env_b": "9090"}


def test_export_json_defaults_env_names(pair_drift):
    out = export_json(pair_drift)
    data = json.loads(out)
    assert data["env_a"] == "env_a"
    assert data["env_b"] == "env_b"


def test_export_json_multi_diff(multi_drift):
    out = export_json(multi_drift, env_names=["prod", "staging"])
    data = json.loads(out)
    assert data["has_drift"] is True
    assert "PORT" in data["inconsistent_keys"]
    assert data["inconsistent_keys"]["PORT"]["prod"] == "80"
    assert "SECRET" in data["missing_in_some"]


def test_export_csv_no_drift(no_drift):
    out = export_csv(no_drift)
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["key", "issue", "env_a_value", "env_b_value"]
    assert len(rows) == 1  # header only


def test_export_csv_drift_rows(pair_drift):
    out = export_csv(pair_drift, env_a="dev", env_b="prod")
    rows = list(csv.reader(io.StringIO(out)))
    header = rows[0]
    assert header[2] == "dev_value"
    assert header[3] == "prod_value"
    issues = {row[0]: row[1] for row in rows[1:]}
    assert issues["SECRET"] == "missing_in_prod"
    assert issues["DEBUG"] == "missing_in_dev"
    assert issues["PORT"] == "value_changed"


def test_export_csv_changed_values_content(pair_drift):
    out = export_csv(pair_drift, env_a="a", env_b="b")
    rows = {r[0]: r for r in csv.reader(io.StringIO(out))}
    assert rows["PORT"][2] == "8080"
    assert rows["PORT"][3] == "9090"
