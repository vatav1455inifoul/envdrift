"""Generate .env.example files from one or more parsed env files."""
from __future__ import annotations
from pathlib import Path
from typing import Sequence
from envdrift.redactor import load_redact_patterns, _is_sensitive


def collect_keys(envs: list[dict[str, str]]) -> list[str]:
    """Return ordered unique keys across all envs."""
    seen: dict[str, None] = {}
    for env in envs:
        for k in env:
            seen[k] = None
    return list(seen)


def build_example(
    envs: list[dict[str, str]],
    redact_patterns: list[str] | None = None,
    placeholder: str = "",
    keep_safe_values: bool = True,
) -> dict[str, str]:
    """Build an example env dict.

    Sensitive keys get *placeholder*; safe keys keep their first-seen value
    (or placeholder if keep_safe_values is False).
    """
    if redact_patterns is None:
        redact_patterns = load_redact_patterns(None)

    merged: dict[str, str] = {}
    for env in envs:
        for k, v in env.items():
            if k not in merged:
                merged[k] = v

    result: dict[str, str] = {}
    for k, v in merged.items():
        if _is_sensitive(k, redact_patterns):
            result[k] = placeholder
        else:
            result[k] = v if keep_safe_values else placeholder
    return result


def render_example(example: dict[str, str]) -> str:
    """Render example dict to .env file text."""
    lines = []
    for k, v in example.items():
        lines.append(f"{k}={v}")
    return "\n".join(lines) + ("\n" if lines else "")


def write_example(
    envs: list[dict[str, str]],
    output: str | Path,
    redact_patterns: list[str] | None = None,
    placeholder: str = "",
    keep_safe_values: bool = True,
) -> None:
    """Write a .env.example file to *output*."""
    example = build_example(envs, redact_patterns, placeholder, keep_safe_values)
    text = render_example(example)
    Path(output).write_text(text)
