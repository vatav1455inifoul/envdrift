"""Format and print ProfileResult objects."""
from __future__ import annotations

from envdrift.profiler import ProfileResult
from envdrift.reporter import _colorize


def format_profile_report(result: ProfileResult, *, color: bool = True) -> str:
    lines: list[str] = []

    def c(text: str, code: str) -> str:
        return _colorize(text, code) if color else text

    lines.append(c(f"=== Profile: {result.env_file} ===", "1;36"))
    lines.append(f"  Total keys   : {result.total_keys}")
    lines.append(f"  Fill rate    : {result.fill_rate}%")
    lines.append(f"  Empty values : {result.empty_count}")

    categories = [
        ("Numeric", result.numeric_values, "33"),
        ("Boolean", result.boolean_values, "34"),
        ("URL", result.url_values, "36"),
        ("Long (>100 chars)", result.long_values, "35"),
    ]

    for label, keys, code in categories:
        if keys:
            lines.append(c(f"  {label}:", code))
            for k in sorted(keys):
                lines.append(f"    - {k}")

    if result.empty_values:
        lines.append(c("  Empty value keys:", "31"))
        for k in sorted(result.empty_values):
            lines.append(f"    - {k}")

    return "\n".join(lines)


def print_profile_report(result: ProfileResult, *, color: bool = True) -> None:
    print(format_profile_report(result, color=color))
