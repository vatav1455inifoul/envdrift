"""Detect and remove unused keys from an env file relative to a reference."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdrift.parser import parse_env_file


@dataclass
class TrimResult:
    env_name: str
    reference_name: str
    all_keys: List[str]
    unused_keys: List[str]
    kept_env: Dict[str, str]


def has_unused(result: TrimResult) -> bool:
    return len(result.unused_keys) > 0


def trim_env(
    env_path: str,
    reference_path: str,
    env_name: str = "",
    reference_name: str = "",
) -> TrimResult:
    """Return keys present in env_path but absent from reference_path."""
    env = parse_env_file(env_path)
    reference = parse_env_file(reference_path)

    env_name = env_name or env_path
    reference_name = reference_name or reference_path

    unused = [k for k in env if k not in reference]
    kept = {k: v for k, v in env.items() if k in reference}

    return TrimResult(
        env_name=env_name,
        reference_name=reference_name,
        all_keys=list(env.keys()),
        unused_keys=unused,
        kept_env=kept,
    )


def render_trimmed(result: TrimResult) -> str:
    """Render the kept env as .env file text."""
    lines = []
    for k, v in result.kept_env.items():
        lines.append(f"{k}={v}")
    return "\n".join(lines) + ("\n" if lines else "")
