"""referencer.py – find which keys are referenced by other keys' values.

Some .env files use shell-style variable references like:
    BASE_URL=https://example.com
    API_URL=${BASE_URL}/api

This module resolves which keys are "consumers" (reference others) and
which are "providers" (referenced by others), and flags any dangling
references where the referenced key is absent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class ReferenceResult:
    env_name: str
    # key -> list of keys it references
    consumers: Dict[str, List[str]] = field(default_factory=dict)
    # key -> list of keys that reference it
    providers: Dict[str, List[str]] = field(default_factory=dict)
    # references that point to a key not present in the env
    dangling: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def has_dangling(self) -> bool:
        return bool(self.dangling)

    @property
    def all_referenced_keys(self) -> Set[str]:
        refs: Set[str] = set()
        for targets in self.consumers.values():
            refs.update(targets)
        return refs


def _extract_refs(value: str) -> List[str]:
    """Return all variable names referenced inside *value*."""
    refs: List[str] = []
    for m in _REF_RE.finditer(value):
        refs.append(m.group(1) or m.group(2))
    return refs


def analyse_references(env: Dict[str, str], env_name: str = "env") -> ReferenceResult:
    """Analyse variable references within a single env mapping."""
    result = ReferenceResult(env_name=env_name)

    for key, value in env.items():
        refs = _extract_refs(value)
        if not refs:
            continue
        result.consumers[key] = refs
        for ref in refs:
            result.providers.setdefault(ref, []).append(key)
            if ref not in env:
                result.dangling.setdefault(key, []).append(ref)

    return result
