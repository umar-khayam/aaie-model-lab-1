
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

Your script expects:

```python
INPUT_PATH = "rub_it_0002.json"
```

So make sure this file exists in the same folder as the script.



