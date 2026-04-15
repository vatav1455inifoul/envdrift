"""CLI subcommand: envdrift profile <env_file> [<env_file> ...]"""
from __future__ import annotations

import argparse
import sys

from envdrift.profiler import profile_env
from envdrift.profile_reporter import print_profile_report


def cmd_profile(args: argparse.Namespace) -> int:
    """Profile one or more .env files and print statistics."""
    exit_code = 0
    for path in args.envfiles:
        try:
            result = profile_env(path)
        except FileNotFoundError:
            print(f"[error] file not found: {path}", file=sys.stderr)
            exit_code = 1
            continue
        print_profile_report(result, color=not args.no_color)
        if len(args.envfiles) > 1:
            print()
    return exit_code


def register_profile_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "profile",
        help="Show key statistics and value patterns for .env files",
    )
    p.add_argument("envfiles", nargs="+", metavar="ENV_FILE", help=".env file(s) to profile")
    p.add_argument("--no-color", action="store_true", help="Disable coloured output")
    p.set_defaults(func=cmd_profile)
