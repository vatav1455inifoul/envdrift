"""Filter drift results by key patterns, severity, or environment names."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import List, Optional

from envdrift.comparator import DriftResult
from envdrift.differ import MultiDiffResult


@dataclass
class FilterOptions:
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    only_missing: bool = False
    only_extra: bool = False
    only_changed: bool = False


def _key_matches_any(key: str, patterns: List[str]) -> bool:
    return any(fnmatch(key, p) for p in patterns)


def _should_keep(key: str, opts: FilterOptions) -> bool:
    if opts.include_patterns and not _key_matches_any(key, opts.include_patterns):
        return False
    if opts.exclude_patterns and _key_matches_any(key, opts.exclude_patterns):
        return False
    return True


def filter_pair_drift(result: DriftResult, opts: FilterOptions) -> DriftResult:
    """Return a new DriftResult with keys filtered by opts."""
    missing = [
        k for k in result.missing_keys
        if _should_keep(k, opts) and not opts.only_extra and not opts.only_changed
    ]
    extra = [
        k for k in result.extra_keys
        if _should_keep(k, opts) and not opts.only_missing and not opts.only_changed
    ]
    changed = {
        k: v for k, v in result.changed_values.items()
        if _should_keep(k, opts) and not opts.only_missing and not opts.only_extra
    }
    return DriftResult(
        env_a=result.env_a,
        env_b=result.env_b,
        missing_keys=missing,
        extra_keys=extra,
        changed_values=changed,
    )


def filter_multi_drift(result: MultiDiffResult, opts: FilterOptions) -> MultiDiffResult:
    """Return a new MultiDiffResult with keys filtered by opts."""
    missing = {
        k: envs for k, envs in result.missing_in_some.items()
        if _should_keep(k, opts)
    }
    inconsistent = {
        k: vals for k, vals in result.inconsistent_keys.items()
        if _should_keep(k, opts)
    }
    return MultiDiffResult(
        env_names=result.env_names,
        missing_in_some=missing,
        inconsistent_keys=inconsistent,
    )
