"""Formatter and printer for OverlapResult."""
from __future__ import annotations

from typing import List

from .differ_overlap import OverlapResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_DIM = "\033[2m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{_RESET}"


def format_overlap_report(result: OverlapResult, *, color: bool = True) -> str:
    lines: List[str] = []

    def h(t: str) -> str:
        return _c(_BOLD, t) if color else t

    envs_label = " vs ".join(result.env_names)
    lines.append(h(f"\n=== Overlap Report: {envs_label} ==="))
    lines.append(f"  Total keys   : {result.total_keys}")

    overlap_str = f"{result.overlap_percent}%"
    if color:
        rate_color = _GREEN if result.overlap_percent >= 80 else _YELLOW
        overlap_str = _c(rate_color, overlap_str)
    lines.append(f"  Overlap rate : {overlap_str}")
    lines.append("")

    if result.shared_keys:
        label = _c(_GREEN, "Shared keys") if color else "Shared keys"
        lines.append(f"  {label} ({len(result.shared_keys)}):")
        for k in sorted(result.shared_keys):
            lines.append(f"    {_c(_DIM, k) if color else k}")
        lines.append("")

    if result.partial_keys:
        label = _c(_YELLOW, "Partial keys") if color else "Partial keys"
        lines.append(f"  {label} (present in some envs, {len(result.partial_keys)}):")
        for k in sorted(result.partial_keys):
            owners = [n for n, ks in result.unique_keys.items() if k not in ks]
            # partial = not unique to one env but not in all; show which envs have it
            has = [n for n, v in zip(result.env_names,
                                     [set(result.shared_keys) | result.unique_keys[n]
                                      for n in result.env_names]) if k in v]
            lines.append(f"    {k}  {_c(_DIM, str(has)) if color else str(has)}")
        lines.append("")

    for env_name, ukeys in result.unique_keys.items():
        if ukeys:
            label = _c(_CYAN, f"Only in {env_name}") if color else f"Only in {env_name}"
            lines.append(f"  {label} ({len(ukeys)}):")
            for k in sorted(ukeys):
                lines.append(f"    {k}")
            lines.append("")

    return "\n".join(lines)


def print_overlap_report(result: OverlapResult, *, color: bool = True) -> None:
    print(format_overlap_report(result, color=color))
