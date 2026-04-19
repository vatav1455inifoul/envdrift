"""Normalize .env values for consistent comparison (trim, lowercase bools, etc.)."""

from dataclasses import dataclass, field
from typing import Dict, List

_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[str] = field(default_factory=list)


def has_changes(result: NormalizeResult) -> bool:
    return bool(result.changes)


def _normalize_value(key: str, value: str) -> tuple[str, str | None]:
    """Return (normalized_value, change_description or None)."""
    stripped = value.strip()
    if stripped != value:
        return stripped, f"{key}: stripped whitespace"

    lower = stripped.lower()
    if lower in _BOOL_TRUE:
        normalized = "true"
        if stripped != normalized:
            return normalized, f"{key}: normalized bool to 'true'"
    elif lower in _BOOL_FALSE:
        normalized = "false"
        if stripped != normalized:
            return normalized, f"{key}: normalized bool to 'false'"

    return stripped, None


def normalize_env(env: Dict[str, str]) -> NormalizeResult:
    """Normalize all values in an env dict."""
    normalized: Dict[str, str] = {}
    changes: List[str] = []

    for key, value in env.items():
        norm_val, change = _normalize_value(key, value)
        normalized[key] = norm_val
        if change:
            changes.append(change)

    return NormalizeResult(original=dict(env), normalized=normalized, changes=changes)


def render_normalized(result: NormalizeResult) -> str:
    """Render normalized env as .env file content."""
    lines = []
    for key, value in result.normalized.items():
        if " " in value or "#" in value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n" if lines else ""
