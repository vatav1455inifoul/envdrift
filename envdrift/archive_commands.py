"""CLI sub-commands for the archive feature."""

import sys
from pathlib import Path
from envdrift.archiver import (
    create_archive,
    extract_archive,
    load_archive_meta,
    list_archives,
)


def cmd_archive_save(args) -> int:
    """envdrift archive save <env_files…> [--name NAME] [--notes NOTES]"""
    paths = args.envfiles
    missing = [p for p in paths if not Path(p).exists()]
    if missing:
        for m in missing:
            print(f"[error] file not found: {m}", file=sys.stderr)
        return 1

    dest = create_archive(paths, name=getattr(args, "name", ""), notes=getattr(args, "notes", ""))
    print(f"Archive saved: {dest}")
    return 0


def cmd_archive_extract(args) -> int:
    """envdrift archive extract <name> --dest DIR"""
    try:
        files = extract_archive(args.name, args.dest)
        print(f"Extracted {len(files)} file(s) to {args.dest}:")
        for f in files:
            print(f"  {f}")
        return 0
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1


def cmd_archive_list(args) -> int:  # noqa: ARG001
    """envdrift archive list"""
    names = list_archives()
    if not names:
        print("No archives found.")
        return 0
    for name in names:
        print(name)
    return 0


def cmd_archive_info(args) -> int:
    """envdrift archive info <name>"""
    try:
        meta = load_archive_meta(args.name)
        print(f"Name    : {meta['name']}")
        print(f"Created : {meta['created_at']}")
        if meta.get("notes"):
            print(f"Notes   : {meta['notes']}")
        print("Files   :")
        for f in meta["files"]:
            print(f"  {f}")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1


def register_archive_subcommand(subparsers) -> None:
    p = subparsers.add_parser("archive", help="Archive and restore .env files")
    sub = p.add_subparsers(dest="archive_cmd")

    save_p = sub.add_parser("save", help="Save env files into a compressed archive")
    save_p.add_argument("envfiles", nargs="+")
    save_p.add_argument("--name", default="")
    save_p.add_argument("--notes", default="")

    ext_p = sub.add_parser("extract", help="Extract an archive")
    ext_p.add_argument("name")
    ext_p.add_argument("--dest", default=".")

    sub.add_parser("list", help="List all archives")

    info_p = sub.add_parser("info", help="Show archive metadata")
    info_p.add_argument("name")
