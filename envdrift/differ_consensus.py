"""Consensus analysis: find keys whose values agree across the majority of envs."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from typing import Dict, List, Set

from envdrift.parser import parse_env_file


@dataclass
class ConsensusEntry:
    key: str
    majority_value: str
    agreeing_envs: List[str]
    dissenting_envs: List[str]

    @property
    def agreement_rate(self) -> float:
        total = len(self.agreeing_envs) + len(self.dissenting_envs)
        return len(self.agreeing_envs) / total if total else 1.0

    @property
    def is_unanimous(self) -> bool:
        return not self.dissenting_envs

    def __str__(self) -> str:
        pct = f"{self.agreement_rate * 100:.0f}%"
        return f"{self.key}: '{self.majority_value}' ({pct} agreement)"


@dataclass
class ConsensusResult:
    env_names: List[str]
    unanimous: List[ConsensusEntry] = field(default_factory=list)
    majority: List[ConsensusEntry] = field(default_factory=list)
    contested: List[ConsensusEntry] = field(default_factory=list)
    absent: List[str] = field(default_factory=list)  # keys missing in >50% of envs

    @property
    def total_keys(self) -> int:
        return len(self.unanimous) + len(self.majority) + len(self.contested) + len(self.absent)

    @property
    def consensus_rate(self) -> float:
        if not self.total_keys:
            return 1.0
        return (len(self.unanimous) + len(self.majority)) / self.total_keys


def analyse_consensus(env_files: Dict[str, str], threshold: float = 0.6) -> ConsensusResult:
    """Analyse value consensus across multiple env files.

    Args:
        env_files: mapping of env_name -> file path
        threshold: fraction of envs that must agree for 'majority' status (default 0.6)
    """
    if len(env_files) < 2:
        raise ValueError("consensus analysis requires at least two environments")

    parsed: Dict[str, Dict[str, str]] = {
        name: parse_env_file(path) for name, path in env_files.items()
    }
    env_names = list(parsed.keys())
    n = len(env_names)

    all_keys: Set[str] = set()
    for data in parsed.values():
        all_keys.update(data.keys())

    result = ConsensusResult(env_names=env_names)

    for key in sorted(all_keys):
        present = {name: data[key] for name, data in parsed.items() if key in data}
        missing_in = [name for name in env_names if key not in parsed[name]]

        if len(missing_in) / n > 0.5:
            result.absent.append(key)
            continue

        counter = Counter(present.values())
        majority_value, majority_count = counter.most_common(1)[0]
        agreeing = [name for name, val in present.items() if val == majority_value]
        dissenting = [name for name, val in present.items() if val != majority_value] + missing_in
        rate = len(agreeing) / n

        entry = ConsensusEntry(
            key=key,
            majority_value=majority_value,
            agreeing_envs=agreeing,
            dissenting_envs=dissenting,
        )

        if not dissenting:
            result.unanimous.append(entry)
        elif rate >= threshold:
            result.majority.append(entry)
        else:
            result.contested.append(entry)

    return result
