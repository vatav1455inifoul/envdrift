"""Reporter for TrimResult."""
from __future__ import annotations
from envdrift.trimmer import TrimResult, has_unused


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_trim_report(result: TrimResult, color: bool = True) -> str:
    lines = []
    header = f"Trim report: {result.env_name} vs reference {result.reference_name}"
    lines.append(_c(header, "1") if color else header)
    lines.append("")

    if not has_unused(result):
        msg = "✓ No unused keys found."
        lines.append(_c(msg, "32") if color else msg)
        return "\n".join(lines)

    label = f"Unused keys ({len(result.unused_keys)}):"
    lines.append(_c(label, "33") if color else label)
    for k in result.unused_keys:
        entry = f"  - {k}"
        lines.append(_c(entry, "31") if color else entry)

    lines.append("")
    kept_label = f"Keys kept: {len(result.kept_env)}/{len(result.all_keys)}"
    lines.append(kept_label)
    return "\n".join(lines)


def print_trim_report(result: TrimResult, color: bool = True) -> None:
    print(format_trim_report(result, color=color))
