# Problem Solving Indicators – README

This folder contains the Problem Solving (PS) indicator extraction module used in the 
Student Interaction Profiling pipeline. The module processes **turn-based input** that 
has already been converted from an RC log using the `rclog_to_turns` adapter.

---

## 1. Expected Input Format

The module expects a list of *turn dictionaries* with the following fields:

- `role`: `"student"` or `"assistant"`
- `text`: raw message text
- `prompt_type` (optional): classification label assigned upstream  
- Additional metadata fields may appear but are ignored by this module.

**Important:**  
The indicators operate only on *turn-level behaviour* and do not require full RC log
structure. All preprocessing (timestamp parsing, metadata extraction, etc.) happens
before this stage.

---

## 2. Internal vs Exposed Fields

### **Internal logic fields (not written to final profile JSON)**
These fields are used only inside the indicator extraction functions:
- Keyword matches for decomposition, feedback, and drafts
- Internal counters for revision detection
- Intermediate rolling comparisons between turns

### **Exposed fields returned in the final JSON**
The `compute_PS_indicators_and_evidence()` function outputs a JSON-compatible dict:

```json
{
  "counts": {
    "decomposition_prompts": int,
    "iterative_revision_count": int,
    "self_proposed_content_turns": int,
    "feedback_uptake_events": int
  },
  "evidence": [
    "evidence snippet 1",
    "evidence snippet 2",
    "evidence snippet 3"
  ]
}
