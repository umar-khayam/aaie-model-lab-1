#!/usr/bin/env python
# coding: utf-8

# # Libraries

# In[35]:


import requests
from typing import List, Dict, Any


# ### 1. List Available Models

# In[5]:


import requests

url = "http://192.168.0.119:1234/v1/models"

response = requests.get(url)
models = response.json()

print("Available Models:")
for model in models['data']:
    model_id = model.get('id', 'N/A')
    model_type = model.get('object', 'N/A')  # usually 'model'
    print(f"ID: {model_id}, Type: {model_type}")


# ### 2. Chat Completion (Multi-turn Conversation)

# In[7]:


url = "http://192.168.0.119:1234/v1/chat/completions"  # Remove 'POST' from the URL

payload = {
    "model": "gemma-3-1b",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the benefits of LMStudio."}
    ]
}

response = requests.post(url, json=payload)
chat_response = response.json()

print("AI Response:", chat_response['choices'][0]['message']['content'])


# ### AAIE Model Prompts

# In[29]:


SYSTEM_PROMPT = "You are a careful academic assistant. Be precise and give clear structured output (not JSON, not CSV, no files)."

def build_detection_prompt(submission: str, few_shots: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Academic Integrity Detector Prompt
    ----------------------------------
    Purpose:
        Classifies student submissions as Human, AI, or Hybrid (AI-assisted).

    Technique:
        - Role-based prompting
        - Few-shot support
        - CoT (reasoning encouraged but hidden from output)
        - Output in plain text 

    Expected Output (example format in plain text):
        Label: Human | AI | Hybrid
        Rationale:
        - short bullet point 1
        - short bullet point 2
        Flags: style_inconsistency / high_verbatim / generic_phrasing / none
    """
    # Build few-shot block
    shot_texts = []
    for s in few_shots:
        shot_texts.append(
            f'Submission: """{s.get("final_submission","")}"""\n'
            f'Your analysis (2–4 bullet points): <analysis>\n'
            f'Label: {s.get("label_type","")}\n'
        )
    examples_block = "\n\n".join(shot_texts) if shot_texts else "/* no examples available */"

    user = f"""
You are an AI text-source classifier for academic integrity.
Decide whether the student submission is Human, AI, or Hybrid (AI-assisted).

Guidelines:
- Consider discourse features (specificity, subjectivity, personal context), style consistency, local/global coherence, repetitiveness, and cliché patterns.
- Hybrid = meaningful human writing with some AI assistance, or explicit admission of mixed use.

Examples:
{examples_block}

Now analyze the NEW submission and respond in plain text with the following structure:
Label: ...
Rationale:
- point 1
- point 2
Flags: ...
NEW submission:
\"\"\"{submission}\"\"\"\n
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


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

# In[43]:


with open("Training_Data/accounting.json", "r") as f:
    data = json.load(f)


# ### Generating Feedback

# In[46]:


# Loop over all submissions
for s in data["submissions"]:
    feedback_prompt = build_feedback_prompt(
        domain=data["domain"],
        assignment_prompt=data["prompt"],
        rubric_text=json.dumps(data["rubric"], indent=2),
        submission=s["final_submission"]
    )

    # Send request to LM Studio
    feedback_response = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "model": MODEL_NAME,
            "messages": feedback_prompt,
            "temperature": 0.2,
            "max_tokens": 500
        }
    )

    feedback_json = feedback_response.json()
    feedback_text = feedback_json['choices'][0]['message']['content']

    feedback_results.append({
        "submission": s["final_submission"],
        "feedback": feedback_text
    })


# In[49]:


print(feedback_results[0]["submission"])

print("*" * 50)
print()

print(feedback_results[0]["feedback"])


# In[ ]:




