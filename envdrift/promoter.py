"""Promote env values from one environment to another, flagging conflicts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envdrift.parser import parse_env_file


@dataclass
class PromoteResult:
    source_name: str
    target_name: str
    promoted: Dict[str, str] = field(default_factory=dict)   # keys copied over
    skipped: Dict[str, str] = field(default_factory=dict)    # keys already in target (no --force)
    conflicts: Dict[str, tuple] = field(default_factory=dict) # key -> (src_val, tgt_val)

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def total_promoted(self) -> int:
        return len(self.promoted)


def promote_env(
    source: str,
    target: str,
    source_name: str = "source",
    target_name: str = "target",
    keys: Optional[List[str]] = None,
    force: bool = False,
    dry_run: bool = False,
) -> PromoteResult:
    """Promote keys from source .env into target .env.

    Args:
        source: path to source .env file
        target: path to target .env file
        source_name: label for source
        target_name: label for target
        keys: if given, only promote these keys
        force: overwrite existing keys in target
        dry_run: do not write changes to disk
    """
    src = parse_env_file(source)
    tgt = parse_env_file(target)

    result = PromoteResult(source_name=source_name, target_name=target_name)

    candidates = {k: v for k, v in src.items() if keys is None or k in keys}

    merged = dict(tgt)
    for k, v in candidates.items():
        if k in tgt:
            if tgt[k] != v:
                result.conflicts[k] = (v, tgt[k])
            if not force:
                result.skipped[k] = v
                continue
        result.promoted[k] = v
        merged[k] = v

    if not dry_run and result.promoted:
        _write_env(target, merged)

    return result


def _write_env(path: str, env: Dict[str, str]) -> None:
    with open(path, "w") as fh:
        for k, v in env.items():
            fh.write(f"{k}={v}\n")
