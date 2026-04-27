"""Reporter for coverage analysis results."""
from __future__ import annotations

from envdrift.differ_coverage import CoverageResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_coverage_report(result: CoverageResult, *, color: bool = True) -> str:
    lines: list[str] = []

    title = "Coverage Report"
    lines.append(_c(title, "1;36") if color else title)
    lines.append(_c(f"Universe: {result.total_keys} keys", "90") if color else f"Universe: {result.total_keys} keys")
    lines.append("")

    for entry in result.entries:
        pct = entry.coverage_percent
        if pct == 100.0:
            rate_str = _c(f"{pct}%", "1;32") if color else f"{pct}%"
        elif pct >= 75.0:
            rate_str = _c(f"{pct}%", "33") if color else f"{pct}%"
        else:
            rate_str = _c(f"{pct}%", "31") if color else f"{pct}%"

        header = f"  {entry.env_name}: {rate_str} ({len(entry.present_keys)}/{entry.total_keys})"
        lines.append(header)

        if entry.missing_keys:
            label = _c("    missing:", "90") if color else "    missing:"
            lines.append(label)
            for k in entry.missing_keys:
                lines.append(f"      - {_c(k, '31') if color else k}")

        lines.append("")

    fully = result.fully_covered
    partial = result.partially_covered
    summary_label = _c("Summary", "1") if color else "Summary"
    lines.append(f"{summary_label}: {len(fully)} fully covered, {len(partial)} partial")

    avg = round(result.average_coverage * 100, 1)
    avg_label = _c(f"Average coverage: {avg}%", "1;32" if avg == 100.0 else "33") if color else f"Average coverage: {avg}%"
    lines.append(avg_label)

    return "\n".join(lines)


def print_coverage_report(result: CoverageResult, *, color: bool = True) -> None:
    print(format_coverage_report(result, color=color))
