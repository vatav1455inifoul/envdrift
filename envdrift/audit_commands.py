"""CLI subcommands for audit trail management."""

from __future__ import annotations

import argparse
import sys

from envdrift.auditor import (
    DEFAULT_AUDIT_DIR,
    audit_summary,
    list_audits,
    load_audit,
    record_audit,
)


def cmd_audit_record(args: argparse.Namespace) -> int:
    """Manually record an audit entry (useful for scripting)."""
    path = record_audit(
        env_files=args.env_files,
        drift_detected=args.drift,
        summary=args.summary,
        audit_dir=args.audit_dir,
        notes=args.notes or "",
    )
    print(f"Audit recorded: {path}")
    return 0


def cmd_audit_list(args: argparse.Namespace) -> int:
    """List all recorded audit entries."""
    entries = list_audits(args.audit_dir)
    if not entries:
        print("No audit entries found.")
        return 0
    for p in entries:
        try:
            entry = load_audit(p)
            print(audit_summary(entry))
        except Exception as exc:  # noqa: BLE001
            print(f"  [error reading {p}: {exc}]")
    return 0


def cmd_audit_show(args: argparse.Namespace) -> int:
    """Show the full contents of a single audit entry."""
    import json

    try:
        entry = load_audit(args.path)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(entry, indent=2))
    return 0


def register_audit_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    audit_p = subparsers.add_parser("audit", help="Manage audit trail")
    audit_sub = audit_p.add_subparsers(dest="audit_cmd")

    # record
    rec = audit_sub.add_parser("record", help="Record an audit entry")
    rec.add_argument("env_files", nargs="+")
    rec.add_argument("--drift", action="store_true")
    rec.add_argument("--summary", default="manual entry")
    rec.add_argument("--notes", default="")
    rec.add_argument("--audit-dir", default=DEFAULT_AUDIT_DIR)

    # list
    lst = audit_sub.add_parser("list", help="List audit entries")
    lst.add_argument("--audit-dir", default=DEFAULT_AUDIT_DIR)

    # show
    shw = audit_sub.add_parser("show", help="Show a single audit entry")
    shw.add_argument("path")
