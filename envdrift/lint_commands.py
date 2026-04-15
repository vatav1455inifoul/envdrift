"""CLI command handler for the `envdrift lint` subcommand."""

from __future__ import annotations

import argparse
from typing import List

from envdrift.linter import LintResult, lint_env_file
from envdrift.lint_reporter import print_lint_report


def cmd_lint(args: argparse.Namespace) -> int:
    """Lint one or more .env files.

    Returns 0 if no errors found, 1 if any errors exist.
    Warnings alone do not cause a non-zero exit unless --strict is set.
    """
    paths: List[str] = args.envfiles
    if not paths:
        print("No .env files specified.")
        return 1

    results: List[LintResult] = [lint_env_file(p) for p in paths]
    no_color: bool = getattr(args, "no_color", False)
    print_lint_report(results, color=not no_color)

    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    strict: bool = getattr(args, "strict", False)
    if total_errors > 0:
        return 1
    if strict and total_warnings > 0:
        return 1
    return 0


def register_lint_subcommand(subparsers) -> None:  # type: ignore[type-arg]
    """Attach the lint subcommand to an existing subparsers group."""
    p = subparsers.add_parser(
        "lint",
        help="Lint .env files for common issues",
    )
    p.add_argument(
        "envfiles",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to lint",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 on warnings as well as errors",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    p.set_defaults(func=cmd_lint)
