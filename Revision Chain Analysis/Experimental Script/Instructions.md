## How to Run the Script

### Prerequisites

* Python **3.9+**
* A valid **Google Gemini API key**
* Required libraries installed:

```bash
pip install google-generativeai
```

### Configuration

1. Open the script and set your API key:

```python
client = genai.Client(api_key="YOUR_API_KEY_HERE")
```

2. Confirm the model configuration:

```python
GEMINI_MODEL = "gemini-2.5-flash-lite"
```

---

## Input Data Used for Testing

### Dataset File

* **Filename:** `TestingSample.json`
* **Location:** Same directory as the script

### Expected JSON Structure

```json
{
  "domain": "Education / AI Writing",
  "prompt": "Assignment prompt text",
  "rubric": {
    "rubric_id": "RUBRIC_001",
    "criteria": [
      {
        "criterion_id": "C1",
        "name": "Reflection",
        "description": "Depth of reflective thinking",
        "performance_descriptors": {
          "0-1": "Minimal reflection",
          "2-3": "Developing reflection",
          "4-5": "Strong reflection"
        }
      }
    ]
  },
  "submissions": [
    {
      "final_submission": "Student final written response",
      "prompt_chain": [
        {"role": "user", "content": "Initial prompt"},
        {"role": "assistant", "content": "AI response"},
        {"role": "user", "content": "Revised prompt"}
      ],
      "label_type": "Human"
    }
  ]
}
```

### Fields Used by the Script

* `domain` → context for assessment
* `prompt` → original assignment prompt
* `rubric` → formatted and injected into the evaluation prompt
* `final_submission` → student’s final answer
* `prompt_chain` → used to assess learning progression and reflection
* `label_type` → printed for reference only (not used in scoring)

---

## Execution Command

Run the script from the project root:

```bash
python testingscript.py
```

---

## Expected Output

For each submission, the script prints structured educational feedback to the console containing:

```
[Rubric Scores]
- Criterion 1: 0–5
- Criterion 2: 0–5
- Criterion 3: 0–5

[Narrative Feedback]
Paragraph-level educator commentary aligned to rubric criteria.

[Learning Summary]
≤300-word summary of learning progress, reflective depth, and rubric alignment.
```

The script confirms successful execution by:

* No runtime errors
* Gemini API returning content
* Outputs strictly following the defined structure

