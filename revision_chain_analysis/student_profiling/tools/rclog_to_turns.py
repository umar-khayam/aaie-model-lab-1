from pathlib import Path
from typing import List, Dict, Any
import json


def load_rclog(path: Path) :
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "revision_chain" not in data:
        raise ValueError("File does not look like an rc_log_v1 (missing 'revision_chain').")

    return data


def rclog_to_turns(rclog: Dict[str, Any]):
    turns: List[Dict[str, Any]] = []
    turn_index = 0

    for step in rclog.get("revision_chain", []):
        student_text = step.get("student_prompt", "") or ""
        llm_text = step.get("llm_response", "") or ""

        # Student turn
        if student_text.strip():
            turns.append(
                {
                    "turn_index": turn_index,
                    "role": "student",
                    "text": student_text,
                }
            )
            turn_index += 1

        # Assistant turn
        if llm_text.strip():
            turns.append(
                {
                    "turn_index": turn_index,
                    "role": "assistant",
                    "text": llm_text,
                }
            )
            turn_index += 1

    return turns
