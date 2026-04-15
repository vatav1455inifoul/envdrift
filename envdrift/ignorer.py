"""Support for .envdriftignore files — keys to exclude from drift checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

DEFAULT_IGNORE_FILE = ".envdriftignore"


def load_ignore_patterns(path: str | Path | None = None) -> list[str]:
    """Load key patterns from an ignore file. Returns empty list if file missing."""
    target = Path(path) if path else Path(DEFAULT_IGNORE_FILE)
    if not target.exists():
        return []
    patterns = []
    for line in target.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _pattern_matches(pattern: str, key: str) -> bool:
    """Match a key against a glob-style pattern (only * wildcard supported)."""
    regex = re.escape(pattern).replace(r"\*", ".*")
    return bool(re.fullmatch(regex, key, flags=re.IGNORECASE))


def should_ignore(key: str, patterns: Iterable[str]) -> bool:
    """Return True if the key matches any ignore pattern."""
    return any(_pattern_matches(p, key) for p in patterns)


def filter_keys(
    env: dict[str, str], patterns: Iterable[str]
) -> dict[str, str]:
    """Return a copy of env with ignored keys removed."""
    plist = list(patterns)
    return {k: v for k, v in env.items() if not should_ignore(k, plist)}
