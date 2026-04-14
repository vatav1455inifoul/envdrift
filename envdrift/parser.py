"""Parser for .env files — handles reading and tokenizing key-value pairs."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_PATTERN = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$'
)
COMMENT_PATTERN = re.compile(r'^\s*#.*$')


def parse_env_file(filepath: str | Path) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dict of key -> value pairs.

    - Strips inline comments (values after unquoted #)
    - Handles quoted values (single and double quotes)
    - Skips blank lines and comment lines
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {filepath}")

    result: Dict[str, Optional[str]] = {}

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            if not line.strip() or COMMENT_PATTERN.match(line):
                continue

            match = ENV_LINE_PATTERN.match(line)
            if not match:
                continue

            key = match.group("key")
            raw_value = match.group("value").strip()
            result[key] = _clean_value(raw_value)

    return result


def _clean_value(raw: str) -> Optional[str]:
    """Strip quotes and inline comments from a raw env value."""
    if not raw:
        return ""

    # Handle quoted values
    if (raw.startswith('"') and raw.endswith('"')) or \
       (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]

    # Strip inline comment
    comment_idx = raw.find(" #")
    if comment_idx != -1:
        raw = raw[:comment_idx].strip()

    return raw
