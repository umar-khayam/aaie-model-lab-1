import pytest

from revision_chain_analysis.student_profiling.summary.summary_generator import build_process_notes


def test_correct_template_for_each_pattern():
    scores = {
        "generator_only": 0.82,
        "reviser": 0.74,
        "planner_checker": 0.67,
        "mixed": 0.55,
    }

    out1 = build_process_notes("generator_only", scores)
    assert "relied primarily on the AI to generate content" in out1

    out2 = build_process_notes("reviser", scores)
    assert "created their own drafts" in out2

    out3 = build_process_notes("planner_checker", scores)
    assert "planning, clarification and checking quality" in out3

    out4 = build_process_notes("mixed", scores)
    assert "balanced mix of behaviours" in out4


def test_unknown_pattern_raises():
    with pytest.raises(KeyError):
        build_process_notes("not_a_real_pattern", {})


def test_scores_are_not_included_in_mvp_output():
    out = build_process_notes("mixed", {"mixed": 0.5})
    assert "Pattern score" not in out
    assert "%" not in out
