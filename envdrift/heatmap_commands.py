"""CLI subcommand: heatmap — show which keys drift most frequently."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdrift.comparator import compare_envs
from envdrift.differ import multi_diff
from envdrift.differ_heatmap import heatmap_from_multi, heatmap_from_pairs
from envdrift.heatmap_reporter import print_heatmap_report
from envdrift.parser import parse_env_file


def cmd_heatmap(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.envs]
    for p in paths:
        if not p.exists():
            print(f"[error] File not found: {p}", file=sys.stderr)
            return 1

    if len(paths) < 2:
        print("[error] At least two env files are required.", file=sys.stderr)
        return 1

    if args.mode == "multi":
        named = {p.name: parse_env_file(p) for p in paths}
        result = multi_diff(named)
        heatmap = heatmap_from_multi(result)
    else:
        # pairwise: compare every consecutive pair (base vs each other)
        base_path = paths[0]
        base = parse_env_file(base_path)
        pair_results = []
        for other_path in paths[1:]:
            other = parse_env_file(other_path)
            pair_results.append(
                compare_envs(base, other, base_path.name, other_path.name)
            )
        heatmap = heatmap_from_pairs(pair_results)

    print_heatmap_report(heatmap, top=args.top)
    return 0


def register_heatmap_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("heatmap", help="Show which keys drift most across env files")
    p.add_argument("envs", nargs="+", metavar="ENV", help="Two or more .env files")
    p.add_argument(
        "--mode",
        choices=["multi", "pair"],
        default="multi",
        help="Comparison mode: multi (default) or pairwise against first file",
    )
    p.add_argument(
        "--top",
        type=int,
        default=0,
        metavar="N",
        help="Show only top N keys (0 = all)",
    )
    p.set_defaults(func=cmd_heatmap)
