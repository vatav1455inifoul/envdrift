"""Format and print lint results for one or more .env files."""

from __future__ import annotations

from typing import List

from envdrift.linter import LintResult

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"


def _severity_color(severity: str) -> str:
    return _RED if severity == "error" else _YELLOW


def format_lint_report(results: List[LintResult], *, color: bool = True) -> str:
    lines: list[str] = []

    def c(text: str, code: str) -> str:
        return f"{code}{text}{_RESET}" if color else text

    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    for result in results:
        lines.append(c(f"\n=== {result.path} ===", _BOLD + _CYAN))

        if not result.has_issues:
            lines.append(c("  ✔ No issues found", _GREEN))
            continue

        for issue in result.issues:
            sev_label = c(issue.severity.upper(), _severity_color(issue.severity))
            location = f"line {issue.line_number}"
            lines.append(f"  [{sev_label}] {location} [{issue.code}] {issue.message}")

    lines.append("")
    if total_errors == 0 and total_warnings == 0:
        lines.append(c("All files passed lint checks.", _GREEN))
    else:
        summary_parts = []
        if total_errors:
            summary_parts.append(c(f"{total_errors} error(s)", _RED))
        if total_warnings:
            summary_parts.append(c(f"{total_warnings} warning(s)", _YELLOW))
        lines.append("Summary: " + ", ".join(summary_parts))

    return "\n".join(lines)


def print_lint_report(results: List[LintResult], *, color: bool = True) -> None:
    print(format_lint_report(results, color=color))
