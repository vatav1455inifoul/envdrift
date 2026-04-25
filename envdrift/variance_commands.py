"""CLI subcommand for variance analysis."""
from __future__ import annotations
import argparse
import sys
from envdrift.differ_variance import analyse_variance
from envdrift.variance_reporter import print_variance_report


def cmd_variance(args: argparse.Namespace) -> int:
    """Run variance analysis across two or more env files."""
    if len(args.envs) < 2:
        print("error: variance requires at least two ENV=FILE arguments", file=sys.stderr)
        return 1

    env_files: dict[str, str] = {}
    for token in args.envs:
        if "=" not in token:
            print(f"error: expected NAME=FILE, got {token!r}", file=sys.stderr)
            return 1
        name, _, path = token.partition("=")
        env_files[name] = path

    try:
        result = analyse_variance(env_files)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_variance_report(result, color=not args.no_color)

    if args.exit_code and not result.is_uniform:
        return 1
    return 0


def register_variance_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "variance",
        help="Analyse value variance across multiple env files",
    )
    p.add_argument(
        "envs",
        nargs="+",
        metavar="NAME=FILE",
        help="Named env files, e.g. staging=.env.staging prod=.env.prod",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when variance is detected",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output",
    )
    p.set_defaults(func=cmd_variance)
