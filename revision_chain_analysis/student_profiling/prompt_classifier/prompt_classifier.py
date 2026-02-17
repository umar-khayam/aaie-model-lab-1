from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Any

import yaml

# Path to YAML config
CONFIG_PATH = Path(__file__).resolve().parent / "prompt_types.yaml"

PROMPT_TYPE_PRIORITY = [
    "revise_content",
    "generate_content",
    "check_quality",
    "plan_structure",
    "understand_prompt",
    "polish_language",
]

KNOWN_TYPES = [
    "understand_prompt",
    "plan_structure",
    "generate_content",
    "revise_content",
    "polish_language",
    "check_quality",
    "unknown_prompt_type",
]


def load_prompt_type_rules():

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        rules = yaml.safe_load(f) or {}
    # Ensure every known type at least has an empty list
    for t in KNOWN_TYPES:
        rules.setdefault(t, [])
    return rules


def classify_prompt(text: str, rules: Dict[str, list]):
    if not text:
        return "unknown_prompt_type"

    lower_text = text.lower()

    for prompt_type in PROMPT_TYPE_PRIORITY:
        keywords = rules.get(prompt_type, []) or []
        for kw in keywords:
            if kw and kw in lower_text:
                return prompt_type

    return "unknown_prompt_type"


def classify_chat_turns(turns: List[Dict[str, Any]], rules: Dict[str, list]):
    classified_turns: List[Dict[str, Any]] = []

    for turn in turns:
        turn_copy = dict(turn)

        if turn_copy.get("role") == "student":
            text = turn_copy.get("text", "")
            prompt_type = classify_prompt(text, rules)
            turn_copy["prompt_type"] = prompt_type

        classified_turns.append(turn_copy)

    return classified_turns


def compute_prompt_type_distribution(classified_turns: List[Dict[str, Any]]):
    counter: Counter = Counter()

    for turn in classified_turns:
        if turn.get("role") == "student":
            pt = turn.get("prompt_type", "unknown_prompt_type")
            counter[pt] += 1

    distribution = {pt: counter.get(pt, 0) for pt in KNOWN_TYPES}
    return distribution


def run_prompt_type_classification(turns: List[Dict[str, Any]]):
    rules = load_prompt_type_rules()
    classified_turns = classify_chat_turns(turns, rules)
    distribution = compute_prompt_type_distribution(classified_turns)
    return classified_turns, distribution
