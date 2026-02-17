"""
Student Interaction Profile assembler.

Assembles outputs into a single JSON object that follows the
StudentInteractionProfile schema (schema/output_schema.json).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from jsonschema import Draft7Validator  # type: ignore[import]
except ImportError: 
    Draft7Validator = None 


@dataclass(frozen=True)
class Scores:
    critical_thinking_score: float
    problem_solving_score: float
    engagement_score: float

    def to_dict(self):
        return {
            "critical_thinking_score": float(self.critical_thinking_score),
            "problem_solving_score": float(self.problem_solving_score),
            "engagement_score": float(self.engagement_score),
        }


@dataclass(frozen=True)
class EvidenceBlocks:
    critical_thinking: List[str]
    problem_solving: List[str]
    engagement: List[str]
    ai_use_pattern: Optional[List[str]] = None  

    def to_schema_explainability(
        self,
        *,
        ct_conf: float,
        ps_conf: float,
        eng_conf: float,
        pattern_conf: float,
    ):
        return {
            "critical_thinking": {
                "confidence": float(_clamp01(ct_conf)),
                "evidence": list(self.critical_thinking or []),
            },
            "problem_solving": {
                "confidence": float(_clamp01(ps_conf)),
                "evidence": list(self.problem_solving or []),
            },
            "engagement": {
                "confidence": float(_clamp01(eng_conf)),
                "evidence": list(self.engagement or []),
            },
            "ai_use_pattern": {
                "confidence": float(_clamp01(pattern_conf)),
                "evidence": list(self.ai_use_pattern or []),
            },
        }


def _clamp01(x: float):
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return float(x)


def compute_pattern_confidence_from_distribution(prompt_type_distribution: Dict[str, Any]):
    if not isinstance(prompt_type_distribution, dict) or not prompt_type_distribution:
        return 0.0

    total = 0
    max_v = 0
    for v in prompt_type_distribution.values():
        try:
            iv = int(v)
        except Exception:
            continue
        if iv < 0:
            iv = 0
        total += iv
        if iv > max_v:
            max_v = iv

    if total <= 0:
        return 0.0
    return max_v / total


def normalise_indicator_metrics(
    *,
    critical_thinking: Dict[str, Any],
    problem_solving: Dict[str, Any],
    engagement: Dict[str, Any],
    prompt_type_distribution: Dict[str, Any],
) :
    return {
        "critical_thinking": dict(critical_thinking or {}),
        "problem_solving": dict(problem_solving or {}),
        "engagement": dict(engagement or {}),
        "prompt_type_distribution": dict(prompt_type_distribution or {}),
    }


def build_student_interaction_profile(
    *,
    submission_id: str,
    scores: Scores,
    ai_use_pattern: str,
    process_notes: str,
    indicator_metrics: Dict[str, Any],
    evidence_blocks: EvidenceBlocks,
    profile_generated_at: Optional[str] = None,
):
    if profile_generated_at is None:
        profile_generated_at = datetime.now(timezone.utc).isoformat()

    # Pull out distribution from indicator_metrics (schema expects it inside indicator_metrics)
    prompt_dist = {}
    if isinstance(indicator_metrics, dict):
        prompt_dist = indicator_metrics.get("prompt_type_distribution") or {}

    # Confidence choices:
    # - CT/PS/ENG confidence: use the scores directly (already in 0..1)
    # - AI use pattern confidence: dominance in prompt distribution
    ct_conf = scores.critical_thinking_score
    ps_conf = scores.problem_solving_score
    eng_conf = scores.engagement_score
    pattern_conf = compute_pattern_confidence_from_distribution(prompt_dist)

    profile: Dict[str, Any] = {
        "submission_id": submission_id,
        "profile_generated_at": profile_generated_at,
        "scores": scores.to_dict(),
        "ai_use_pattern": ai_use_pattern,
        "process_notes": process_notes,
        "indicator_metrics": dict(indicator_metrics or {}),
        "explainability_evidence": evidence_blocks.to_schema_explainability(
            ct_conf=ct_conf,
            ps_conf=ps_conf,
            eng_conf=eng_conf,
            pattern_conf=pattern_conf,
        ),
    }

    return profile

def load_profile_schema(schema_path: Path) :
    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_profile_against_schema(profile: Dict[str, Any], schema_path: Path) -> None:
    if Draft7Validator is None:
        print("[WARN] jsonschema not installed; schema validation skipped.")
        return

    schema = load_profile_schema(schema_path)
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(profile))
    if errors:
        msgs = []
        for e in errors:
            path = ".".join(str(p) for p in e.path)
            msgs.append(f"{path}: {e.message}")
        raise ValueError("StudentInteractionProfile failed schema validation:\n" + "\n".join(msgs))


def save_profile_json(profile: Dict[str, Any], output_dir: Path, filename_stem: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{filename_stem}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    return out_path
