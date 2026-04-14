"""High-level snapshot commands wired into the CLI."""

import sys
from typing import Optional

from envdrift.parser import parse_env_file
from envdrift.snapshot import create_snapshot, load_snapshot, save_snapshot, snapshot_summary
from envdrift.comparator import compare_envs
from envdrift.reporter import format_report, print_report


def cmd_snapshot_save(
    env_file: str,
    env_name: str,
    output: str,
    notes: Optional[str] = None,
) -> int:
    """Parse an env file and persist it as a snapshot. Returns exit code."""
    try:
        parsed = parse_env_file(env_file)
    except FileNotFoundError:
        print(f"error: env file not found: {env_file}", file=sys.stderr)
        return 1

    snapshot = create_snapshot(env_name, parsed, notes=notes)
    save_snapshot(snapshot, output)
    print(f"Snapshot saved → {output}")
    print(snapshot_summary(snapshot))
    return 0


def cmd_snapshot_diff(
    env_file: str,
    snapshot_path: str,
    ignore_values: bool = False,
    use_exit_code: bool = False,
) -> int:
    """Compare a live env file against a saved snapshot. Returns exit code."""
    try:
        live = parse_env_file(env_file)
    except FileNotFoundError:
        print(f"error: env file not found: {env_file}", file=sys.stderr)
        return 1

    try:
        snap = load_snapshot(snapshot_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = compare_envs(
        snap["values"],
        live,
        env_a_name=snap["env_name"],
        env_b_name=env_file,
        ignore_values=ignore_values,
    )

    report = format_report(result)
    print_report(report)

    if use_exit_code and result.has_drift:
        return 1
    return 0


def cmd_snapshot_info(snapshot_path: str) -> int:
    """Print metadata about a saved snapshot. Returns exit code."""
    try:
        snap = load_snapshot(snapshot_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(snapshot_summary(snap))
    print(f"  version   : {snap['version']}")
    print(f"  env_name  : {snap['env_name']}")
    print(f"  created_at: {snap['created_at']}")
    if snap.get("notes"):
        print(f"  notes     : {snap['notes']}")
    print(f"  keys ({len(snap['values'])}): {', '.join(sorted(snap['values'].keys()))}")
    return 0
