"""Profile an .env file: compute key statistics and value patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envdrift.parser import parse_env_file


@dataclass
class ProfileResult:
    env_file: str
    total_keys: int
    empty_values: List[str] = field(default_factory=list)
    numeric_values: List[str] = field(default_factory=list)
    url_values: List[str] = field(default_factory=list)
    boolean_values: List[str] = field(default_factory=list)
    long_values: List[str] = field(default_factory=list)  # >100 chars
    key_lengths: Dict[str, int] = field(default_factory=dict)

    @property
    def empty_count(self) -> int:
        return len(self.empty_values)

    @property
    def fill_rate(self) -> float:
        if self.total_keys == 0:
            return 0.0
        return round((self.total_keys - self.empty_count) / self.total_keys * 100, 1)


_URL_RE = re.compile(r'^https?://', re.IGNORECASE)
_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}


def profile_env(path: str) -> ProfileResult:
    """Parse *path* and return a ProfileResult with key statistics."""
    data = parse_env_file(path)
    result = ProfileResult(env_file=path, total_keys=len(data))

    for key, value in data.items():
        result.key_lengths[key] = len(value)

        if value == "":
            result.empty_values.append(key)
        if value.lstrip("-").replace(".", "", 1).isdigit():
            result.numeric_values.append(key)
        if _URL_RE.match(value):
            result.url_values.append(key)
        if value.lower() in _BOOL_VALUES:
            result.boolean_values.append(key)
        if len(value) > 100:
            result.long_values.append(key)

    return result
