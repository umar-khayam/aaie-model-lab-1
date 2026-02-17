# Engagement Indicators

## Overview for Contributors

This folder contains the **engagement indicators** used by the Student Interaction
Profiling module. The code here turns a student–AI chat (after adapters) into
simple engagement metrics and a few student evidence snippets.

---

# Engagement Indicators

## Overview for Contributors

This folder contains the **engagement indicators** used by the Student Interaction
Profiling module. The code here turns a student–AI chat (after adapters) into
simple engagement metrics and a few student evidence snippets.

---

## 1. What This Folder Contains

### FILES:

- `engagement.py`  
  Core functions that compute engagement metrics and pick evidence snippets.

- `engagement_sample.json`  
  Example outputs for three chats (MFA, zero-trust, and a small synthetic chat).

These outputs are used in the **engagement** part of the
`StudentInteractionProfile` defined in  
`revision_chain_analysis/student_profiling/schema/output_schema.json`.

---

## 2. Where This Runs in the Pipeline

The engagement code does not read raw rclogs directly.

Typical flow:

1. Raw revision chain log JSON (AAIE Revision Chain Log schema)  
2. `rclog_to_turns` adapter  
   * Converts the log into a list of `turn` dicts with:
     * `role` (`\"student\"`, `\"assistant\"`, `\"system\"`)
     * `text` (message string)
     * optional `timestamp` (ISO string)
3. Prompt Type Classifier (rule based)  
   * Produces `classified_turns` with a `prompt_type` label for each student turn.
4. Engagement module  
   * Calls `compute_engagement_indicators_and_evidence(turns, classified_turns)`
   * Returns counts and evidence snippets.
5. Profiling module  
   * Writes these into the final `StudentInteractionProfile` JSON.

---

## 3. Public Function and Metrics

### 3.1 Main entry point

```python
from revision_chain_analysis.student_profiling.indicators.engagement import (
    compute_engagement_indicators_and_evidence,
)

result = compute_engagement_indicators_and_evidence(
    turns=turns,
    classified_turns=classified_turns,
    max_snippets=2,
)
```

### 3.2 Metrics in `engagement.py`

- `compute_student_token_ratio(turns)`  
  Student tokens / all tokens (simple whitespace split).

- `compute_turn_count(turns)`  
  Number of student turns.

- `compute_prompt_diversity(classified_turns)`  
  Number of unique `prompt_type` values.

- `compute_session_duration(turns)`  
  Uses timestamps if present; otherwise uses turn count as a proxy.

- `extract_engagement_evidence(turns, eng_metrics, max_snippets)`  
  Picks the longest student messages as evidence snippets.

- `compute_engagement_indicators_and_evidence(...)`  
  Wrapper that calls all of the above and returns a single dict.

---

### 3.3 Return format

Example structure:

```json
{
  "counts": {
    "student_token_ratio": 0.41,
    "student_turn_count": 11,
    "prompt_type_diversity": 5,
    "distinct_episode_types": 5,
    "session_time_minutes": 47.5,
    "session_duration_is_proxy": false
  },
  "evidence": [
    "student evidence line 1",
    "student evidence line 2"
  ]
}
```

### 4. Exposed vs Internal Fields

In the final `StudentInteractionProfile` JSON  
(see `schema/output_schema.json`):

**Exposed under `indicator_metrics.engagement`:**

- `student_token_ratio`
- `student_turn_count`
- `distinct_episode_types`
- `session_time_minutes`

**Exposed under `explainability_evidence.engagement`:**

- `evidence` (list of student excerpts from `engagement.py`)

**Internal / helper fields (not written to the profile JSON):**

- `prompt_type_diversity`
- `session_duration_is_proxy`  
  (true if duration came from turn count only, false if real timestamps)

---

### 5. Sample Output File

`engagement_sample.json` contains three example runs:

- `sample_mfa` - MFA revision chain example  
- `sample_zero_trust` - zero-trust revision chain example  
- `sample_synthetic` - small hand-crafted conversation  

Each entry has the same shape as the return value of  
`compute_engagement_indicators_and_evidence`. These samples were used to:

- test the function on 2–3 different chats  
- check that `student_token_ratio` is between 0 and 1  
- confirm that evidence snippets come from real student turns



