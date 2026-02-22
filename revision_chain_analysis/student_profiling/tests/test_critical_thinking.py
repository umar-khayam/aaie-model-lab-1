import pytest

from revision_chain_analysis.student_profiling.indicators.critical_thinking import (
    detect_explanation_prompts,
    detect_verification_prompts,
    detect_comparison_prompts,
    detect_evidence_prompts,
    compute_ct_indicators_and_evidence,
)


def _wrap_student(text: str):
    return [{"role": "student", "text": text}]


def test_explanation_prompt_detects_explain():
    turns = _wrap_student("Can you explain why SMS based MFA is weaker?")
    assert detect_explanation_prompts(turns) == 1
    assert detect_verification_prompts(turns) == 0


def test_verification_prompt_detects_is_this_correct():
    turns = _wrap_student("Is this explanation correct for phishing resistant MFA?")
    assert detect_verification_prompts(turns) == 1
    assert detect_explanation_prompts(turns) == 0


def test_comparison_prompt_detects_difference_between():
    turns = _wrap_student("What is the difference between SMS and app based MFA?")
    assert detect_comparison_prompts(turns) == 1
    assert detect_explanation_prompts(turns) == 0


def test_evidence_prompt_detects_source():
    turns = _wrap_student("Can you provide any evidence or sources for this claim?")
    assert detect_evidence_prompts(turns) == 1
    assert detect_explanation_prompts(turns) == 0


def test_compute_ct_indicators_and_evidence_combined():
    turns = [
        {"role": "student", "text": "Can you explain why SMS based MFA is weaker?"},
        {"role": "assistant", "text": "..."},  # ignored
        {"role": "student", "text": "Is this explanation correct for phishing resistant MFA?"},
        {"role": "student", "text": "Are there any studies or evidence that support this?"},
    ]

    counts, evidence = compute_ct_indicators_and_evidence(turns, max_snippets=3)

    assert counts["explanation_prompts"] == 1
    assert counts["verification_prompts"] == 1
    assert counts["comparison_prompts"] == 0
    assert counts["evidence_prompts"] == 1

    assert len(evidence) >= 2
    assert any("explain why sms based mfa is weaker" in e.lower() for e in evidence)
    assert any("is this explanation correct" in e.lower() for e in evidence)
