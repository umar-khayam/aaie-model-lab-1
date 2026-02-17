# Summary Generator

This module generates short, natural-language **process notes** that describe how a student used AI during a revision chain.

It converts detected behaviour patterns into concise, human-readable summaries that can be used for reporting, analysis, or downstream modelling.

---

## Summary Patterns

The generator supports the following student behaviour patterns:

- `generator_only`  
  The student relies primarily on the AI to generate content.

- `reviser`  
  The student writes their own text and uses the AI mainly for revision.

- `planner_checker`  
  The student uses the AI for planning, understanding prompts, and checking quality.

- `mixed`  
  No dominant behaviour pattern; a blend of different behaviours.

---

## How It Works (MVP)

Given a detected behaviour `pattern` (string), the generator:

1. Loads the corresponding text template from a YAML file
2. Returns a short, natural-language summary sentence

The `scores` argument is accepted for API compatibility but is not used in the current MVP.  
This keeps the logic simple and aligned with the task requirements.

---

## Files in this folder

- `summary_generator.py`  
  Main implementation containing `build_process_notes`.

- `pattern_summaries.yaml`  
  YAML templates for each behaviour pattern.

- `summary_samples/`  
  Example output summaries for each pattern.

- `test_summary_generator.py`  
  Pytest tests validating correct template selection and error handling.

---

## Usage

```python
from revision_chain_analysis.student_profiling.summary.summary_generator import build_process_notes

summary = build_process_notes("generator_only", {})
print(summary)
