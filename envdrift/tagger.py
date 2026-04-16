"""Tag env files with metadata labels for grouping and filtering."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_TAGS_DIR = Path(".envdrift") / "tags"


def _tags_path(label: str) -> Path:
    return _TAGS_DIR / f"{label}.json"


def save_tag(label: str, paths: List[str], notes: Optional[str] = None) -> Path:
    """Associate a tag label with a list of env file paths."""
    _TAGS_DIR.mkdir(parents=True, exist_ok=True)
    data = {"label": label, "paths": paths, "notes": notes or ""}
    dest = _tags_path(label)
    dest.write_text(json.dumps(data, indent=2))
    return dest


def load_tag(label: str) -> Dict:
    """Load a tag by label. Raises FileNotFoundError if missing."""
    p = _tags_path(label)
    if not p.exists():
        raise FileNotFoundError(f"Tag '{label}' not found at {p}")
    return json.loads(p.read_text())


def list_tags() -> List[str]:
    """Return all saved tag labels."""
    if not _TAGS_DIR.exists():
        return []
    return sorted(p.stem for p in _TAGS_DIR.glob("*.json"))


def delete_tag(label: str) -> bool:
    """Delete a tag. Returns True if deleted, False if not found."""
    p = _tags_path(label)
    if p.exists():
        p.unlink()
        return True
    return False


def tag_summary(tag: Dict) -> str:
    lines = [
        f"Label : {tag['label']}",
        f"Files : {len(tag['paths'])}",
    ]
    for fp in tag["paths"]:
        lines.append(f"  - {fp}")
    if tag.get("notes"):
        lines.append(f"Notes : {tag['notes']}")
    return "\n".join(lines)
