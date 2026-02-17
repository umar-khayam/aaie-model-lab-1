# Critical Thinking Indicator Extraction

## 1. Purpose

This module extracts **Critical Thinking (CT) indicators** from a student’s chat history with an LLM. It focuses on how the student interacts with the AI, not on the quality of the final essay.

Outputs are designed to support:

* **Scoring** of the Critical Thinking dimension in the Student Interaction Profile.
* **Explainability** for educators by returning example excerpts that triggered each indicator.
* **Downstream analysis** in the Revision Chain Analysis (RCA) and UI.

The module is rule based for the MVP so that behaviour is deterministic and transparent.

---

## 2. Input and Dependencies

### 2.1 Input format

The module expects **unified chat turns**, produced from an `rc_log` using the utility:

`revision_chain_analysis/student_profiling/tools/rclog_to_turns.py`

Each turn is a dictionary with at least:

```json
{
  "turn_index": 0,
  "role": "student",
  "text": "..."
}
```

Only turns with `role == "student"` are considered for Critical Thinking indicators.

### 2.2 Dependencies

* `revision_chain_analysis/student_profiling/tools/rclog_to_turns.py`
* `revision_chain_analysis/student_profiling/prompt_classifier/prompt_classifier.py` 

---

## 3. Indicators

The module identifies four types of Critical Thinking behaviour.

### 3.1 Explanation Prompts

Student messages that seek explanations or deeper understanding of concepts.

Examples:

* "Can you explain why SMS based MFA is weaker"
* "How does zero trust architecture work"
* "Help me understand the core principles"

These are counted in `explanation_prompts`.

### 3.2 Verification Prompts

Student messages that check correctness or seek confirmation.

Examples:

* "Is this explanation correct"
* "Does this make sense"
* "Do I understand this correctly"

These are counted in `verification_prompts`.

### 3.3 Comparison Prompts

Student messages that compare or contrast alternatives.

Examples:

* "What is the difference between SMS and app based MFA"
* "Compare hardware keys and authenticator apps"
* "What are the pros and cons of these approaches"

These are counted in `comparison_prompts`.

### 3.4 Evidence Prompts

Student messages that request sources, references or supporting evidence.

Examples:

* "Are there any studies or evidence for this"
* "Can you provide sources"
* "What research supports this claim"

These are counted in `evidence_prompts`.

---

## 4. Keyword Rules

Keywords are defined in `CT_KEYWORDS` inside:

`revision_chain_analysis/student_profiling/indicators/critical_thinking.py`

Example (shortened):

```python
CT_KEYWORDS = {
    "explanation_prompts": [
        "explain",
        "explanation of",
        "why ",
        "how does",
        "help me understand",
        "can you clarify",
        "describe the concept",
        "basic explanation",
    ],
    "verification_prompts": [
        "is this correct",
        "is this right",
        "does this make sense",
        "can you verify",
        "confirm this",
        "is this explanation correct",
    ],
    "comparison_prompts": [
        "difference between",
        "compare",
        "pros and cons",
        "advantages and disadvantages",
        "how is this different",
    ],
    "evidence_prompts": [
        "evidence",
        "source",
        "sources",
        "reference",
        "references",
        "cite",
        "studies show",
        "can you provide a source",
    ],
}
```

Matching is:

* Case insensitive.
* Simple substring search on the student message text.
* Counted per message, not per occurrence.

These lists can be refined over time as more data is observed.

---

## 5. Module API

### 5.1 File

`revision_chain_analysis/student_profiling/indicators/critical_thinking.py`

### 5.2 Functions

#### 5.2.1 Low level detectors

Each function returns an integer count.

```python
def detect_explanation_prompts(turns) 
def detect_verification_prompts(turns) 
def detect_comparison_prompts(turns) 
def detect_evidence_prompts(turns) 
```

They iterate over student turns and count messages that contain at least one keyword from the corresponding category.

#### 5.2.2 Evidence extraction

```python
def extract_critical_thinking_evidence(
    turns,
    ct_counts,
    max_snippets: int = 3,
)
```

Behaviour:

* Ignores categories where the count is zero.
* For each active category, finds the first student message that contains one of the category’s keywords.
* Returns up to `max_snippets` messages in total.
* If all counts are zero, returns an empty list.

#### 5.2.3 Public wrapper

```python
def compute_ct_indicators_and_evidence(
    turns,
    max_snippets: int = 3,
) 
```

Returns:

```json
{
  "counts": {
    "explanation_prompts": 3,
    "verification_prompts": 1,
    "comparison_prompts": 0,
    "evidence_prompts": 1
  },
  "evidence": [
    "Can you explain why SMS based MFA is weaker",
    "Is this explanation correct for phishing resistant MFA",
    "Are there any studies or evidence that support this"
  ]
}
```

In the Student Interaction Profile JSON, these values map to:

* `indicator_metrics.critical_thinking`: counts
* `explainability_evidence.critical_thinking`: evidence snippets (exact field path to be finalised)

---

## 6. CLI Tool for Generating CT Samples

To generate CT samples for real `rc_log` files, use:

`revision_chain_analysis/student_profiling/tools/run_critical_thinking_on_file.py`

### 6.1 Script behaviour

The script:

1. Reads an `rc_log` JSON file.
2. Converts it to turns using `rclog_to_turns`.
3. Runs `compute_ct_indicators_and_evidence`.
4. Writes output JSON to the CT sample directory.

### 6.2 Arguments

```bash
python -m revision_chain_analysis.student_profiling.tools.run_critical_thinking_on_file \
  --input revision_chain_analysis/student_profiling/test_files/rclog_MFA_example.json \
  --output-dir revision_chain_analysis/student_profiling/indicators/CT_sample
```

* `--input` (required)
  Path to `rc_log` JSON file.
* `--output-dir` (optional)
  Output directory for the sample JSON. If omitted, defaults to
  `revision_chain_analysis/student_profiling/indicators/CT_sample`.

### 6.3 Output

Example file:

`revision_chain_analysis/student_profiling/indicators/CT_sample/ct_sample_rclog_MFA_example.json`

Structure:

```json
{
  "counts": {
    "explanation_prompts": 3,
    "verification_prompts": 1,
    "comparison_prompts": 0,
    "evidence_prompts": 1
  },
  "evidence": [
    "Can you explain why SMS based MFA is weaker",
    "Is this explanation correct for phishing resistant MFA"
  ]
}
```

---

## 7. Testing

Unit tests reside in:

`revision_chain_analysis/student_profiling/tests/test_critical_thinking.py`

They cover:

* Each indicator detection function with simple synthetic sentences.
* Combined behaviour of `compute_ct_indicators_and_evidence` on a small test conversation.

Run:

```bash
pytest revision_chain_analysis/student_profiling/tests/test_critical_thinking.py
```

All tests should pass before merging changes.

---

## 8. Integration with Student Interaction Profile

In the full profiling pipeline, this module will be called from the main runner:

```python
ct_counts, ct_evidence = compute_ct_indicators_and_evidence(turns)
```

The runner will then:

* Store `ct_counts` under `indicator_metrics.critical_thinking`.
* Store `ct_evidence` under a dedicated explainability field for Critical Thinking.
* Use `ct_counts` as input to the scoring engine to compute the `critical_thinking_score` between 0 and 1.

This ensures that:

* Educators see both the numeric score and concrete examples.
* RCA dashboards can surface short excerpts that justify the classification.
* The module aligns with the project requirement for explainable AI outputs.

---

## 9. Future Improvements

Potential enhancements for later sprints:

* Externalise keyword lists into a YAML config for easier tuning.
* Add phrase level pattern matching to reduce false positives.
* Weight indicators differently when computing scores.
* Compare rule based CT indicators with an LLM based classifier as a shadow experiment.
* Extend evidence extraction to group snippets by indicator type in the final JSON.

