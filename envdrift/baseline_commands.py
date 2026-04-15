"""CLI command handlers for baseline sub-commands."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdrift.baseline import (
    save_baseline,
    load_baseline,
    list_baselines,
    diff_against_baseline,
    baseline_has_drift,
)
from envdrift.baseline_reporter import print_baseline_report
from envdrift.snapshot import create_snapshot


def cmd_baseline_save(args: argparse.Namespace) -> int:
    """Save a snapshot file as a named baseline."""
    snap_path = Path(args.snapshot)
    if not snap_path.exists():
        print(f"Error: snapshot file not found: {snap_path}", file=sys.stderr)
        return 1
    try:
        dest = save_baseline(snap_path, args.name)
        print(f"Baseline '{args.name}' saved to {dest}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Error saving baseline: {exc}", file=sys.stderr)
        return 1


def cmd_baseline_diff(args: argparse.Namespace) -> int:
    """Diff a .env file against a named baseline."""
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: env file not found: {env_path}", file=sys.stderr)
        return 1
    try:
        baseline = load_baseline(args.name)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    current_snap = create_snapshot(env_path, env_name=args.name)
    diff = diff_against_baseline(current_snap, baseline)
    print_baseline_report(diff, args.name, env_label=str(env_path))

    if args.exit_code and baseline_has_drift(diff):
        return 1
    return 0


def cmd_baseline_list(args: argparse.Namespace) -> int:  # noqa: ARG001
    """List all saved baselines."""
    names = list_baselines()
    if not names:
        print("No baselines saved yet.")
    else:
        print("Saved baselines:")
        for name in names:
            print(f"  - {name}")
    return 0
