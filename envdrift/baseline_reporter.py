"""Formatting helpers for baseline diff output."""

from __future__ import annotations

from envdrift.reporter import _colorize


def format_baseline_report(diff: dict, baseline_name: str, env_label: str = "current") -> str:
    """Return a human-readable string describing drift vs a baseline."""
    lines: list[str] = []
    lines.append(_colorize(f"=== Baseline diff: '{baseline_name}' vs {env_label} ===", "cyan"))

    if not any(diff[k] for k in ("added", "removed", "changed")):
        lines.append(_colorize("  No drift detected against baseline.", "green"))
        return "\n".join(lines)

    if diff["added"]:
        lines.append(_colorize("  Keys added (not in baseline):", "yellow"))
        for key in sorted(diff["added"]):
            lines.append(f"    + {key}={diff['added'][key]}")

    if diff["removed"]:
        lines.append(_colorize("  Keys removed (missing from current):", "red"))
        for key in sorted(diff["removed"]):
            lines.append(f"    - {key}={diff['removed'][key]}")

    if diff["changed"]:
        lines.append(_colorize("  Values changed:", "yellow"))
        for key in sorted(diff["changed"]):
            old, new = diff["changed"][key]
            lines.append(f"    ~ {key}: '{old}' -> '{new}'")

    return "\n".join(lines)


def print_baseline_report(diff: dict, baseline_name: str, env_label: str = "current") -> None:
    """Print the baseline diff report to stdout."""
    print(format_baseline_report(diff, baseline_name, env_label))
