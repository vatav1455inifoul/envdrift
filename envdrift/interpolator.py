"""Detect and report variable interpolation references in .env files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)")


@dataclass
class InterpolationResult:
    env_name: str
    references: Dict[str, List[str]] = field(default_factory=dict)  # key -> [refs]
    unresolved: Dict[str, List[str]] = field(default_factory=dict)  # key -> [missing refs]

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved)

    @property
    def all_referenced_keys(self) -> Set[str]:
        refs: Set[str] = set()
        for v in self.references.values():
            refs.update(v)
        return refs


def _extract_refs(value: str) -> List[str]:
    """Return all variable names referenced in *value*."""
    found = []
    for m in _REF_RE.finditer(value):
        found.append(m.group(1) or m.group(2))
    return found


def check_interpolation(env: Dict[str, str], env_name: str = "env") -> InterpolationResult:
    """Analyse *env* for interpolation references and flag unresolved ones."""
    result = InterpolationResult(env_name=env_name)
    for key, value in env.items():
        refs = _extract_refs(value)
        if refs:
            result.references[key] = refs
            missing = [r for r in refs if r not in env]
            if missing:
                result.unresolved[key] = missing
    return result
