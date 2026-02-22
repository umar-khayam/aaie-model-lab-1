
# **How to Execute This Script (Step-by-Step)**

## **1. Make sure you have Python installed**

Check:

```bash
python --version
```

If Python is not installed, install **Python 3.10+** from python.org.

---

## **2. Create a project folder**

Example:

```
FG-Pipeline/
    refined_FG_Model.py               ← your script
    updatetestingfile.py               ← your script
    rub_it_0002.json        ← your input data
```

---

## 3. Install required libraries

### Required packages

* google-genai
* python-dotenv (optional)
* anything else you imported (json, re, etc. are built-in)

Install:

```bash
pip install google-genai
```

You don’t need to install json, re, or typing.

---

## 4. Put your Google API key in the script

Find:

```python
API_KEY = ""
```

Replace with your key:

```python
API_KEY = "YOUR_GOOGLE_API_KEY"
```

**OR** load from environment variables for safety:

```python
import os
API_KEY = os.getenv("GEMINI_API_KEY")
```

---

## 5. Make sure the input JSON file exists

This script expects the following data input schema:

```python
{
  "domain": "YOUR_DOMAIN_NAME",
  "prompt": "YOUR_ASSIGNMENT_PROMPT_HERE",
  "rubric": {
    "rubric_id": "rub_XXXX",
    "criteria": [
      {
        "criterion_id": "c1",
        "name": "Criterion Name 1",
        "description": "Detailed description of evaluation criterion.",
        "performance_descriptors": {
          "excellent": "Descriptor for excellent performance.",
          "good": "Descriptor for good performance.",
          "average": "Descriptor for average performance.",
          "needs_improvement": "Descriptor for needs improvement.",
          "poor": "Descriptor for poor performance."
        },
        "weight": 25
      },
      {
        "criterion_id": "c2",
        "name": "Criterion Name 2",
        "description": "Detailed description of evaluation criterion.",
        "performance_descriptors": {
          "excellent": "...",
          "good": "...",
          "average": "...",
          "needs_improvement": "...",
          "poor": "..."
        },
        "weight": 25
      },
      {
        "criterion_id": "c3",
        "name": "Criterion Name 3",
        "description": "...",
        "performance_descriptors": { ... },
        "weight": 25
      },
      {
        "criterion_id": "c4",
        "name": "Criterion Name 4",
        "description": "...",
        "performance_descriptors": { ... },
        "weight": 25
      }
    ]
  },
  "submissions": [
    {
      "final_submission": "ANOTHER STUDENT SUBMISSION"
    }
  ]
}
Your script expects:

```python
INPUT_PATH = "rub_it_0002.json"
```

So make sure this file exists in the same folder as the script.



