"""Schema validation for .env files against a defined schema."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SchemaViolation:
    key: str
    rule: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class SchemaResult:
    env_name: str
    violations: list[SchemaViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return bool(self.violations)

    @property
    def errors(self) -> list[SchemaViolation]:
        return [v for v in self.violations if v.severity == "error"]

    @property
    def warnings(self) -> list[SchemaViolation]:
        return [v for v in self.violations if v.severity == "warning"]


def load_schema(path: str | Path) -> dict[str, Any]:
    """Load a JSON schema file describing expected env keys."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with p.open() as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file '{path}': {e}") from e


def validate_env(env: dict[str, str], schema: dict[str, Any], env_name: str = "env") -> SchemaResult:
    """
    Validate an env dict against a schema.

    Schema format (JSON):
    {
      "KEY_NAME": {
        "required": true,
        "pattern": "^[a-z]+$",
        "min_length": 3,
        "severity": "error"
      }
    }
    """
    result = SchemaResult(env_name=env_name)

    for key, rules in schema.items():
        severity = rules.get("severity", "error")
        required = rules.get("required", False)
        pattern = rules.get("pattern")
        min_length = rules.get("min_length")
        max_length = rules.get("max_length")

        if required and key not in env:
            result.violations.append(SchemaViolation(
                key=key, rule="required",
                message=f"Required key '{key}' is missing.",
                severity=severity,
            ))
            continue

        value = env.get(key)
        if value is None:
            continue

        if pattern and not re.fullmatch(pattern, value):
            result.violations.append(SchemaViolation(
                key=key, rule="pattern",
                message=f"Value for '{key}' does not match pattern '{pattern}'.",
                severity=severity,
            ))

        if min_length is not None and len(value) < min_length:
            result.violations.append(SchemaViolation(
                key=key, rule="min_length",
                message=f"Value for '{key}' is shorter than min_length {min_length}.",
                severity=severity,
            ))

        if max_length is not None and len(value) > max_length:
            result.violations.append(SchemaViolation(
                key=key, rule="max_length",
                message=f"Value for '{key}' exceeds max_length {max_length}.",
                severity=severity,
            ))

    return result
