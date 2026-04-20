"""CLI command for drift statistics."""
import argparse
from envdrift.parser import parse_env_file
from envdrift.comparator import compare_envs
from envdrift.differ import multi_diff
from envdrift.differ_stats import stats_from_pair, stats_from_multi
from envdrift.stats_reporter import print_stats_report


def cmd_stats(args: argparse.Namespace) -> int:
    envs = args.envs
    if len(envs) < 2:
        print("error: at least two env files required")
        return 1
    try:
        if len(envs) == 2:
            base = parse_env_file(envs[0])
            other = parse_env_file(envs[1])
            result = compare_envs(base, other)
            stats = stats_from_pair(result)
            label = f"{envs[0]} vs {envs[1]}"
        else:
            parsed = {e: parse_env_file(e) for e in envs}
            result = multi_diff(parsed)
            stats = stats_from_multi(result)
            label = ", ".join(envs)
    except FileNotFoundError as exc:
        print(f"error: {exc}")
        return 1
    print_stats_report(stats, label=label)
    return 0


def register_stats_subcommand(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("stats", help="show drift statistics for env files")
    p.add_argument("envs", nargs="+", metavar="ENV", help="env files to analyse")
    p.set_defaults(func=cmd_stats)
