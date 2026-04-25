"""Reporter for variance analysis results."""
from __future__ import annotations
from envdrift.differ_variance import VarianceResult

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _c(color: str, text: str, use_color: bool = True) -> str:
    return f"{color}{text}{_RESET}" if use_color else text


def format_variance_report(result: VarianceResult, *, color: bool = True) -> str:
    lines: list[str] = []
    envs = ", ".join(result.env_names)
    lines.append(_c(_BOLD, f"=== Variance Report: {envs} ===", color))
    lines.append(f"Total keys : {len(result.entries)}")
    lines.append(f"Uniform    : {len(result.uniform_keys)}")
    lines.append(f"Divergent  : {len(result.divergent_keys)}")
    lines.append(f"Partial    : {len(result.partial_keys)}")

    if result.is_uniform:
        lines.append(_c(_GREEN, "\n✔ All keys are uniform across environments.", color))
        return "\n".join(lines)

    if result.divergent_keys:
        lines.append(_c(_BOLD, "\nDivergent keys:", color))
        for entry in sorted(result.divergent_keys, key=lambda e: -e.variance_ratio):
            ratio_pct = f"{entry.variance_ratio * 100:.0f}%"
            lines.append(
                f"  {_c(_RED, entry.key, color)}"
                f" — {entry.unique_values} unique values"
                f" (variance {ratio_pct})"
            )
            for env, val in entry.values.items():
                display = repr(val) if val is not None else _c(_YELLOW, "<missing>", color)
                lines.append(f"      {env}: {display}")

    if result.partial_keys:
        lines.append(_c(_BOLD, "\nPartial keys (missing in some envs):", color))
        for entry in result.partial_keys:
            missing = ", ".join(entry.missing_in)
            lines.append(
                f"  {_c(_YELLOW, entry.key, color)} — missing in: {missing}"
            )

    return "\n".join(lines)


def print_variance_report(result: VarianceResult, *, color: bool = True) -> None:
    print(format_variance_report(result, color=color))
