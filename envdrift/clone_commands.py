"""CLI sub-command: clone."""
from __future__ import annotations

import argparse

from envdrift.cloner import clone_env


def cmd_clone(args: argparse.Namespace) -> int:
    include = [k.strip() for k in args.include.split(",")] if args.include else None
    exclude = [k.strip() for k in args.exclude.split(",")] if args.exclude else None

    try:
        result = clone_env(
            source=args.source,
            target=args.target,
            include=include,
            exclude=exclude,
            redact=args.redact,
            redact_patterns_file=args.redact_patterns,
        )
    except FileNotFoundError as exc:
        print(f"[error] {exc}")
        return 1

    print(f"Cloned {result.source} -> {result.target}")
    print(f"  keys written : {len(result.keys_written)}")
    if result.keys_skipped:
        print(f"  keys skipped : {len(result.keys_skipped)} ({', '.join(result.keys_skipped)})")
    if result.redacted_keys:
        print(f"  keys redacted: {len(result.redacted_keys)} ({', '.join(result.redacted_keys)})")
    return 0


def register_clone_subcommand(subparsers) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("clone", help="Clone an env file to a new path")
    p.add_argument("source", help="Source .env file")
    p.add_argument("target", help="Destination .env file")
    p.add_argument("--include", default=None, help="Comma-separated keys to include")
    p.add_argument("--exclude", default=None, help="Comma-separated keys to exclude")
    p.add_argument("--redact", action="store_true", help="Redact sensitive values")
    p.add_argument("--redact-patterns", default=None, metavar="FILE",
                   help="Custom redact patterns file")
    p.set_defaults(func=cmd_clone)
