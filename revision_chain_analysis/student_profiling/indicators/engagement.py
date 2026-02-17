"""
Engagement indicators for Revision Chain Analysis.

Input format (MVP assumption):

turn = {
    "role": "student" or "assistant" or "system",
    "text": "message text here",
    "timestamp": "2025-12-04T10:30:00Z"  # optional ISO string
}

turns = [turn1, turn2, ...]
classified_turns = [
    {
        "prompt_type": "revise_content",  # from Prompt Type Classifier
        # you can include other fields if needed
    },
    ...
]
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


def _parse_timestamp(ts: str) -> Optional[datetime]:
    """
    Helper to parse simple ISO timestamps.
    Handles values like '2025-12-04T10:30:00Z' or '2025-12-04T10:30:00'.
    Returns None if parsing fails.
    """
    if not ts:
        return None
    try:
        ts_str = str(ts)
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1]
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


def compute_student_token_ratio(turns: List[Dict[str, Any]]) -> float:
    """
    Count tokens for student messages vs all messages.
    Use simple whitespace split for tokens (MVP).
    Returns a float between 0 and 1.
    """
    total_tokens = 0
    student_tokens = 0

    for turn in turns:
        text = str(turn.get("text", "") or "")
        token_count = len(text.split())

        total_tokens += token_count
        if turn.get("role") == "student":
            student_tokens += token_count

    if total_tokens == 0:
        return 0.0

    return student_tokens / float(total_tokens)


def compute_turn_count(turns: List[Dict[str, Any]]) -> int:
    """
    Count how many student messages are in the conversation.
    """
    return sum(1 for turn in turns if turn.get("role") == "student")


def compute_prompt_diversity(classified_turns: List[Dict[str, Any]]) -> int:
    """
    Count unique prompt_type values from the classifier output.

    MVP assumption:
    - classified_turn is a dict that has a 'prompt_type' key.
    """
    if not classified_turns:
        return 0

    types = set()
    for ct in classified_turns:
        pt = ct.get("prompt_type")
        if pt:
            types.add(pt)

    return len(types)


def compute_session_duration(turns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute session duration.

    If timestamps exist:
      - use max_timestamp - min_timestamp in minutes.

    If not:
      - use number of turns as a proxy.
    """
    parsed_times: List[datetime] = []

    for turn in turns:
        ts = turn.get("timestamp")
        if ts:
            dt = _parse_timestamp(ts)
            if dt:
                parsed_times.append(dt)

    if parsed_times:
        start = min(parsed_times)
        end = max(parsed_times)
        minutes = (end - start).total_seconds() / 60.0
        return {
            "session_time_minutes": float(minutes),
            "is_proxy": False,
        }

    # no valid timestamps, use turn count as proxy
    return {
        "session_time_minutes": float(len(turns)),
        "is_proxy": True,
    }


def extract_engagement_evidence(
    turns: List[Dict[str, Any]],
    eng_metrics: Dict[str, Any],
    max_snippets: int = 2,
) -> List[str]:
    """
    Return a list of student message snippets that show engagement.

    Simple MVP rule:
    - take the longest student messages as evidence.
    """
    student_turns = [
        turn for turn in turns if turn.get("role") == "student"
    ]

    # sort by text length, longest first
    student_turns.sort(
        key=lambda t: len(str(t.get("text", "") or "")),
        reverse=True,
    )

    snippets: List[str] = []
    for turn in student_turns:
        text = str(turn.get("text", "") or "").strip()
        if not text:
            continue
        snippets.append(text)
        if len(snippets) >= max_snippets:
            break

    return snippets


def compute_engagement_indicators_and_evidence(
    turns: List[Dict[str, Any]],
    classified_turns: Optional[List[Dict[str, Any]]] = None,
    max_snippets: int = 2,
) -> Dict[str, Any]:
    """
    Module level public function.

    Returns a dict with:
    {
        "counts": {
            "student_token_ratio": ...,
            "student_turn_count": ...,
            "prompt_type_diversity": ...,
            "distinct_episode_types": ...,
            "session_time_minutes": ...,
            "session_duration_is_proxy": bool
        },
        "evidence": [
            "snippet 1",
            "snippet 2"
        ]
    }
    """
    counts: Dict[str, Any] = {}

    # core metrics
    counts["student_token_ratio"] = compute_student_token_ratio(turns)
    counts["student_turn_count"] = compute_turn_count(turns)

    # prompt type diversity - use classifier output if provided
    if classified_turns is not None:
        ptd = compute_prompt_diversity(classified_turns)
    else:
        ptd = 0

    counts["prompt_type_diversity"] = ptd
    # alias to match sample naming in card
    counts["distinct_episode_types"] = ptd

    # session duration
    duration_info = compute_session_duration(turns)
    counts["session_time_minutes"] = duration_info["session_time_minutes"]
    counts["session_duration_is_proxy"] = duration_info["is_proxy"]

    # evidence snippets
    evidence = extract_engagement_evidence(turns, counts, max_snippets=max_snippets)

    return {
        "counts": counts,
        "evidence": evidence,
    }
if __name__ == "__main__":
    # Fake chat history
    turns = [
        {
            "role": "student",
            "text": "here is my full draft for the discussion section I think it is still rough but I tried to link back to the research question",
            "timestamp": "2025-12-04T10:00:00Z",
        },
        {
            "role": "assistant",
            "text": "Thanks, I will review this draft now.",
            "timestamp": "2025-12-04T10:05:00Z",
        },
        {
            "role": "student",
            "text": "I rewrote the conclusion again can you check if it now aligns with the introduction and thesis",
            "timestamp": "2025-12-04T10:40:00Z",
        },
    ]

    # Fake classified turns from Prompt Type Classifier
    classified_turns = [
        {"prompt_type": "share_draft"},
        {"prompt_type": "tutor_feedback"},
        {"prompt_type": "revise_content"},
    ]

    result = compute_engagement_indicators_and_evidence(
        turns, classified_turns, max_snippets=2
    )

    print("COUNTS:")
    print(result["counts"])
    print("\nEVIDENCE:")
    for snip in result["evidence"]:
        print("-", snip)
