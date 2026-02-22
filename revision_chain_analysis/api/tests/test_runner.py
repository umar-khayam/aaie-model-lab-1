from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

# Ensure repo root is on sys.path so `revision_chain_analysis` imports work
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from revision_chain_analysis.api.runner import run_student_profiling

try:
    from jsonschema import Draft7Validator  # type: ignore[import]
except ImportError:
    Draft7Validator = None


SCHEMA_PATH = Path("revision_chain_analysis/student_profiling/schema/output_schema.json")
TEST_RCLOG_PATH = Path("revision_chain_analysis/student_profiling/test_files/rclog_MFA_example.json")


def _load_schema() -> Dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate_schema(profile: Dict[str, Any]) -> None:
    """
    If jsonschema is installed, validate. If not, do basic key checks.
    """
    required_keys = {"submission_id", "scores", "ai_use_pattern", "process_notes"}
    assert required_keys.issubset(profile.keys())

    scores = profile.get("scores", {})
    assert "critical_thinking_score" in scores
    assert "problem_solving_score" in scores
    assert "engagement_score" in scores

    if Draft7Validator is None:
        return

    schema = _load_schema()
    v = Draft7Validator(schema)
    errors = list(v.iter_errors(profile))
    if errors:
        msgs = []
        for e in errors:
            path = ".".join(str(p) for p in e.path)
            msgs.append(f"{path}: {e.message}")
        raise AssertionError("Schema validation failed:\n" + "\n".join(msgs))


def _load_test_rclog() -> Dict[str, Any]:
    assert TEST_RCLOG_PATH.exists(), f"Missing test RCLog file: {TEST_RCLOG_PATH}"
    return json.loads(TEST_RCLOG_PATH.read_text(encoding="utf-8"))


def test_complete_rclog_produces_schema_valid_profile() -> None:
    payload = _load_test_rclog()
    profile = run_student_profiling(payload)

    _validate_schema(profile)

    scores = profile["scores"]
    assert 0.0 <= scores["critical_thinking_score"] <= 1.0
    assert 0.0 <= scores["problem_solving_score"] <= 1.0
    assert 0.0 <= scores["engagement_score"] <= 1.0


def test_turns_only_payload_returns_fallback_profile() -> None:
    # API runner expects full RCLog JSON. Turns-only payload should return fallback.
    payload = {
        "submission_id": "rc_test_turns_only_0001",
        "turns": [
            {"role": "student", "text": "Can you help me plan my essay?", "timestamp": "2025-12-01T10:00:00Z"},
            {"role": "assistant", "text": "Sure. Here is a structure.", "timestamp": "2025-12-01T10:00:10Z"},
        ],
    }
    profile = run_student_profiling(payload)

    _validate_schema(profile)
    assert isinstance(profile["process_notes"], str)
    assert "fallback" in profile["process_notes"].lower() or "error" in profile["process_notes"].lower()


def test_malformed_input_returns_fallback_profile() -> None:
    # not a dict -> must not crash
    profile = run_student_profiling("this is not json")  # type: ignore[arg-type]

    _validate_schema(profile)
    assert "fallback" in profile["process_notes"].lower() or "error" in profile["process_notes"].lower()
