"""Reporter for schema validation results."""
from __future__ import annotations

from .schema import SchemaResult, SchemaViolation

_COLORS = {
    "red": "\033[31m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def _c(text: str, *styles: str) -> str:
    codes = "".join(_COLORS.get(s, "") for s in styles)
    return f"{codes}{text}{_COLORS['reset']}"


def format_schema_report(result: SchemaResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Schema validation: {result.env_name}"
    lines.append(_c(header, "bold") if color else header)
    lines.append("-" * len(header))

    if not result.has_violations:
        ok = "  ✔ All checks passed."
        lines.append(_c(ok, "green") if color else ok)
        return "\n".join(lines)

    errors = result.errors
    warnings = result.warnings

    if errors:
        section = f"  Errors ({len(errors)}):"
        lines.append(_c(section, "red", "bold") if color else section)
        for v in errors:
            msg = f"    [{v.rule}] {v.message}"
            lines.append(_c(msg, "red") if color else msg)

    if warnings:
        section = f"  Warnings ({len(warnings)}):"
        lines.append(_c(section, "yellow", "bold") if color else section)
        for v in warnings:
            msg = f"    [{v.rule}] {v.message}"
            lines.append(_c(msg, "yellow") if color else msg)

    summary = f"  {len(errors)} error(s), {len(warnings)} warning(s)."
    lines.append(summary)
    return "\n".join(lines)


def print_schema_report(result: SchemaResult, *, color: bool = True) -> None:
    print(format_schema_report(result, color=color))
