"""Reporter for chain diff results."""
from __future__ import annotations

from envdrift.differ_chain import ChainResult, ChainLink


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _format_link(link: ChainLink) -> str:
    lines: list[str] = []
    arrow = f"  {link.from_name} → {link.to_name}"
    if not link.has_drift:
        lines.append(_c(arrow + "  ✓ no drift", "32"))
        return "\n".join(lines)

    lines.append(_c(arrow, "33"))

    if link.result.missing_keys:
        lines.append(_c("    missing keys:", "31"))
        for k in sorted(link.result.missing_keys):
            lines.append(f"      - {k}")

    if link.result.extra_keys:
        lines.append(_c("    extra keys:", "36"))
        for k in sorted(link.result.extra_keys):
            lines.append(f"      + {k}")

    if link.result.changed_values:
        lines.append(_c("    changed values:", "35"))
        for k, (old, new) in sorted(link.result.changed_values.items()):
            lines.append(f"      ~ {k}: {old!r} → {new!r}")

    return "\n".join(lines)


def format_chain_report(result: ChainResult) -> str:
    lines: list[str] = []
    chain_str = " → ".join(result.env_names)
    lines.append(_c(f"Chain diff: {chain_str}", "1"))
    lines.append("")

    for link in result.links:
        lines.append(_format_link(link))

    lines.append("")
    s = result.summary()
    if not result.has_drift:
        lines.append(_c("All links clean — no drift detected.", "32"))
    else:
        lines.append(
            _c(
                f"{s['drifting_links']}/{s['links']} link(s) drifting  "
                f"(missing={s['total_missing']}, extra={s['total_extra']}, "
                f"changed={s['total_changed']})",
                "33",
            )
        )

    return "\n".join(lines)


def print_chain_report(result: ChainResult) -> None:
    print(format_chain_report(result))
