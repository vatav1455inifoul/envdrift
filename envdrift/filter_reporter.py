"""Reporter for filtered drift output."""

from __future__ import annotations

from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult
from envdrift.differ_filter import FilterOptions
from envdrift.reporter import format_report
from envdrift.multi_reporter import format_multi_report


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_filter_summary(opts: FilterOptions) -> str:
    parts = []
    if opts.include_patterns:
        parts.append("include: " + ", ".join(opts.include_patterns))
    if opts.exclude_patterns:
        parts.append("exclude: " + ", ".join(opts.exclude_patterns))
    flags = []
    if opts.only_missing:
        flags.append("only-missing")
    if opts.only_extra:
        flags.append("only-extra")
    if opts.only_changed:
        flags.append("only-changed")
    if flags:
        parts.append("flags: " + ", ".join(flags))
    if not parts:
        return ""
    return _c("[filter] ", "36") + " | ".join(parts) + "\n"


def format_filtered_pair_report(result: DriftResult, opts: FilterOptions) -> str:
    header = format_filter_summary(opts)
    body = format_report(result)
    return header + body


def format_filtered_multi_report(result: MultiDiffResult, opts: FilterOptions) -> str:
    header = format_filter_summary(opts)
    body = format_multi_report(result)
    return header + body


def print_filtered_pair_report(result: DriftResult, opts: FilterOptions) -> None:
    print(format_filtered_pair_report(result, opts), end="")


def print_filtered_multi_report(result: MultiDiffResult, opts: FilterOptions) -> None:
    print(format_filtered_multi_report(result, opts), end="")
