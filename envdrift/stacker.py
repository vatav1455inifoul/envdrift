"""stacker.py — merge multiple .env files in priority order (last wins).

Useful for layered config patterns like:
  base.env  <  staging.env  <  local.env
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdrift.parser import parse_env_file


@dataclass
class StackResult:
    """Result of stacking multiple env files."""
    env_names: List[str]
    merged: Dict[str, str]
    # key -> list of (env_name, value) for every layer that defined it
    provenance: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    @property
    def total_keys(self) -> int:
        return len(self.merged)

    @property
    def overridden_keys(self) -> List[str]:
        """Keys that appeared in more than one layer."""
        return sorted(k for k, layers in self.provenance.items() if len(layers) > 1)

    @property
    def unique_keys(self) -> List[str]:
        """Keys that appeared in exactly one layer."""
        return sorted(k for k, layers in self.provenance.items() if len(layers) == 1)


def stack_envs(paths: List[str], names: List[str] | None = None) -> StackResult:
    """Stack env files in order; later files override earlier ones.

    Args:
        paths: ordered list of .env file paths (lowest to highest priority).
        names: optional display names; defaults to the file paths.

    Returns:
        StackResult with merged values and full provenance.
    """
    if len(paths) < 1:
        raise ValueError("stack_envs requires at least one env file")

    env_names = names if names else list(paths)
    merged: Dict[str, str] = {}
    provenance: Dict[str, List[Tuple[str, str]]] = {}

    for name, path in zip(env_names, paths):
        parsed = parse_env_file(path)
        for key, value in parsed.items():
            merged[key] = value
            provenance.setdefault(key, []).append((name, value))

    return StackResult(
        env_names=env_names,
        merged=merged,
        provenance=provenance,
    )


def winning_layer(result: StackResult, key: str) -> str | None:
    """Return the name of the env layer whose value 'won' for *key*."""
    layers = result.provenance.get(key)
    if not layers:
        return None
    return layers[-1][0]
