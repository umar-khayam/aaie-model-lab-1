#!/usr/bin/env python
# coding: utf-8

# NanoGPT

# In[2]:


import requests
import json
from google.colab import userdata
from typing import List, Dict, Any


# API Accessing

# In[11]:


BASE_URL = "https://nano-gpt.com/api/v1"
API_KEY = "fe7dbca6-4709-4385-9698-acd163f901e6"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}


# Function to communicate with the model

# In[23]:


def stream_chat_completion(messages, model="chatgpt-4o-latest"):
    """
    Send a streaming chat completion request using the OpenAI-compatible endpoint.
    """
    data = {
        "model": model,
        "messages": messages,
        "stream": True  # Enable streaming
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=180 # Add a timeout
        )
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        return # Stop the generator if the request fails

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                line = line[6:]
            if line == '[DONE]':
                break
            try:
                chunk = json.loads(line)
                if chunk['choices'][0]['delta'].get('content'):
                    yield chunk['choices'][0]['delta']['content']
            except (json.JSONDecodeError, IndexError, KeyError):
                continue


# Prompts

# In[34]:


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


# Loading the dataset

# In[35]:


import json
import os

def load_multiple_json_files(file_paths: list) -> list:
    """
    Loads multiple JSON files and returns a list of loaded data dictionaries.

    Args:
        file_paths (list): List of full file paths to JSON files.

    Returns:
        List of dictionaries, each representing the data from one JSON file.
    """
    loaded_data = []
    for file_name in file_paths:
        try:
            with open(file_name, 'r') as f:
                data = json.load(f)
                if 'domain' in data and 'submissions' in data:
                    print(f"Loaded domain '{data['domain']}' with {len(data['submissions'])} submissions from '{file_name}'.")
                    loaded_data.append(data)
                else:
                    print(f"WARNING: File '{file_name}' missing 'domain' or 'submissions' keys. Skipping.")
        except FileNotFoundError:
            print(f"ERROR: The file '{file_name}' was not found. Skipping.")
        except json.JSONDecodeError:
            print(f"ERROR: The file '{file_name}' is not a valid JSON. Skipping.")
    return loaded_data

# --- Example usage ---
file_list = [
    'accounting.json',
    'teaching.json',
    'psychology.json',
    'it.json',
    'engineering.json'
]

all_domains_data = load_multiple_json_files(file_list)
print(f"\nTotal domains loaded: {len(all_domains_data)}")


# Evaluation Function

# In[36]:


# Function to generate self-evaluation rating
def build_self_eval_prompt(rubric: Dict, essay: str, feedback: str) -> str:
    crit = [c.get('name','Criterion') for c in rubric.get('criteria',[])]
    crit_str = ", ".join(crit) if crit else "the rubric"
    return (
        "You are a strict but fair assessor. Rate how well the FEEDBACK addresses the rubric for the ESSAY.\n"
        "Rate on a 1-5 scale (integers only). Provide ONLY the number.\n\n"
        f"ESSAY:\n{essay}\n\n"
        f"RUBRIC CRITERIA: {crit_str}\n\n"
        f"FEEDBACK:\n{feedback}\n\n"
        "RATING (1-5): "
    )


# Function to detect and generate feedback based on training data and prompt and also evaulate the model performance.

# In[40]:


# Define allowed standard labels globally
ALLOWED_LABELS = ["AI", "Human", "Hybrid"]

from collections import defaultdict
import pandas as pd

# Initialize overall counters
overall_true = []
overall_pred = []

for domain_data in all_domains_data:
    domain = domain_data['domain']
    assignment_prompt = domain_data['prompt']
    rubric_text = json.dumps(domain_data['rubric'], indent=2)
    submissions = domain_data['submissions']

    # Domain-level counters
    domain_true = []
    domain_pred = []

    print(f"\n{'='*80}")
    print(f"=== STARTING EVALUATION FOR '{domain}' DOMAIN ===")
    print(f"{'='*80}\n")

    for i, submission_data in enumerate(submissions):
        submission_text = submission_data['final_submission']
        ground_truth_label = submission_data['label_type'].strip()

        # Normalize ground truth
        if ground_truth_label not in ALLOWED_LABELS:
            for label in ALLOWED_LABELS:
                if label.lower() in ground_truth_label.lower():
                    ground_truth_label = label
                    break
            else:
                ground_truth_label = "Unknown"

        print(f"{'-'*80}")
        print(f"Submission {i+1} (Ground Truth: {ground_truth_label})")
        print(f"{'-'*80}\n")

        # --- TASK 1: Detection ---
        few_shots = [s for j, s in enumerate(submissions) if i != j][:2]
        detection_messages = build_detection_prompt(submission_text, few_shots)
        full_detection = ""
        predicted_label = "Unknown"

        try:
            for chunk in stream_chat_completion(detection_messages):
                print(chunk, end='', flush=True)
                full_detection += chunk

            # --- Normalize predicted label ---
            for line in full_detection.splitlines():
                if "Label" in line:
                    predicted_label = line.split(":")[1].strip()
                    break

            # Standardize predicted label
            if predicted_label not in ALLOWED_LABELS:
                for label in ALLOWED_LABELS:
                    if label.lower() in predicted_label.lower():
                        predicted_label = label
                        break
                else:
                    predicted_label = "Unknown"

        except Exception as e:
            print(f"Error generating detection: {str(e)}")
            full_detection = "Error generating detection."

        # Add to domain and overall lists
        domain_true.append(ground_truth_label)
        domain_pred.append(predicted_label)
        overall_true.append(ground_truth_label)
        overall_pred.append(predicted_label)

        print("\n")

        # --- TASK 2: Feedback ---
        feedback_messages = build_feedback_prompt(
            domain=domain,
            assignment_prompt=assignment_prompt,
            rubric_text=rubric_text,
            submission=submission_text
        )
        full_feedback = ""
        try:
            for chunk in stream_chat_completion(feedback_messages):
                print(chunk, end='', flush=True)
                full_feedback += chunk
        except Exception as e:
            print(f"Error generating feedback: {str(e)}")
            full_feedback = "Error generating feedback."
        print("\n")

        # --- TASK 3: Self-Evaluation Rating ---
        print(">>> 3. Self-Evaluation Rating (1-5):")
        rating_prompt_text = build_self_eval_prompt(domain_data['rubric'], submission_text, full_feedback)
        rating_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": rating_prompt_text},
        ]
        try:
            rating_response = get_chat_completion(rating_messages)
            print(rating_response)
        except Exception as e:
            print(f"Error generating rating: {str(e)}")

    # --- Domain-Level Confusion Matrix ---
    domain_cm = pd.crosstab(
        pd.Series(domain_true, name='Ground Truth'),
        pd.Series(domain_pred, name='Predicted'),
        rownames=['Ground Truth'],
        colnames=['Predicted'],
        dropna=False
    )
    print(f"\nConfusion Matrix for Domain '{domain}':")
    print(domain_cm)
    print(f"\n{'='*80}\n")

# --- Overall Confusion Matrix ---
overall_cm = pd.crosstab(
    pd.Series(overall_true, name='Ground Truth'),
    pd.Series(overall_pred, name='Predicted'),
    rownames=['Ground Truth'],
    colnames=['Predicted'],
    dropna=False
)
print("\nOverall Confusion Matrix Across All Domains:")
print(overall_cm)

