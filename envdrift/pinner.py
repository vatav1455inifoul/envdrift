"""Pin specific env keys to expected values and detect deviations."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

PINS_DIR = Path(".envdrift") / "pins"


@dataclass
class PinViolation:
    key: str
    expected: str
    actual: Optional[str]  # None means key is missing


@dataclass
class PinResult:
    env_file: str
    violations: List[PinViolation] = field(default_factory=list)

    def has_violations(self) -> bool:
        return bool(self.violations)


def pins_path(name: str) -> Path:
    return PINS_DIR / f"{name}.json"


def save_pins(name: str, pins: Dict[str, str]) -> Path:
    path = pins_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pins, indent=2))
    return path


def load_pins(name: str) -> Dict[str, str]:
    path = pins_path(name)
    if not path.exists():
        raise FileNotFoundError(f"No pin set found: {name}")
    return json.loads(path.read_text())


def list_pins() -> List[str]:
    if not PINS_DIR.exists():
        return []
    return [p.stem for p in sorted(PINS_DIR.glob("*.json"))]


def check_pins(name: str, env: Dict[str, str], env_file: str = "") -> PinResult:
    pins = load_pins(name)
    result = PinResult(env_file=env_file)
    for key, expected in pins.items():
        actual = env.get(key)
        if actual != expected:
            result.violations.append(PinViolation(key=key, expected=expected, actual=actual))
    return result
