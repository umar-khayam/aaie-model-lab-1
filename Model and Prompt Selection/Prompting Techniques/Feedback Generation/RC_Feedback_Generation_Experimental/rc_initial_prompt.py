# import required libraries
import json
import os
from typing import Optional
from google import genai
from google.genai import types

# Initialize Gemini API client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
GEMINI_MODEL = "gemini-2.5-flash-lite"

# prompt templates
SYSTEM_PROMPT = """
You are an expert educational feedback generator trained to provide credible, educator-trusted feedback on student work.

⚠️ CRITICAL INSTRUCTION ⚠️
You are evaluating ONLY what the STUDENT typed/asked in their prompts.
You are NOT evaluating the AI assistant's responses or interpretations.

In the conversation:
- "User:" = STUDENT (the person being graded)
- "AI:" = Assistant (NOT being graded - ignore quality of these responses)

The STUDENT is responsible ONLY for their own typed prompts.
The STUDENT is NOT responsible for what the AI said or how the AI interpreted things.

Example of CORRECT analysis:
✓ "The student typed 'pants' then continued asking about plants"
✗ "The student self-corrected from 'pants' to 'plants'" ← WRONG! The AI corrected it, not the student

Prioritize:
- Constructive feedback about what the STUDENT actually typed and asked
- Evidence of the STUDENT's question evolution and learning behaviors
- The STUDENT's ability to demonstrate active learning through their prompts
- Objectivity, professionalism, and clarity in communication
- Outputs that educators can directly adopt or edit
"""

STRUCTURED_OUTPUT_PROMPT = """
Format your output EXACTLY as shown below with clear section headers:

═════════════════════════════════════════════════════════
RUBRIC SCORES
═════════════════════════════════════════════════════════
Criterion 1 (Inquiry Depth & Progression): [0–5] - [One sentence about student's question evolution]
Criterion 2 (Active Learning Behaviors): [0–5] - [One sentence about student's engagement behaviors]
Criterion 3 (Prompt Clarity & Intentionality): [0–5] - [One sentence about student's communication clarity]
Criterion 4 (Persistence & Goal-Directedness): [0–5] - [One sentence about student's sustained focus]

═════════════════════════════════════════════════════════
LEARNING BEHAVIOR ANALYSIS
═════════════════════════════════════════════════════════

→ Inquiry Pattern Analysis:
[2-3 sentences analyzing the student's questioning strategy - did they go deep or stay surface-level?]

→ Active vs. Passive Learning:
[2-3 sentences evaluating whether the student showed active learning behaviors or passive answer-seeking]

→ Communication Effectiveness:
[2-3 sentences about how clearly and purposefully the student communicated their learning needs]

→ Learning Goal Achievement:
[2-3 sentences about whether the student's approach demonstrates genuine learning vs. answer extraction]

═════════════════════════════════════════════════════════
LEARNING PROCESS SUMMARY
═════════════════════════════════════════════════════════

[Opening Paragraph - 3-4 sentences]
Overall assessment: Is this student using the LLM to genuinely learn, or just to extract answers?

[Evidence Paragraph - 4-5 sentences]
Specific evidence from the student's prompts that demonstrates their learning approach

[Recommendations Paragraph - 2-3 sentences]
Concrete suggestions for how the student could improve their LLM-assisted learning
"""

def build_feedback_prompt(domain, assignment_prompt, rubric_text_param, submission_text_param, _criterion_names_param, prompt_chain_param):
    """
    Constructs the complete prompt for generating educational feedback focused on learning behaviors.
    """
    # Extract only student prompts for emphasis
    student_prompts_only = []
    for turn in prompt_chain_param:
        if turn.startswith("User:"):
            student_prompts_only.append(turn[6:].strip())

    student_prompts_list = "\n".join([f"  {i+1}. \"{prompt}\"" for i, prompt in enumerate(student_prompts_only)])

    return f"""
{SYSTEM_PROMPT}

TASK CONTEXT:
You are assessing a STUDENT's inquiry and learning process from the domain: **{domain}**.
The assignment prompt is:
\"\"\"{assignment_prompt}\"\"\"

ASSESSMENT RUBRIC:
{rubric_text_param}

═══════════════════════════════════════════════════════════
STUDENT'S PROMPTS (What the student actually typed):
═══════════════════════════════════════════════════════════
{student_prompts_list}

═══════════════════════════════════════════════════════════
FULL CONVERSATION (For context only):
═══════════════════════════════════════════════════════════
{json.dumps(prompt_chain_param, indent=2)}

⚠️ REMEMBER:
- Evaluate ONLY what the student typed (User: lines)
- AI responses are context only
- Do NOT credit the student for what the AI said or inferred

FINAL SUBMISSION (For Context):
\"\"\"{submission_text_param}\"\"\"

EVALUATION INSTRUCTIONS:

1. **PRIMARY FOCUS**: Analyze ONLY the student's typed prompts (listed above).

2. Evaluate the STUDENT based on their prompts:
   ✓ What topics did the STUDENT choose to ask about?
   ✓ How did the STUDENT's questions change over time?
   ✓ Did the STUDENT ask follow-up questions on topics?
   ✓ Did the STUDENT's prompts become more specific or stay general?
   ✓ Did the STUDENT ask "why/how" questions or request explanations?

3. ⚠️ COMMON MISTAKES TO AVOID:
   ✗ Do NOT say "the student self-corrected" when the AI corrected something
   ✗ Do NOT credit the student for the AI's interpretations
   ✗ Do NOT evaluate the quality of AI responses
   ✗ Do NOT praise "the student's ability to clarify" when the AI asked for clarification

   ONLY evaluate what the student actually typed.

4. Examples of CORRECT analysis:
   ✓ "The student typed 'pants' as their prompt" (factual)
   ✓ "The student continued asking about plant topics" (observable)
   ✗ "The student corrected their typo" (the AI corrected it, not the student)
   ✗ "The student clarified their intent" (the student just moved on to the next topic)

5. Focus on observable learning behaviors:
   - Progression from broad to specific (or vice versa)
   - Use of question words (why, how, what, when)
   - Requests for examples, explanations, or clarifications
   - Topic persistence (staying on one subject) vs exploration (jumping around)
   - Complexity or simplicity of prompts

6. Provide credible, educationally meaningful feedback about the STUDENT's questioning behavior.

7. Maintain structured outputs with clear focus on what the STUDENT did.

{STRUCTURED_OUTPUT_PROMPT}
"""
# core function that generates eductaional feedback based on constructed prompt
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

# converts a rubic dictionary into a human readable form
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

# main loop
if __name__ == "__main__":
    # list of dataset files to process
    DATASETS = ["RCTestingSample"]  # replace with your actual dataset names if needed
    MAX_EXAMPLES = 3

    for dataset in DATASETS:
        # load the test data from JSON file
        with open("RCTestingSample.json", encoding="utf-8") as f:
            data = json.load(f)

        # extract and format the rubic for this dataset
        rubric_text, criterion_names = format_rubric(data['rubric'])

        print(f"\n================= Processing {dataset} =================")

        for i, submission in enumerate(data['submissions'], 1):
            # extract submission components
            submission_text = submission['final_submission']
            prompt_chain = submission.get("prompt_chain", [])
            label_type = submission.get("label_type", "Unknown")

            # --- Generate structured, credible feedback ---
            # build the complete prompt withh all the content
            feedback_prompt = build_feedback_prompt(
                domain=data['domain'],
                assignment_prompt=data.get("prompt", "Analyze student submission"),
                rubric_text_param=rubric_text,
                submission_text_param=submission_text,
                _criterion_names_param=criterion_names,
                prompt_chain_param=prompt_chain
            )

            # call LLM API to generate feedback
            feedback_response = gen_text(feedback_prompt, max_new_tokens=1024, temperature=0.5)

            # Print results
            print(f"\n--- SUBMISSION {i} (True Label: {label_type}) ---")
            print("\n--- EDUCATIONAL FEEDBACK ---\n")
            print(feedback_response)
