"""digest_reporter.py – human-readable output for DigestResult comparisons."""
from __future__ import annotations

from typing import List

from envdrift.digester import DigestResult, changed_keys, digests_match


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_digest_report(
    digests: List[DigestResult],
    *,
    strict: bool = False,
    color: bool = True,
) -> str:
    lines: List[str] = []

    header = "Digest Report"
    lines.append(_c(header, "1;36") if color else header)
    lines.append("")

    for d in digests:
        label = f"  {d.env_name}  ({d.path})"
        lines.append(_c(label, "1") if color else label)
        lines.append(f"    file_hash   : {d.file_hash}")
        lines.append(f"    content_hash: {d.content_hash}")
        lines.append(f"    keys        : {d.key_count}")
        lines.append("")

    if len(digests) < 2:
        return "\n".join(lines)

    base = digests[0]
    for other in digests[1:]:
        match = digests_match(base, other, strict=strict)
        if match:
            msg = f"  ✔  {base.env_name} == {other.env_name}  (no content drift)"
            lines.append(_c(msg, "32") if color else msg)
        else:
            msg = f"  ✘  {base.env_name} != {other.env_name}  (content differs)"
            lines.append(_c(msg, "31") if color else msg)
            diffs = changed_keys(base, other)
            for key, (ha, hb) in diffs.items():
                if ha is None:
                    lines.append(f"      + {key}  (only in {other.env_name})")
                elif hb is None:
                    lines.append(f"      - {key}  (only in {base.env_name})")
                else:
                    lines.append(f"      ~ {key}  (value changed)")
        lines.append("")

    return "\n".join(lines)


def print_digest_report(
    digests: List[DigestResult],
    *,
    strict: bool = False,
    color: bool = True,
) -> None:
    print(format_digest_report(digests, strict=strict, color=color))
