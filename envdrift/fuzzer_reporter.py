"""Reporting for fuzzy key match results."""
from __future__ import annotations

from .fuzzer import FuzzyResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_fuzzy_report(result: FuzzyResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Fuzzy diff: {result.env_a}  vs  {result.env_b}"
    lines.append(_c(header, "1;36") if color else header)
    lines.append("")

    if not result.has_suggestions and not result.unmatched_a and not result.unmatched_b:
        msg = "  No fuzzy matches or unmatched keys found."
        lines.append(_c(msg, "32") if color else msg)
        return "\n".join(lines)

    if result.matches:
        section = "Possible renames / typos:"
        lines.append(_c(section, "1;33") if color else section)
        for m in result.matches:
            arrow = f"  {m.key_a}  →  {m.key_b}  ({m.score:.0%} similar)"
            lines.append(_c(arrow, "33") if color else arrow)
        lines.append("")

    if result.unmatched_a:
        section = f"Only in {result.env_a} (no close match):"
        lines.append(_c(section, "1;31") if color else section)
        for k in result.unmatched_a:
            lines.append(f"  - {k}")
        lines.append("")

    if result.unmatched_b:
        section = f"Only in {result.env_b} (no close match):"
        lines.append(_c(section, "1;34") if color else section)
        for k in result.unmatched_b:
            lines.append(f"  + {k}")
        lines.append("")

    return "\n".join(lines)


def print_fuzzy_report(result: FuzzyResult, *, color: bool = True) -> None:
    print(format_fuzzy_report(result, color=color))
