"""Format and print interpolation check results."""
from __future__ import annotations
from .interpolator import InterpolationResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_interpolation_report(result: InterpolationResult) -> str:
    lines: list[str] = []
    lines.append(_c(f"=== Interpolation Report: {result.env_name} ===", "1"))

    if not result.references:
        lines.append(_c("  No interpolation references found.", "32"))
        return "\n".join(lines)

    lines.append(f"  References found in {len(result.references)} key(s):")
    for key, refs in result.references.items():
        ref_str = ", ".join(refs)
        lines.append(f"    {_c(key, '36')} -> [{ref_str}]")

    if result.has_unresolved:
        lines.append("")
        lines.append(_c("  Unresolved references:", "33"))
        for key, missing in result.unresolved.items():
            for ref in missing:
                lines.append(f"    {_c(key, '36')}: ${ref} is not defined")
    else:
        lines.append(_c("  All references resolve to defined keys.", "32"))

    return "\n".join(lines)


def print_interpolation_report(result: InterpolationResult) -> None:
    print(format_interpolation_report(result))
