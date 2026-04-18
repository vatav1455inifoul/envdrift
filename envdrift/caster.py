"""Type casting hints for .env values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CastIssue:
    key: str
    value: str
    expected_type: str
    message: str


@dataclass
class CastResult:
    env_file: str
    issues: List[CastIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)


_BOOL_VALUES = {"true", "false", "1", "0", "yes", "no"}


def _looks_like_int(v: str) -> bool:
    try:
        int(v)
        return True
    except ValueError:
        return False


def _looks_like_float(v: str) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


def _infer_type(value: str) -> str:
    if value.lower() in _BOOL_VALUES:
        return "bool"
    if _looks_like_int(value):
        return "int"
    if _looks_like_float(value):
        return "float"
    return "str"


def cast_env(env: Dict[str, str], schema: Dict[str, str], env_file: str = "") -> CastResult:
    """Check that values in *env* match expected types declared in *schema*.

    schema maps key -> expected type string: 'str', 'int', 'float', 'bool'.
    Keys not present in schema are skipped.
    """
    result = CastResult(env_file=env_file)
    for key, expected in schema.items():
        if key not in env:
            continue
        value = env[key]
        actual = _infer_type(value)
        if actual != expected:
            result.issues.append(
                CastIssue(
                    key=key,
                    value=value,
                    expected_type=expected,
                    message=f"expected {expected}, looks like {actual}",
                )
            )
    return result
