"""Reporter for drift heatmaps."""
from __future__ import annotations

from envdrift.differ_heatmap import HeatmapResult


def _c(text: str, color: str) -> str:
    codes = {"red": "\033[31m", "yellow": "\033[33m", "green": "\033[32m", "bold": "\033[1m", "reset": "\033[0m"}
    return f"{codes.get(color, '')}{text}{codes['reset']}"


def _bar(rate: float, width: int = 20) -> str:
    filled = round(rate * width)
    bar = "█" * filled + "░" * (width - filled)
    if rate >= 0.75:
        return _c(bar, "red")
    if rate >= 0.40:
        return _c(bar, "yellow")
    return _c(bar, "green")


def format_heatmap_report(result: HeatmapResult, top: int = 0) -> str:
    lines = []
    lines.append(_c("Drift Heatmap", "bold"))
    lines.append(f"  Total comparisons: {result.total_comparisons}")
    lines.append("")

    entries = result.hottest
    if top > 0:
        entries = entries[:top]

    if not entries:
        lines.append(_c("  No keys tracked.", "green"))
        return "\n".join(lines)

    max_key_len = max(len(e.key) for e in entries)

    lines.append(f"  {'KEY'.ljust(max_key_len)}  {'DRIFT':>6}  BAR")
    lines.append("  " + "-" * (max_key_len + 32))

    for entry in entries:
        pct = f"{entry.drift_rate * 100:.0f}%".rjust(5)
        bar = _bar(entry.drift_rate)
        key_label = entry.key.ljust(max_key_len)
        lines.append(f"  {key_label}  {pct}   {bar}  ({entry.drift_count}/{entry.total_comparisons})")

    lines.append("")
    drifting = len(result.drifting_keys)
    stable = len(result.stable_keys)
    lines.append(f"  {_c(str(drifting), 'red')} drifting  |  {_c(str(stable), 'green')} stable")
    return "\n".join(lines)


def print_heatmap_report(result: HeatmapResult, top: int = 0) -> None:
    print(format_heatmap_report(result, top=top))
