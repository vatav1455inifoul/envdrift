"""CLI entry point for envdrift using argparse."""

import argparse
import sys
from pathlib import Path

from envdrift.parser import parse_env_file
from envdrift.comparator import compare_envs
from envdrift.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdrift",
        description="Detect configuration drift between .env files across environments.",
    )
    parser.add_argument(
        "base",
        metavar="BASE",
        help="Path to the base .env file (e.g. .env.development)",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target .env file to compare against (e.g. .env.production)",
    )
    parser.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Only check for key presence; ignore value differences",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if drift is detected",
    )
    return parser


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    target_path = Path(args.target)

    for path in (base_path, target_path):
        if not path.exists():
            print(f"envdrift: error: file not found: {path}", file=sys.stderr)
            return 2

    base_env = parse_env_file(base_path)
    target_env = parse_env_file(target_path)

    result = compare_envs(
        base_env,
        target_env,
        env_names=(base_path.name, target_path.name),
        ignore_values=args.ignore_values,
    )

    print_report(result, use_color=not args.no_color)

    if args.exit_code and result.has_drift():
        return 1
    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
