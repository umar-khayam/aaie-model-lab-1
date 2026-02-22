"""Experimental Plan - Experimental script for educationally oriented feedback generation using Gemini models.
### Author
*Name: Qasim Nasir*,
*Student ID: 223282352*,
*E-mail: 223282352@deakin.edu.au*

## Import Libraries
"""
import re
import json
from typing import Optional
from google import genai
from google.genai import types

"""## CONFIGURATION"""

API_KEY = "api_key_goes_here"
GEMINI_MODEL = "gemini-2.5-flash-lite"
INPUT_PATH = "TestingSample.json"   # file using the new schema

client = genai.Client(api_key=API_KEY)

"""## Prompt Templates"""

SYSTEM_PROMPT = """
You are an expert educational feedback generator trained to provide credible, educator-trusted feedback.

⚠️ CRITICAL INSTRUCTION ⚠️
You are evaluating ONLY the STUDENT's typed prompts ("User:" lines).
NEVER evaluate or interpret the AI's responses ("AI:" lines).
"""

STRUCTURED_OUTPUT_PROMPT = """
You MUST follow the structure below EXACTLY.
You MUST fill in ALL sections fully.
You MUST NOT leave any bracketed text, placeholders, or instructions.

═════════════════════════════════════════════════════════
EDUCATOR FEEDBACK & ACTIONABLE INSIGHTS
═════════════════════════════════════════════════════════

[Strengths Section - 2-3 sentences]
Identify the key strengths demonstrated by this student's learning approach and questioning strategy. What did they do well?

[Areas for Improvement - 2-3 sentences]
Identify specific areas where the student could enhance their LLM-assisted learning process. Be constructive and specific.

[Engagement Level - 1-2 sentences]
Rate and describe the student's overall engagement with the assignment on a spectrum from passive to deeply engaged.

[Follow-up Actions - 2-3 sentences]
Suggest concrete follow-up actions or strategies the student could implement to strengthen their learning outcomes. Provide actionable next steps.

═════════════════════════════════════════════════════════
RUBRIC SCORES
═════════════════════════════════════════════════════════
Criterion 1 (Inquiry Depth & Progression): [0–5] - One sentence evaluating how the student's questions evolved
Criterion 2 (Active Learning Behaviors): [0–5] - One sentence evaluating the student's engagement behaviors
Criterion 3 (Prompt Clarity & Intentionality): [0–5] - One sentence evaluating the clarity of the student's prompts
Criterion 4 (Persistence & Goal-Directedness): [0–5] - One sentence evaluating the student's sustained focus

═════════════════════════════════════════════════════════
LEARNING BEHAVIOR ANALYSIS
═════════════════════════════════════════════════════════

→ Inquiry Pattern Analysis:
Provide 2–3 complete sentences analyzing the student's questioning strategy.

→ Active vs. Passive Learning:
Provide 2–3 complete sentences evaluating the student's active learning behaviors.

→ Communication Effectiveness:
Provide 2–3 complete sentences explaining how clearly the student communicated.

→ Learning Goal Achievement:
Provide 2–3 complete sentences explaining whether the student's prompts support actual learning.

═════════════════════════════════════════════════════════
LEARNING PROCESS SUMMARY
═════════════════════════════════════════════════════════

Write a 3–4 sentence opening paragraph summarizing the student's learning behavior.
Write a 4–5 sentence evidence paragraph based on the student's prompts.
Write a 2–3 sentence recommendations paragraph.

IMPORTANT:
- NO placeholders.
- NO bracketed text.
- NO missing sections.
"""

# ============================================================================
# OUTPUT VALIDATION
# ============================================================================

def output_incomplete(text: str) -> bool:
    patterns = [
        r"\[0–5\].*?sentence",
        r"\[.*?sentence",
        r"→ .*?:\s*\[",
        r"\[2–3.*?\]",
        r"Write a 3–4 sentence",
    ]
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

"""## Helper: Model Call"""

# MODEL CALL
# ============================================================================
def gen_text(prompt_str: str,
             max_new_tokens: int = 2048,
             temperature: float = 0.4):

    cfg = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_new_tokens,
    )

    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt_str,
        config=cfg
    )

    return "".join(p.text for p in resp.candidates[0].content.parts)

"""## Build Feedback Prompt"""

def build_feedback_prompt(domain: str,
                          assignment_prompt: str,
                          rubric: dict,
                          submission: dict) -> str:
    """
    Builds the full evaluation prompt from the new schema:
    - domain
    - assignment_prompt (top-level prompt)
    - rubric (object)
    - submission with fields like quality, authorship, llm_questions, llm_answers, final_submission
    """
    rubric_text = json.dumps(rubric, indent=2)

    # Rebuild a User/AI conversation from llm_questions + llm_answers
    prompt_chain = []
    questions = submission.get("llm_questions", [])
    answers = submission.get("llm_answers", [])

    for q, a in zip(questions, answers):
        prompt_chain.append(f"User: {q}")
        prompt_chain.append(f"AI: {a}")

    # Student prompts = questions only
    student_prompts_only = questions
    student_prompts_list = "\n".join(
        f"  {i+1}. \"{p}\"" for i, p in enumerate(student_prompts_only)
    )

    final_submission = submission.get("final_submission", "")
    quality = submission.get("quality", "")
    authorship = submission.get("authorship", "")

    return f"""
{SYSTEM_PROMPT}

TASK CONTEXT:
You are assessing a STUDENT's inquiry and learning process from the domain: **{domain}**.
The assignment prompt is:
\"\"\"{assignment_prompt}\"\"\"

ASSESSMENT RUBRIC:
{rubric_text}

GROUND TRUTH LABELS (for analysis only, do not let this bias your scoring):
- Declared quality band: {quality}
- Authorship label: {authorship}

═══════════════════════════════════════════════════════════
STUDENT'S PROMPTS (What the student actually typed):
═══════════════════════════════════════════════════════════
{student_prompts_list}

═══════════════════════════════════════════════════════════
FULL CONVERSATION (For context only):
═══════════════════════════════════════════════════════════
{json.dumps(prompt_chain, indent=2)}

⚠️ REMEMBER:
- Evaluate ONLY what the student typed (User: lines)
- AI responses are context only
- Do NOT credit the student for what the AI said or inferred

FINAL SUBMISSION (For Context):
\"\"\"{final_submission}\"\"\"

EVALUATION INSTRUCTIONS:

1. PRIMARY FOCUS: Analyze ONLY the student's typed prompts (listed above).

2. Evaluate the STUDENT based on their prompts:
   ✓ What topics did the STUDENT choose to ask about?
   ✓ How did the STUDENT's questions change over time?
   ✓ Did the STUDENT ask follow-up questions on topics?
   ✓ Did the STUDENT's prompts become more specific or stay general?
   ✓ Did the STUDENT ask "why/how" questions or request explanations?

3. COMMON MISTAKES TO AVOID:
   ✗ Do NOT say "the student self-corrected" when the AI corrected something
   ✗ Do NOT credit the student for the AI's interpretations
   ✗ Do NOT evaluate the quality of AI responses
   ✗ Do NOT praise "the student's ability to clarify" when the AI asked for clarification

   ONLY evaluate what the student actually typed.

4. Focus on observable learning behaviors:
   - Progression from broad to specific (or vice versa)
   - Use of question words (why, how, what, when)
   - Requests for examples, explanations, or clarifications
   - Topic persistence (staying on one subject) vs exploration (jumping around)
   - Complexity or simplicity of prompts

5. Provide credible, educationally meaningful feedback about the STUDENT's questioning behavior.

6. Maintain structured outputs with clear focus on what the STUDENT did.

{STRUCTURED_OUTPUT_PROMPT}
"""

"""## Load Data & Run Feedback Generation over Submissions"""

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

domain = data["domain"]
assignment_prompt = data["prompt"]
rubric = data["rubric"]
submissions = data["submissions"]

print(f"Loaded domain: {domain}")
print(f"Total submissions: {len(submissions)}")

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

    result_record = {
        "index": idx,
        "quality": submission.get("quality"),
        "authorship": submission.get("authorship"),
        "feedback_report": feedback_text
    }
    all_results.append(result_record)

    # Optional: print a short preview
    print(feedback_text[:5000], "...\n")

"""## Save Results"""

output_path = "FeedbackResults.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(all_results)} feedback reports to {output_path}")