"""Lint .env files for common issues like duplicate keys, unsafe values, and missing quotes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    line_number: int
    key: str | None
    code: str
    message: str
    severity: str  # "warning" | "error"


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def lint_env_file(path: str) -> LintResult:
    """Lint a single .env file and return a LintResult."""
    result = LintResult(path=path)
    seen_keys: dict[str, int] = {}

    try:
        lines = open(path).readlines()
    except FileNotFoundError:
        result.issues.append(LintIssue(0, None, "E001", f"File not found: {path}", "error"))
        return result

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        if not line.strip() or line.strip().startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(LintIssue(lineno, None, "E002", f"Invalid syntax (no '='): {line!r}", "error"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(LintIssue(lineno, key, "E003", "Empty key name", "error"))
            continue

        if key in seen_keys:
            result.issues.append(LintIssue(
                lineno, key, "W001",
                f"Duplicate key '{key}' (first seen on line {seen_keys[key]})",
                "warning",
            ))
        else:
            seen_keys[key] = lineno

        if not value:
            result.issues.append(LintIssue(lineno, key, "W002", f"Key '{key}' has an empty value", "warning"))

        if any(c in value for c in (" ", "\t")) and not (
            (value.startswith('"') and value.endswith('"')) or
            (value.startswith("'") and value.endswith("'"))
        ):
            result.issues.append(LintIssue(
                lineno, key, "W003",
                f"Key '{key}' has unquoted whitespace in value",
                "warning",
            ))

        if key.lower() in ("password", "secret", "token", "api_key", "private_key") and not value:
            result.issues.append(LintIssue(lineno, key, "W004", f"Sensitive key '{key}' has empty value", "warning"))

    return result
