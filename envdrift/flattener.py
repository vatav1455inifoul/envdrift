"""Flatten nested or prefixed env keys into a structured dict of groups with stats."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FlattenResult:
    env_name: str
    keys: List[str]
    flat: Dict[str, str]  # key -> value
    overrides: Dict[str, List[str]]  # key -> list of raw keys that mapped to it


def has_overrides(result: FlattenResult) -> bool:
    return any(len(v) > 1 for v in result.overrides.values())


def override_keys(result: FlattenResult) -> List[str]:
    return [k for k, v in result.overrides.items() if len(v) > 1]


def _strip_prefix(key: str, prefix: str) -> str:
    """Remove a leading prefix (case-insensitive) and return normalised key."""
    if prefix and key.upper().startswith(prefix.upper()):
        return key[len(prefix):].lstrip("_")
    return key


def flatten_env(
    env: Dict[str, str],
    env_name: str = "env",
    strip_prefix: str = "",
    lowercase: bool = True,
) -> FlattenResult:
    """Flatten an env dict by optionally stripping a prefix and normalising case.

    When two source keys collapse to the same flat key the last one wins;
    all collisions are recorded in *overrides*.
    """
    flat: Dict[str, str] = {}
    overrides: Dict[str, List[str]] = {}

    for raw_key, value in env.items():
        normalised = _strip_prefix(raw_key, strip_prefix)
        if lowercase:
            normalised = normalised.lower()

        overrides.setdefault(normalised, []).append(raw_key)
        flat[normalised] = value

    return FlattenResult(
        env_name=env_name,
        keys=list(flat.keys()),
        flat=flat,
        overrides=overrides,
    )
