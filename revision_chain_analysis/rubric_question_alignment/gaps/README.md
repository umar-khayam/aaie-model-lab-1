# Rubric Coverage Gap Analyzer

This module is part of the Rubric–Question Alignment (RQA) pipeline. Its purpose is to detect coverage gaps between rubric criteria and student prompts within a revision chain.

It analyses how well each rubric criterion is addressed and produces two outputs:

* **flags** which are structured, machine-readable indicators of coverage problems
* **gaps** which are human-readable descriptions of what is missing or under-explored

These outputs are used by downstream systems for diagnostics, reporting, and feedback generation.

## Overview

The gap analyzer uses the following inputs:

* Coverage per rubric criterion
* Importance (weight) per criterion
* Number of prompts linked to each criterion
* Unmatched rubric keywords per criterion (from keyword matching)
* Off-topic prompt count (from keyword matching)

Using these inputs, the module identifies weak, missing, or misaligned rubric coverage and produces structured outputs describing the issues.

## Output Structure

The module returns two things.

### Flags

Each flag is a dictionary with the following fields:
```json
{
  "type": "rubric_gap | coverage_issue | off_topic_questions",
  "severity": "high | medium | low",
  "criteria_id": "string | null",
  "message": "string"
}
```

Valid flag types are:

* `rubric_gap`
* `coverage_issue`
* `off_topic_questions`

### Gaps

Gaps are returned per criterion as a list of short natural language descriptions explaining what was not sufficiently explored.

Example:
```json
{
  "C1": ["No questions about key areas (difference, trade-off)."],
  "C2": ["No questions about key areas (penetration testing, vulnerability scanning)."],
  "C3": []
}
```

## Thresholds and Rules

### rubric_gap

Triggered when coverage for a criterion is below 0.50.

* If coverage is below 0.30, the severity is **high**
* Otherwise the severity is **medium**

### coverage_issue

Triggered for coverage patterns, including:

**High weight undercovered**
* Condition: weight ≥ 0.70 and coverage < 0.60
* Severity: high

**Minimal prompts**
* Condition: prompt count ≤ 1
* Severity: low

**Summary coverage issue**
* Condition: one or more criteria have coverage below 0.50
* Message format: "X out of Y criteria are undercovered"
* Severity: medium

### off_topic_questions

Triggered when off-topic prompt count is greater than 0. Severity is **medium**.

## Gaps Generation

Gaps are generated per criterion using unmatched rubric keywords.

**Rules:**

* If coverage is ≥ 0.80, the gaps list must be empty
* If coverage is < 0.80 and unmatched keywords exist, keywords are grouped into coherent gap descriptions
* If coverage is < 0.80 and no unmatched keywords exist, a generic gap is created indicating limited coverage

**Gap message format:**

* When unmatched keywords exist: All keywords are combined into a single message: `"No questions about key areas (keyword1, keyword2, ...)."`
* When no unmatched keywords provided: `"Limited coverage for this criterion, but no unmatched keywords were provided."`

## Main Functions

### identify_gaps

Generates `rubric_gap` and `coverage_issue` flags from coverage, weights, and prompt counts.

**Parameters:**
- `coverage`: Dict[str, float] - Coverage scores per criterion (0.0 to 1.0)
- `criteria_weights`: Optional[Dict[str, float]] - Importance weights per criterion
- `prompt_counts`: Optional[Dict[str, int]] - Number of prompts linked to each criterion
- `total_criteria`: Optional[int] - Total number of criteria (defaults to len(coverage))

**Returns:** List[Flag]

### generate_gaps

Generates a list of human-readable gaps per criterion using unmatched keywords and coverage context.

**Parameters:**
- `coverage`: Dict[str, float] - Coverage scores per criterion (0.0 to 1.0)
- `unmatched_keywords`: Optional[Dict[str, List[str]]] - Unmatched keywords per criterion

**Returns:** Dict[str, List[str]] - Gap descriptions per criterion

### generate_flags

Top-level function that returns both flags and gaps using inputs from the keyword matching and coverage pipeline.

**Parameters:**
- `coverage`: Dict[str, float] - Coverage scores per criterion (0.0 to 1.0)
- `criteria_weights`: Optional[Dict[str, float]] - Importance weights per criterion
- `prompt_counts`: Optional[Dict[str, int]] - Number of prompts linked to each criterion
- `total_criteria`: Optional[int] - Total number of criteria (defaults to len(coverage))
- `off_topic_prompts`: int - Count of prompts not matching any criterion (default: 0)
- `unmatched_keywords`: Optional[Dict[str, List[str]]] - Unmatched keywords per criterion

**Returns:** Dict[str, Any] with keys "flags" and "gaps"

## Inputs

### coverage

Dictionary mapping criterion ID to coverage score between 0.0 and 1.0.

### criteria_weights

Dictionary mapping criterion ID to importance weight.

### prompt_counts

Dictionary mapping criterion ID to number of linked prompts.

### unmatched_keywords

Dictionary mapping criterion ID to a list of rubric keywords that had no or minimal student engagement.

### off_topic_prompts

Integer count of prompts that did not match any rubric criterion.

## Running Tests

From the repository root, run:
```bash
python revision_chain_analysis/rubric_question_alignment/gaps/test_gap_analyzer.py
```

**Expected output:**
```
All gap analyzer tests passed.
```