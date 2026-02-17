### Import libraries
"""

import json
from typing import Optional
from google import genai
from google.genai import types
from collections import Counter

"""### CONFIGURATION"""

# Initialize Gemini
client = genai.Client(api_key="YOUR_API_KEY_HERE")
GEMINI_MODEL = "gemini-2.5-flash-lite"

"""### PROMPT TEMPLATES"""

SYSTEM_PROMPT = """
You are an expert educational feedback generator trained to provide credible, educator-trusted feedback on student work.

Prioritize:
- Constructive and educationally meaningful insights
- Alignment with the course’s rubric and learning objectives
- Evidence of reflection and progress in the student’s prompt/revision chain
- Objectivity, professionalism, and clarity in communication
- Outputs that educators can directly adopt or edit
"""

STRUCTURED_OUTPUT_PROMPT = """
Format your output as follows:

[Rubric Scores]
- Criterion 1: [0–5]
- Criterion 2: [0–5]
- Criterion 3: [0–5]

[Narrative Feedback]
Provide concise, paragraph-level commentary explaining performance and improvement strategies for each rubric area.

[Learning Summary]
Write a one-page (≤300 words) summary describing the student’s learning progress, reflective depth, and rubric alignment.
"""

def build_feedback_prompt(domain, assignment_prompt, rubric_text, submission, criterion_names, prompt_chain):
    return f"""
{SYSTEM_PROMPT}

TASK CONTEXT:
You are assessing a student submission from the domain: **{domain}**.
The assignment prompt is:
\"\"\"{assignment_prompt}\"\"\"

ASSESSMENT RUBRIC:
{rubric_text}

STUDENT SUBMISSION:
\"\"\"{submission}\"\"\"

PROMPT CHAIN:
{json.dumps(prompt_chain, indent=2)}

EVALUATION INSTRUCTIONS:
1. Analyze the prompt chain to judge whether learning goals and reflective thinking are demonstrated.
2. Explain how effectively the student’s revisions and AI interactions align with course outcomes and rubric criteria.
3. Provide credible, educationally meaningful feedback that educators can adopt directly.
4. Maintain structured outputs: numeric rubric scores, concise narrative feedback, and a one-page summary of learning progress.
5. Keep responses concise, clear, professional, and actionable.

{STRUCTURED_OUTPUT_PROMPT}
"""

"""### GENERATION FUNCTION"""

def gen_text(prompt_str: str, max_new_tokens=512, temperature: Optional[float] = None):
    cfg = types.GenerateContentConfig(
        temperature=temperature if temperature is not None else 0.5,
        max_output_tokens=max_new_tokens,
    )
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt_str,
        config=cfg,
    )
    return (resp.text or "").strip()

"""### Rubric Formatting"""

def format_rubric(r: dict):
    formatted, names = [], []
    formatted.append(f"Rubric ID: {r.get('rubric_id', 'N/A')}\n")
    formatted.append("Criteria:\n")
    for item in r.get('criteria', []):
        nm = item.get('name', 'Criterion')
        names.append(nm)
        formatted.append(f"Criterion: {item.get('criterion_id','')}\nName: {nm}\nDescription: {item.get('description','')}\nPerformance Descriptors:\n")
        for key, val in item.get('performance_descriptors', {}).items():
            formatted.append(f"  - {key}: {val}\n")
    return "".join(formatted), names

"""### Few-Shots Helper"""

def pick_few_shots(subs, max_examples=3):
    buckets = {"Human": [], "AI": [], "Hybrid": []}
    for s in subs:
        label = str(s.get("label_type", "")).strip()
        if label in buckets:
            buckets[label].append(s)
    shots = []
    for lbl in ["Human","AI","Hybrid"]:
        if buckets[lbl]:
            shots.append(buckets[lbl][0])
    for s in subs:
        if len(shots) >= max_examples:
            break
        if s not in shots:
            shots.append(s)
    return shots[:max_examples]

"""### MAIN LOOP"""

if __name__ == "__main__":
    DATASETS = ["TestingSample"]  # replace with your actual dataset names if needed
    MAX_EXAMPLES = 3

    for dataset in DATASETS:
        with open("TestingSample.json", encoding="utf-8") as f:
            data = json.load(f)
        rubric_text, criterion_names = format_rubric(data['rubric'])
        few_shots = pick_few_shots(data['submissions'], MAX_EXAMPLES)

        print(f"\n================= Processing {dataset} =================")

        for i, submission in enumerate(data['submissions'], 1):
            submission_text = submission['final_submission']
            prompt_chain = submission.get("prompt_chain", [])
            label_type = submission.get("label_type", "Unknown")

            # Generate structured, credible feedback
            feedback_prompt = build_feedback_prompt(
                domain=data['domain'],
                assignment_prompt=data.get("prompt", "Analyze student submission"),
                rubric_text=rubric_text,
                submission=submission_text,
                criterion_names=criterion_names,
                prompt_chain=prompt_chain
            )
            feedback_response = gen_text(feedback_prompt, max_new_tokens=1024, temperature=0.5)

            # Print results
            print(f"\n--- SUBMISSION {i} (True Label: {label_type}) ---")
            print("\n--- EDUCATIONAL FEEDBACK ---\n")
            print(feedback_response)