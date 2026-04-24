"""Fuzzy key matching — find likely renamed or misspelled keys across envs."""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


DEFAULT_THRESHOLD = 0.75


@dataclass
class FuzzyMatch:
    key_a: str
    key_b: str
    score: float

    def __str__(self) -> str:
        return f"{self.key_a!r} ~ {self.key_b!r} ({self.score:.0%})"


@dataclass
class FuzzyResult:
    env_a: str
    env_b: str
    matches: List[FuzzyMatch] = field(default_factory=list)
    unmatched_a: List[str] = field(default_factory=list)
    unmatched_b: List[str] = field(default_factory=list)

    @property
    def has_suggestions(self) -> bool:
        return bool(self.matches)


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _best_match(key: str, candidates: List[str], threshold: float) -> Optional[Tuple[str, float]]:
    best: Optional[Tuple[str, float]] = None
    for candidate in candidates:
        score = _similarity(key, candidate)
        if score >= threshold and (best is None or score > best[1]):
            best = (candidate, score)
    return best


def fuzzy_diff(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    name_a: str = "env_a",
    name_b: str = "env_b",
    threshold: float = DEFAULT_THRESHOLD,
) -> FuzzyResult:
    """Find fuzzy matches between keys that exist in one env but not the other."""
    keys_a = set(env_a)
    keys_b = set(env_b)

    only_a = sorted(keys_a - keys_b)
    only_b = sorted(keys_b - keys_a)

    result = FuzzyResult(env_a=name_a, env_b=name_b)
    matched_b: set[str] = set()

    for key in only_a:
        remaining_b = [k for k in only_b if k not in matched_b]
        hit = _best_match(key, remaining_b, threshold)
        if hit:
            matched_key, score = hit
            result.matches.append(FuzzyMatch(key_a=key, key_b=matched_key, score=score))
            matched_b.add(matched_key)
        else:
            result.unmatched_a.append(key)

    result.unmatched_b = [k for k in only_b if k not in matched_b]
    return result
