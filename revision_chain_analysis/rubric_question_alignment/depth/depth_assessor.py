from typing import Dict, List, Union
import yaml


def assess_engagement_depth(
    prompts: List[str],
    depth_rules: Dict[str, List[str]],
) -> str:
    """
    Analyse question sophistication for ONE specific criterion.

    Frequency-based rule:
    - Count keyword matches per depth level across all prompts.
    - Assign the level with the highest match count.
    - In ties, the deeper level wins (deep > moderate > surface).
    - If no keywords match, return "none".
    """
    text = " ".join(prompts).lower()

    # Ensure keys exist (safe defaults)
    none_rules = depth_rules.get("none", [])
    surface_rules = depth_rules.get("surface", [])
    moderate_rules = depth_rules.get("moderate", [])
    deep_rules = depth_rules.get("deep", [])

    counts = {
        "none": 0,
        "surface": 0,
        "moderate": 0,
        "deep": 0,
    }

    # Count occurrences (simple substring counting)
    for kw in none_rules:
        kw_l = kw.lower()
        if kw_l:
            counts["none"] += text.count(kw_l)

    for kw in surface_rules:
        kw_l = kw.lower()
        if kw_l:
            counts["surface"] += text.count(kw_l)

    for kw in moderate_rules:
        kw_l = kw.lower()
        if kw_l:
            counts["moderate"] += text.count(kw_l)

    for kw in deep_rules:
        kw_l = kw.lower()
        if kw_l:
            counts["deep"] += text.count(kw_l)

    # If nothing matches at all, return none
    if counts["surface"] == 0 and counts["moderate"] == 0 and counts["deep"] == 0:
        return "none"

    # Pick the highest count; on tie choose deeper
    # Order matters for tie-breaking (deep wins ties)
    priority = ["surface", "moderate", "deep"]
    max_count = max(counts[lvl] for lvl in priority)

    tied = [lvl for lvl in priority if counts[lvl] == max_count]
    if "deep" in tied:
        return "deep"
    if "moderate" in tied:
        return "moderate"
    return "surface"


def assess_all_criteria(
    prompts_by_criteria: Dict[str, List[str]],
    rules_source: Union[str, Dict[str, List[str]]],
) -> Dict[str, str]:
    """
    Assess depth for ALL criteria.

    Returns:
      { "criteria_id": "none|surface|moderate|deep", ... }
    """
    if isinstance(rules_source, str):
        with open(rules_source, "r", encoding="utf-8") as f:
            depth_rules = yaml.safe_load(f) or {}
    else:
        depth_rules = rules_source

    results: Dict[str, str] = {}
    for criteria_id, prompts in prompts_by_criteria.items():
        results[criteria_id] = assess_engagement_depth(prompts, depth_rules)

    return results
