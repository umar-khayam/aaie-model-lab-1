# Developing an Automated LLM Feedback Evaluation Pipeline

Author: Steven Christolis

Version: 1.0

Date: 21 Jan 2026

---

## 1. Overview

As part of 2025 T3, G-Eval from DeepEval was introduce to evaluate the educator feedback being generated as part of the Feedback Generation function of the the AAIE product.

G-Eval enables the evaluation of feedback produced by an LLM. In our case, the feedback produced by the Feedback Generation LLM is evaluated by a second LLM. This is known as the **LLM-as-judge** pattern (the **Judge LLM**).

The Judge LLM requires its own rubric in order to judge whether the feedback generated is '*good*' feedback.

This second rubric used by the Judge LLM is known as a meta-rubric and we have used the following dimensions:

| Dimension                            | Description                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------ |
| **Accuracy**                         | Does the feedback correctly reflect the student’s submission?                  |
| **Specificity**                      | Is the feedback concrete and supported with examples rather than vague advice? |
| **Constructiveness**                 | Does the feedback guide the student on how to improve?                         |
| **Alignment with assignment rubric** | Does the feedback actually reference the criteria used to judge the work?      |
| **Tone and clarity**                 | Is the feedback easy to understand and supportive?                             |

When G-Eval is run, a score from 0 to 10 and a justification is provided for each dimension, in addition to an overall score and a summary is provided.

Currently this is performed manually by running python script: `evaluate_feedback_llm_judge.py`. 

The objective is to transition from an ad-hoc, manual evaluation process to a structured, versioned, and automated pipeline. 

This system should allow for the measuring the impact of changes to the Feedback Generation LLM (e.g. prompt engineering or model swapping) by leveraging DeepEval’s G-Eval framework as a consistent judge, supplemented by critical human-in-the-loop validation.

Additionally, this pipeline should integrate G-Eval into the CI/CD workflow as an automated unit with regression tests to ensure that code updates or prompt modifications do not degrade the quality of generated student feedback.



## 2. Proposed System Architecture

The proposed architecture would introduce an **Experimentation and Validation Layer**. This layer tracks "runs" - specific configurations of Model + Prompt + Parameters - and cross-references automated G-Eval scores with output from Feedback Generation LLM to to evaluate its performance.

### Core Components:

1. **Configuration Registry:** Centralised store for versioning prompt templates and model configurations.

2. **Orchestration Engine:** Manages the sequential execution of the Feedback Generation LLM and the Judge LLM (G-Eval).

3. **CI/CD Integration Gate:** An automated testing layer that triggers G-Eval evaluations upon *relevant* GitHub pull request to act as a quality "gate". This will save on computational costs by ensuring the Judge LLM only runs when changes actually affect the feedback generation logic.

4. **Result Store (Telemetry):** Logs inputs, outputs, G-Eval scores, and Binary Human Feedback (see Step 4 below for how Binary Human Feedback is collected).

5. **Analytics Dashboard:** Used to visualise performance deltas and to highlight discrepancies.



## 3. Proposed Implementation Steps

#### Step 1: Define the Evaluation "Golden" Dataset

- **Define a Representative Set:** Select 20–50 anonymised student submissions across varying performance levels.

- **Version Control:** Store as JSON/CSV to ensure every experiment is benchmarked against identical data to maintain a stable baseline.

#### Step 2: Formalise the Experimentation Schema

Create a structured record for every "Run" that captures the current output schema:

- **Metadata:** Version Name, Model ID, and Prompt Template.

- **Metric Scores:** Individual scores for each criterion (e.g. 0-10 scale) and a calculated weighted percentage.

- **Human Validation Data:** A placeholder field for the "Evaluator-in-the-loop" binary feedback.

#### Step 3: Integrate G-Eval into CI/CD (Automated Regressions)

Transform the evaluation script into an automated quality gate for *relevant* GitHub Pull Requests:

- **Automated Triggering:** Every push to the repository automatically triggers a`meta_evaluator.measure(test_case)` process using the "Golden Dataset".

- **Threshold Enforcement:** Define a minimum acceptable G-Eval score (e.g. 0.85). If a code change (such as a prompt update or logic shift) results in a score below this threshold, the GitHub build is marked as "Failed".

- **Regression Prevention:** This ensures that updates meant to optimise performance or cost do not accidentally result in lower-quality feedback.

#### Step 4: UI Enhancements for Evaluator-in-the-Loop

Transform the UI from a viewing tool into a data collection tool:

- **Binary Feedback:** Add "Thumbs Up/Down" buttons next to the generated feedback for the human evaluator.

#### Step 5: Discrepancy Analysis Logic (Closing the Loop)

- **Flagging Outliers:** Create a workflow that automatically flags instances where G-Eval provides a high score (e.g. >0.8) but the human evaluator provides a "Thumbs Down."

- **Root Cause Analysis:** Prioritise these data points for review. They indicate where the G-Eval prompt or the Feedback LLM’s instructions are misaligned with human pedagogical standards.

- **Iterative Tuning:** Use these findings to refine the G-Eval "Evaluation Steps" to better capture the nuances identified by human experts.



## 4. Evaluation Strategy & Metrics

To quantify the impact of changes, calculate the **Delta** between runs and the **Alignment Rate** between AI and Human judges.

| **Metric**                | **Calculation / Definition**                               | **Importance**                                        |
| ------------------------- | ---------------------------------------------------------- | ----------------------------------------------------- |
| **Human Alignment Score** | % of cases where G-Eval and Human Evaluator agree.         | Measures the reliability of the automated judge.      |
| **Pass/Fail Rate**        | % of automated CI/CD runs that meet the quality threshold. | Tracks codebase stability regarding feedback quality. |
| **Discrepancy Volume**    | Count of "High AI Score / Low Human Score" events.         | Pinpoints specific areas for prompt refinement.       |
| **Mean Evaluation Score** | Average of G-Eval metrics for a dataset.                   | Overall quality tracking.                             |



## 5. Evaluation over time

- **Judge Drift:** G-Eval may gradually lose alignment with human standards as underlying models update. Continuous Discrepancy Analysis acts as a safety net.

- **Prompt Stability:** Use the CI/CD gate to catch "prompt drift," where small instruction changes lead to large, unintended changes in output quality.

- **Human Bias:** Ensure multiple evaluators provide feedback on the same submissions occasionally to calibrate the "Human Truth" used to judge the AI.
