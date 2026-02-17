"""
Simple rule-based classifier for student AI use patterns.

Inputs
------
prompt_distribution : dict
    Proportions in [0, 1] for different prompt types, expected keys:
    - "generate_content"
    - "revise_content"
    - "understand_prompt"
    - "check_quality"

ps_indicators : dict
    Problem-solving indicators. For this MVP we expect:
    - "self_authored_turns": int

ct_indicators : dict
    Critical thinking indicators (not used yet, kept for future rules).

Output
------
One of:
- "generator_only"
- "reviser"
- "planner_checker"
- "mixed"
"""

from __future__ import annotations
from typing import Dict, Any


PATTERN_GENERATOR_ONLY = "generator_only"
PATTERN_REVISER = "reviser"
PATTERN_PLANNER_CHECKER = "planner_checker"
PATTERN_MIXED = "mixed"


def _get_float(d: Dict[str, Any], key: str) -> float:
    value = d.get(key, 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _get_int(d: Dict[str, Any], key: str) -> int:
    value = d.get(key, 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def classify_ai_use_pattern(
    prompt_distribution: Dict[str, Any],
    ps_indicators: Dict[str, Any],
    ct_indicators: Dict[str, Any],  # kept for future use
) -> str:
    """
    Classify a student's overall AI-use pattern using simple thresholds.

    Rule order also acts as tie-break logic:

    1. generator_only
    2. reviser
    3. planner_checker
    4. mixed (fallback)
    """
    generate_content = _get_float(prompt_distribution, "generate_content")
    revise_content = _get_float(prompt_distribution, "revise_content")
    understand_prompt = _get_float(prompt_distribution, "understand_prompt")
    check_quality = _get_float(prompt_distribution, "check_quality")

    self_authored_turns = _get_int(ps_indicators, "self_authored_turns")

    # Rule 1: generator_only
    # If generate_content proportion >= 0.60 -> generator_only
    if generate_content >= 0.60:
        return PATTERN_GENERATOR_ONLY

    # Rule 2: reviser
    # If revise_content proportion >= 0.40 and self-authored turns ≥ 2 -> reviser
    if revise_content >= 0.40 and self_authored_turns >= 2:
        return PATTERN_REVISER

    # Rule 3: planner_checker
    # If understand_prompt + check_quality >= 0.50 -> planner_checker
    if (understand_prompt + check_quality) >= 0.50:
        return PATTERN_PLANNER_CHECKER

    # Rule 4: otherwise -> mixed
    return PATTERN_MIXED
