"""Value-format validator: checks env values against regex rules."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationIssue:
    key: str
    value: str
    rule_name: str
    message: str
    severity: str = "error"  # error | warning


@dataclass
class ValidationResult:
    env_name: str
    issues: List[ValidationIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)

    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


# Built-in named rules
_BUILTIN_RULES: Dict[str, tuple] = {
    "url": (r"^https?://.+", "must be a valid HTTP/HTTPS URL"),
    "port": (r"^\d{1,5}$", "must be a numeric port"),
    "bool": (r"^(true|false|1|0|yes|no)$", "must be a boolean-like value"),
    "email": (r"^[^@]+@[^@]+\.[^@]+$", "must be a valid email address"),
    "semver": (r"^\d+\.\d+\.\d+", "must start with a semver string"),
}


def load_rules(rules_dict: Dict[str, str]) -> Dict[str, re.Pattern]:
    """Compile a {KEY: rule_name_or_regex} mapping into patterns."""
    compiled: Dict[str, re.Pattern] = {}
    for key, rule in rules_dict.items():
        if rule in _BUILTIN_RULES:
            pattern, _ = _BUILTIN_RULES[rule]
        else:
            pattern = rule
        compiled[key] = re.compile(pattern, re.IGNORECASE)
    return compiled


def validate_env(
    env: Dict[str, str],
    rules: Dict[str, str],
    env_name: str = "env",
) -> ValidationResult:
    result = ValidationResult(env_name=env_name)
    compiled = load_rules(rules)
    for key, pattern in compiled.items():
        if key not in env:
            continue
        value = env[key]
        if not pattern.match(value):
            rule = rules[key]
            if rule in _BUILTIN_RULES:
                msg = _BUILTIN_RULES[rule][1]
            else:
                msg = f"must match pattern {rule}"
            result.issues.append(
                ValidationIssue(key=key, value=value, rule_name=rule, message=msg)
            )
    return result
