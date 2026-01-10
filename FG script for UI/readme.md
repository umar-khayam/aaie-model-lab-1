# Refined FG Model with Future Updates

This script implements an **educator-oriented Feedback Generation (FG) pipeline** powered by Gemini. It processes rubric-based evaluation data, generates structured feedback, extracts rubric scores, computes weighted percentages, **latency**, and **confidence scores**, and then saves UI-ready outputs.  
The FG model accepts RCA output consisting of the **domain, prompt, rubric, and final_submission only**  as structured input, producing refined outputs that integrate directly with the project’s user interface.

***

## Repository Overview

This repository now contains **two notebook versions**:

1. **`refined_FG_Model.py`**  
   - All previous **LLM question and answer pairs** have been **removed**.  
   - Focuses entirely on student **final submissions** to maintain unbiased evaluations.

2. **`for_future_use_FG.py`**  
   - Builds upon the refined model.  
   - Adds **latency tracking** and **confidence score computation** for performance analysis and model reliability estimation.  
   - Intended for **future scalability and analytics** in model evaluation.

***

## Key Changes Made

### FG Future Updates
**1. Added Latency Tracking**
```python
start_time = time.time()
feedback_text = gen_text(prompt_str)
latency_seconds = round(end_time - start_time, 3)
```
Measures **end-to-end response time** for each Gemini API call per submission.

**✅ 2. Added Confidence Score**
```python
def compute_confidence_score(scores: Dict[str, int], expected_criteria: int) -> float:
```
Calculates a **heuristic score (0.0–1.0)** based on rubric coverage and score consistency, offering a measure of **result confidence**.

### FG Refined  Model
**1. Removed LLM Question/Answer Evaluation**
- Removed all `User:` / `AI:` conversation logs.  
- Evaluates **only the student’s final submission**, according to RCA team guidance.  
- The system prompt explicitly instructs:  
  _"Evaluate ONLY the STUDENT'S FINAL SUBMISSION."_

**2. Clean Input Schema**
- One `final_submission` field per entry.  
- No conversational data or multi-turn metadata.  

***

## Pipeline Flow (1–9)

1. **Imports & Config**  
   Loads dependencies and initializes the Google GenAI client with your Gemini API key.

2. **System Prompt**  
   Enforces strict educator behavior and ensures evaluation is limited to the final written work.

3. **Output Validation**  
   Detects incomplete or template-based responses and retries automatically.

4. **Score Parsing**  
   - Uses regex to extract lines in the format:  
     `CriterionName: 8/10 - short explanation`  
   - Computes a **weighted score percentage (0–100)** using rubric criteria and weights.  
   - Integrates the **confidence score heuristic.**

5. **Gemini Helper**  
   Contains retry/backoff logic for handling API failures or overload (HTTP 503).

6. **Build Feedback Prompt**  
   Combines domain, prompt, rubric, and final submission in a structured way, forcing a **two-section Gemini output**:
   - Section 1: *Educator Feedback & Actionable Insights*  
   - Section 2: *Rubric Scores*

7. **Load Data**  
   Reads input files such as `rub_it_XXXX.json` containing domain, prompt, rubric, and submissions.

8. **Process Submissions**  
   For each submission:
   - Build prompt → Send to Gemini → Parse output  
   - Calculate **latency** and **confidence_score**(Only for Future update)
   - Append structured results to the list.

9. **Save Results**  
   Stores all finalized feedback evaluations inside **`FG_Feedback_Results_with_Scores.json`** — ready for direct UI consumption.(Only for Future update)

***

## Output Schema (UI Ready)

Each record in the output JSON includes:

```json
{
  "index": 1,
  "quality": "...",
  "authorship": "...",
  "criterion_scores": {...},
  "weighted_score_percent": 88.0, 
  "confidence_score": 0.9,    // NEW (Only for Future update)
  "latency_seconds": 3.657,   // NEW (Only for Future update)
  "feedback": "Full educator text..."
}
```

***

## Summary

- The **refined_FG_Model.ipynb** streamlines the evaluation, focusing only on **final submissions**.  
- The **for_future_use_FG.ipynb** enhances the framework with **latency** and **confidence analytics** for better performance analysis.  
- Together, they form the foundation for an advanced, evaluation-ready feedback system for the **AAIE project dashboard**.  
