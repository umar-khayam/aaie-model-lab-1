#!/usr/bin/env python
# coding: utf-8

# # Gemini 1.5 -flash Academic Integrity & Feedback Script (Chain-of-Thought)

# ## Overview
# This notebook processes five domain datasets, generates rubric-aligned feedback, and performs AI/Human/Hybrid detection with Chain-of-Thought prompting and voting. CoT allows the AI to reason step-by-step before giving final structured output.

# ## Setup & Dependencies
# 
# Install and import the required Python libraries and the Google GenAI SDK for API access, JSON handling, and data processing.

# In[1]:


# --- Setup & dependencies ---
# pip install -U google-genai
# Environment: export GEMINI_API_KEY="YOUR_KEY"

import os, json, re
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from collections import Counter


# ## Configuration
# 
# Define dataset file paths and maximum few-shot examples.

# In[3]:


# -----------------------------
# CONFIG
# -----------------------------
DATASETS = [
    "engineering.json",
    "accounting.json",
    "it.json",
    "psychology.json",
    "teaching.json"
]
MAX_EXAMPLES = 3


# ## Initialize Gemini
# 
# Set up the Gemini API client and select the model.

# In[5]:


# -----------------------------
# Initialize Gemini
# -----------------------------
client = genai.Client(api_key="ADD YOUR API KEY")
GEMINI_MODEL = "gemini-1.5-flash"


# ## Output Sanitizers & Parsers
# 
# Functions to clean AI outputs and enforce structured format

# In[7]:


# Output sanitizers & parsers
# -----------------------------
_LEAK_PAT = re.compile(
    r"(?im)^(?:reasoning|hidden reasoning|internal reasoning|analysis|"
    r"chain[- ]?of[- ]?thought|scratchpad|thought process)\s*:.*?$"
)

def _strip_leaks(txt: str) -> str:
    return _LEAK_PAT.sub("", txt)

def enforce_detection_format(txt: str) -> str:
    txt = _strip_leaks(txt).strip()
    if "Label:" not in txt:
        txt = "Label: Unknown\n" + txt
    if "Confidence:" not in txt:
        txt += "\nConfidence: 0.50"
    if "Rationale:" not in txt:
        txt += "\nRationale:\n- concise point\n- concise point"
    if "Flags:" not in txt:
        txt += "\nFlags: none"
    if "Diagnostics:" not in txt:
        txt += (
            "\nDiagnostics:\n"
            "- style_repetitiveness: medium\n"
            "- predictability_cues: some\n"
            "- structure_artifacts: some\n"
            "- perturbation_note: not checked"
        )
    return txt.strip()

_det_label_re = re.compile(r"(?im)^Label:\s*(.*)$")
_det_conf_re  = re.compile(r"(?im)^Confidence:\s*([01](?:\.\d+)?)")
_det_flags_re = re.compile(r"(?im)^Flags:\s*(.*)$")

def parse_detection_blocks(txt: str) -> Dict[str, Any]:
    label, conf, flags = None, None, None
    m = _det_label_re.search(txt)
    if m: label = m.group(1).strip()
    m = _det_conf_re.search(txt)
    if m:
        try:
            conf = float(m.group(1))
        except:
            conf = None
    m = _det_flags_re.search(txt)
    if m: flags = m.group(1).strip()
    return {"label": label, "confidence": conf, "flags": flags, "raw": txt}


# ## Chat Rendering
# 
# Format system, user, and assistant messages for Gemini.

# In[9]:


# Chat rendering
# -----------------------------
SYSTEM_PROMPT = (
    "You are a careful academic assistant. Use internal reasoning but never reveal it. "
    "Only output the requested final structured sections (not JSON, not CSV, no files)."
)

def render_chat(system: str, user: str) -> str:
    return f"[SYSTEM] {system}\n[USER] {user}\n[ASSISTANT]"


# In[11]:


# Rubric formatting
# -----------------------------
def format_rubric(r: Dict[str,Any]):
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


# ## Few-Shots Helper
# 
# Select representative examples from Human, AI, and Hybrid labels.

# In[13]:


# Few-shots helper
# -----------------------------
def pick_few_shots(subs: List[Dict[str,Any]], max_examples:int=3) -> List[Dict[str,Any]]:
    """
    Prioritize one example from each label (Human, AI, Hybrid) if available, then fill up.
    """
    buckets = {"Human": [], "AI": [], "Hybrid": []}
    for s in subs:
        label = str(s.get("label_type", "")).strip()
        if label in buckets:
            buckets[label].append(s)
    shots: List[Dict[str,Any]] = []
    for lbl in ["Human","AI","Hybrid"]:
        if buckets[lbl]:
            shots.append(buckets[lbl][0])
    for s in subs:
        if len(shots) >= max_examples:
            break
        if s not in shots:
            shots.append(s)
    return shots[:max_examples]


# ## Feedback Prompt (Chain-of-Thought)
# 
# Prompt the model to reason step-by-step before giving structured feedback.

# In[15]:


# Feedback prompt
# -----------------------------
def build_feedback_prompt(domain: str, assignment_prompt: str, rubric_text: str,
                          submission: str, criterion_names: Optional[List[str]] = None) -> str:
    crit_block = ""
    if criterion_names:
        crit_lines = [f"- {n}" for n in criterion_names]
        crit_block = "Criteria List:\n" + "\n".join(crit_lines) + "\n"
    user_block = f"""
You are a supportive assessor. 
Think step by step about the rubric, the domain, and the student’s submission before producing feedback.  
Internally, perform the following reasoning process (do not show this reasoning in your final output):  
1. Understand assignment context (domain, goals)  
2. Map submission to rubric descriptors  
3. Identify strengths (align with "excellent" or "good")  
4. Identify weaknesses (gaps, misalignments)  
5. Select concrete evidence from text  
6. Suggest actionable, domain-relevant improvements  
7. Ensure tone is constructive, professional, encouraging  
Final output ONLY in this structure (no extra text):
1) Overall Summary: 2–4 sentences  
2) Criteria Feedback:
{('   (cover each criterion listed below)\n' + crit_block) if crit_block else ''}
   - Criterion  
   - Rating (excellent, good, average, needs_improvement, poor)  
   - Evidence (1–3 bullet points tied to submission)  
   - Improvement Tip (1 concrete step)  
3) Suggested Grade (optional)  
DOMAIN:
{domain}
ASSIGNMENT:
{assignment_prompt}
Rubric (verbatim):
{rubric_text}
Student submission:
\"\"\"{submission}\"\"\""""
    return render_chat(SYSTEM_PROMPT, user_block)


# ## Detection Prompt (Chain-of-Thought)
# 
# Prompt the model to reason before deciding Human, AI, or Hybrid.

# In[17]:


# Detection prompt
# -----------------------------
def build_detection_prompt(submission: str, few_shots: List[Dict[str, Any]] = None) -> str:
    examples_block = "/* no examples available */"
    if few_shots:
        shot_texts = []
        for s in few_shots:
            fs_txt = s.get("final_submission", "")
            fs_lbl = s.get("label_type", "Unknown")
            shot_texts.append(
                f'Submission: """{fs_txt}"""\n'
                f'Notes:\n- lexical diversity\n- predictability/artifacts\n- overall evidence\n'
                f'Label: {fs_lbl}\n'
            )
        examples_block = "\n\n".join(shot_texts)

    user_block = f"""
You are an AI text-source classifier for academic integrity.
Internally, think step by step, but only output the final structured result.
Final output ONLY in this structure (no extra commentary):
Label: Human | AI | Hybrid
Confidence: 0.00–1.00
Rationale:
- concise point 1
- concise point 2
Flags: style_inconsistency / high_verbatim / generic_phrasing / none
Diagnostics:
- style_repetitiveness: low|medium|high
- predictability_cues: none|some|strong
- structure_artifacts: none|some|strong
- perturbation_note: one sentence summary
Few-shot exemplars:
{examples_block}
NEW submission:
\"\"\"{submission}\"\"\""""
    return render_chat(SYSTEM_PROMPT, user_block)


# ## Generation Utility
# 
# Call Gemini API to generate text based on the prompt.

# In[19]:


# Generation utility
# -----------------------------
def gen_text(prompt_str: str, max_new_tokens=512, temperature: Optional[float]=None):
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


# ## Self-Consistency Voting
# 
# Run multiple passes and aggregate results for reliability.

# In[21]:


# Self-consistency voting
# -----------------------------
def detect_with_votes(submission: str, few_shots: List[Dict[str,Any]], k: int = 3):
    votes = []
    for j in range(k):
        prompt = build_detection_prompt(submission, few_shots=few_shots)
        raw = gen_text(prompt, max_new_tokens=384, temperature=0.3)
        norm = enforce_detection_format(raw)
        parsed = parse_detection_blocks(norm)
        votes.append(parsed)

    labels = [v.get("label","").lower() for v in votes if v.get("label")]
    confs = [v.get("confidence") for v in votes if isinstance(v.get("confidence"), (int,float))]

    majority = "unknown"
    if labels:
        c = Counter(labels)
        top_label, top_count = c.most_common(1)[0]
        if "ai" in c and "human" in c and abs(c["ai"] - c["human"]) <= 1:
            majority = "hybrid"
        else:
            majority = top_label
    mean_conf = round(sum(confs)/len(confs), 3) if confs else None
    return {"votes": votes, "majority_label": majority.capitalize(), "mean_confidence": mean_conf}


# ## Main Loop – Process 5 Datasets
# 
# Load datasets, generate CoT feedback, and detect AI/Human/Hybrid submissions.

# In[23]:


# MAIN LOOP – process 5 datasets
# -----------------------------
if __name__ == "__main__":
    for dataset in DATASETS:
        with open(dataset, encoding="utf-8") as f:
            data = json.load(f)
        rubric_text, criterion_names = format_rubric(data['rubric'])
        few_shots = pick_few_shots(data['submissions'], MAX_EXAMPLES)

        print(f"\n================= Processing {dataset} =================")

        for i, submission in enumerate(data['submissions'], 1):
            submission_text = submission['final_submission']
            label_type = submission.get("label_type", "Unknown")

            # Generate rubric-aligned feedback
            feedback_prompt = build_feedback_prompt(
                domain=data['domain'],
                assignment_prompt=data.get("prompt", "Analyze student submission"),
                rubric_text=rubric_text,
                submission=submission_text,
                criterion_names=criterion_names
            )
            feedback_response = gen_text(feedback_prompt, max_new_tokens=768, temperature=0.5)

            # Run AI Detection with voting
            det_result = detect_with_votes(submission_text, few_shots, k=3)

            # Print results
            print(f"\n--- SUBMISSION {i} (True Label: {label_type}) ---")
            print("\n--- RUBRIC-ALIGNED FEEDBACK ---\n")
            print(feedback_response)
            print("\n--- ACADEMIC INTEGRITY DETECTION ---\n")
            print(f"Majority Label: {det_result['majority_label']}")
            print(f"Mean Confidence: {det_result['mean_confidence']}")
            for v in det_result['votes']:
                print(f"- Vote: {v['label']} (conf={v['confidence']})")

