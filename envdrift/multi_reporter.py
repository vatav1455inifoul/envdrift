"""Reporter for multi-environment diff results (differ.py output)."""

from __future__ import annotations

from typing import Optional

from envdrift.differ import MultiDiffResult
from envdrift.reporter import _colorize


def format_multi_report(
    result: MultiDiffResult,
    use_color: bool = True,
) -> str:
    """Return a human-readable report for a multi-env diff."""
    lines: list[str] = []

    env_list = ", ".join(result.env_names)
    header = f"Multi-env drift report: [{env_list}]"
    lines.append(_colorize(header, "bold", use_color))
    lines.append("")

    if not result.has_drift:
        lines.append(_colorize("  No drift detected across all environments.", "green", use_color))
        return "\n".join(lines)

    # Keys missing in at least one env
    missing = result.missing_in_some
    if missing:
        lines.append(_colorize("  Keys missing in some environments:", "yellow", use_color))
        for key, present_in in sorted(missing.items()):
            absent_in = [e for e in result.env_names if e not in present_in]
            present_str = ", ".join(present_in)
            absent_str = ", ".join(absent_in)
            lines.append(f"    {key}")
            lines.append(f"      present in : {present_str}")
            lines.append(f"      absent in  : {absent_str}")
        lines.append("")

    # Keys with inconsistent values
    inconsistent = result.inconsistent_keys
    if inconsistent:
        lines.append(_colorize("  Keys with inconsistent values:", "red", use_color))
        for key, env_values in sorted(inconsistent.items()):
            lines.append(f"    {key}")
            for env_name, value in sorted(env_values.items()):
                display = "(not set)" if value is None else repr(value)
                lines.append(f"      {env_name}: {display}")
        lines.append("")

    return "\n".join(lines)


def print_multi_report(
    result: MultiDiffResult,
    use_color: bool = True,
    file=None,
) -> None:
    """Print the multi-env drift report to *file* (default: stdout)."""
    import sys

    print(format_multi_report(result, use_color=use_color), file=file or sys.stdout)
