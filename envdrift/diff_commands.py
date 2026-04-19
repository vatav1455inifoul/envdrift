"""CLI subcommand: envdrift diff — pairwise .env comparison."""
from __future__ import annotations
import argparse
from pathlib import Path

from envdrift.parser import parse_env_file
from envdrift.comparator import compare_envs
from envdrift.differ_reporter import print_diff_report
from envdrift.ignorer import load_ignore_patterns, filter_keys


def cmd_diff(args: argparse.Namespace) -> int:
    path_a = Path(args.env_a)
    path_b = Path(args.env_b)

    if not path_a.exists():
        print(f"[error] File not found: {path_a}")
        return 1
    if not path_b.exists():
        print(f"[error] File not found: {path_b}")
        return 1

    env_a = parse_env_file(path_a)
    env_b = parse_env_file(path_b)

    ignore = load_ignore_patterns(args.ignore_file) if args.ignore_file else []
    if ignore:
        env_a = filter_keys(env_a, ignore)
        env_b = filter_keys(env_b, ignore)

    result = compare_envs(
        env_a, env_b,
        ignore_values=getattr(args, "ignore_values", False)
    )

    print_diff_report(result, str(path_a), str(path_b))

    if args.exit_code and result.has_drift():
        return 1
    return 0


def register_diff_subcommand(subparsers) -> None:
    p = subparsers.add_parser("diff", help="Compare two .env files")
    p.add_argument("env_a", help="First .env file")
    p.add_argument("env_b", help="Second .env file")
    p.add_argument("--ignore-values", action="store_true",
                   help="Only check key presence, not values")
    p.add_argument("--ignore-file", default=None,
                   help="Path to .envdriftignore file")
    p.add_argument("--exit-code", action="store_true",
                   help="Exit with code 1 if drift is detected")
    p.set_defaults(func=cmd_diff)
