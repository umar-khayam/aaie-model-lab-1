# Student Profiling Scoring Engine

## 1. Overview

The scoring engine normalises raw student interaction indicators into standardised scores (0.0 to 1.0) across three key dimensions: critical thinking, problem solving, and engagement. It converst raw student behavior indicators into normalised score by comparing them against predefined thresholds.

## 2. Files
- scoring_engine.py - Core scoring functionality
- scoring_thresholds.ymal - Threshold values for normalisation
- test_scoring_engine.py - Test script with JSON input/output
- scoring_samples/ - Sample outputs

## 3. Input
This module expects JSON files containing raw student interaction indicators:
```json
{"test_case": "example_case",
    "input_indicators": {
        "critical_thinking": {
            "explanation_prompts": 2,
            "verification_prompts": 1,
            "comparison_prompts": 1,
            "evidence_prompts": 1
        },
        "problem_solving": {
            "decomposition_prompts": 3,
            "iterative_revision_count": 2,
            "self_proposed_content_turns": 2,
            "feedback_uptake_events": 3
        },
        "engagement": {
            "student_token_ratio": 0.6,
            "student_turn_count": 8,
            "distinct_episode_types": 2,
            "session_minutes": 45
        }
    }
}
```

## 3. Output

Output JSON files contain the normalised scores (0.0. to 1.0).
Examples: [scoring_samples/](./scoring_samples/)

Structure:
```json
{
    "test_case": "example_case",
    "scores": {
        "critical_thinking": {
            "explanation_prompts": 0.67,
            "verification_prompts": 0.5,
            "comparison_prompts": 0.33,
            "evidence_prompts": 0.5
        },
        "problem_solving": {
            "decomposition_prompts": 0.75,
            "iterative_revision_count": 0.5,
            "self_proposed_content_turns": 0.67,
            "feedback_uptake_events": 1.0
        },
        "engagement": {
            "student_token_ratio": 0.8,
            "student_turn_count": 0.67,
            "distinct_episode_types": 0.5,
            "session_minutes": 0.75
        }
    }
}
```
