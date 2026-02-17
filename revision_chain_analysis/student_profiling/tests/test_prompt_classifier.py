import pytest

from revision_chain_analysis.student_profiling.prompt_classifier.prompt_classifier import (
    load_prompt_type_rules,
    classify_prompt,
    classify_chat_turns,
    compute_prompt_type_distribution,
    run_prompt_type_classification,
)


@pytest.fixture(scope="module")
def rules():
    return load_prompt_type_rules()


def test_classify_prompt_generate_content(rules):
    text = "Using this outline, draft an academic introduction about zero-trust."
    pt = classify_prompt(text, rules)
    assert pt == "generate_content"


def test_classify_prompt_revise_content(rules):
    text = "Refine this outline into more detailed section headings with bullet points."
    pt = classify_prompt(text, rules)
    assert pt == "revise_content"


def test_classify_prompt_plan_structure(rules):
    text = "Give me a high-level outline for a zero-trust essay."
    pt = classify_prompt(text, rules)
    assert pt == "plan_structure"


def test_classify_prompt_check_quality(rules):
    text = "Does this answer address the prompt and is it correct?"
    pt = classify_prompt(text, rules)
    assert pt == "check_quality"


def test_classify_chat_turns_and_distribution(rules):
    turns = [
        {"turn_index": 0, "role": "student", "text": "Give me a high-level outline."},
        {"turn_index": 1, "role": "assistant", "text": "Here is an outline."},
        {"turn_index": 2, "role": "student", "text": "Refine this outline."},
        {"turn_index": 3, "role": "assistant", "text": "Here is a refined outline."},
        {"turn_index": 4, "role": "student", "text": "Now draft the introduction."},
        {"turn_index": 5, "role": "assistant", "text": "Here is an introduction."},
    ]

    classified = classify_chat_turns(turns, rules)
    dist = compute_prompt_type_distribution(classified)

    # Check that student turns have prompt_type
    student_turns = [t for t in classified if t["role"] == "student"]
    assert all("prompt_type" in t for t in student_turns)

    # Basic behavioural expectations
    assert dist["plan_structure"] == 1
    assert dist["revise_content"] == 1
    assert dist["generate_content"] == 1


def test_run_prompt_type_classification_wrapper():
    rules = load_prompt_type_rules()
    turns = [
        {"turn_index": 0, "role": "student", "text": "Explain zero-trust architecture."},
        {"turn_index": 1, "role": "assistant", "text": "Zero-trust is based on ..."},
    ]

    classified, dist = run_prompt_type_classification(turns)

    # Wrapper should not change length
    assert len(classified) == len(turns)

    # Distribution should include at least one understand_prompt
    assert dist["understand_prompt"] == 1
