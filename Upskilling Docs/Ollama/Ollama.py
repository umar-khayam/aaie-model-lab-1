#!/usr/bin/env python
# coding: utf-8

# # Libraries

# In[13]:


import requests
from typing import List, Dict, Any
import json
import time


# ### 1. List Available Models

# In[5]:


import requests

url = "http://127.0.0.1:11434/api/tags"

response = requests.get(url)
models = response.json()

print("Available Models:")
for model in models['models']:
    name = model.get('name', 'N/A')
    model_id = model.get('model', 'N/A')
    size = model.get('size', 'N/A')
    parameters = model.get('details', {}).get('parameter_size', 'N/A')
    quantization = model.get('details', {}).get('quantization_level', 'N/A')
    print(f"Name: {name}, Model ID: {model_id}, Size: {size}, Parameters: {parameters}, Quantization: {quantization}")


# ### 2. Chat Completion (Multi-turn Conversation)

# In[6]:


url = "http://127.0.0.1:11434/v1/chat/completions"

payload = {
    "model": "gemma3:latest",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the benefits of LMStudio."}
    ]
}

response = requests.post(url, json=payload)
chat_response = response.json()

print("AI Response:", chat_response['choices'][0]['message']['content'])


# ### AAIE Model Prompts

# In[25]:


SYSTEM_PROMPT = "You are a careful academic assistant. Be precise and give clear structured output (not JSON, not CSV, no files)."

def build_feedback_prompt(domain: str, assignment_prompt: str, rubric_text: str, submission: str) -> List[Dict[str, str]]:
    """
    Rubric-Aligned Feedback Prompt
    ------------------------------
    Purpose:
        Generates structured, supportive feedback for a student submission.

    Technique:
        - Role-based prompting
        - Rubric-grounded evaluation
        - Output in plain text 

    Expected Output (example format in plain text):
        Overall Summary:
        <2–4 sentence overview>

        Criteria Feedback:
        Criterion: <criterion_id>
        Rating: Excellent | Good | Average | Needs Improvement | Poor
        Reason:
        - point 1
        - point 2
        Improvement Tip: one concrete suggestion

        Overall Rating: Excellent | Good | Average | Needs Improvement | Poor
    """
    user = f"""
You are a supportive assessor. Provide actionable feedback aligned to the rubric.
Return plain structured text only (no JSON, no files).

Sections to include:
1) Overall Summary: 2–4 sentences on strengths and priorities.
2) Criteria Feedback: for each rubric criterion include:
   - Criterion
   - Rating (excellent, good, average, needs_improvement, poor)
   - Evidence (1–3 bullet points citing excerpts or behaviors)
   - Improvement Tip (one concrete step)
3) Overall Rating: Excellent | Good | Average | Needs Improvement | Poor

Context:
- Domain: {domain}
- Assignment prompt: {assignment_prompt}

Rubric (verbatim):
{rubric_text}

Student submission:
\"\"\"{submission}\"\"\"\n
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


# ### Loading Training Data

# In[12]:


with open("accounting.json", "r") as f:
    data = json.load(f)


# ### Generating Feedback

# In[26]:


feedback_results = []

for s in data["submissions"]:
    feedback_prompt = build_feedback_prompt(
        domain=data["domain"],
        assignment_prompt=data["prompt"],
        rubric_text=json.dumps(data["rubric"], indent=2),
        submission=s["final_submission"]
    )

    payload = {
        "model": "gemma3:latest",
        "messages": feedback_prompt,
        "temperature": 0.2,
        "max_tokens": 500
    }

    feedback_response = requests.post(url, json=payload)
    try:
        feedback_json = feedback_response.json()
        feedback_text = feedback_json['choices'][0]['message']['content']
    except Exception as e:
        print("Error parsing response:", feedback_response.text)
        feedback_text = "ERROR: Could not generate feedback"

    feedback_results.append({
        "submission": s["final_submission"],
        "feedback": feedback_text
    })


# In[27]:


print(feedback_results[0]["submission"])

print("*" * 50)
print()

print(feedback_results[0]["feedback"])


# In[ ]:




