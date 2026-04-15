"""Merge multiple .env files into a unified template with all known keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envdrift.parser import parse_env_file


@dataclass
class MergeResult:
    """Result of merging multiple env files."""

    keys: List[str]  # ordered list of all unique keys
    sources: Dict[str, str]  # key -> which env first defined it
    values: Dict[str, Optional[str]]  # key -> value from primary env (or first found)
    missing_in: Dict[str, List[str]]  # key -> list of env names that lack it
    env_names: List[str]

    @property
    def complete_keys(self) -> Set[str]:
        """Keys present in every env."""
        return {k for k, absent in self.missing_in.items() if not absent}

    @property
    def partial_keys(self) -> Set[str]:
        """Keys missing in at least one env."""
        return {k for k, absent in self.missing_in.items() if absent}


def merge_envs(
    env_paths: Dict[str, str],
    primary: Optional[str] = None,
) -> MergeResult:
    """
    Merge env files from *env_paths* (name -> path) into a MergeResult.

    Parameters
    ----------
    env_paths:
        Mapping of environment name to file path.
    primary:
        Name of the env whose values take precedence in ``values``.
        Defaults to the first key in *env_paths*.
    """
    if len(env_paths) < 1:
        raise ValueError("At least one env file is required for merging.")

    env_names = list(env_paths.keys())
    primary = primary or env_names[0]
    if primary not in env_paths:
        raise ValueError(f"Primary env '{primary}' not found in env_paths.")

    parsed: Dict[str, Dict[str, str]] = {
        name: parse_env_file(path) for name, path in env_paths.items()
    }

    # Collect all keys preserving insertion order (primary first)
    seen: Dict[str, str] = {}  # key -> first-seen env name
    for name in [primary] + [n for n in env_names if n != primary]:
        for key in parsed[name]:
            if key not in seen:
                seen[key] = name

    keys = list(seen.keys())
    sources = seen

    values: Dict[str, Optional[str]] = {}
    for key in keys:
        values[key] = parsed[primary].get(key, None)

    missing_in: Dict[str, List[str]] = {}
    for key in keys:
        missing_in[key] = [name for name in env_names if key not in parsed[name]]

    return MergeResult(
        keys=keys,
        sources=sources,
        values=values,
        missing_in=missing_in,
        env_names=env_names,
    )


def render_template(result: MergeResult, placeholder: str = "") -> str:
    """Render a merged .env template string with all known keys."""
    lines: List[str] = []
    for key in result.keys:
        value = result.values.get(key)
        if value is None:
            value = placeholder
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"
