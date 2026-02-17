from typing import List, Dict, Any, Tuple

# MVP keyword rules for each indicator category.
# Matching is case insensitive and uses simple substring checks.
CT_KEYWORDS: Dict[str, List[str]] = {
    "explanation_prompts": [
        "explain",
        "explanation of",
        "why ",
        "why is",
        "why does",
        "how does",
        "how do",
        "how does this work",
        "help me understand",
        "help me to understand",
        "can you clarify",
        "clarify",
        "describe the concept",
        "tell me what this means",
        "overview of",
        "background on",
        "key concepts",
        "basic explanation",
        "foundational explanation",
    ],
    "verification_prompts": [
        "is this correct",
        "is this right",
        "is this accurate",
        "is this true",
        "check if this is correct",
        "does this make sense",
        "does this sound right",
        "can you verify",
        "verify this",
        "confirm this",
        "confirm if this is correct",
        "is this explanation correct",
        "do i understand this correctly",
    ],
    "comparison_prompts": [
        "compare",
        "comparison between",
        "difference between",
        "differences between",
        "how is this different",
        "how is this similar",
        "similarities and differences",
        "pros and cons",
        "advantages and disadvantages",
        "stronger than",
        "weaker than",
        "relative to",
    ],
    "evidence_prompts": [
        "evidence",
        "any evidence",
        "supporting evidence",
        "source",
        "sources",
        "reference",
        "references",
        "cite",
        "citation",
        "link to a study",
        "research shows",
        "studies show",
        "can you provide a source",
    ],
}


def _is_student_turn(turn: Dict[str, Any]):
    return turn.get("role") == "student"


def _count_matches(turns: List[Dict[str, Any]], keywords: List[str]):
    if not keywords:
        return 0

    count = 0
    lowered_keywords = [kw.lower() for kw in keywords]

    for turn in turns:
        if not _is_student_turn(turn):
            continue

        text = (turn.get("text") or "").lower()
        if any(kw in text for kw in lowered_keywords):
            count += 1

    return count


def detect_explanation_prompts(turns: List[Dict[str, Any]]):
    return _count_matches(turns, CT_KEYWORDS["explanation_prompts"])


def detect_verification_prompts(turns: List[Dict[str, Any]]):
    return _count_matches(turns, CT_KEYWORDS["verification_prompts"])


def detect_comparison_prompts(turns: List[Dict[str, Any]]):
    return _count_matches(turns, CT_KEYWORDS["comparison_prompts"])


def detect_evidence_prompts(turns: List[Dict[str, Any]]):
    return _count_matches(turns, CT_KEYWORDS["evidence_prompts"])


def extract_critical_thinking_evidence(
    turns: List[Dict[str, Any]],
    ct_counts: Dict[str, int],
    max_snippets: int = 3,
):
    evidence: List[str] = []
    if max_snippets <= 0:
        return evidence

    categories = [
        "explanation_prompts",
        "verification_prompts",
        "comparison_prompts",
        "evidence_prompts",
    ]

    # Track which categories already have an example
    captured_for: Dict[str, bool] = {cat: False for cat in categories}

    lowered_keywords: Dict[str, List[str]] = {
        key: [kw.lower() for kw in CT_KEYWORDS.get(key, [])] for key in categories
    }

    for turn in turns:
        if not _is_student_turn(turn):
            continue

        text = turn.get("text") or ""
        lower_text = text.lower()

        for category in categories:
            if ct_counts.get(category, 0) <= 0:
                continue
            if captured_for[category]:
                continue

            kws = lowered_keywords.get(category, [])
            if any(kw in lower_text for kw in kws):
                evidence.append(text)
                captured_for[category] = True

                if len(evidence) >= max_snippets:
                    return evidence

    return evidence


def compute_ct_indicators_and_evidence(
    turns: List[Dict[str, Any]],
    max_snippets: int = 3,
):
    """
    Public entry point for the pipeline.

    Inputs:
      - turns: unified list of chat turns (with role and text).
      - max_snippets: maximum number of evidence messages to return.

    Outputs:
      - counts: dict with raw indicator counts.
      - evidence: list of up to max_snippets student messages that
                  illustrate these behaviours.
    """
    counts = {
        "explanation_prompts": detect_explanation_prompts(turns),
        "verification_prompts": detect_verification_prompts(turns),
        "comparison_prompts": detect_comparison_prompts(turns),
        "evidence_prompts": detect_evidence_prompts(turns),
    }

    evidence = extract_critical_thinking_evidence(
        turns,
        counts,
        max_snippets=max_snippets,
    )

    return counts, evidence
