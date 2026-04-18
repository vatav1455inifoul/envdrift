"""Sort and organize .env keys alphabetically or by group."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

from envdrift.parser import parse_env_file


@dataclass
class SortResult:
    env_name: str
    original_order: List[str]
    sorted_order: List[str]
    values: Dict[str, str]

    @property
    def is_sorted(self) -> bool:
        return self.original_order == self.sorted_order

    @property
    def moved_keys(self) -> List[str]:
        return [
            k for i, k in enumerate(self.sorted_order)
            if self.original_order.index(k) != i
        ]


def sort_env(path: str, env_name: str | None = None) -> SortResult:
    """Parse an env file and return a SortResult with ordering info."""
    name = env_name or path
    data = parse_env_file(path)
    original = list(data.keys())
    sorted_keys = sorted(original, key=str.lower)
    return SortResult(
        env_name=name,
        original_order=original,
        sorted_order=sorted_keys,
        values=data,
    )


def render_sorted(result: SortResult) -> str:
    """Render sorted env content as a string."""
    lines = []
    for key in result.sorted_order:
        val = result.values[key]
        if " " in val or val == "":
            lines.append(f'{key}="{val}"')
        else:
            lines.append(f"{key}={val}")
    return "\n".join(lines) + "\n"


def write_sorted(result: SortResult, path: str) -> None:
    """Write sorted env content back to a file."""
    with open(path, "w") as fh:
        fh.write(render_sorted(result))
