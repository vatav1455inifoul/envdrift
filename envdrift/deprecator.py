"""Detect deprecated keys in .env files based on a deprecation map."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
from pathlib import Path


@dataclass
class DeprecationWarning_:
    key: str
    message: str
    replacement: Optional[str] = None


@dataclass
class DeprecationResult:
    env_name: str
    warnings: List[DeprecationWarning_] = field(default_factory=list)

    def has_warnings(self) -> bool:
        return bool(self.warnings)

    def keys(self) -> List[str]:
        return [w.key for w in self.warnings]


def load_deprecation_map(path: str | Path) -> Dict[str, dict]:
    """Load a JSON deprecation map.

    Format::

        {
          "OLD_KEY": {"message": "Use NEW_KEY", "replacement": "NEW_KEY"},
          "LEGACY_KEY": {"message": "No longer used"}
        }
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Deprecation map not found: {p}")
    with p.open() as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Deprecation map must be a JSON object")
    return data


def check_deprecations(
    env: Dict[str, str],
    deprecation_map: Dict[str, dict],
    env_name: str = "env",
) -> DeprecationResult:
    """Check *env* for keys listed in *deprecation_map*."""
    result = DeprecationResult(env_name=env_name)
    for key in env:
        if key in deprecation_map:
            entry = deprecation_map[key]
            result.warnings.append(
                DeprecationWarning_(
                    key=key,
                    message=entry.get("message", "Deprecated key"),
                    replacement=entry.get("replacement"),
                )
            )
    return result
