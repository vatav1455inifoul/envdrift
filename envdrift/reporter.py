"""Formats and outputs drift reports to the terminal."""

from typing import Optional
from envdrift.comparator import DriftResult


ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_report(result: DriftResult, env_a: str, env_b: str, use_color: bool = True) -> str:
    """Build a human-readable drift report string from a DriftResult."""
    lines = []

    header = f"Drift report: {env_a}  →  {env_b}"
    lines.append(_colorize(header, ANSI_BOLD, use_color))
    lines.append("-" * len(header))

    if not result.has_drift():
        lines.append(_colorize("✔  No drift detected.", ANSI_GREEN, use_color))
        return "\n".join(lines)

    if result.missing_keys:
        lines.append(_colorize(f"\nMissing in {env_b} ({len(result.missing_keys)}):", ANSI_RED, use_color))
        for key in sorted(result.missing_keys):
            lines.append(f"  - {key}")

    if result.extra_keys:
        lines.append(_colorize(f"\nExtra in {env_b} ({len(result.extra_keys)}):", ANSI_YELLOW, use_color))
        for key in sorted(result.extra_keys):
            lines.append(f"  + {key}")

    if result.changed_values:
        lines.append(_colorize(f"\nChanged values ({len(result.changed_values)}):", ANSI_CYAN, use_color))
        for key, (val_a, val_b) in sorted(result.changed_values.items()):
            lines.append(f"  ~ {key}")
            lines.append(f"      {env_a}: {val_a!r}")
            lines.append(f"      {env_b}: {val_b!r}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def print_report(
    result: DriftResult,
    env_a: str,
    env_b: str,
    use_color: bool = True,
    output=None,
) -> None:
    """Print the formatted drift report. Accepts an optional file-like output."""
    import sys
    out = output or sys.stdout
    print(format_report(result, env_a, env_b, use_color=use_color), file=out)
