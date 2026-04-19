"""Reporter for ValidationResult."""
from __future__ import annotations
from .validator import ValidationResult


def _c(text: str, color: str) -> str:
    codes = {"red": "\033[31m", "yellow": "\033[33m", "cyan": "\033[36m", "bold": "\033[1m", "reset": "\033[0m"}
    return f"{codes.get(color, '')}{text}{codes['reset']}"


def format_validation_report(result: ValidationResult, color: bool = True) -> str:
    lines = []
    title = f"Validation report — {result.env_name}"
    lines.append(_c(title, "bold") if color else title)
    lines.append("-" * len(title))

    if not result.has_issues():
        lines.append(_c("✔ All values pass validation.", "cyan") if color else "✔ All values pass validation.")
        return "\n".join(lines)

    for issue in result.errors():
        tag = _c("[ERROR]", "red") if color else "[ERROR]"
        lines.append(f"  {tag} {issue.key}={issue.value!r} — {issue.message}")

    for issue in result.warnings():
        tag = _c("[WARN]", "yellow") if color else "[WARN]"
        lines.append(f"  {tag} {issue.key}={issue.value!r} — {issue.message}")

    total = len(result.issues)
    summary = f"{total} issue(s) found."
    lines.append("")
    lines.append(_c(summary, "red") if color else summary)
    return "\n".join(lines)


def print_validation_report(result: ValidationResult, color: bool = True) -> None:
    print(format_validation_report(result, color=color))
