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


# Explanation of the Script

This script runs an **educator-oriented Feedback Generation (FG) pipeline** using a Gemini model. It loads rubric-based evaluation data, builds a structured prompt, sends it to Gemini, validates the output, extracts rubric scores, calculates a weighted score, and saves all results.
In this FG script, we take a predefined RCA output that FG uses as an input. This input includes the domain, the prompt, the rubric, and the submissions. The RCA output schema is therefore taken as the input schema by FG. The way we perform this is by checking the final submission against the defined rubric criteria to generate feedback.
After the script generates feedback, it produces an output that follows a specific FG output schema. This output schema is designed to integrate directly with our project’s UI. As a result, the script generates an output that matches the predefined schema and seamlessly connects with the UI.

---

## 1. Imports & Config

```python
import json
import re
from typing import Optional, List
from google import genai
from google.genai import types
```

* Loads Python libraries for JSON, regex, typing hints, and the Google GenAI client.

```python
API_KEY = ""
GEMINI_MODEL = "gemini-2.5-flash-lite"
INPUT_PATH = "rub_it_0002.json"
client = genai.Client(api_key=API_KEY)
```

* Sets API key (placeholder), model name, and path to your dataset.
* Creates a Gemini client.

---

## 2. System Prompt

```python
SYSTEM_PROMPT = """ ... """
```

This is the strict safety + role prompt.

The key rule:

### Evaluate ONLY the student’s typed prompts (`User:`). NEVER evaluate the AI responses (`AI:`).

This ensures unbiased assessment of student inquiry.

---

## 3. Output Validation

```python
def output_incomplete(text: str) -> bool:
```

This function checks if Gemini left **placeholders**, such as:

* `[3–4 sentences]`
* `[0–5]`
* Pattern templates

If any placeholder exists, the script retries the prompt up to 2 times.

---

## 4. Rubric Score Extraction & Weighting

### Regex patter

```python
score_with_text_pattern = re.compile(
    r"^(.*?):\s*(10|[0-9])\s*/\s*10\s*-\s*(.*)$",
    re.MULTILINE
)
```

This matches lines like:

```
Understanding Depth: 8/10 - strong curiosity…
```

### extract_scores_and_feedback()

Parses rubric lines and returns:

* dict of numeric scores
* dict of explanations

### compute_weighted_score()

Calculates overall score using:

* each criterion’s weight
* model's score (0–10)

Final output = **percentage 0–100**.

---

## 5. Gemini Call Helper

```python
def gen_text(prompt_str: str, ...)
```

A clean wrapper around `client.models.generate_content()`.

Returns plain text generated by Gemini.

---

## 6. Build Feedback Prompt

```python
def build_feedback_prompt(...):
```

This is the core function.

### What it does:

1. Reads rubric criteria from JSON.
2. Extracts student questions and AI answers.
3. Prepares:

   * student’s prompt list
   * conversation pairs
   * rubric text
   * final submission text
4. Forces Gemini to output exactly TWO SECTIONS:

#### **Section 1 — Educator Feedback & Actionable Insights**

* One paragraph
* Max 100 words
* Must cover strengths, improvement areas, engagement, and next steps.

#### **Section 2 — Rubric Scores**

One line per rubric criterion:

```
CriterionName: SCORE/10 - explanation
```

No square brackets allowed.

This ensures **schema consistency**.

---

## 7. Load Data

Loads JSON file containing:

* domain
* assignment prompt
* rubric
* submissions list

```python
with open(INPUT_PATH) as f:
    data = json.load(f)
```

---

## 8. Run FG Pipeline Over Submissions

Loops through each student submission:

1. Build the full prompt.
2. Generate feedback with Gemini.
3. Retry if placeholders detected.
4. Parse criterion scores.
5. Compute weighted score.
6. Bundle everything into a results record.

It prints:

* First 1300 chars of feedback
* Parsed scores
* Weighted percentage

---

## 9. Save Results

```python
json.dump(all_results, ...)
```

Saves the full evaluation results into:

`FG_Feedback_Results_with_Scores.json`

This file is the finalized structured output of the entire pipeline.

---


