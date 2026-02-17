import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from output_builder import build_output, validate_output, save_output, load_output
import json

def test_systematic_coverage():
    #mock inputs - systematic coverage
    alignment_summary = {
        "overall_alignment": 0.92,
        "status": "systematic_coverage",
        "total_prompts_analyzed": 10,
        "off_topic_prompts": 0
    }
    
    criterion_coverages = [
        {
            "criteria_id": "c1",
            "criteria_name": "Understanding",
            "weight": 0.5,
            "coverage_score": 0.92,
            "status": "well_covered",
            "prompts_matched": 5,
            "unmatched_keywords": []
        },
        {
            "criteria_id": "c2",
            "criteria_name": "Application",
            "weight": 0.5,
            "coverage_score": 0.92,
            "status": "well_covered",
            "prompts_matched": 5,
            "unmatched_keywords": []
        }
    ]
    
    flags = []
    
    gaps_by_criterion = {
        "c1": [],
        "c2": []
    }
    
    depths_by_criterion = {
        "c1": "deep",
        "c2": "moderate"
    }
    
    #build output
    filepath = build_output(
        submission_id="test_001",
        rubric_id="rub_test_001",
        domain="Test Domain",
        alignment_summary=alignment_summary,
        criterion_coverages=criterion_coverages,
        flags=flags,
        gaps_by_criterion=gaps_by_criterion,
        depths_by_criterion=depths_by_criterion
    )
    
    #validate
    output = load_output(filepath)
    assert validate_output(output), "Output validation failed"
    assert output["alignment_summary"]["status"] == "systematic_coverage"
    assert len(output["rubric_coverage"]) == 2
    assert output["rubric_coverage"][0]["engagement_depth"] == "deep"
    
    #cleanup
    os.remove(filepath)
    
    print("Test systematic coverage output: Pass")


def test_partial_coverage():
    #mock inputs - partial coverage with gaps and flags
    alignment_summary = {
        "overall_alignment": 0.58,
        "status": "partial_coverage",
        "total_prompts_analyzed": 6,
        "off_topic_prompts": 1
    }
    
    criterion_coverages = [
        {
            "criteria_id": "c1",
            "criteria_name": "Understanding",
            "weight": 0.5,
            "coverage_score": 0.48,
            "status": "undercovered",
            "prompts_matched": 1,
            "unmatched_keywords": ["concept", "definition"]
        },
        {
            "criteria_id": "c2",
            "criteria_name": "Application",
            "weight": 0.5,
            "coverage_score": 0.68,
            "status": "adequately_covered",
            "prompts_matched": 2,
            "unmatched_keywords": ["example"]
        }
    ]
    
    flags = [
        {
            "type": "rubric_gap",
            "severity": "medium",
            "criteria_id": "c1",
            "message": "Coverage is 0.48, below 0.50 threshold."
        },
        {
            "type": "off_topic_questions",
            "severity": "medium",
            "criteria_id": None,
            "message": "1 prompt(s) do not match any criterion."
        }
    ]
    
    gaps_by_criterion = {
        "c1": ["No questions about key areas (concept, definition)."],
        "c2": ["No questions about key areas (example)."]
    }
    
    depths_by_criterion = {
        "c1": "surface",
        "c2": "moderate"
    }
    
    #build output
    filepath = build_output(
        submission_id="test_002",
        rubric_id="rub_test_002",
        domain="Test Domain",
        alignment_summary=alignment_summary,
        criterion_coverages=criterion_coverages,
        flags=flags,
        gaps_by_criterion=gaps_by_criterion,
        depths_by_criterion=depths_by_criterion
    )
    
    #validate
    output = load_output(filepath)
    assert validate_output(output), "Output validation failed"
    assert output["alignment_summary"]["status"] == "partial_coverage"
    assert len(output["flags"]) == 2
    assert len(output["rubric_coverage"][0]["gaps"]) > 0
    
    #cleanup
    os.remove(filepath)
    
    print("Test partial coverage output with gaps and flags: Pass")


def test_save_and_load():
    #test saving and loading output
    alignment_summary = {
        "overall_alignment": 0.75,
        "status": "broad_coverage",
        "total_prompts_analyzed": 8,
        "off_topic_prompts": 0
    }
    
    criterion_coverages = [
        {
            "criteria_id": "c1",
            "criteria_name": "Test Criterion",
            "weight": 1.0,
            "coverage_score": 0.75,
            "status": "adequately_covered",
            "prompts_matched": 3,
            "unmatched_keywords": []
        }
    ]
    
    filepath = build_output(
        submission_id="test_003",
        rubric_id="rub_test_003",
        domain="Test Domain",
        alignment_summary=alignment_summary,
        criterion_coverages=criterion_coverages,
        flags=[],
        gaps_by_criterion={"c1": []},
        depths_by_criterion={"c1": "moderate"}
    )
    
    #load
    loaded = load_output(filepath)
    
    #verify
    assert loaded["submission_id"] == "test_003"
    assert loaded["alignment_summary"]["overall_alignment"] == 0.75
    
    #cleanup
    os.remove(filepath)
    
    print("Test save and load output: Pass")




if __name__ == "__main__":
    test_systematic_coverage()
    test_partial_coverage()
    test_save_and_load()