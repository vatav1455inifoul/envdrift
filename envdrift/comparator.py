"""Comparator — diffs two parsed env dicts and categorises the drift."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DriftResult:
    """Holds the full drift report between two env snapshots."""

    base_label: str
    target_label: str
    missing_keys: List[str] = field(default_factory=list)   # in base, not in target
    extra_keys: List[str] = field(default_factory=list)     # in target, not in base
    changed_keys: Dict[str, tuple] = field(default_factory=dict)  # key -> (base_val, target_val)

    @property
    def has_drift(self) -> bool:
        return bool(self.missing_keys or self.extra_keys or self.changed_keys)

    @property
    def summary(self) -> str:
        parts = []
        if self.missing_keys:
            parts.append(f"{len(self.missing_keys)} missing")
        if self.extra_keys:
            parts.append(f"{len(self.extra_keys)} extra")
        if self.changed_keys:
            parts.append(f"{len(self.changed_keys)} changed")
        return ", ".join(parts) if parts else "no drift"


def compare_envs(
    base: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
    base_label: str = "base",
    target_label: str = "target",
    ignore_values: bool = False,
) -> DriftResult:
    """
    Compare two env dicts and return a DriftResult.

    Args:
        base: The reference env (e.g. .env.example)
        target: The env being checked (e.g. .env.production)
        base_label: Human-readable name for base
        target_label: Human-readable name for target
        ignore_values: If True, only check key presence, not values
    """
    result = DriftResult(base_label=base_label, target_label=target_label)

    base_keys = set(base.keys())
    target_keys = set(target.keys())

    result.missing_keys = sorted(base_keys - target_keys)
    result.extra_keys = sorted(target_keys - base_keys)

    if not ignore_values:
        for key in base_keys & target_keys:
            if base[key] != target[key]:
                result.changed_keys[key] = (base[key], target[key])

    return result
