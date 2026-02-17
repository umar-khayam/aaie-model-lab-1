# Student Interaction Profiling

This folder contains the code for the **Student Interaction Profiling** module in the Revision Chain Analysis (RCA) pipeline. The goal is to analyse a student’s chat history with an LLM and extract behavioural signals that describe how they used AI during their writing process.

The module supports:

* Prompt type classification
* Critical Thinking indicator extraction
* Problem Solving indicator extraction 
* Engagement indicator extraction 

Future components will add scoring, pattern classification and a single runner that returns a `StudentInteractionProfile` JSON document for each submission.

---

## 1. Folder Structure

Within `revision_chain_analysis/student_profiling`:

* `prompt_classifier/`

  * `prompt_classifier.py`

    * Rule based prompt type classifier.
  * `prompt_types.yaml`

    * Configuration file with keyword and phrase lists for each prompt type.
* `tools/`

  * `rclog_to_turns.py`

    * Utility to convert an `rc_log_v1` record into a unified list of turns.
  * `run_prompt_classifier_on_file.py`

    * Script to run the classifier on a single rc_log JSON file and save outputs.
* `indicators/` (planned)

  * `critical_thinking.py` (planned)
  * `problem_solving.py`(planned)
  * `engagement.py` (planned)
* `scoring/` (planned)

  * `scoring_engine.py`
* `patterns/` (planned)

  * `pattern_classifier.py`
* `summary/` (planned)

  * `summary_generator.py`
* `output/` (planned)

  * `profile_builder.py`
* `tests/`

  * Unit tests for classifier and indicators.

---

## 2. Input Assumptions

The profiling module currently assumes input in the **rc_log** format:

```json
{
  "rc_log_id": "rclog_MFA_example",
  "rubric_id": "rub_it_0002",
  "revision_chain": [
    {
      "step_index": 0,
      "student_prompt": "I need to write a 1500 word essay about...",
      "llm_response": "Here is an outline..."
    },
    {
      "step_index": 1,
      "student_prompt": "Refine this outline into more detailed section headings...",
      "llm_response": "Here is a refined outline..."
    }
  ],
  "final_submission": { ... }
}
```

Only the `revision_chain` is used for Student Profiling. The utility `rclog_to_turns.py` converts this into a unified list of turns:

```json
[
  { "turn_index": 0, "role": "student", "text": "I need to write a 1500 word essay..." },
  { "turn_index": 1, "role": "assistant", "text": "Here is an outline..." },
  { "turn_index": 2, "role": "student", "text": "Refine this outline..." },
  { "turn_index": 3, "role": "assistant", "text": "Here is a refined outline..." }
]
```

All downstream profiling logic (prompt types, indicators, scoring) uses this unified turn structure.

---

## 3. Prompt Type Classifier 

**File**
`prompt_classifier/prompt_classifier.py`
`prompt_classifier/prompt_types.yaml`

### 3.1 What it does

The classifier:

1. Loads rule definitions from `prompt_types.yaml`.
2. Classifies each **student** message into exactly one `prompt_type`.
3. Computes a distribution of prompt types across the conversation.

Supported prompt types:

* `understand_prompt`
* `plan_structure`
* `generate_content`
* `revise_content`
* `polish_language`
* `check_quality`
* `unknown_prompt_type`

These prompt types feed into later components:

* Problem Solving indicators (revision sequences, content generation vs revision).
* Engagement indicators (prompt type diversity).
* AI use pattern classification.

### 3.2 YAML configuration

`prompt_types.yaml` defines trigger phrases for each prompt type. Matching is done by case insensitive substring search. Examples:

```yaml
generate_content:
  - write an essay
  - draft an introduction
  - draft 3 to 4 paragraphs
  - create a section
  - continue the essay
```

You can refine or extend these lists as you see real data. The classifier will pick up changes without code modification.

### 3.3 Public API

The main entry point is:

```python
from revision_chain_analysis.student_profiling.prompt_classifier.prompt_classifier import (
    run_prompt_type_classification,
)

classified_turns, distribution = run_prompt_type_classification(turns)
```

* `turns` is the unified list of turns from `rclog_to_turns`.
* `classified_turns` mirrors `turns` but adds `"prompt_type"` to each student turn.
* `distribution` is a dict of counts per prompt type.

Example distribution:

```json
{
  "understand_prompt": 1,
  "plan_structure": 1,
  "generate_content": 3,
  "revise_content": 2,
  "polish_language": 0,
  "check_quality": 1,
  "unknown_prompt_type": 0
}
```

This map is intended to populate `indicator_metrics.prompt_type_distribution` in the final profile JSON.

---

## 4. Indicator Extraction (To be Built)

Indicator extraction uses the classified turns to derive raw behavioural metrics. These modules are implemented as standalone functions that return counts or measurements and evidence snippets for explainability.


---

## 5. Running the Classifier on a Real rc_log

You can test the classifier on a single rc_log using the tool script.

**Script**
`tools/run_prompt_classifier_on_file.py`

### 5.1 Command and arguments

From the repo root:

```bash
python -m revision_chain_analysis.student_profiling.tools.run_prompt_classifier_on_file \
  revision_chain_analysis/student_profiling/test_files/rclog_MFA_example.json \
  --output-dir revision_chain_analysis/student_profiling/test_files/test_output
```

This script will:

1. Load the rc_log JSON.
2. Convert `revision_chain` to unified turns.
3. Run `run_prompt_type_classification`.
4. Print the prompt type distribution.
5. Save:

   * `*_classified_turns.json`
   * `*_prompt_distribution.json`

in the specified output directory.

This is useful for:

* Manual inspection of prompt type labels.
* Sanity checking keyword rules.
* Providing sample outputs to frontend and RCA teams.

---

## 6. Integration with the Full Profiling Pipeline

In the final RCA pipeline, Student Profiling will be called through a single runner:

```python
from revision_chain_analysis.student_profiling.api.runner import run_student_profiling

profile_json = run_student_profiling(chat_history_turns, submission_id)
```

This runner will:
1. Run prompt type classification.
2. Compute Critical Thinking, Problem Solving and Engagement indicators.
3. Apply scoring to map raw metrics into scores from 0 to 1.
4. Assign an AI use pattern label (`generator_only`, `reviser`, `planner_checker`, `mixed`).
5. Generate short process notes.
6. Assemble a `StudentInteractionProfile` JSON matching the agreed output schema.

The resulting profile will be consumed by:
* The RCA backend for reporting.
* The frontend dashboard for visualisation.

---

## 7. Tests

Unit tests for this module live under:

`revision_chain_analysis/student_profiling/tests/`

To run tests from the repo root:

```bash
pytest
```

or

```bash
pytest revision_chain_analysis/student_profiling/tests
```

Tests currently focus on:

* Prompt type classification correctness.
* Distribution counts for controlled sample conversations.

Future tests will cover:

* Indicator extraction logic.
* Scoring functions.
* Full profile assembly for known sample rc_logs.

---

## 8. Future Uses and Extensions

The Student Profiling module is designed to be:

* **Config driven**
  All prompt type rules live in `prompt_types.yaml`, so contributors can refine behaviour without changing code.

* **Explainable**
  Each indicator returns counts and associated evidence snippets to support transparency and educator trust.

* **Composable**
  The same indicators can be reused for:

  * Research on student AI usage patterns.
  * Rule based flags for responsible AI use.
  * Shadow experiments that compare rule based profiling with LLM based profiling.

Planned extensions:

* Shadow LLM profiler that runs over the same rc_logs for research comparison.
* More detailed AI use pattern taxonomy.
* Additional indicators for metacognition and self regulation.
* Configuration files for thresholds used in scoring.


