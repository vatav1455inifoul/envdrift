"""CLI subcommand: fuzzy-diff — suggest likely renamed keys between two envs."""
from __future__ import annotations

import argparse
import sys

from .parser import parse_env_file
from .fuzzer import fuzzy_diff, DEFAULT_THRESHOLD
from .fuzzer_reporter import print_fuzzy_report


def cmd_fuzzy_diff(args: argparse.Namespace) -> int:
    try:
        env_a = parse_env_file(args.env_a)
    except FileNotFoundError:
        print(f"[error] file not found: {args.env_a}", file=sys.stderr)
        return 1

    try:
        env_b = parse_env_file(args.env_b)
    except FileNotFoundError:
        print(f"[error] file not found: {args.env_b}", file=sys.stderr)
        return 1

    threshold = args.threshold
    if not (0.0 < threshold <= 1.0):
        print("[error] --threshold must be between 0 (exclusive) and 1.0", file=sys.stderr)
        return 1

    result = fuzzy_diff(
        env_a,
        env_b,
        name_a=args.env_a,
        name_b=args.env_b,
        threshold=threshold,
    )

    no_color = getattr(args, "no_color", False)
    print_fuzzy_report(result, color=not no_color)
    return 0


def register_fuzzy_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "fuzzy-diff",
        help="suggest likely renamed or misspelled keys between two .env files",
    )
    p.add_argument("env_a", help="first .env file")
    p.add_argument("env_b", help="second .env file")
    p.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        metavar="N",
        help=f"similarity threshold 0–1 (default: {DEFAULT_THRESHOLD})",
    )
    p.add_argument("--no-color", action="store_true", help="disable coloured output")
    p.set_defaults(func=cmd_fuzzy_diff)
