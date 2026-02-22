# RQA Output Builder

## Overview
This module assembles the final JSON output for the Rubric Question Alignment (RQA) analysis pipeline. The output builder combines results from all the previous RQA components into a single, validated JSON structure that conforms to output_schema.json.

## Input Sources
The module integrates data from:
1. Keyword Matching
    * alignment_summary - Overall alignment score and status
    * criterion_coverage - Coverage metrics per criterion
    * off_topic_prompts - Number of off-topic prompts

2. Gap Detection
    * flags - Structured alerts for coverage issues
    * gaps - Human-readbale gap description per criterion

3. Engagement Depth Assessment
    * depths - Congnitive depth classification per criterion (none/surface/moderate/deep)

## Output Structure
The final output follows this structure:
{
  "submission_id": "rc_rub_it_0029_224666041_0001",
  "rubric_id": "rub_it_0029",
  "domain": "Information Technology",
  "alignment_summary": {
    "overall_alignment": 0.72,
    "status": "broad_coverage",
    "total_prompts_analyzed": 10,
    "off_topic_prompts": 1
  },
  "rubric_coverage": [
    {
      "criteria_id": "c1",
      "criteria_name": "Conceptual Understanding",
      "weight": 0.3,
      "coverage_score": 0.85,
      "status": "well_covered",
      "prompts_matched": 5,
      "engagement_depth": "moderate",
      "gaps": []
    }
  ],
  "flags": [
    {
      "type": "rubric_gap",
      "severity": "medium",
      "criteria_id": "c2",
      "message": "Coverage is 0.45, below 0.50 threshold."
    }
  ]
}

