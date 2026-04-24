"""Chain diff: compare a sequence of env files in order (v1→v2→v3…)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from envdrift.comparator import compare_envs, DriftResult
from envdrift.parser import parse_env_file


@dataclass
class ChainLink:
    """Drift between two consecutive environments in the chain."""
    from_name: str
    to_name: str
    result: DriftResult

    @property
    def has_drift(self) -> bool:
        return (
            bool(self.result.missing_keys)
            or bool(self.result.extra_keys)
            or bool(self.result.changed_values)
        )


@dataclass
class ChainResult:
    """Full chain diff across all consecutive pairs."""
    env_names: List[str]
    links: List[ChainLink] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return any(link.has_drift for link in self.links)

    @property
    def drifting_links(self) -> List[ChainLink]:
        return [link for link in self.links if link.has_drift]

    @property
    def stable_links(self) -> List[ChainLink]:
        return [link for link in self.links if not link.has_drift]

    def summary(self) -> Dict[str, int]:
        total_missing = sum(len(l.result.missing_keys) for l in self.links)
        total_extra = sum(len(l.result.extra_keys) for l in self.links)
        total_changed = sum(len(l.result.changed_values) for l in self.links)
        return {
            "links": len(self.links),
            "drifting_links": len(self.drifting_links),
            "total_missing": total_missing,
            "total_extra": total_extra,
            "total_changed": total_changed,
        }


def chain_diff(
    env_paths: List[Tuple[str, str]],
    ignore_values: bool = False,
) -> ChainResult:
    """Compare env files in sequence.

    Args:
        env_paths: list of (name, path) tuples in chain order.
        ignore_values: if True only check key presence, not values.

    Returns:
        ChainResult with a ChainLink for every consecutive pair.
    """
    if len(env_paths) < 2:
        raise ValueError("chain_diff requires at least two environments")

    names = [name for name, _ in env_paths]
    result = ChainResult(env_names=names)

    for i in range(len(env_paths) - 1):
        from_name, from_path = env_paths[i]
        to_name, to_path = env_paths[i + 1]

        base = parse_env_file(from_path)
        target = parse_env_file(to_path)
        drift = compare_envs(base, target, ignore_values=ignore_values)

        result.links.append(ChainLink(
            from_name=from_name,
            to_name=to_name,
            result=drift,
        ))

    return result
