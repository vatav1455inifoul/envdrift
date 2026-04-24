"""digest_commands.py – CLI sub-commands for file digest / hash checks."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdrift.digester import digest_file, digests_match, digest_to_dict
from envdrift.digest_reporter import print_digest_report


def cmd_digest(args: argparse.Namespace) -> int:
    """Compute and display digests for one or more .env files."""
    digests = []
    for path in args.files:
        if not Path(path).exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1
        digests.append(digest_file(path))

    if getattr(args, "json", False):
        print(json.dumps([digest_to_dict(d) for d in digests], indent=2))
        return 0

    print_digest_report(
        digests,
        strict=getattr(args, "strict", False),
        color=not getattr(args, "no_color", False),
    )

    if len(digests) >= 2 and getattr(args, "exit_code", False):
        base = digests[0]
        for other in digests[1:]:
            if not digests_match(base, other, strict=getattr(args, "strict", False)):
                return 1
    return 0


def register_digest_subcommand(subparsers) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "digest",
        help="compute SHA-256 content hashes for .env files and compare them",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to hash")
    p.add_argument(
        "--strict",
        action="store_true",
        help="compare raw file bytes instead of parsed content",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        dest="exit_code",
        help="exit with code 1 when digests differ",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="output results as JSON",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        dest="no_color",
    )
    p.set_defaults(func=cmd_digest)
