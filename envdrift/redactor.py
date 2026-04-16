"""Redact sensitive keys from env data before display or export."""

import re
from typing import Dict, List

DEFAULT_PATTERNS = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
]

REDACTED = "[REDACTED]"


def load_redact_patterns(path: str | None = None) -> List[str]:
    """Load redact patterns from a file, falling back to defaults."""
    if path is None:
        return list(DEFAULT_PATTERNS)
    try:
        with open(path) as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        return lines if lines else list(DEFAULT_PATTERNS)
    except FileNotFoundError:
        return list(DEFAULT_PATTERNS)


def _is_sensitive(key: str, patterns: List[str]) -> bool:
    key_upper = key.upper()
    return any(re.fullmatch(p, key_upper) for p in patterns)


def redact_env(env: Dict[str, str], patterns: List[str] | None = None) -> Dict[str, str]:
    """Return a copy of env with sensitive values replaced by REDACTED."""
    if patterns is None:
        patterns = DEFAULT_PATTERNS
    return {k: (REDACTED if _is_sensitive(k, patterns) else v) for k, v in env.items()}


def redact_keys(keys: List[str], patterns: List[str] | None = None) -> Dict[str, bool]:
    """Return a mapping of key -> is_sensitive for a list of keys."""
    if patterns is None:
        patterns = DEFAULT_PATTERNS
    return {k: _is_sensitive(k, patterns) for k in keys}
