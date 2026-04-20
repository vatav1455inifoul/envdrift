"""Reporter for DriftStats."""
from envdrift.differ_stats import DriftStats

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


def _score_color(score: float) -> str:
    if score == 0.0:
        return GREEN
    if score < 0.4:
        return YELLOW
    return RED


def format_stats_report(stats: DriftStats, label: str = "env") -> str:
    lines = []
    lines.append(f"{BOLD}=== Drift Statistics: {label} ==={RESET}")
    lines.append(f"  Total keys   : {stats.total_keys}")
    lines.append(f"  Missing      : {_c(YELLOW, str(stats.missing_count))}")
    lines.append(f"  Extra        : {_c(YELLOW, str(stats.extra_count))}")
    lines.append(f"  Changed      : {_c(YELLOW, str(stats.changed_count))}")
    color = _score_color(stats.drift_score)
    pct = f"{stats.drift_score * 100:.1f}%"
    lines.append(f"  Drift score  : {_c(color, pct)}")
    if stats.most_drifted_key:
        lines.append(f"  Most drifted : {_c(RED, stats.most_drifted_key)}")
    if stats.is_clean:
        lines.append(_c(GREEN, "  ✔ No drift detected."))
    return "\n".join(lines)


def print_stats_report(stats: DriftStats, label: str = "env") -> None:
    print(format_stats_report(stats, label))
