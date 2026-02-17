# Rubric Question Alignment Schema

## Overview

This folder contains the JSON schema used for the Rubric Question Alignment (RQA) module. Three sample outputs are included to demonstrate how the module represents different levels of alignment/relevance to the rubric.

## 1. Schema Importance

Rubric Question Alignment captures how closely a student's questions to an AI system align with the assessment grading criteria (rubric). This process analyzes the chat history and relevant rubric but does not analyze the final submission.

This schema defines:

* A summary of the alignment (score, status, off-topic question tracking)
* Quantitative coverage score for each rubric criterion
* Qualitative depth assessment for student engagement
* Flags for gaps in rubric alignment

This allows other RCA components to understand and process the alignment of student questions to the rubric.

## 2. Schema File

### `output_schema.json`

This file outlines the expected structure of all rubric coverage outputs.

It includes:

* `submission_id`
* `rubric_id`
* `domain`
* `alignment_summary` (overall_alignment, status, total_prompts_analyzed, off_topic_prompts)
* `rubric_coverage` (array of criterion-level results with criteria_id, criteria_name, weight, coverage_score, status, prompts_matched, engagement_depth, gaps)
* `flags` (warnings for rubric gaps, completion requests, or insufficient data)
* `quality_annotation`

Contributors should use this file to understand how the rubric alignment module formats its output and how other RCA components can consume it.

## 3. Understanding Coverage Scores

### 3.1 What Coverage Scores Measure

Coverage scores (0-1 scale) assess both the relevance and depth of students questions related to each rubric criterion. The score considers question relevance to the rubric criterion, and engagement depth.

### 3.2 Coverage Score Calculation

Coverage scores are initially calculated using keyword matching to identify direct terminology alignment between student questions and rubric criteria. The system will later evolve to a hybrid approach that combines keyword matching with semantic similarity analysis, enabling detection of conceptual relevance through natural language processing.

This dual approach ensures the system captures both explicit rubric terminology and semantically related questions that demonstrate criterion understanding, even when students use different phrasing.

## 4. Rubric Coverage Status Categories

The schema supports four coverage status labels for individual rubric criteria. Each describes the extent to which a student engaged with that specific criterion through their questioning.

### 4.1 well_covered

Coverage score ≥ 0.80. 
The student asked multiple relevant, in-depth questions addressing this criterion. 

### 4.2 adequately_covered

Coverage score 0.50-0.79. 
The student asked some relevant questions about this criterion but with moderate depth. 

### 4.3 undercovered

Coverage score 0.20-0.49. 
The student asked few relevant questions about this criterion, or questions lacked depth despite reasonable quantity. 

### 4.4 significantly_undercovered

Coverage score < 0.20. 
The student asked minimal or no questions addressing this criterion.

## 5. Overall Alignment Status Categories

The overall alignment status summarizes the student's engagement and rubric coverage across all rubric criteria. Overall alignment scores measure the breadth and depth of student engagement with rubric criteria through their questioning patterns; it does not analyze the final submission.

High rubric coverage through questioning should be interpreted carefully within context. While it may indicate thorough preparation by a diligent student, it could also signal gaps in prior instruction—areas where many students needed additional clarification, suggesting the educator may need to provide more support for these criteria in future iterations. Similarly, high coverage could reflect either limited prior engagement with course content or a student's deliberate strategy to ensure comprehensive understanding before submission.

Educators should interpret these metrics as indictors of:
- Rubric awareness: Does the student understand what's being assessed?
- Preparation patterns: How systematically did they explore requirements?
- Potential support needs: Which criteria need additional guidance?


### 5.1 systematic_coverage

Overall alignment ≥ 0.85. The student systematically addressed all or nearly all rubric criteria through thoughtful questioning.

### 5.2 broad_coverage

Overall alignment 0.70-0.84. The student addressed most rubric criteria with some minor gaps.

### 5.3 partial_coverage

Overall alignment 0.55-0.69. The student addressed some rubric criteria but with notable gaps.
### 5.4 minimal_coverage

Overall alignment < 0.55. The student showed minimal engagement with rubric criteria. 

## 6. Sample Output Files

This folder includes three sample JSON outputs that follow the schema. Their goal is to help contributors understand how the alignment module represents different student preparation levels.

### Files:
* `output_sample_excellent.json`
* `output_sample_adequate.json`
* `output_sample_poor.json`
