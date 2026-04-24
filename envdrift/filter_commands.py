"""CLI sub-commands for filtered drift comparisons."""

from __future__ import annotations

import argparse
import sys

from envdrift.parser import parse_env_file
from envdrift.comparator import compare_envs
from envdrift.differ import multi_diff
from envdrift.differ_filter import FilterOptions, filter_pair_drift, filter_multi_drift
from envdrift.filter_reporter import print_filtered_pair_report, print_filtered_multi_report


def _build_filter_opts(args: argparse.Namespace) -> FilterOptions:
    return FilterOptions(
        include_patterns=args.include or [],
        exclude_patterns=args.exclude or [],
        only_missing=getattr(args, "only_missing", False),
        only_extra=getattr(args, "only_extra", False),
        only_changed=getattr(args, "only_changed", False),
    )


def cmd_filter_diff(args: argparse.Namespace) -> int:
    try:
        a = parse_env_file(args.env_a)
        b = parse_env_file(args.env_b)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    opts = _build_filter_opts(args)
    raw = compare_envs(args.env_a, args.env_b, a, b)
    filtered = filter_pair_drift(raw, opts)
    print_filtered_pair_report(filtered, opts)

    if args.exit_code and (filtered.missing_keys or filtered.extra_keys or filtered.changed_values):
        return 1
    return 0


def cmd_filter_multi(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.envs:
        try:
            envs[path] = parse_env_file(path)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    opts = _build_filter_opts(args)
    raw = multi_diff(envs)
    filtered = filter_multi_drift(raw, opts)
    print_filtered_multi_report(filtered, opts)

    if args.exit_code and (filtered.missing_in_some or filtered.inconsistent_keys):
        return 1
    return 0


def register_filter_subcommand(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--include", nargs="*", metavar="PATTERN", help="only show keys matching patterns")
        p.add_argument("--exclude", nargs="*", metavar="PATTERN", help="hide keys matching patterns")
        p.add_argument("--only-missing", action="store_true")
        p.add_argument("--only-extra", action="store_true")
        p.add_argument("--only-changed", action="store_true")
        p.add_argument("--exit-code", action="store_true")

    p_diff = sub.add_parser("filter-diff", help="filtered two-env diff")
    p_diff.add_argument("env_a")
    p_diff.add_argument("env_b")
    _add_common(p_diff)
    p_diff.set_defaults(func=cmd_filter_diff)

    p_multi = sub.add_parser("filter-multi", help="filtered multi-env diff")
    p_multi.add_argument("envs", nargs="+")
    _add_common(p_multi)
    p_multi.set_defaults(func=cmd_filter_multi)
