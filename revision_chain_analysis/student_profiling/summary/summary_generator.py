from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml

TEMPLATES_FILE = Path(__file__).with_name("pattern_summaries.yaml")


def _load_templates(path: Path = TEMPLATES_FILE) -> Dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing YAML templates file: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("pattern_summaries.yaml must contain a mapping of pattern -> template string")

    templates: Dict[str, str] = {}
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError("All keys and values in pattern_summaries.yaml must be strings")
        templates[k.strip()] = v.strip()

    return templates


def build_process_notes(pattern: str, scores: dict) -> str:
    """
    Goal: Produce short, natural language process notes summarising student behaviour.

    Args:
        pattern: One of the keys in pattern_summaries.yaml
                 (e.g., generator_only, reviser, planner_checker, mixed)
        scores: Optional dict of scores. Kept for API compatibility, but not used in the MVP.

    Returns:
        A short natural language summary string.
    """
    templates = _load_templates()

    if not isinstance(pattern, str) or not pattern.strip():
        raise ValueError("pattern must be a non-empty string")

    pattern = pattern.strip()

    if pattern not in templates:
        valid = ", ".join(sorted(templates.keys()))
        raise KeyError(f"Unknown pattern '{pattern}'. Valid patterns: {valid}")

    return templates[pattern]
