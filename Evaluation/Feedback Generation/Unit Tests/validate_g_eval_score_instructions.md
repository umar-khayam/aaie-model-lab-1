# G-Eval Unit Test – Feedback Generation

## Purpose
This unit test enforces a minimum quality standard for
LLM-generated feedback using a g-eval score threshold.

If the score drops below the defined threshold, the test
fails and prevents the pull request from being merged.

## How It Works
1. Calls a lightweight test hook in `evaluate_model_genai.py`
2. Retrieves a representative g-eval score
3. Asserts the score meets or exceeds a configurable threshold

## Threshold Configuration
The threshold can be configured using an environment variable:

```bash
export G_EVAL_THRESHOLD=0.6