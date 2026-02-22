from typing import List, Dict, Any

"""
Problem Solving Indicators – Rule-Based Detection Module
"""


# Helpers

STUDENT_ROLES = {"student", "user"}


def _is_student_turn(turn: Dict[str, Any]) -> bool:
    return str(turn.get("role", "")).lower() in STUDENT_ROLES


def _get_text(turn: Dict[str, Any]) -> str:
    return str(turn.get("text", "") or "")


def _get_prompt_type(turn: Dict[str, Any]) -> str:
    # Pull prompt type from previous task
    if "prompt_type" in turn:
        return str(turn["prompt_type"]).lower()
    if "type" in turn:
        return str(turn["type"]).lower()
    return ""


def _token_count(text: str) -> int:
    return len(text.split())


# 1. Task decomposition

def detect_task_decomposition(turns: List[Dict[str, Any]]) -> int:
    keywords = [
        "break this down",
        "break it down",
        "step by step",
        "outline the steps",
        "list the steps",
        "split this into steps",
        "can you break this",
        "can we break this",
    ]

    count = 0

    for turn in turns:
        if not _is_student_turn(turn):
            continue

        text = _get_text(turn).lower()

        # 1) Exact phrase matches
        if any(kw in text for kw in keywords):
            count += 1
            continue

        # 2) NEW fallback:
        # Catch things like:
        # "Can we break the data analysis part into steps?"
        if "break" in text and ("step" in text or "steps" in text):
            count += 1
            continue

    return count



# 2. Iterative revisions

def detect_iterative_revisions(classified_turns: List[Dict[str, Any]]) -> int:
    types = [_get_prompt_type(t) for t in classified_turns]
    n = len(types)
    count = 0

    for i in range(n):
        if types[i] != "revise_content":
            continue

        for j in range(i + 1, min(i + 4, n)):
            if types[j] == "revise_content":
                count += 1
                break
    return count


# 3. Student drafts

def detect_student_drafts(turns: List[Dict[str, Any]], length_threshold: int = 40) -> int:
    count = 0
    for turn in turns:
        if not _is_student_turn(turn):
            continue
        if _token_count(_get_text(turn)) > length_threshold:
            count += 1
    return count


# 4. Feedback uptake

def detect_feedback_uptake(turns: List[Dict[str, Any]]) -> int:
    phrases = [
        "i applied",
        "i have applied",
        "i updated",
        "i have updated",
        "i fixed",
        "i have fixed",
        "i changed",
        "i revised",
        "based on your feedback",
        "based on your suggestion",
        "based on your suggestions",
        "after your feedback",
        "after your suggestions",
        "as you suggested",
        "like you suggested",
    ]

    count = 0
    for turn in turns:
        if not _is_student_turn(turn):
            continue
        text = _get_text(turn).lower()
        if any(p in text for p in phrases):
            count += 1
    return count


# Evidence Snippets

def extract_problem_solving_evidence(
    turns: List[Dict[str, Any]],
    ps_counts: Dict[str, int],
    max_snippets: int = 3
) -> List[str]:

    decomposition_left = ps_counts.get("decomposition_prompts", 0)
    drafts_left = ps_counts.get("self_proposed_content_turns", 0)
    feedback_left = ps_counts.get("feedback_uptake_events", 0)
    iterative_left = ps_counts.get("iterative_revision_count", 0)

    snippets: List[str] = []
    seen: set[str] = set()

    decomp_keywords = [
        "break this down",
        "break it down",
        "step by step",
        "outline the steps",
        "list the steps",
        "can you break this",
        "can we break this",
    ]

    feedback_keywords = [
        "i updated",
        "i fixed",
        "i applied",
        "i have updated",
        "as you suggested",
        "based on your",
    ]

    def add_snip(text: str) -> None:
        t = text.strip()
        if t and t not in seen and len(snippets) < max_snippets:
            snippets.append(t)
            seen.add(t)

    for turn in turns:
        if len(snippets) >= max_snippets:
            break
        if not _is_student_turn(turn):
            continue

        text = _get_text(turn)
        lower = text.lower()

        # 1) Task decomposition evidence
        if decomposition_left > 0 and any(k in lower for k in decomp_keywords):
            add_snip(text)
            decomposition_left -= 1
            continue

        # 2) Draft evidence (long student-written text)
        if drafts_left > 0 and _token_count(text) > 40:
            add_snip(text)
            drafts_left -= 1
            continue

        # 3) Feedback uptake evidence
        if feedback_left > 0 and any(k in lower for k in feedback_keywords):
            add_snip(text)
            feedback_left -= 1
            continue

        # 4) NEW: iterative revision evidence
        if iterative_left > 0 and _get_prompt_type(turn) == "revise_content":
            add_snip(text)
            iterative_left -= 1
            continue

    return snippets


# Public API

def compute_PS_indicators_and_evidence(
    turns: List[Dict[str, Any]],
    classified_turns: List[Dict[str, Any]] | None = None,
    max_snippets: int = 3
) -> Dict[str, Any]:
    """
    Compute the Problem Solving (PS) indicators and evidence.

    Returns a JSON-compatible dict with shape:

    {
        "counts": {
            "decomposition_prompts": int,
            "iterative_revision_count": int,
            "self_proposed_content_turns": int,
            "feedback_uptake_events": int
        },
        "evidence": [
            "example snippet 1",
            "example snippet 2",
            "example snippet 3"
        ]
    }
    """
    if classified_turns is None:
        classified_turns = turns

    counts = {
        "decomposition_prompts": detect_task_decomposition(turns),
        "iterative_revision_count": detect_iterative_revisions(classified_turns),
        "self_proposed_content_turns": detect_student_drafts(turns),
        "feedback_uptake_events": detect_feedback_uptake(turns),
    }

    evidence = extract_problem_solving_evidence(
        turns, counts, max_snippets=max_snippets
    )

    return {
        "counts": counts,
        "evidence": evidence,
    }

