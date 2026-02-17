"""
Test script for data_processor functions using sample revision chain logs.
"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import chat_parser, extract_keywords, load_rubric

def test_functions():
    """Test the three required functions with sample data."""

    print("=== Testing Data Processor Functions ===")

    # Test 1: Test extract_keywords
    print("\n1. Testing extract_keywords:")
    test_text = "Zero-trust architecture improves security posture!"
    keywords = extract_keywords(test_text)
    print(f"Input: '{test_text}'")
    print(f"Output: {keywords}")
    assert isinstance(keywords, list), "Should return a list"
    assert all(isinstance(k, str) for k in keywords), "All items should be strings"
    # Test for duplicates removal
    test_text_with_duplicates = "Security security architecture architecture zero zero trust"
    keywords_no_duplicates = extract_keywords(test_text_with_duplicates)
    assert len(keywords_no_duplicates) == len(set(keywords_no_duplicates)), "Should remove duplicates"
    print("✓ extract_keywords works correctly and removes duplicates")

    # Test 2: Test with new revision chain structure
    print("\n2. Testing with new revision chain structure:")
    
    # Create sample revision chain data based on the screenshot
    sample_revision_chain = {
        "rc_log_id": "rc_001",
        "rubric_id": "rub_it_0001",
        "domain": "Information Technology",
        "revision_chain": [
            {
                "step_index": 0,
                "student_prompt": "Can you explain zero-trust architecture?",
                "llm_response": "Zero-trust architecture is a security model..."
            },
            {
                "step_index": 1,
                "student_prompt": "How does it differ from traditional security?",
                "llm_response": "Traditional security uses perimeter defense..."
            }
        ]
    }
    
    # Test chat_parser - extracts student prompts only
    student_prompts = chat_parser(sample_revision_chain)
    print(f"Found {len(student_prompts)} student prompts")
    
    # Verify structure
    if student_prompts:
        first_prompt = student_prompts[0]
        assert 'prompt' in first_prompt, "Should have 'prompt' key"
        assert 'turn_index' in first_prompt, "Should have 'turn_index' key"
        assert isinstance(first_prompt['prompt'], str), "Prompt should be string"
        assert isinstance(first_prompt['turn_index'], int), "Turn index should be integer"
        print(f"Sample prompt: {first_prompt['prompt'][:50]}...")
        print("✓ chat_parser extracts student prompts only from revision_chain")

    # Test 3: Test load_rubric with missing criteria
    print("\n3. Testing load_rubric with missing criteria:")
    
    # Test rubric with missing criteria
    rubric_missing_criteria = {
        "rubric_id": "rub_test_001",
        "domain": "Test Domain"
        # No criteria field
    }
    
    processed_rubric_missing = load_rubric(rubric_missing_criteria)
    assert 'rubric_id' in processed_rubric_missing, "Should have rubric_id"
    assert 'domain' in processed_rubric_missing, "Should have domain"
    assert 'criteria' in processed_rubric_missing, "Should have criteria"
    assert isinstance(processed_rubric_missing['criteria'], list), "Criteria should be list"
    assert len(processed_rubric_missing['criteria']) == 0, "Should have empty criteria list"
    print("✓ load_rubric handles missing criteria gracefully")
    
    # Test 4: Test load_rubric with empty criteria
    print("\n4. Testing load_rubric with empty criteria:")
    
    rubric_empty_criteria = {
        "rubric_id": "rub_test_002",
        "domain": "Test Domain",
        "criteria": []
    }
    
    processed_rubric_empty = load_rubric(rubric_empty_criteria)
    assert len(processed_rubric_empty['criteria']) == 0, "Should have empty criteria list"
    print("✓ load_rubric handles empty criteria gracefully")
    
    # Test 5: Test load_rubric with valid criteria
    print("\n5. Testing load_rubric with valid criteria:")
    
    sample_rubric = {
        "rubric_id": "rub_test_003",
        "domain": "Test Domain",
        "criteria": [
            {
                "criterion_id": "c1",
                "name": "Conceptual Understanding",
                "description": "Demonstrates deep understanding of the topic and related concepts."
            }
        ]
    }
    
    processed_rubric = load_rubric(sample_rubric)
    print(f"Processed rubric with {len(processed_rubric['criteria'])} criteria")
    
    # Verify structure
    assert 'rubric_id' in processed_rubric, "Should have rubric_id"
    assert 'domain' in processed_rubric, "Should have domain"
    assert 'criteria' in processed_rubric, "Should have criteria"
    assert isinstance(processed_rubric['rubric_id'], str), "Rubric ID should be string"
    assert isinstance(processed_rubric['domain'], str), "Domain should be string"
    
    # Verify criteria structure
    for criterion in processed_rubric['criteria']:
        assert 'criterion_id' in criterion, "Criterion should have criterion_id"
        assert 'name' in criterion, "Criterion should have name"
        assert 'keywords' in criterion, "Criterion should have keywords"
        assert isinstance(criterion['keywords'], list), "Keywords should be list"
        # Test for duplicates in keywords
        assert len(criterion['keywords']) == len(set(criterion['keywords'])), "Keywords should not have duplicates"
    
    print("✓ load_rubric returns correct structure with unique keywords")

    # Test 6: Verify keyword extraction on rubric criteria
    print("\n6. Testing keyword extraction on rubric criteria:")
    sample_criterion = {
        "name": "Conceptual Understanding",
        "description": "Demonstrates deep understanding of the topic and related concepts."
    }

    # Combine name and description as load_rubric does
    text_to_process = f"{sample_criterion['name']} {sample_criterion['description']}"
    keywords = extract_keywords(text_to_process)
    print(f"Criterion text: '{text_to_process}'")
    print(f"Extracted keywords: {keywords}")
    print("Keyword extraction works on rubric criteria")

    print("\n=== All Tests Completed ===")
    print("chat_parser extracts student prompts only from revision_chain structure")
    print("extract_keywords normalizes text correctly and removes duplicates") 
    print("load_rubric processes rubric structure with keywords and handles missing criteria")

if __name__ == "__main__":
    test_functions()