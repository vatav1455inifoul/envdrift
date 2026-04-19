"""Reporter for pairwise diff results with colored output."""
from envdrift.comparator import DriftResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_diff_report(result: DriftResult, env_a: str, env_b: str) -> str:
    lines = []
    lines.append(_c(f"\n=== Diff: {env_a} vs {env_b} ===", "1;34"))

    if not result.has_drift():
        lines.append(_c("  No drift detected.", "32"))
        return "\n".join(lines)

    if result.missing_keys:
        lines.append(_c(f"\n  Missing in {env_b}:", "1;33"))
        for k in sorted(result.missing_keys):
            lines.append(f"    - {_c(k, '33')}")

    if result.extra_keys:
        lines.append(_c(f"\n  Extra in {env_b}:", "1;36"))
        for k in sorted(result.extra_keys):
            lines.append(f"    + {_c(k, '36')}")

    if result.changed_values:
        lines.append(_c("\n  Changed values:", "1;31"))
        for k, (va, vb) in sorted(result.changed_values.items()):
            lines.append(f"    ~ {_c(k, '31')}")
            lines.append(f"        {env_a}: {_c(repr(va), '90')}")
            lines.append(f"        {env_b}: {_c(repr(vb), '90')}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def print_diff_report(result: DriftResult, env_a: str, env_b: str) -> None:
    print(format_diff_report(result, env_a, env_b))
