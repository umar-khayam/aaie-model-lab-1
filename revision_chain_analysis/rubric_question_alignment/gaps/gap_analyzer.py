from typing import Dict, List, Optional, Any

Flag = Dict[str, Any]


def identify_gaps(
    coverage: Dict[str, float],
    criteria_weights: Optional[Dict[str, float]] = None,
    prompt_counts: Optional[Dict[str, int]] = None,
    total_criteria: Optional[int] = None,
) -> List[Flag]:
    """
    Generate coverage-related flags.

    Types:
    - rubric_gap: per-criterion coverage < 0.50
    - coverage_issue: coverage patterns (minimal prompts, high-weight undercovered, summary)
    """
    criteria_weights = criteria_weights or {}
    prompt_counts = prompt_counts or {}

    if total_criteria is None:
        total_criteria = len(coverage)

    flags: List[Flag] = []

    for cid, score in coverage.items():

        # rubric_gap
        if score < 0.50:
            severity = "high" if score < 0.30 else "medium"
            flags.append({
                "type": "rubric_gap",
                "severity": severity,
                "criteria_id": cid,
                "message": f"Coverage is {score:.2f}, below 0.50 threshold."
            })

        # coverage_issue: high-weight undercovered
        weight = criteria_weights.get(cid, 0.0)
        if weight >= 0.70 and score < 0.60:
            flags.append({
                "type": "coverage_issue",
                "severity": "high",
                "criteria_id": cid,
                "message": "High-weight criterion is undercovered (weight ≥ 0.70 and coverage < 0.60)."
            })

        # coverage_issue: minimal prompts
        count = prompt_counts.get(cid, 0)
        if count <= 1:
            flags.append({
                "type": "coverage_issue",
                "severity": "low",
                "criteria_id": cid,
                "message": "Minimal prompts linked to this criterion (prompt count ≤ 1)."
            })

    # coverage_issue: summary
    undercovered = sum(1 for v in coverage.values() if v < 0.50)
    if undercovered > 0:
        flags.append({
            "type": "coverage_issue",
            "severity": "medium",
            "criteria_id": None,
            "message": f"{undercovered} out of {total_criteria} criteria are undercovered."
        })

    return flags


def generate_gaps(
    coverage: Dict[str, float],
    unmatched_keywords: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, List[str]]:
    """
    Generate human-readable gap descriptions per criterion using unmatched keywords.

    Rules:
    - coverage >= 0.80 → no gaps
    - coverage < 0.80 → group unmatched keywords into coherent gap messages
    """
    unmatched_keywords = unmatched_keywords or {}
    gaps: Dict[str, List[str]] = {}

    for cid, score in coverage.items():
        if score >= 0.80:
            gaps[cid] = []
            continue

        keywords = unmatched_keywords.get(cid, [])
        keywords = [k for k in keywords if k]

        if not keywords:
            gaps[cid] = ["Limited coverage for this criterion, but no unmatched keywords were provided."]
            continue

        joined = ", ".join(keywords)
        gaps[cid] = [f"No questions about key areas ({joined})."]

    return gaps


def generate_flags(
    coverage: Dict[str, float],
    criteria_weights: Optional[Dict[str, float]] = None,
    prompt_counts: Optional[Dict[str, int]] = None,
    total_criteria: Optional[int] = None,
    off_topic_prompts: int = 0,
    unmatched_keywords: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Generate both flags and gaps.

    off_topic_prompts is provided by keyword matching / input processing.
    unmatched_keywords is provided per criterion by keyword matching.
    """
    flags = identify_gaps(coverage, criteria_weights, prompt_counts, total_criteria)

    if off_topic_prompts > 0:
        flags.append({
            "type": "off_topic_questions",
            "severity": "medium",
            "criteria_id": None,
            "message": f"{off_topic_prompts} prompt(s) do not match any criterion."
        })

    gaps = generate_gaps(coverage, unmatched_keywords)

    return {
        "flags": flags,
        "gaps": gaps
    }
