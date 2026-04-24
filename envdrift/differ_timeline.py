"""Timeline analysis across multiple snapshots or audit records.

Builds a chronological view of how a key's value (or presence) has
changed over time, using the audit records stored by the auditor module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineEntry:
    """A single point in time for one key."""

    timestamp: str          # ISO-8601 string from the audit record
    audit_id: str           # identifier of the audit record
    env_name: str           # which env file was audited
    value: str | None       # None means the key was absent

    def __str__(self) -> str:  # pragma: no cover
        val = self.value if self.value is not None else "<absent>"
        return f"{self.timestamp}  [{self.env_name}]  {val}"


@dataclass
class KeyTimeline:
    """All recorded states for a single key."""

    key: str
    entries: list[TimelineEntry] = field(default_factory=list)

    # ------------------------------------------------------------------ helpers

    @property
    def changed_count(self) -> int:
        """Number of transitions where the value differed from the previous entry."""
        if len(self.entries) < 2:
            return 0
        changes = 0
        for prev, curr in zip(self.entries, self.entries[1:]):
            if prev.value != curr.value:
                changes += 1
        return changes

    @property
    def is_stable(self) -> bool:
        """True when the key never changed across all recorded snapshots."""
        return self.changed_count == 0

    @property
    def first_seen(self) -> str | None:
        return self.entries[0].timestamp if self.entries else None

    @property
    def last_seen(self) -> str | None:
        return self.entries[-1].timestamp if self.entries else None


@dataclass
class TimelineResult:
    """Aggregated timeline for every key found across all audit records."""

    env_name: str
    timelines: dict[str, KeyTimeline] = field(default_factory=dict)

    # ------------------------------------------------------------------ helpers

    @property
    def unstable_keys(self) -> list[str]:
        """Keys that changed at least once."""
        return sorted(k for k, tl in self.timelines.items() if not tl.is_stable)

    @property
    def stable_keys(self) -> list[str]:
        """Keys that never changed."""
        return sorted(k for k, tl in self.timelines.items() if tl.is_stable)

    @property
    def total_keys(self) -> int:
        return len(self.timelines)

    @property
    def total_changes(self) -> int:
        return sum(tl.changed_count for tl in self.timelines.values())


# --------------------------------------------------------------------------- #
#  Public API                                                                  #
# --------------------------------------------------------------------------- #

def build_timeline(audit_records: list[dict[str, Any]], env_name: str) -> TimelineResult:
    """Build a :class:`TimelineResult` from a list of audit record dicts.

    Each record is expected to have the shape produced by
    :func:`envdrift.auditor.record_audit`::

        {
            "id": "...",
            "timestamp": "2024-01-01T00:00:00",
            "env_file": "...",
            "keys": {"KEY": "value", ...},
        }

    Records are assumed to be in ascending chronological order; if not,
    they are sorted by their ``timestamp`` field before processing.
    """
    # Sort defensively by timestamp (lexicographic sort works for ISO-8601).
    sorted_records = sorted(audit_records, key=lambda r: r.get("timestamp", ""))

    result = TimelineResult(env_name=env_name)

    for record in sorted_records:
        audit_id = record.get("id", "unknown")
        timestamp = record.get("timestamp", "")
        keys: dict[str, str] = record.get("keys", {})

        # Collect all keys we have seen so far plus those in this record so we
        # can mark previously-present keys as <absent> when they disappear.
        all_known = set(result.timelines) | set(keys)

        for key in all_known:
            if key not in result.timelines:
                result.timelines[key] = KeyTimeline(key=key)

            value = keys.get(key)  # None when key absent in this record
            entry = TimelineEntry(
                timestamp=timestamp,
                audit_id=audit_id,
                env_name=env_name,
                value=value,
            )
            result.timelines[key].entries.append(entry)

    return result
