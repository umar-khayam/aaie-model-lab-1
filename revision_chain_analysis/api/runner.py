from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from revision_chain_analysis.student_profiling.output.profile_builder import (
    EvidenceBlocks,
    Scores,
    build_student_interaction_profile,
)
from revision_chain_analysis.student_profiling.tools.profile_runner import (
    run_student_profiling_from_rclog,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_submission_id(chat_history_json: Dict[str, Any]) -> str:
    sid = chat_history_json.get("submission_id") or chat_history_json.get("id")
    if isinstance(sid, str) and sid.strip():
        return sid.strip()
    return f"unknown_submission_{int(datetime.now(timezone.utc).timestamp())}"


def _schema_valid_fallback_profile(submission_id: str, reason: str) -> Dict[str, Any]:
    scores = Scores(0.0, 0.0, 0.0)
    indicator_metrics = {
        "critical_thinking": {},
        "problem_solving": {},
        "engagement": {},
        "prompt_type_distribution": {},
    }
    evidence = EvidenceBlocks(
        critical_thinking=[],
        problem_solving=[],
        engagement=[],
        ai_use_pattern=[],
    )
    return build_student_interaction_profile(
        submission_id=submission_id,
        scores=scores,
        ai_use_pattern="mixed",
        process_notes=reason,
        indicator_metrics=indicator_metrics,
        evidence_blocks=evidence,
        profile_generated_at=_now_iso(),
    )


def _write_tmp_rclog(chat_history_json: Dict[str, Any], tmp_dir: Path) -> Path:
    import json

    tmp_dir.mkdir(parents=True, exist_ok=True)
    submission_id = _safe_submission_id(chat_history_json)
    out_path = tmp_dir / f"{submission_id}.json"
    out_path.write_text(json.dumps(chat_history_json, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def run_student_profiling(chat_history_json: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not isinstance(chat_history_json, dict):
            return _schema_valid_fallback_profile(
                "unknown_submission",
                "Profiling fallback: input is not a JSON object (dict).",
            )

        submission_id = _safe_submission_id(chat_history_json)

        # If the caller passes turns-only payload, it is not a valid RCLog structure for
        # rclog_to_turns. We treat it as partial and return a safe fallback.
        if "turns" in chat_history_json and not any(k in chat_history_json for k in ("events", "revisions", "messages")):
            return _schema_valid_fallback_profile(
                submission_id,
                "Profiling fallback: turns-only payload provided. Expected full RCLog JSON for the API runner.",
            )

        # Reuse existing profiling runner by writing the payload to a temp RCLog file.
        tmp_dir = Path(".tmp") / "aaie_api_rclogs"
        rclog_path = _write_tmp_rclog(chat_history_json, tmp_dir)

        profile = run_student_profiling_from_rclog(rclog_path=rclog_path)
        if isinstance(profile, dict) and profile:
            return profile

        return _schema_valid_fallback_profile(
            submission_id,
            "Profiling fallback: profiling runner returned an empty profile.",
        )

    except Exception as e:
        return _schema_valid_fallback_profile(
            "unknown_submission",
            f"Profiling error fallback: {type(e).__name__}: {e}",
        )
