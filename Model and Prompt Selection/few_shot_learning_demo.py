import openai
import os
import json

#OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

#student input
prompt_text = "Write about why reducing car use in cities, like in Vauban, Germany, can be a good idea. What are the benefits, and do you think more places should do the same?"

student_submission = (
    "Reducing car use can help improve air quality and reduce accidents. "
    "Vauban, Germany, is a good example where car-free living improves quality of life."
)

chat_log = (
    "Prompt 1: Write about why reducing car use in cities, like in Vauban, Germany, can be a good idea...\n"
    "AI Response: Reducing car use can significantly lower pollution levels, improve public spaces, and reduce noise pollution...\n"
    "Prompt 2: Add more on global examples.\n"
    "AI Response: Cities like Amsterdam and Copenhagen have already implemented bike-friendly policies..."
)

#Few-shot prompt
few_shot_prompt = f"""
You are an academic evaluator. Given a student submission and GenAI chat log, return:

- Structure, Clarity, Relevance scores (1–3 scale)
- AI Content Score (0–100%) → then label it:
  - 0–25 → Human-Written
  - 26–50 → Partial Human + AI
  - 51–100 → Likely AI-Generated
- Prompt Similarity (0–100%) → if ≥40%, mark as "Flagged – Resubmission Required"
- Highlight AI-generated text using <mark>...</mark>
- Provide a 1-sentence feedback message
- Return valid JSON

Example:

Prompt: Discuss how social media affects teenage mental health.

Student Submission:
"Social media connects teenagers but also causes stress, anxiety, and comparison. Using it moderately can improve mental health."

Chat Log:
Prompt: Discuss how social media affects teenage mental health.
AI: Social media helps teens connect but is linked to anxiety, depression, and low self-esteem.

Evaluation:
{{
  "submission_id": "P002-S001",
  "rubric_scores": {{
    "structure": 2,
    "clarity": 2,
    "relevance": 3
  }},
  "ai_content_score": 60,
  "ai_label": "Likely AI-Generated",
  "prompt_similarity": 45,
  "similarity_label": "Flagged – Resubmission Required",
  "highlighted_submission": "Social media connects teenagers but also <mark>causes stress, anxiety, and comparison</mark>...",
  "llm_feedback": "Try to include more personal examples or perspectives."
}}

Now evaluate this:

Prompt: {prompt_text}

Student Submission:
{student_submission}

Chat Log:
{chat_log}

Return only the JSON object.
"""

# Call OpenAI GPT-4 API 
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": few_shot_prompt}],
    temperature=0.3,
    max_tokens=1000
)

#Output
result_text = response['choices'][0]['message']['content']

try:
    result_json = json.loads(result_text)
    print("Evaluation Result:")
    print(json.dumps(result_json, indent=2))
except json.JSONDecodeError:
    print("JSON could not be parsed. Raw output:")
    print(result_text)


#Sammple output
{
  "submission_id": "P001-S01",
  "rubric_scores": {
    "structure": 3,
    "clarity": 2,
    "relevance": 3
  },
  "ai_content_score": 42,
  "ai_label": "Partial Human + AI",
  "prompt_similarity": 38,
  "similarity_label": "Acceptable",
  "highlighted_submission": "Reducing car use can <mark>help improve air quality and reduce accidents</mark>...",
  "llm_feedback": "Include more personal insights or additional global examples."
}
