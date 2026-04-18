"""Reporter for pin check results."""
from __future__ import annotations
from envdrift.pinner import PinResult

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _c(color: str, text: str, use_color: bool = True) -> str:
    return f"{color}{text}{RESET}" if use_color else text


def format_pin_report(result: PinResult, color: bool = True) -> str:
    lines = []
    label = result.env_file or "<env>"
    lines.append(_c(BOLD, f"Pin Check: {label}", color))

    if not result.has_violations():
        lines.append(_c(GREEN, "  ✔ All pinned keys match.", color))
        return "\n".join(lines)

    lines.append(_c(RED, f"  ✘ {len(result.violations)} violation(s) found:", color))
    for v in result.violations:
        if v.actual is None:
            detail = _c(YELLOW, "(missing)", color)
        else:
            detail = f"expected {_c(GREEN, repr(v.expected), color)}, got {_c(RED, repr(v.actual), color)}"
        lines.append(f"    {v.key}: {detail}")
    return "\n".join(lines)


def print_pin_report(result: PinResult, color: bool = True) -> None:
    print(format_pin_report(result, color=color))
