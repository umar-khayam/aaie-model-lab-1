
## 1. Current Evaluation Plan (High-Level Overview)

We designed **Evaluation mechanisms** to assess the quality of AI-generated educator feedback:

1. **Schema & Constraint Validator**
   A deterministic validator that enforces structural correctness, rubric coverage, and length constraints.

2. **LLM-as-Judge Evaluation (G-Eval via DeepEval)**
   A rubric-based evaluation using a separate judge LLM to assess pedagogical quality across defined dimensions.

Both evaluators can be found in the PRs as follows:
- Schema & Constraint Validator: https://github.com/InnovAIte-Deakin/aaie-model-lab/pull/202
- G-Eval: https://github.com/InnovAIte-Deakin/aaie-model-lab/pull/174
---

## 2. Evaluation Setup 1: LLM-as-Judge with Meta-Rubric

### 2.1 Approach

We use an **LLM-as-Judge** paradigm, where a judge model (distinct from the feedback-generation model) evaluates both **human-written** and **AI-generated** feedback.

The Judge LLM is provided with:

* Student submission
* Assignment rubric
* Generated feedback
* A **meta-feedback rubric**

The Judge is instructed to:

* Score each quality dimension (e.g., 1–5)
* Justify each score with evidence
* Provide an overall assessment
* Identify missing, weak, or incorrect feedback elements

This setup enables consistent, automated, and scalable feedback quality evaluation.

---

### 2.2 Meta-Rubric: Feedback Quality Dimensions

The meta-rubric evaluates feedback along the following dimensions:

* **Accuracy**
  Does the feedback correctly reflect the student’s actual submission?

* **Specificity**
  Does it reference concrete examples or sections of the work, rather than vague advice?

* **Constructiveness**
  Does it provide actionable guidance on how the student can improve?

* **Alignment with Assignment Rubric**
  Does it explicitly relate feedback to the rubric criteria used for assessment?

* **Tone and Clarity**
  Is the feedback clear, respectful, supportive, and easy to understand?

These criteria are **model-agnostic** and apply equally to human and machine-generated feedback.

---

### 2.3 Prompting Strategy

To reduce variance, hallucination, and ambiguity, we use **highly structured evaluation prompts**:

* Clearly separated sections:

  * Inputs
  * Assignment rubric
  * Generated feedback
  * Meta-rubric
  * Evaluation task
* Explicit instructions **not to invent or assume student content**
* Fixed scoring scale (e.g., 1–5)
* Mandatory **JSON output schema** for downstream parsing
* Required outputs:

  * Per-dimension score and rationale
  * Overall summary judgment
  * Identification of missing or incorrect elements

This design ensures evaluations are **repeatable, auditable, and automation-friendly**.

---


## 3. Evaluation Setup 2: Schema & Constraint Validator

The **Python-based FeedbackValidator** enforces hard constraints independently of any LLM.

It validates that:

### 3.1 Required Structure

* Mandatory sections are present:

  * **EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS**
  * **RUBRIC SCORES**

### 3.2 Length Constraints

* Main feedback paragraph ≤ **100 words** (warning if very short)
* Per-criterion explanation ≤ **40 words** (warning if extremely short)

### 3.3 Rubric Coverage & Scoring

* All rubric criterion IDs (e.g., `c1`, `c2`, …) are present
* Scores fall within the valid range (**0–10**)
* Rubric lines follow the expected format:

  * `c1: 8/10 – short explanation`

### 3.4 Content Completeness

* Detects placeholders or incomplete outputs:

  * `[...]`, `TODO`, `PLACEHOLDER`, etc.

This validator acts as a **gatekeeper**, ensuring malformed or incomplete feedback never reaches educators.

---

## 4. Tooling Choice: Why G-Eval (DeepEval)

We evaluated multiple evaluation frameworks, including **LangSmith**, **Pydantic Evals**, **TruLens**, and **G-Eval (DeepEval)**.
G-Eval was selected as the primary tool for feedback quality evaluation.

### 4.1 Framework Comparison (Summary)

| Aspect               | LangSmith                  | Pydantic Evals       | TruLens                     | G-Eval (DeepEval)               |
| -------------------- | -------------------------- | -------------------- | --------------------------- | ------------------------------- |
| Primary focus        | Observability & monitoring | Code-first evals     | Pipeline tracing & feedback | Rubric-based LLM-as-judge       |
| Hosting              | Managed SaaS               | Library only         | Library + dashboards        | Library + optional Confident AI |
| Best suited for      | Production monitoring      | Offline / CI testing | RAG & agent pipelines       | Prompt → output quality scoring |
| LLM-as-judge support | Yes                        | Yes                  | Yes                         | **Yes (purpose-built)**         |
| Setup complexity     | High                       | Low                  | Medium                      | **Low**                         |
| Open source          | Partial                    | Yes                  | Yes                         | **Yes (DeepEval core)**         |

G-Eval aligns best with our need for **structured, rubric-driven evaluation** with minimal overhead.

---

## 5. Current Status and Future Plan

### 5.1 Current Implementation

* A **G-Eval-based evaluation API endpoint** has been implemented and submitted as a PR.
* The endpoint:

  * Accepts student submission, assignment rubric, generated feedback, and meta-rubric
  * Runs G-Eval to compute per-dimension scores and rationales
  * Returns structured JSON for UI display or aggregation

### 5.2 Future Direction

* Replace manual feedback evaluation with a **fully automated, version-controlled evaluation pipeline**
* Integrate evaluation into **CI/CD**:

  * Track model and prompt versions
  * Enforce quality thresholds
  * Prevent regressions when prompts or models change
* Introduce an **Experimentation & Validation Layer** for longitudinal performance tracking
* Maintain **human-in-the-loop calibration** and discrepancy analysis to ensure G-Eval remains aligned with human judgment over time

