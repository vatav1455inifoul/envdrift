"""Clone an env file to a new target, optionally filtering or redacting keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdrift.parser import parse_env_file
from envdrift.redactor import load_redact_patterns, redact_env


@dataclass
class CloneResult:
    source: str
    target: str
    keys_written: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)
    redacted_keys: List[str] = field(default_factory=list)


def clone_env(
    source: str,
    target: str,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    redact: bool = False,
    redact_patterns_file: Optional[str] = None,
) -> CloneResult:
    """Read *source*, optionally filter/redact, write to *target*."""
    env = parse_env_file(source)
    result = CloneResult(source=source, target=target)

    if redact:
        patterns = load_redact_patterns(redact_patterns_file)
        redacted = redact_env(env, patterns)
        result.redacted_keys = [k for k in env if redacted.get(k) != env.get(k)]
        env = redacted

    filtered: Dict[str, str] = {}
    for key, value in env.items():
        if include is not None and key not in include:
            result.keys_skipped.append(key)
            continue
        if exclude is not None and key in exclude:
            result.keys_skipped.append(key)
            continue
        filtered[key] = value
        result.keys_written.append(key)

    _write_env(filtered, target)
    return result


def _write_env(env: Dict[str, str], path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}\n" for k, v in env.items()]
    out.write_text("".join(lines))
