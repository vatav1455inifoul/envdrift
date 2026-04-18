"""Annotate .env keys with inline comments describing their drift status."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdrift.parser import parse_env_file
from envdrift.comparator import compare_envs


@dataclass
class AnnotatedLine:
    key: str
    value: str
    annotation: str = ""

    def render(self) -> str:
        line = f"{self.key}={self.value}"
        if self.annotation:
            line += f"  # [envdrift] {self.annotation}"
        return line


@dataclass
class AnnotationResult:
    env_name: str
    lines: List[AnnotatedLine] = field(default_factory=list)

    def render(self) -> str:
        return "\n".join(ln.render() for ln in self.lines)


def annotate_env(
    env_path: str,
    reference_path: str,
    env_name: str = "env",
    ref_name: str = "ref",
) -> AnnotationResult:
    """Compare env_path against reference_path and return annotated lines."""
    env = parse_env_file(env_path)
    ref = parse_env_file(reference_path)
    drift = compare_envs(env_name, env, ref_name, ref)

    missing = set(drift.missing_keys)
    extra = set(drift.extra_keys)
    changed = {k for k, _, _ in drift.changed_values}

    lines: List[AnnotatedLine] = []
    for key, value in env.items():
        if key in changed:
            ref_val = next(r for k, _, r in drift.changed_values if k == key)
            annotation = f"CHANGED (ref={ref_val!r})"
        elif key in extra:
            annotation = "EXTRA (not in reference)"
        else:
            annotation = ""
        lines.append(AnnotatedLine(key=key, value=value, annotation=annotation))

    for key in missing:
        lines.append(AnnotatedLine(key=key, value="", annotation="MISSING"))

    return AnnotationResult(env_name=env_name, lines=lines)


def write_annotated(result: AnnotationResult, output_path: str) -> None:
    """Write annotated env content to a file."""
    with open(output_path, "w") as f:
        f.write(result.render())
        f.write("\n")
