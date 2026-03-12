# =========================================================
# 1. Imports & Config
# =========================================================
import json
import re
import time
import random
from typing import Optional
from google import genai
from google.genai import types
from google.genai.errors import ServerError

API_KEY = ""
GEMINI_MODEL = "gemini-2.5-flash-lite"
INPUT_PATH = "rub_it_0002.json"

client = genai.Client(api_key=API_KEY)

# =========================================================
# 2. System Prompt
# =========================================================
SYSTEM_PROMPT = """
You are an expert educational feedback generator trained to provide credible, educator-trusted feedback.

CRITICAL INSTRUCTION
You are evaluating ONLY the STUDENT'S FINAL SUBMISSION.
Do NOT infer intent beyond the written submission.
Do NOT evaluate any AI interactions or drafting process.
"""

# =========================================================
# 3. Output Validation
# =========================================================
def output_incomplete(text: str) -> bool:
    patterns = [
        r"\[.*?sentence.*?\]",
        r"→ .*?:\s*\[",
        r"Write a \d–\d sentence",
        r"\[\d–\d\]",
    ]
    return any(re.search(p, text) for p in patterns)

# =========================================================
# 4. Rubric Score Parsing & Weighting
# =========================================================
score_with_text_pattern = re.compile(
    r"^(.*?):\s*(10|[0-9])\s*/\s*10\s*-\s*(.*)$",
    re.MULTILINE
)

def extract_scores_and_feedback(feedback_text: str):
    scores = {}
    feedback = {}
    for match in score_with_text_pattern.finditer(feedback_text):
        name = match.group(1).strip()
        score = int(match.group(2))
        explanation = match.group(3).strip()
        scores[name] = score
        feedback[name] = explanation
    return scores, feedback


def compute_weighted_score(rubric: dict, scores_by_name: dict) -> float:
    total_weight = 0.0
    weighted_sum = 0.0

    for c in rubric.get("criteria", []):
        name = c.get("name")
        weight = float(c.get("weight", 0))
        if name in scores_by_name:
            weighted_sum += (scores_by_name[name] / 10.0) * weight
            total_weight += weight

    if total_weight == 0:
        return 0.0

    return round((weighted_sum / total_weight) * 100, 1)

# =========================================================
# 5. Gemini Call Helper (with retry for 503)
# =========================================================
def gen_text(prompt_str: str,
             max_new_tokens: int = 1536,
             temperature: Optional[float] = 0.4,
             max_retries: int = 5) -> str:

    cfg = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_new_tokens,
    )

    for attempt in range(1, max_retries + 1):
        try:
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt_str,
                config=cfg,
            )
            return "".join(p.text for p in resp.candidates[0].content.parts)

        except ServerError:
            wait = min(2 ** attempt + random.uniform(0, 1), 20)
            print(f"Gemini overloaded (attempt {attempt}/{max_retries}). Retrying in {wait:.1f}s...")
            time.sleep(wait)

    raise RuntimeError("Gemini API unavailable after multiple retries.")

# =========================================================
# 6. Build Feedback Prompt (FINAL SUBMISSION ONLY)
# =========================================================
def build_feedback_prompt(domain: str,
                          assignment_prompt: str,
                          rubric: dict,
                          submission: dict) -> str:

    rubric_text = json.dumps(rubric, indent=2)
    criteria = rubric.get("criteria", [])

    c1 = criteria[0]["name"] if len(criteria) > 0 else "Criterion 1"
    c2 = criteria[1]["name"] if len(criteria) > 1 else "Criterion 2"
    c3 = criteria[2]["name"] if len(criteria) > 2 else "Criterion 3"
    c4 = criteria[3]["name"] if len(criteria) > 3 else "Criterion 4"

    final_submission = submission.get("final_submission", "")
    quality = submission.get("quality", "")
    authorship = submission.get("authorship", "")

    structured_output_prompt = f"""
You MUST produce EXACTLY TWO SECTIONS in plain text, in this order:
1) EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS
2) RUBRIC SCORES

═════════════════════════════════════════════════════════
EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS
═════════════════════════════════════════════════════════
Write ONE cohesive paragraph (maximum 100 words) covering:
- Strengths demonstrated in the submission
- Areas for improvement
- Academic quality and depth
- Practical next steps for improvement

═════════════════════════════════════════════════════════
RUBRIC SCORES
═════════════════════════════════════════════════════════
For EACH criterion below, output a single line in this format:
CriterionName: SCORE/10 - short explanation (maximum 40 words).

Use an INTEGER SCORE from 0 to 10.

{c1}: SCORE/10 - explanation
{c2}: SCORE/10 - explanation
{c3}: SCORE/10 - explanation
{c4}: SCORE/10 - explanation
"""

    return f"""
{SYSTEM_PROMPT}

DOMAIN:
{domain}

ASSIGNMENT PROMPT:
\"\"\"{assignment_prompt}\"\"\"

ASSESSMENT RUBRIC (reference only):
{rubric_text}

GROUND TRUTH LABELS (do not bias judgement):
- Declared quality: {quality}
- Authorship label: {authorship}

═══════════════════════════════════════════════════════════
STUDENT FINAL SUBMISSION (EVALUATE THIS ONLY):
═══════════════════════════════════════════════════════════
\"\"\"{final_submission}\"\"\"

EVALUATION INSTRUCTIONS:
- Evaluate clarity, depth, critical thinking, structure, and academic tone
- Align judgement strictly to the rubric
- Do NOT reference AI use or drafting process

NOW GENERATE THE OUTPUT USING THIS STRUCTURE:
{structured_output_prompt}
"""

# =========================================================
# 7. Load Input
# =========================================================
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

domain = data["domain"]
assignment_prompt = data["prompt"]
rubric = data["rubric"]
submissions = data["submissions"]

print(f"Loaded domain: {domain}")
print(f"Total submissions: {len(submissions)}")

# =========================================================
# 8. Run Feedback Generation
# =========================================================
all_results = []

for idx, submission in enumerate(submissions, start=1):
    print(f"\n================= Processing submission {idx} =================")

    prompt_str = build_feedback_prompt(
        domain,
        assignment_prompt,
        rubric,
        submission
    )

    feedback_text = gen_text(prompt_str)

    retry = 0
    while output_incomplete(feedback_text) and retry < 2:
        print("Incomplete output detected — retrying...")
        feedback_text = gen_text(prompt_str)
        retry += 1

    feedback_text = feedback_text.strip()

    criterion_scores, criterion_feedback = extract_scores_and_feedback(feedback_text)
    weighted_score_percent = compute_weighted_score(rubric, criterion_scores)

    all_results.append({
        "index": idx,
        "quality": submission.get("quality"),
        "authorship": submission.get("authorship"),
        "criterion_scores": criterion_scores,
        "criterion_feedback": criterion_feedback,
        "weighted_score_percent": weighted_score_percent,
        "feedback": feedback_text
    })

    print("Parsed scores:", criterion_scores)
    print("Weighted score (%):", weighted_score_percent)

# =========================================================
# 9. Save Results
# =========================================================
OUTPUT_PATH = "FG_Feedback_Results_with_Scores.json"
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(all_results)} feedback reports to {OUTPUT_PATH}")

