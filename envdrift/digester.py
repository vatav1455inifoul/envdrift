"""digester.py – compute and compare content hashes for .env files."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from envdrift.parser import parse_env_file


@dataclass
class DigestResult:
    env_name: str
    path: str
    file_hash: str          # SHA-256 of raw file bytes
    content_hash: str       # SHA-256 of sorted key=value pairs (ignores comments/whitespace)
    key_count: int
    key_hashes: Dict[str, str] = field(default_factory=dict)  # per-key value hashes


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def digest_file(path: str, env_name: Optional[str] = None) -> DigestResult:
    """Compute hashes for a single .env file."""
    p = Path(path)
    name = env_name or p.stem

    raw = p.read_bytes()
    file_hash = hashlib.sha256(raw).hexdigest()

    pairs = parse_env_file(path)
    # content hash: deterministic over key=value pairs regardless of file order
    canonical = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    content_hash = _sha256(canonical)

    key_hashes = {k: _sha256(v) for k, v in pairs.items()}

    return DigestResult(
        env_name=name,
        path=str(p.resolve()),
        file_hash=file_hash,
        content_hash=content_hash,
        key_count=len(pairs),
        key_hashes=key_hashes,
    )


def digests_match(a: DigestResult, b: DigestResult, *, strict: bool = False) -> bool:
    """Return True when two digests represent identical content.

    strict=False  → compare content_hash (ignores comments/whitespace)
    strict=True   → compare file_hash (byte-for-byte identical)
    """
    if strict:
        return a.file_hash == b.file_hash
    return a.content_hash == b.content_hash


def changed_keys(a: DigestResult, b: DigestResult) -> Dict[str, tuple]:
    """Return keys whose value hash differs between two digests.
    Returns {key: (hash_a, hash_b)}; missing side uses None.
    """
    all_keys = set(a.key_hashes) | set(b.key_hashes)
    result = {}
    for k in sorted(all_keys):
        ha = a.key_hashes.get(k)
        hb = b.key_hashes.get(k)
        if ha != hb:
            result[k] = (ha, hb)
    return result


def digest_to_dict(d: DigestResult) -> dict:
    return {
        "env_name": d.env_name,
        "path": d.path,
        "file_hash": d.file_hash,
        "content_hash": d.content_hash,
        "key_count": d.key_count,
        "key_hashes": d.key_hashes,
    }
