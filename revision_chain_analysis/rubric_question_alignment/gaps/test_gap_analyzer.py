from gap_analyzer import identify_gaps, generate_flags, generate_gaps


def _find(flags, flag_type, criteria_id=None):
    return [
        f for f in flags
        if f["type"] == flag_type and (criteria_id is None or f["criteria_id"] == criteria_id)
    ]


def _find_msg(flags, flag_type, criteria_id, text):
    return [
        f for f in flags
        if f["type"] == flag_type
        and f["criteria_id"] == criteria_id
        and text in f["message"]
    ]


def test_rubric_gap_high():
    flags = identify_gaps({"C1": 0.20}, {"C1": 0.20}, {"C1": 3}, 1)
    assert _find(flags, "rubric_gap", "C1")[0]["severity"] == "high"


def test_rubric_gap_medium():
    flags = identify_gaps({"C1": 0.40}, {"C1": 0.20}, {"C1": 3}, 1)
    assert _find(flags, "rubric_gap", "C1")[0]["severity"] == "medium"


def test_no_rubric_gap_when_coverage_is_good():
    flags = identify_gaps({"C1": 0.80}, {"C1": 0.20}, {"C1": 3}, 1)
    assert _find(flags, "rubric_gap", "C1") == []


def test_high_weight_undercovered_as_coverage_issue():
    flags = identify_gaps({"C1": 0.55}, {"C1": 0.80}, {"C1": 3}, 1)
    hit = _find_msg(flags, "coverage_issue", "C1", "High-weight")
    assert hit[0]["severity"] == "high"


def test_minimal_prompts_as_coverage_issue():
    flags = identify_gaps({"C1": 0.90}, {"C1": 0.20}, {"C1": 1}, 1)
    hit = _find_msg(flags, "coverage_issue", "C1", "Minimal prompts")
    assert hit[0]["severity"] == "low"


def test_coverage_issue_flag_summary_created():
    coverage = {"C1": 0.40, "C2": 0.90, "C3": 0.20}
    weights = {"C1": 0.20, "C2": 0.20, "C3": 0.20}
    counts = {"C1": 2, "C2": 2, "C3": 2}

    flags = identify_gaps(coverage, weights, counts, 3)

    summary = _find(flags, "coverage_issue")[0]
    assert summary["severity"] == "medium"
    assert summary["criteria_id"] is None
    assert "2 out of 3" in summary["message"]


def test_off_topic_flag_added_from_int():
    out = generate_flags(
        coverage={"C1": 0.90},
        criteria_weights={"C1": 0.20},
        prompt_counts={"C1": 2},
        total_criteria=1,
        off_topic_prompts=2,
        unmatched_keywords={"C1": []},
    )
    flags = out["flags"]
    assert _find(flags, "off_topic_questions")[0]["severity"] == "medium"


def test_generate_gaps_empty_when_well_covered():
    gaps = generate_gaps({"C1": 0.85}, {"C1": ["penetration testing"]})
    assert gaps["C1"] == []


def test_generate_gaps_when_undercovered():
    gaps = generate_gaps({"C1": 0.60}, {"C1": ["penetration testing", "vulnerability scanning"]})
    assert len(gaps["C1"]) >= 1


def test_real_world_scenario():
    out = generate_flags(
        coverage={"C1": 0.40, "C2": 0.55, "C3": 0.82},
        criteria_weights={"C1": 0.30, "C2": 0.80, "C3": 0.20},
        prompt_counts={"C1": 2, "C2": 1, "C3": 4},
        total_criteria=3,
        off_topic_prompts=1,
        unmatched_keywords={
            "C1": ["difference", "trade-off"],
            "C2": ["penetration testing", "vulnerability scanning"],
            "C3": ["ignored"],
        },
    )

    flags = out["flags"]
    gaps = out["gaps"]

    assert len(_find(flags, "rubric_gap", "C1")) == 1
    assert len(_find(flags, "coverage_issue", "C2")) == 2  # FIXED: Changed from >= 1 to == 2
    assert len(_find(flags, "off_topic_questions")) == 1

    assert gaps["C3"] == []
    assert len(gaps["C1"]) >= 1
    assert len(gaps["C2"]) >= 1


if __name__ == "__main__":
    test_rubric_gap_high()
    test_rubric_gap_medium()
    test_no_rubric_gap_when_coverage_is_good()
    test_high_weight_undercovered_as_coverage_issue()
    test_minimal_prompts_as_coverage_issue()
    test_coverage_issue_flag_summary_created()
    test_off_topic_flag_added_from_int()
    test_generate_gaps_empty_when_well_covered()
    test_generate_gaps_when_undercovered()
    test_real_world_scenario()
    print("All gap analyzer tests passed.")