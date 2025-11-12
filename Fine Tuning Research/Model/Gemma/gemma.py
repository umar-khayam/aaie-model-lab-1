#!/usr/bin/env python
# coding: utf-8

# # Gemma Model

# In[ ]:


get_ipython().system('pip install -U llama-cpp-python')


# In[ ]:


get_ipython().system('pip install llama-cpp-python')


# In[1]:


from google.colab import drive
drive.mount('/content/drive')


# In[2]:


cd /content/drive/MyDrive/Capston_Project/Training_Data


# ### Libraries

# In[3]:


import json
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

from sklearn.metrics import confusion_matrix, classification_report


# ## Local Inference on GPU
# Model page: https://huggingface.co/google/gemma-2b-it
# 
# ⚠️ If the generated code snippets do not work, please open an issue on either the [model repo](https://huggingface.co/google/gemma-2b-it)
# 			and/or on [huggingface.js](https://github.com/huggingface/huggingface.js/blob/main/packages/tasks/src/model-libraries-snippets.ts) 🙏

# The model you are trying to use is gated. Please make sure you have access to it by visiting the model page.To run inference, either set HF_TOKEN in your environment variables/ Secrets or run the following cell to login. 🤗

# In[ ]:


from huggingface_hub import login
login(new_session=False)


# ### Model Loading

# In[ ]:


from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-1b-it")
model_gemma = AutoModelForCausalLM.from_pretrained(
    "google/gemma-3-1b-it",
    torch_dtype=torch.bfloat16
)


# ### Prompts

# In[39]:


SYSTEM_PROMPT = "You are a careful academic assistant. Be precise and return strict JSON."

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
        - Strict JSON schema output

    JSON Schema (strict):
        {
          "label": "Human|AI|Hybrid",
          "rationale": "1–3 short bullet points of evidence",
          "flags": ["style_inconsistency","high_verbatim","generic_phrasing","none"]
        }
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

    # User-facing content
    user = f"""
You are an AI text-source classifier for academic integrity.
Decide whether the student submission is Human, AI, or Hybrid (AI-assisted).

Guidelines:
- Consider discourse features (specificity, subjectivity, personal context), style consistency, local/global coherence, repetitiveness, and cliché patterns.
- Hybrid = meaningful human writing with some AI assistance (ideas, phrasing, structure), or explicit admission of mixed use.

Examples:
{examples_block}

Now analyze the NEW submission step by step and return STRICT JSON.
NEW submission:
\"\"\"{submission}\"\"\"\n
Think briefly, then answer only with the JSON object.
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


# In[40]:


def build_feedback_prompt(domain: str, assignment_prompt: str, rubric_text: str, submission: str) -> List[Dict[str, str]]:
    user = f"""
You are a supportive assessor. Provide actionable feedback aligned to the rubric.
Return a STRUCTURED report (no extraneous text).

Sections:
1) "overall_summary": 2–4 sentences on strengths and priorities.
2) "criteria_feedback": array of items, one per rubric criterion with fields:
   - "criterion_id"
   - "rating": one of ["excellent","good","average","needs_improvement","poor"]
   - "evidence": 1–3 bullet points citing concrete excerpt(s) or behaviors
   - "improvement_tip": one concrete next step

Context:
- Domain: {domain}
- Assignment prompt: {assignment_prompt}

Rubric (verbatim):
{rubric_text}

Student submission:
\"\"\"{submission}\"\"\"\n

Constraints:
- Be concise but specific. Do not invent rubric fields. If evidence is insufficient, say so.
- Output MUST be valid JSON with the exact top-level keys: overall_summary, criteria_feedback, suggested_grade.
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


# ### Function to run model

# In[41]:


def run_messages(model, tokenizer, messages, max_new_tokens=400):
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_ids_length = inputs.input_ids.shape[1]

    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=max_new_tokens,
        temperature=0.0,
        top_p=1.0,
        do_sample=False
    )

    gen_tokens = outputs[0, input_ids_length:]
    resp = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    # Remove common wrappers
    resp = re.sub(r"^```(?:json)?", "", resp.strip(), flags=re.IGNORECASE | re.MULTILINE)
    resp = re.sub(r"```$", "", resp.strip(), flags=re.MULTILINE)

    try:
        start, end = resp.find("{"), resp.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(resp[start:end])
    except Exception:
        pass

    return {"error": "Could not parse output", "raw_output": resp}


# ### Function to Evaluate Model

# In[42]:


def self_eval_prompt(rubric: Dict, essay: str, feedback: str) -> str:
    crit = [c.get('name','Criterion') for c in rubric.get('criteria',[])]
    crit_str = ", ".join(crit) if crit else "the rubric"

    return (
        "You are a strict but fair assessor. Rate how well the FEEDBACK addresses the rubric for the ESSAY.\n"
        "Rate on a 1-5 scale (integers only). Provide ONLY the number.\n\n"
        f"ESSAY:\n{essay}\n\nRUBRIC CRITERIA: {crit_str}\n\nFEEDBACK:\n{feedback}\n\nRATING (1-5): "
    )


# ### Selection from the data to balance each class

# In[43]:


def select_balanced_few_shots(submissions: List[Dict[str, Any]], max_per_class: int = 1) -> List[Dict[str, Any]]:
    """
    Pick up to max_per_class examples from each label type.
    Ensures few-shots are not biased toward one label.
    """
    buckets = {"Human": [], "AI": [], "Hybrid": []}
    for s in submissions:
        label = s.get("label_type")
        if label in buckets and len(buckets[label]) < max_per_class:
            buckets[label].append(s)
    return buckets["Human"] + buckets["AI"] + buckets["Hybrid"]


# ### Content Detection and Feedback Generation

# In[44]:


# class for evaluating the model
class AcademicEvaluator:
    # takes the model and tokenizer
    def __init__(self, model: AutoModelForCausalLM, tokenizer: AutoTokenizer, data: Dict[str, Any]):
        self.model = model
        self.tokenizer = tokenizer
        self.data = data
        self.domain = self.data["domain"]
        self.assignment_prompt = self.data["prompt"]
        self.rubric_text = json.dumps(self.data["rubric"], indent=2)
        self.submissions = self.data["submissions"]

    def detect(self, submission_text: str, few_shot_count: int = 2) -> Dict[str, Any]:
        few_shots = select_balanced_few_shots(self.submissions, max_per_class=1)
        messages = build_detection_prompt(submission_text, few_shots)
        return run_messages(self.model, self.tokenizer, messages, max_new_tokens=300)

    def feedback(self, submission_text: str) -> Dict[str, Any]:
        messages = build_feedback_prompt(self.domain, self.assignment_prompt, self.rubric_text, submission_text)
        # It passes the model and tokenizer to the runner function.
        return run_messages(self.model, self.tokenizer, messages, max_new_tokens=800)

    def rate_feedback(self, submission_text: str, feedback: str) -> float:
        prompt = self_eval_prompt(self.data["rubric"], submission_text, feedback)
        messages = [
            {"role": "system", "content": "You are a careful academic assistant. Reply ONLY with a number."},
            {"role": "user", "content": prompt}
        ]
        result = run_messages(self.model, self.tokenizer, messages, max_new_tokens=10)

        if isinstance(result, dict):
            raw = result.get("raw_output", "")
            return float(re.sub(r"\D", "", raw) or 3)
        elif isinstance(result, str):
            return float(result.strip())
        else:
            return 3.0

class DomainManager:
    # takes the model and tokenizer
    def __init__(self, model: AutoModelForCausalLM, tokenizer: AutoTokenizer, file_paths: List[str]):
        self.model = model
        self.tokenizer = tokenizer
        self.domains_data = {}
        print(f"Loading data from {len(file_paths)} files...")
        for path in file_paths:
            try:
                with open(path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    domain_name = data.get("domain")
                    if domain_name:
                        self.domains_data[domain_name] = data
                        print(f"  - Loaded domain: {domain_name}")
            except Exception as e:
                print(f"  - ERROR: Failed to load or parse {path}: {e}")

    def list_domains(self) -> List[str]:
        return list(self.domains_data.keys())

    def get_evaluator(self, domain_name: str) -> Optional[AcademicEvaluator]:
        domain_data = self.domains_data.get(domain_name)
        if domain_data:
            # It passes the model and tokenizer when creating the evaluator.
            return AcademicEvaluator(self.model, self.tokenizer, domain_data)
        else:
            print(f"Error: Domain '{domain_name}' not found.")
            return None


# ### Main Function to Run

# IT Domain

# In[13]:


if __name__ == "__main__":
    json_files = ["it.json"]

    # loading of model and tokenizer
    manager = DomainManager(model_gemma, tokenizer, json_files)
    print("-" * 20)
    print(f"Available domains: {manager.list_domains()}")
    print("-" * 20)

    # loop through all domains
    for domain_to_evaluate in manager.list_domains():
        print(f"\n=== STARTING EVALUATION FOR '{domain_to_evaluate}' DOMAIN ===")
        evaluator = manager.get_evaluator(domain_to_evaluate)

        if evaluator:
            for idx, submission_data in enumerate(evaluator.submissions):
                submission_text = submission_data["final_submission"]
                ground_truth_label = submission_data["label_type"]

                print(f"\n--- Submission {idx + 1} ---")
                print(f"Ground truth label: {ground_truth_label}")
                print(f"Submission Text: \"{submission_text[:100]}...\"")

                print("\n--- DETECTION ---")
                detection_result = evaluator.detect(submission_text)
                print(json.dumps(detection_result, indent=2, ensure_ascii=False))

                print("\n--- FEEDBACK ---")
                feedback_result = evaluator.feedback(submission_text)
                print(json.dumps(detection_result, indent=2, ensure_ascii=False))

                print("\n--- FEEDBACK RATING ---")
                feedback_str = json.dumps(feedback_result)
                rating = evaluator.rate_feedback(submission_text, feedback_str)
                print(f"Feedback rating (1–5): {rating}")


# ### Engineering Domain

# In[63]:


if __name__ == "__main__":
    json_files = ["engineering.json"]

    # The manager is created with the loaded model and tokenizer.
    manager = DomainManager(model_gemma, tokenizer, json_files)
    print("-" * 20)
    print(f"Available domains: {manager.list_domains()}")
    print("-" * 20)

    # Loop through all domains
    for domain_to_evaluate in manager.list_domains():
        print(f"\n=== STARTING EVALUATION FOR '{domain_to_evaluate}' DOMAIN ===")
        evaluator = manager.get_evaluator(domain_to_evaluate)

        if evaluator:
            for idx, submission_data in enumerate(evaluator.submissions):
                submission_text = submission_data["final_submission"]
                ground_truth_label = submission_data["label_type"]

                print(f"\n--- Submission {idx + 1} ---")
                print(f"Ground truth label: {ground_truth_label}")
                print(f"Submission Text: \"{submission_text[:100]}...\"")

                print("\n--- DETECTION ---")
                detection_result = evaluator.detect(submission_text)
                print(json.dumps(detection_result, indent=2, ensure_ascii=False))

                print("\n--- FEEDBACK ---")
                feedback_result = evaluator.feedback(submission_text)
                print(json.dumps(feedback_result, indent=2, ensure_ascii=False))

                print("\n--- FEEDBACK RATING ---")
                feedback_str = json.dumps(feedback_result)
                rating = evaluator.rate_feedback(submission_text, feedback_str)
                print(f"Feedback rating (1–5): {rating}")


# ### Gen AI Rating
# Gemma Model Evaluation
# 
# - Feedback Generation Quality: 4/5
# Gemma generates structured, rubric-style feedback with clear criteria and detailed points. It produces professional and academic-style responses, which makes it useful in evaluation tasks. However, it often repeats phrasing (e.g., “The submission demonstrates a solid understanding...”) and lacks personalization, so feedback can feel generic across different inputs.
# 
# - AI Detection Accuracy: 1/5
# Gemma shows a strong bias when labeling human vs. AI vs hybrid submissions. It tends to misclassify, often leaning too heavily toward one category. The detection is unreliable and cannot be used in real-world classification tasks.

# ### Human Evaluation
# 
# ##### 1. Feedback Generation
# - Clarity & Structure: Responses are rubric-style, structured, and well-aligned with evaluation criteria.
# - Weakness: Repetitive language, limited personalization, identical phrases across multiple submissions.
# 
# Score: 4/5
# Reasoning: Clear, structured, but lacks originality and personalization.
# 
# ##### 2. AI Detection
# - Binary Classification Performance: Frequently misclassifies. Strong bias and tends to over-predict hybrid 
# AI-generated and human structured content are labeled incorrectly. And accuracy is very low (close to chance).
# 
# Score: 1/5
# Reasoning: Detection is unreliable and unusable for real-world use.
# 
# 
# #### Submission based feedback
# ##### 1. Submission
# 
# - True Classification: AI
# - Model Prediction: hybrid
# - Evaluation Result: Wrong
# - Confidence Level: High
# -Key Observations: Structured, polished writing with formal tone. Gemma misclassified as hybrid due to generic fluency.
# - Rater: Umar Khayam
# - Date: 04/09/2025
# 
# ##### 2. Submission
# 
# - True Classification: AI
# - Model Prediction: AI
# - Evaluation Result: Correct
# - Confidence Level: High
# - Key Observations: Technical termenology and sturctured writing. 
# - Rater: Umar Khayam
# - Date: 04/09/2025
# 
# ##### 3. Submission
# 
# - True Classification: Human
# - Model Prediction: Hybrid
# - Evaluation Result: Wrong
# - Confidence Level: Hybrid
# - Key Observations: Natural imperfections misclassified as Hybrid.
# - Rater: Umar Khayam
# - Date: 04/09/2025
# 
# ##### 4. Submission
# 
# - True Classification: Human
# - Model Prediction: Hybrid
# - Evaluation Result: Wrong
# - Confidence Level: High
# - Key Observations: Describes lived experience as junior analyst. Imperfect flow, but Gemma misclassified.
# - Rater: Umar Khayam
# - Date: 04/09/2025
# 
# ##### 5. Submission
# 
# - True Classification: Hybrid
# - Model Prediction: Hybrid
# - Evaluation Result: correct
# - Confidence Level: Medium
# - Key Observations: Mix of AI-like structure and human  reflection. Over-classified as hybrid, missing the nuance.
# - Rater: Umar Khayam
# - Date: 04/09/2025
# 
# ##### 6. Submission
# 
# - True Classification: Hybrid
# - Model Prediction: Hybrid
# - Evaluation Result: correct
# - Confidence Level: Medium
# - Key Observations: Balanced account of AI + human collaboration in red/blue team context.
# - Rater: Umar Khayam
# - Date: 04/09/2025

# 

# In[61]:




