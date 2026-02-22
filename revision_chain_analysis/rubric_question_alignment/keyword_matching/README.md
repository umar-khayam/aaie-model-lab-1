# RQA - Keyword Matching

## Overview
This module implements keyword-based relevance scoring to match student prompts to rubric criteria. It analyses how well students' questions to LLMs align with assessment criteria by calculating coverage scores and identifying gaps in engagement.

This module helps educators to:
* Assess whether students are engaging with all aspects of assessment criteria.
* Identify which rubric criteria receive adequate attention in student and LLM interactions.
* Detect off-topic questions that don't align with any assessment criterion, such as completion requests.
* Measure overall alignment between student inquiry patterns and learning objectives.

## Module Components

### keyword_matcher.py
Contains functions for matching individual prompts to criteria and calculating relevance scores:
* match_prompts_to_criterion() - Matches prompts to specific criteria using keyword matching.
* calculate_relevance_score() - Calculates 0-1 relevance score based on keyword matches.

### coverage_calculator.py
Contains functions for calculating coverage metrics across all criteria:
* calculate_criterion_coverage() - Calculates coverage for individual criteria.
* calculate_overall_alignment() - Calculates weighted average alignment across all criteria.
* calculate_off_topic_prompts() - Counts prompts that don't match any criterion.

### output_samples/
Contains example outputs demonstrating complete criterion coverage analysis with gap arrays showing unmatched keywords and prompts.

## Input Data Format
This module receives input in the following format:
{
  "parsed_chat": [
    {
      "prompt": "Can you elaborate on the core principles of zero-trust?",
      "turn_index": 0
    },
    {
      "prompt": "How does micro-segmentation work within a zero-trust framework?",
      "turn_index": 1
    }
  ],
  "rubric_keywords": {
    "rubric_id": "rub_it_0001",
    "domain": "Information Technology",
    "criteria": [
      {
        "criterion_id": "c1",
        "name": "Conceptual Understanding",
        "weight": 0.5,
        "keywords": ["conceptual", "understanding", "demonstrates", "deep"]
      },
      {
        "criterion_id": "c2",
        "name": "Application to Real-World Scenarios",
        "weight": 0.5,
        "keywords": ["application", "realworld", "scenarios", "applies"]
      }
    ]
  }
}


## Coverage Status Categories

Criterion Coverage:
* well_covered (>= 0.80) - Strong engagement with criterion
* adequately_covered (0.50-0.79) - Sufficient engagement
* undercovered (0.20-0.49) - Limited engagement
* significantly_undercovered (< 0.20) - Minimal or no engagement

Overall Alignment:
* systematic_coverage (>= 0.85) - Comprehensive engagement across criteria
* broad_coverage (0.70-0.84) - Good engagement with most criteria
* partial_coverage (0.55-0.69) - Moderate engagement with gaps
* minimal_coverage (< 0.55) - Significant gaps in criterion coverage

## Score Calculation

### Relevance Score Calculation
Each prompt is scored against a criterion's keywords on a 0-1 scale:

relevance_score = (0.6 x base_score) + (0.4 x frequency_score)

* base_score = matched_keywords / total_keywords
* frequency_score = total_occurrences / (total_keywords x 3)

#### Base Score (60% weight)
Measures diversity of the prompts, indicating how many different keywords were mentioned. For example, if the criterion has ["concept", 'definition", "principle'] and prompt mentions "concept" and "definition". The base_score would be 2/3 (0.67).

#### Frequency Score (40% weight)
Measures the depth of each prompt by calculating the frequency of the keywords in each prompt (capped at 3 per keyword). For example, prompt says "concept, concept, definition". The frequency_score the equals 3/(3 keywords × 3 max) = 3/9 = 0.33.

There is a 60/40 split to prioritize breadth over depth of prompts.

### Coverage Score Calculation
For each criterion, coverage is calculated as: 

coverage_score = (0.5 × keyword_coverage) + (0.5 × avg_relevance)

* keyword_coverage = matched_keywords / total_criterion_keywords
* avg_relevance = average of all matched prompts' relevance scores

### Overall Alignment Calculation
Weighted average across all criteria:

overall_alignment = Σ(coverage_score × weight) for all criteria

* weights sum to 1.0
