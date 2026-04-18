"""CLI command for the templater feature."""
from __future__ import annotations
import argparse
from pathlib import Path
from envdrift.parser import parse_env_file
from envdrift.templater import build_example, render_example, write_example


def cmd_template(args: argparse.Namespace) -> int:
    envs = []
    for p in args.envfiles:
        path = Path(p)
        if not path.exists():
            print(f"[error] file not found: {p}")
            return 1
        envs.append(parse_env_file(path))

    placeholder = args.placeholder if args.placeholder is not None else ""
    keep = not args.blank_safe

    if args.output:
        write_example(envs, args.output, placeholder=placeholder, keep_safe_values=keep)
        print(f"Written to {args.output}")
    else:
        example = build_example(envs, placeholder=placeholder, keep_safe_values=keep)
        print(render_example(example), end="")
    return 0


def register_template_subcommand(subparsers) -> None:
    p = subparsers.add_parser(
        "template",
        help="Generate a .env.example from one or more env files",
    )
    p.add_argument("envfiles", nargs="+", help="Input .env files")
    p.add_argument("-o", "--output", default=None, help="Output file path")
    p.add_argument(
        "--placeholder",
        default="",
        help="Value to use for sensitive keys (default: empty)",
    )
    p.add_argument(
        "--blank-safe",
        action="store_true",
        help="Also blank out non-sensitive values",
    )
    p.set_defaults(func=cmd_template)
