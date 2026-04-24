"""compactor.py – remove redundant/overridden keys from a stacked env.

When multiple .env layers are stacked, earlier layers may define keys
that are fully overridden by later layers.  The compactor identifies
those shadowed keys so users can clean up lower-priority files.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from envdrift.parser import parse_env_file


@dataclass
class CompactResult:
    """Result of a compaction analysis across layered env files."""

    # file path -> list of keys that are shadowed by a later layer
    shadowed: Dict[str, List[str]] = field(default_factory=dict)
    # final resolved key->value after stacking all layers
    resolved: Dict[str, str] = field(default_factory=dict)
    # ordered list of (path, parsed_env) tuples used during analysis
    layers: List[Tuple[str, Dict[str, str]]] = field(default_factory=list)

    @property
    def has_shadowed(self) -> bool:
        return any(keys for keys in self.shadowed.values())

    @property
    def total_shadowed(self) -> int:
        return sum(len(v) for v in self.shadowed.values())


def compact_envs(paths: Sequence[str | Path]) -> CompactResult:
    """Analyse *paths* as ordered env layers (first = lowest priority).

    Returns a :class:`CompactResult` describing which keys in earlier
    layers are completely overridden by a later layer.
    """
    if not paths:
        raise ValueError("compact_envs requires at least one path")

    layers: List[Tuple[str, Dict[str, str]]] = []
    for p in paths:
        parsed = parse_env_file(str(p))
        layers.append((str(p), parsed))

    # Build the final resolved env (last layer wins)
    resolved: Dict[str, str] = {}
    for _, env in layers:
        resolved.update(env)

    # For each layer except the last, find keys overridden by any later layer
    shadowed: Dict[str, List[str]] = {}
    for idx, (path, env) in enumerate(layers[:-1]):
        later_keys: set[str] = set()
        for _, later_env in layers[idx + 1 :]:
            later_keys.update(later_env.keys())
        overridden = sorted(k for k in env if k in later_keys)
        shadowed[path] = overridden

    # Last layer shadows nothing
    last_path = layers[-1][0]
    if last_path not in shadowed:
        shadowed[last_path] = []

    return CompactResult(shadowed=shadowed, resolved=resolved, layers=layers)


def render_compact_summary(result: CompactResult) -> str:
    """Return a human-readable summary of shadowed keys per layer."""
    lines: List[str] = []
    for path, keys in result.shadowed.items():
        if keys:
            lines.append(f"  {path}: {len(keys)} shadowed key(s)")
            for k in keys:
                lines.append(f"    - {k}")
        else:
            lines.append(f"  {path}: no shadowed keys")
    return "\n".join(lines)
