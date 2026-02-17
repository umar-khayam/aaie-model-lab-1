import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keyword_matching import match_prompts_to_criterion, calculate_relevance_score
from coverage_calculator import (
    calculate_criterion_coverage,
    calculate_overall_alignment,
    calculate_off_topic_prompts
)


# Test Data
SAMPLE_PROMPTS = [
    {"prompt_id": 1, "text": "What is the definition of recursion?"},
    {"prompt_id": 2, "text": "Can you explain the concept of object-oriented programming?"},
    {"prompt_id": 3, "text": "Show me an example of binary search."},
    {"prompt_id": 4, "text": "How do I implement a linked list?"},
    {"prompt_id": 5, "text": "What's the weather like today?"},
    {"prompt_id": 6, "text": "Explain the principle of encapsulation with examples."},
]

SAMPLE_CRITERIA = [
    {
        "criteria_id": "C1",
        "criteria_name": "Core Concepts",
        "weight": 0.5,
        "keywords": ["definition", "concept", "principle", "theory"]
    },
    {
        "criteria_id": "C2",
        "criteria_name": "Application Skills",
        "weight": 0.5,
        "keywords": ["example", "implement", "application", "practice"]
    }
]


class TestKeywordMatcher:
    
    def test_match_prompts_to_criterion_basic(self):
        result = match_prompts_to_criterion(
            prompts=SAMPLE_PROMPTS,
            criterion_keywords=["definition", "concept", "principle"]
        )
        
        #should match prompts 1, 2, and 6
        assert len(result["matched_prompts"]) == 3
        matched_ids = [p["prompt_id"] for p in result["matched_prompts"]]
        assert 1 in matched_ids
        assert 2 in matched_ids
        assert 6 in matched_ids
    
    def test_match_prompts_tracks_unmatched_keywords(self):
        result = match_prompts_to_criterion(
            prompts=SAMPLE_PROMPTS,
            criterion_keywords=["definition", "concept", "axiom", "theorem"]
        )
        
        # "axiom" and "theorem" should be in unmatched_keywords
        assert "axiom" in result["unmatched_keywords"]
        assert "theorem" in result["unmatched_keywords"]
        # "definition" and "concept" should NOT be in unmatched
        assert "definition" not in result["unmatched_keywords"]
        assert "concept" not in result["unmatched_keywords"]
    
    def test_calculate_relevance_score_range(self):
        score1 = calculate_relevance_score(
            "What is the definition of recursion?",
            ["definition", "concept"]
        )
        assert 0 <= score1 <= 1
        
        score2 = calculate_relevance_score(
            "Unrelated text about weather",
            ["definition", "concept"]
        )
        assert score2 == 0
        
        score3 = calculate_relevance_score(
            "The definition, concept, and principle are fundamental",
            ["definition", "concept", "principle"]
        )
        assert 0 < score3 <= 1
    
    def test_calculate_relevance_score_keyword_matching(self):
        keywords = ["definition", "concept", "principle"]
        
        score_one = calculate_relevance_score("What is the definition?", keywords)
        score_two = calculate_relevance_score("The definition and concept are important.", keywords)
        score_three = calculate_relevance_score("The definition, concept, and principle matter.", keywords)
        
        assert score_one < score_two < score_three


class TestCoverageCalculator:
    
    def test_calculate_criterion_coverage_structure(self):
        matched_prompts = [
            {"prompt_id": 1, "text": "What is the definition?", "relevance_score": 0.8},
            {"prompt_id": 2, "text": "Explain the concept.", "relevance_score": 0.7}
        ]
        
        coverage = calculate_criterion_coverage(
            criterion_id="C1",
            criterion_name="Test Criterion",
            weight=0.5,
            matched_prompts=matched_prompts,
            criterion_keywords=["definition", "concept", "principle"]
        )
        
        #verify all required fields present
        assert "criteria_id" in coverage
        assert "criteria_name" in coverage
        assert "weight" in coverage
        assert "coverage_score" in coverage
        assert "status" in coverage
        assert "prompts_matched" in coverage
        assert "matched_prompt_ids" in coverage
        assert "unmatched_keywords" in coverage
        
        #verify values
        assert coverage["criteria_id"] == "C1"
        assert coverage["prompts_matched"] == 2
        assert coverage["matched_prompt_ids"] == [1, 2]
    
    def test_coverage_status_mapping(self):
        #test well_covered (≥0.80)
        coverage_high = calculate_criterion_coverage(
            criterion_id="C1",
            criterion_name="Test",
            weight=0.5,
            matched_prompts=[
                {"prompt_id": 1, "text": "definition concept principle", "relevance_score": 0.9}
            ],
            criterion_keywords=["definition", "concept", "principle"]
        )
        assert coverage_high["status"] == "well_covered"
        assert coverage_high["coverage_score"] >= 0.80
        
        #test adequately_covered (0.50-0.79)
        coverage_med = calculate_criterion_coverage(
            criterion_id="C2",
            criterion_name="Test",
            weight=0.5,
            matched_prompts=[
                {"prompt_id": 1, "text": "definition concept", "relevance_score": 0.6}
            ],
            criterion_keywords=["definition", "concept", "principle"]
        )
        assert coverage_med["status"] == "adequately_covered"
        assert 0.50 <= coverage_med["coverage_score"] < 0.80
        
        #test significantly_undercovered (<0.20)
        coverage_low = calculate_criterion_coverage(
            criterion_id="C3",
            criterion_name="Test",
            weight=0.5,
            matched_prompts=[],
            criterion_keywords=["definition", "concept", "principle"]
        )
        assert coverage_low["status"] == "significantly_undercovered"
        assert coverage_low["coverage_score"] < 0.20
    
    def test_calculate_overall_alignment_weighted_average(self):
        coverages = [
            {
                "criteria_id": "C1",
                "weight": 0.6,
                "coverage_score": 0.9,
                "matched_prompt_ids": [1, 2, 3]
            },
            {
                "criteria_id": "C2",
                "weight": 0.4,
                "coverage_score": 0.7,
                "matched_prompt_ids": [2, 4]
            }
        ]
        
        overall = calculate_overall_alignment(coverages, total_prompts=5)
        
        #expected: (0.9 * 0.6) + (0.7 * 0.4) = 0.54 + 0.28 = 0.82
        expected = 0.82
        assert abs(overall["overall_alignment"] - expected) < 0.01
    
    def test_overall_alignment_status_mapping(self):
        # systematic_coverage (≥0.85)
        coverage_systematic = [
            {"weight": 1.0, "coverage_score": 0.90, "matched_prompt_ids": [1, 2]}
        ]
        result = calculate_overall_alignment(coverage_systematic, total_prompts=2)
        assert result["status"] == "systematic_coverage"
        
        # broad_coverage (0.70-0.84)
        coverage_broad = [
            {"weight": 1.0, "coverage_score": 0.75, "matched_prompt_ids": [1]}
        ]
        result = calculate_overall_alignment(coverage_broad, total_prompts=2)
        assert result["status"] == "broad_coverage"
        
        # minimal_coverage (<0.55)
        coverage_minimal = [
            {"weight": 1.0, "coverage_score": 0.30, "matched_prompt_ids": [1]}
        ]
        result = calculate_overall_alignment(coverage_minimal, total_prompts=3)
        assert result["status"] == "minimal_coverage"
    
    def test_calculate_off_topic_prompts(self):
        all_prompts = SAMPLE_PROMPTS  # 6 prompts total
        matched_ids = {1, 2, 3, 4, 6}  # 5 matched
        
        off_topic = calculate_off_topic_prompts(all_prompts, matched_ids)
        assert off_topic == 1  # prompt 5 is off-topic
    
    def test_prompts_matching_multiple_criteria_counted_once(self):
        coverages = [
            {
                "criteria_id": "C1",
                "weight": 0.5,
                "coverage_score": 0.8,
                "matched_prompt_ids": [1, 2, 3]
            },
            {
                "criteria_id": "C2",
                "weight": 0.5,
                "coverage_score": 0.7,
                "matched_prompt_ids": [2, 3, 4]  # 2 and 3 overlap
            }
        ]
        
        overall = calculate_overall_alignment(coverages, total_prompts=5)
        
        # total unique matched prompts: {1, 2, 3, 4} = 4
        # off-topic: 5 - 4 = 1
        assert overall["off_topic_prompts"] == 1
        assert overall["total_prompts_analyzed"] == 5
    
    def test_total_prompts_analyzed_counts_correctly(self):
        coverages = [
            {"weight": 1.0, "coverage_score": 0.5, "matched_prompt_ids": [1, 2]}
        ]
        
        overall = calculate_overall_alignment(coverages, total_prompts=10)
        assert overall["total_prompts_analyzed"] == 10


class TestIntegrationScenarios:
    
    def test_complete_workflow(self):
        # test end-to-end workflow from matching to overall alignment
        # Step 1: Match prompts to each criterion
        all_matched_ids = set()
        criterion_coverages = []
        
        for criterion in SAMPLE_CRITERIA:
            # Match prompts
            match_result = match_prompts_to_criterion(
                prompts=SAMPLE_PROMPTS,
                criterion_keywords=criterion["keywords"]
            )
            
            # Calculate coverage
            coverage = calculate_criterion_coverage(
                criterion_id=criterion["criteria_id"],
                criterion_name=criterion["criteria_name"],
                weight=criterion["weight"],
                matched_prompts=match_result["matched_prompts"],
                criterion_keywords=criterion["keywords"]
            )
            
            criterion_coverages.append(coverage)
            all_matched_ids.update(coverage["matched_prompt_ids"])
        
        # Step 2: Calculate overall alignment
        overall = calculate_overall_alignment(
            criterion_coverages=criterion_coverages,
            total_prompts=len(SAMPLE_PROMPTS)
        )
        
        # Step 3: Verify results
        assert overall["overall_alignment"] > 0
        assert overall["status"] in [
            "systematic_coverage", "broad_coverage", 
            "partial_coverage", "minimal_coverage"
        ]
        assert overall["total_prompts_analyzed"] == len(SAMPLE_PROMPTS)
        
        # Calculate off-topic
        off_topic = calculate_off_topic_prompts(SAMPLE_PROMPTS, all_matched_ids)
        assert off_topic == overall["off_topic_prompts"]
    
    def test_empty_prompts(self):
        result = match_prompts_to_criterion(
            prompts=[],
            criterion_keywords=["test"]
        )
        assert len(result["matched_prompts"]) == 0
        
        coverage = calculate_criterion_coverage(
            criterion_id="C1",
            criterion_name="Test",
            weight=1.0,
            matched_prompts=[],
            criterion_keywords=["test"]
        )
        assert coverage["coverage_score"] == 0
        assert coverage["status"] == "significantly_undercovered"
    
    def test_no_keyword_matches(self):
        result = match_prompts_to_criterion(
            prompts=[{"prompt_id": 1, "text": "Completely unrelated content"}],
            criterion_keywords=["algorithm", "complexity", "optimization"]
        )
        
        assert len(result["matched_prompts"]) == 0
        assert len(result["unmatched_keywords"]) == 3


def run_all_tests():
    import traceback
    
    test_classes = [TestKeywordMatcher, TestCoverageCalculator, TestIntegrationScenarios]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
                print(f"Pass: {test_class.__name__}.{method_name}")
            except AssertionError as e:
                failed_tests.append((test_class.__name__, method_name, str(e)))
                print(f"Fail: {test_class.__name__}.{method_name}")
                print(f"  Error: {e}")
            except Exception as e:
                failed_tests.append((test_class.__name__, method_name, str(e)))
                print(f"Fail: {test_class.__name__}.{method_name}")
                print(f"  Exception: {e}")
                traceback.print_exc()
    
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    
    if failed_tests:
        print(f"\nFailed Tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  - {class_name}.{method_name}: {error}")
    else:
        print("\nAll tests passed!")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Run tests if executed directly
    success = run_all_tests()
    sys.exit(0 if success else 1)
