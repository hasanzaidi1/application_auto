from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import UserPreferences


DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "settings.json"


def load_preferences(path: Path = DEFAULT_CONFIG_PATH) -> UserPreferences:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")

    with path.open("r", encoding="utf-8") as fh:
        raw: Dict[str, Any] = json.load(fh)

    return UserPreferences(
        target_locations=raw.get("target_locations", []),
        target_titles=raw.get("target_titles", []),
        required_skills=[s.lower() for s in raw.get("required_skills", [])],
        optional_skills=[s.lower() for s in raw.get("optional_skills", [])],
        throttle_seconds=float(raw.get("throttle_seconds", 2.0)),
        review_mode=bool(raw.get("review_mode", False)),
        min_score=float(raw.get("min_score", 0.45)),
    )
