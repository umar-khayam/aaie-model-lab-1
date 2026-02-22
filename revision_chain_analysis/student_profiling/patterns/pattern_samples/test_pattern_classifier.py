import json
from pathlib import Path

from revision_chain_analysis.student_profiling.patterns.pattern_classifier import (
    classify_ai_use_pattern,
    PATTERN_GENERATOR_ONLY,
    PATTERN_REVISER,
    PATTERN_PLANNER_CHECKER,
    PATTERN_MIXED,
)

SAMPLES_DIR = Path(__file__).parent


def _load_sample(name: str):
    with open(SAMPLES_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def test_generator_only_sample():
    sample = _load_sample("generator_only_sample.json")
    pattern = classify_ai_use_pattern(
        sample["prompt_distribution"],
        sample["ps_indicators"],
        sample["ct_indicators"],
    )
    assert pattern == PATTERN_GENERATOR_ONLY
    assert pattern == sample["expected_pattern"]


def test_reviser_sample():
    sample = _load_sample("reviser_sample.json")
    pattern = classify_ai_use_pattern(
        sample["prompt_distribution"],
        sample["ps_indicators"],
        sample["ct_indicators"],
    )
    assert pattern == PATTERN_REVISER
    assert pattern == sample["expected_pattern"]


def test_planner_checker_sample():
    sample = _load_sample("planner_checker_sample.json")
    pattern = classify_ai_use_pattern(
        sample["prompt_distribution"],
        sample["ps_indicators"],
        sample["ct_indicators"],
    )
    assert pattern == PATTERN_PLANNER_CHECKER
    assert pattern == sample["expected_pattern"]


def test_boundary_generator_vs_reviser_sample():
    sample = _load_sample("boundary_generator_vs_reviser_sample.json")
    pattern = classify_ai_use_pattern(
        sample["prompt_distribution"],
        sample["ps_indicators"],
        sample["ct_indicators"],
    )
    # generator_only wins on boundary
    assert pattern == PATTERN_GENERATOR_ONLY
    assert pattern == sample["expected_pattern"]


def test_missing_keys_defaults_to_mixed():
    prompt_distribution = {}  # everything zero
    ps_indicators = {}
    ct_indicators = {}

    pattern = classify_ai_use_pattern(
        prompt_distribution,
        ps_indicators,
        ct_indicators,
    )

    assert pattern == PATTERN_MIXED
