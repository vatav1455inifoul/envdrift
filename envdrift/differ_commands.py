"""CLI commands for multi-env diff."""
from __future__ import annotations
import argparse
from envdrift.differ import multi_diff
from envdrift.multi_reporter import print_multi_report
from envdrift.parser import parse_env_file
from envdrift.ignorer import load_ignore_patterns, filter_keys
from envdrift.exporter import export_json_file


def cmd_multi_diff(args: argparse.Namespace) -> int:
    envs: dict[str, dict[str, str]] = {}
    for path in args.envs:
        try:
            data = parse_env_file(path)
        except FileNotFoundError:
            print(f"[error] file not found: {path}")
            return 1
        if args.ignore_file:
            patterns = load_ignore_patterns(args.ignore_file)
            data = filter_keys(data, patterns)
        envs[path] = data

    if len(envs) < 2:
        print("[error] at least two env files are required")
        return 1

    result = multi_diff(envs, ignore_values=args.ignore_values)
    print_multi_report(result)

    if args.export_json:
        export_json_file(result, args.export_json)
        print(f"[info] exported JSON to {args.export_json}")

    if args.exit_code and result.has_drift:
        return 1
    return 0


def register_multi_diff_subcommand(subparsers) -> None:
    p = subparsers.add_parser("multi-diff", help="Compare multiple .env files at once")
    p.add_argument("envs", nargs="+", metavar="ENV", help="Two or more .env file paths")
    p.add_argument("--ignore-values", action="store_true", help="Only check key presence")
    p.add_argument("--ignore-file", metavar="FILE", default=None)
    p.add_argument("--export-json", metavar="FILE", default=None)
    p.add_argument("--exit-code", action="store_true", help="Exit 1 if drift detected")
    p.set_defaults(func=cmd_multi_diff)
