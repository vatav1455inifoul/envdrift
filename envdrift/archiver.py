"""Archive and restore .env file snapshots to/from a compressed tarball."""

import tarfile
import json
import io
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List

ARCHIVE_DIR = Path(".envdrift") / "archives"


def _archive_path(name: str) -> Path:
    return ARCHIVE_DIR / f"{name}.tar.gz"


def create_archive(env_paths: List[str], name: str = "", notes: str = "") -> Path:
    """Bundle one or more .env files into a compressed archive with metadata."""
    if not name:
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    dest = _archive_path(name)
    dest.parent.mkdir(parents=True, exist_ok=True)

    meta = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
        "files": [str(p) for p in env_paths],
    }
    meta_bytes = json.dumps(meta, indent=2).encode()

    with tarfile.open(dest, "w:gz") as tar:
        # add metadata
        info = tarfile.TarInfo(name="meta.json")
        info.size = len(meta_bytes)
        tar.addfile(info, io.BytesIO(meta_bytes))

        for path in env_paths:
            tar.add(path, arcname=os.path.basename(path))

    return dest


def extract_archive(name: str, dest_dir: str) -> List[str]:
    """Extract an archive into dest_dir, returning list of extracted file paths."""
    src = _archive_path(name)
    if not src.exists():
        raise FileNotFoundError(f"Archive not found: {src}")

    out = Path(dest_dir)
    out.mkdir(parents=True, exist_ok=True)

    extracted = []
    with tarfile.open(src, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name == "meta.json":
                continue
            tar.extract(member, path=out)
            extracted.append(str(out / member.name))

    return extracted


def load_archive_meta(name: str) -> dict:
    """Return the metadata stored inside an archive."""
    src = _archive_path(name)
    if not src.exists():
        raise FileNotFoundError(f"Archive not found: {src}")

    with tarfile.open(src, "r:gz") as tar:
        f = tar.extractfile("meta.json")
        if f is None:
            raise ValueError("Archive is missing meta.json")
        return json.loads(f.read())


def list_archives() -> List[str]:
    """Return sorted list of archive names (without extension)."""
    if not ARCHIVE_DIR.exists():
        return []
    return sorted(p.stem for p in ARCHIVE_DIR.glob("*.tar.gz"))
