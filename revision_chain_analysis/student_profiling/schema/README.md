# Student Interaction Profiling Schema

## Overview for Contributors

This folder contains the JSON Schema used for the Student Interaction Profiling module, along with four sample output files that demonstrate how the module represents different patterns of student behaviour when interacting with AI.

---

## 1. What This Schema Represents

The Student Interaction Profile captures how a student engaged with an AI assistant throughout their writing process, based entirely on the chat history. It does not analyse the final submission.

The schema defines:

* Metadata (submission id, timestamps)
* Quantitative scores for the three profiling dimensions
  • Critical Thinking
  • Problem Solving
  • Engagement
* The AI Use Pattern classification
* A natural-language behavioural summary
* Raw indicator metrics that drive the scoring
* Prompt type distribution
* Explainability fields (evidence excerpts and confidence scores)

This structure allows downstream components (backend, frontend, feedback generator, RCA explainability layer) to understand and process the behavioural insights generated during profiling which also includes transparency and explainability.

---

## 2. Schema File

### `output_schema.json`

This file outlines the expected structure for all profiling outputs.
It includes:

* `submission_id`
* `profile_generated_at`
* `scores`
* `ai_use_pattern`
* `process_notes`
* `indicator_metrics` (raw counts for each dimension)
* `prompt_type_distribution`
* `explainability_evidence`

  * confidence values
  * evidence excerpts per dimension
  * evidence for AI Use Pattern decision

Contributors should use this file to understand how the profiling module formats its output and how other RCA components can consume it.

---

## 3. AI Use Pattern Categories

The schema supports four AI Use Pattern labels. Each describes a different style of interaction with the AI model. Understanding these categories is important for interpreting sample outputs and contributing to the profiling logic.

### 3.1 generator_only

The student relies almost entirely on direct generation prompts. Typical behaviour includes short requests like “write the essay” or “generate this section” with little or no revision, planning or evaluation.

### 3.2 reviser

The student writes most of the content themselves and uses the AI to revise or improve the text. This pattern shows active ownership of the work and consistent refinement behavior.

### 3.3 planner_checker

The student uses the AI mostly for planning, understanding the task and checking quality. This reflects high agency, critical inquiry and metacognitive engagement.

### 3.4 mixed

The student shows no dominant pattern. This label applies when behaviors are spread across multiple categories.

---

## 4. Sample Output Files

This folder includes four sample JSON outputs that follow the schema. Their goal is to help contributors understand what each AI Use Pattern looks like when represented as structured data.

### Files:

* `output_sample_ai.json`
* `output_sample_reviser.json`
* `output_sample_plannerchecker.json`
* `output_sample_mixed.json`

Each file contains:

* Valid dimension scores
* Raw indicator metrics
* Natural-language behaviour summary
* Prompt type distribution
* Explainability evidence and confidence scores
  • Critical Thinking
  • Problem Solving
  • Engagement
  • AI Use Pattern


hese samples help contributors understand:

* how the profiling module will populate fields
* how frontend components should render explainability evidence
* how RCA integrates the profiling output into the overall analysis

They also serve as reference cases for backend testing and sprint development.
