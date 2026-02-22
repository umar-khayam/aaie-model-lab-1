# RCA Profiling API

This folder exposes a single, stable API entry point for running the Student Interaction Profiling pipeline. The API is designed for backend integration and provides a defensive, schema-safe interface over the existing Student Profiling runner.

---

## Purpose

The API layer provides:

- One callable entry point for backend and product integration
- A stable JSON-in, JSON-out interface
- Defensive handling of malformed or incomplete inputs
- Guaranteed schema-valid outputs

The API delegates all profiling logic to the internal Student Profiling runner and does not reimplement profiling behaviour.

---

## Public Interface

### Function

```
run_student_profiling(chat_history_json)
```

### Location

```
revision_chain_analysis/api/runner.py
```

---

## Input

### `chat_history_json` (dict)

Accepted format:

* Full RCLog JSON (required)

Turns-only payloads are treated as partial inputs and will return a schema-valid fallback profile. The API never raises exceptions to the caller.

---

## Output

Returns a dictionary conforming to:

```
StudentInteractionProfile
revision_chain_analysis/student_profiling/schema/output_schema.json
```

The output always includes:

* `submission_id`
* `scores` (critical thinking, problem solving, engagement)
* `ai_use_pattern`
* `process_notes`
* `indicator_metrics`
* `explainability_evidence`

---

## Backend Usage Guide

### Example Usage

```python
from revision_chain_analysis.api.runner import run_student_profiling

def handle_submission(chat_history_json: dict):
    profile = run_student_profiling(chat_history_json)
    return profile
```

### Backend Guarantees

* The function never throws exceptions
* A valid profile dictionary is always returned
* Fallback outputs are safe to store or forward
* Error context is provided in `process_notes`

This makes the API suitable for synchronous requests, background jobs, batch processing, and future service deployment.

---

## Internal Behaviour

The API runner:

* Validates and normalises input
* Delegates profiling execution to
  `student_profiling/tools/profile_runner.py`
* Returns the generated profile or a schema-valid fallback

All indicator extraction, scoring, pattern classification, and JSON assembly are handled by the Student Profiling runner.

---

## Testing

Automated tests are located in:

```
revision_chain_analysis/api/tests/test_runner.py
```

Run from the repository root:

```bash
python -m pytest -q revision_chain_analysis/api/tests/test_runner.py
```

Tests validate:

* Complete RCLog inputs
* Partial or unsupported inputs
* Malformed inputs
* Schema compliance and resilience guarantees

---

## Dependencies

Internal:

* Student Profiling runner
* Profile builder and schema
* Summary generator
* Scoring engine
* AI use pattern classifier

