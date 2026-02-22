# 1. Imports & Config
# =========================
import json
import re
from typing import Optional, List
from google import genai
from google.genai import types

API_KEY = ""
GEMINI_MODEL = "gemini-2.5-flash-lite"
INPUT_PATH = "rub_it_0002.json"   # uses your rubric + submissions schema

client = genai.Client(api_key=API_KEY)

# =========================
# 2. Prompts
# =========================
SYSTEM_PROMPT = """
You are an expert educational feedback generator trained to provide credible, educator-trusted feedback.

⚠️ CRITICAL INSTRUCTION ⚠️
You are evaluating ONLY the STUDENT's typed prompts ("User:" lines).
NEVER evaluate or interpret the AI's responses ("AI:" lines).
"""

# ================================================================
# 3. OUTPUT VALIDATION
# ================================================================
def output_incomplete(text: str) -> bool:
    """
    Detects missing placeholders or instructions left in the output.
    """
    patterns = [
        r"\[.*?sentence.*?\]",
        r"→ .*?:\s*\[",
        r"Write a 3–4 sentence",
        r"Write a 4–5 sentence",
        r"Write a 2–3 sentence",
        r"\[0–5\]",
    ]
    return any(re.search(p, text) for p in patterns)

# ================================================================
# 4. RUBRIC SCORE & FEEDBACK EXTRACTION + WEIGHTING
# ================================================================
# Lines like: CriterionName: 8/10 - explanation...
score_with_text_pattern = re.compile(
    r"^(.*?):\s*(10|[0-9])\s*/\s*10\s*-\s*(.*)$",
    re.MULTILINE
)

def extract_scores_and_feedback(feedback_text: str) -> tuple[dict, dict]:
    """
    Parse 'CriterionName: SCORE/10 - explanation' lines.

    Returns:
      scores_by_name:   {criterion_name: int_score}
      feedback_by_name: {criterion_name: explanation_text}
    """
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
    """
    Compute weighted percentage using rubric['criteria'][].weight.

    Each criterion:
      - has a 'weight' (any scale, e.g. 40,20,15,25)
      - score is 0–10 from the model

    Returns overall score as percentage 0–100 (float, 1 decimal).
    """
    total_weight = 0.0
    weighted_sum = 0.0

    for c in rubric.get("criteria", []):
        name = c.get("name")
        weight = float(c.get("weight", 0))
        if not name or weight <= 0:
            continue
        total_weight += weight
        score = scores_by_name.get(name)
        if score is None:
            continue
        weighted_sum += (score / 10.0) * weight  # 0–10 scale

    if total_weight == 0:
        return 0.0
    return round((weighted_sum / total_weight) * 100, 1)

# =========================
# 5. Gemini Call Helper
# =========================
def gen_text(prompt_str: str,
             max_new_tokens: int = 1536,
             temperature: Optional[float] = 0.4) -> str:
    cfg = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_new_tokens,
    )
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt_str,
        config=cfg,
    )
    return "".join(p.text for p in resp.candidates[0].content.parts)

# =========================
# 6. Build Feedback Prompt
# =========================
def build_feedback_prompt(domain: str,
                          assignment_prompt: str,
                          rubric: dict,
                          submission: dict) -> str:
    """
    Builds the full prompt for Gemini and the two-section output
    with numeric rubric scores (0–10).
    """
    rubric_text = json.dumps(rubric, indent=2)

    # rubric criterion names from input schema
    criteria = rubric.get("criteria", [])
    c1_name = criteria[0]["name"] if len(criteria) > 0 else "Criterion 1"
    c2_name = criteria[1]["name"] if len(criteria) > 1 else "Criterion 2"
    c3_name = criteria[2]["name"] if len(criteria) > 2 else "Criterion 3"
    c4_name = criteria[3]["name"] if len(criteria) > 3 else "Criterion 4"

    # student prompts + conversation
    questions: List[str] = submission.get("llm_questions", [])
    answers: List[str] = submission.get("llm_answers", [])

    conversation_pairs = []
    for q, a in zip(questions, answers):
        conversation_pairs.append(f"User: {q}")
        conversation_pairs.append(f"AI: {a}")

    student_prompts_list = "\n".join(
        f"{i+1}. \"{q}\"" for i, q in enumerate(questions)
    )

    final_submission = submission.get("final_submission", "")
    quality = submission.get("quality", "")
    authorship = submission.get("authorship", "")

    structured_output_prompt = f"""
You MUST produce EXACTLY TWO SECTIONS in plain text, in this order:
1) EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS
2) RUBRIC SCORES

Do NOT include headings for any other sections.
Do NOT stop after the first section.

═════════════════════════════════════════════════════════
EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS
═════════════════════════════════════════════════════════
Write ONE cohesive paragraph (maximum 100 words) that clearly covers, in flowing prose:
- Strengths: strong learning behaviours the student shows.
- Areas for Improvement: where the student can grow, specific and constructive.
- Engagement Level: how actively and consistently the student engaged.
- Follow-up Actions: practical next steps or strategies the student could try.

═════════════════════════════════════════════════════════
RUBRIC SCORES
═════════════════════════════════════════════════════════
For EACH criterion below, output a single line in this format:
CriterionName: SCORE/10 - short explanation (maximum 40 words).

Use an INTEGER SCORE from 0 to 10.
Do NOT put any text in square brackets.

{c1_name}: SCORE/10 - explanation
{c2_name}: SCORE/10 - explanation
{c3_name}: SCORE/10 - explanation
{c4_name}: SCORE/10 - explanation
"""

    return f"""
{SYSTEM_PROMPT}

TASK CONTEXT:
You are assessing a STUDENT's inquiry and learning process from the domain: **{domain}**.
The assignment prompt is:
\"\"\"{assignment_prompt}\"\"\"

ASSESSMENT RUBRIC (for your reference only):
{rubric_text}

GROUND TRUTH LABELS (for analysis only, do not let this bias you):
- Declared quality band: {quality}
- Authorship label: {authorship}

═══════════════════════════════════════════════════════════
STUDENT'S PROMPTS (What the student actually typed):
═══════════════════════════════════════════════════════════
{student_prompts_list}

═══════════════════════════════════════════════════════════
FULL CONVERSATION (context only — do NOT evaluate AI responses):
═══════════════════════════════════════════════════════════
{json.dumps(conversation_pairs, indent=2)}

FINAL SUBMISSION (context only):
\"\"\"{final_submission}\"\"\"

EVALUATION INSTRUCTIONS:
- Evaluate ONLY the student's prompts.
- Focus on inquiry depth, active learning behaviours, clarity, and persistence.
- Use evidence from the prompts to support all explanations.
- Do NOT comment on the quality of AI responses.

NOW GENERATE THE OUTPUT USING THIS STRUCTURE:
{structured_output_prompt}
"""

# =========================
# 7. Load Data
# =========================
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

domain = data["domain"]
assignment_prompt = data["prompt"]
rubric = data["rubric"]
submissions = data["submissions"]

print(f"Loaded domain: {domain}")
print(f"Total submissions: {len(submissions)}")

# =========================
# 8. Run FG Over Submissions
# =========================
all_results = []

for idx, submission in enumerate(submissions, start=1):
    print(f"\n================= Processing submission {idx} =================")

    prompt_str = build_feedback_prompt(
        domain=domain,
        assignment_prompt=assignment_prompt,
        rubric=rubric,
        submission=submission,
    )

    feedback_text = gen_text(prompt_str)

    # Retry only if obvious placeholders remain
    retry = 0
    while output_incomplete(feedback_text) and retry < 2:
        print("⚠️ Output appears incomplete – retrying...")
        feedback_text = gen_text(prompt_str)
        retry += 1

    feedback_text = feedback_text.strip()

    # ----- rubric scores and per‑criterion feedback -----
    criterion_scores, criterion_feedback = extract_scores_and_feedback(feedback_text)
    weighted_score_percent = compute_weighted_score(rubric, criterion_scores)

    result_record = {
        "index": idx,
        "quality": submission.get("quality"),
        "authorship": submission.get("authorship"),
        "criterion_scores": criterion_scores,        # {criterion_name: score}
        "criterion_feedback": criterion_feedback,    # {criterion_name: explanation}
        "weighted_score_percent": weighted_score_percent,
        "feedback": feedback_text,                   # full text output
    }
    all_results.append(result_record)

    print(feedback_text[:1300], "...\n")
    print("Parsed scores:", criterion_scores)
    print("Weighted score (%):", weighted_score_percent)

# =========================
# 9. Save Results
# =========================
OUTPUT_PATH = "FG_Feedback_Results_with_Scores.json"
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(all_results)} feedback reports with scores to {OUTPUT_PATH}")

