from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from revision_chain_analysis.student_profiling.tools.rclog_to_turns import load_rclog, rclog_to_turns
from revision_chain_analysis.student_profiling.prompt_classifier.prompt_classifier import run_prompt_type_classification

from revision_chain_analysis.student_profiling.indicators.critical_thinking import compute_ct_indicators_and_evidence
from revision_chain_analysis.student_profiling.indicators.problem_solving import compute_PS_indicators_and_evidence
from revision_chain_analysis.student_profiling.indicators.engagement import compute_engagement_indicators_and_evidence

from revision_chain_analysis.student_profiling.scoring.scoring_engine import (
    score_critical_thinking,
    score_problem_solving,
    score_engagement,
    load_thresholds
)

from revision_chain_analysis.student_profiling.patterns.pattern_classifier import classify_ai_use_pattern
from revision_chain_analysis.student_profiling.summary.summary_generator import build_process_notes

from revision_chain_analysis.student_profiling.output.profile_builder import (
    Scores,
    EvidenceBlocks,
    build_student_interaction_profile,
    save_profile_json,
    validate_profile_against_schema,
)


def _to_counts_and_props(distribution: Dict[str, Any]):
    counts: Dict[str, int] = {}
    total = 0
    for k, v in (distribution or {}).items():
        try:
            iv = int(v)
        except Exception:
            iv = 0
        if iv < 0:
            iv = 0
        counts[k] = iv
        total += iv

    if total <= 0:
        props = {k: 0.0 for k in counts.keys()}
    else:
        props = {k: (counts[k] / total) for k in counts.keys()}

    return counts, props


def _normalise_ct(ct_out: Any) :
    if isinstance(ct_out, tuple) and len(ct_out) == 2:
        return dict(ct_out[0] or {}), list(ct_out[1] or [])
    # fallback: dict style
    if isinstance(ct_out, dict):
        return dict(ct_out.get("counts") or ct_out.get("critical_thinking") or {}), list(ct_out.get("evidence") or [])
    return {}, []


def _normalise_ps(ps_out: Any):
    if isinstance(ps_out, tuple) and len(ps_out) == 2:
        return dict(ps_out[0] or {}), list(ps_out[1] or [])
    if isinstance(ps_out, dict):
        return dict(ps_out.get("counts") or {}), list(ps_out.get("evidence") or [])
    return {}, []


def _normalise_eng(eng_out: Any) :
    if isinstance(eng_out, tuple) and len(eng_out) == 2:
        return dict(eng_out[0] or {}), list(eng_out[1] or [])
    if isinstance(eng_out, dict):
        return dict(eng_out.get("counts") or eng_out.get("metrics") or eng_out.get("engagement") or {}), list(eng_out.get("evidence") or [])
    return {}, []


def run_student_profiling_from_rclog(
    *,
    rclog_path: str | Path,
    output_dir: Optional[str | Path] = None,
    schema_path: Optional[str | Path] = None,
):
    rclog_path = Path(rclog_path)
    rclog = load_rclog(rclog_path)
    turns: List[Dict[str, Any]] = rclog_to_turns(rclog)

    submission_id = rclog.get("submission_id") or rclog.get("id") or rclog_path.stem

    # Prompt type classification
    classified_turns, distribution_raw = run_prompt_type_classification(turns)
    dist_counts, dist_props = _to_counts_and_props(distribution_raw or {})

    # Indicators + evidence (normalise return shapes)
    ct_counts, ct_evidence = _normalise_ct(compute_ct_indicators_and_evidence(turns))
    ps_counts, ps_evidence = _normalise_ps(compute_PS_indicators_and_evidence(turns, classified_turns))
    eng_metrics, eng_evidence = _normalise_eng(compute_engagement_indicators_and_evidence(turns, classified_turns))

    indicator_metrics = {
        "critical_thinking": ct_counts,
        "problem_solving": ps_counts,
        "engagement": eng_metrics,
        "prompt_type_distribution": dist_counts,
    }
    
    thresholds = load_thresholds()
    
    # scoring engine expects "session_minutes"
    if "session_time_minutes" in eng_metrics and "session_minutes" not in eng_metrics:
        eng_metrics["session_minutes"] = eng_metrics["session_time_minutes"]

    ct_score_dict = score_critical_thinking(ct_counts, thresholds)
    ps_score_dict = score_problem_solving(ps_counts, thresholds)
    eng_score_dict = score_engagement(eng_metrics, thresholds)

    # convert per-indicator normalised scores -> single dimension score (0..1)
    ct_score = sum(ct_score_dict.values()) / len(ct_score_dict) if ct_score_dict else 0.0
    ps_score = sum(ps_score_dict.values()) / len(ps_score_dict) if ps_score_dict else 0.0
    eng_score = sum(eng_score_dict.values()) / len(eng_score_dict) if eng_score_dict else 0.0

    scores = Scores(ct_score, ps_score, eng_score)
    
    # schema expects "session_time_minutes"
    if "session_minutes" in eng_metrics and "session_time_minutes" not in eng_metrics:
        eng_metrics["session_time_minutes"] = eng_metrics["session_minutes"]

    # AI use pattern (expects proportions)
    pattern = classify_ai_use_pattern(dist_props, ps_counts, ct_counts)

    # Process notes
    notes = build_process_notes(pattern, scores.to_dict())

    # Evidence blocks (schema requires explainability_evidence.ai_use_pattern too)
    # For MVP we can reuse a few snippets from other evidence as justification,
    # or leave empty list.
    pattern_evidence = []
    # simple heuristic: borrow 1-2 snippets if available
    for snippet in (ct_evidence + ps_evidence + eng_evidence):
        if snippet and snippet not in pattern_evidence:
            pattern_evidence.append(snippet)
        if len(pattern_evidence) >= 2:
            break

    evidence = EvidenceBlocks(
        critical_thinking=ct_evidence,
        problem_solving=ps_evidence,
        engagement=eng_evidence,
        ai_use_pattern=pattern_evidence,
    )

    # Build final profile (schema compliant)
    profile = build_student_interaction_profile(
        submission_id=submission_id,
        scores=scores,
        ai_use_pattern=pattern,
        process_notes=notes,
        indicator_metrics=indicator_metrics,
        evidence_blocks=evidence,
    )

    # Save output
    if output_dir is None:
        output_dir = Path("revision_chain_analysis/student_profiling/output/sample_profiles")
    else:
        output_dir = Path(output_dir)

    out_path = save_profile_json(profile, output_dir, filename_stem=submission_id)

    # Validate if schema is provided (recommended)
    if schema_path is None:
        schema_path = Path("revision_chain_analysis/student_profiling/schema/output_schema.json")
    schema_path = Path(schema_path)

    try:
        validate_profile_against_schema(profile, schema_path)
        print(f"[OK] Profile schema-valid. Written to: {out_path}")
    except Exception as e:
        print(f"[WARN] Wrote profile to {out_path} but schema validation failed:\n{e}")

    return profile
