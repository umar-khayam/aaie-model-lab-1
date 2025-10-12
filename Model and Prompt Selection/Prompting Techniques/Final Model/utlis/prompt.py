
from typing import List, Dict, Any
import json
import pandas as pd
import numpy as np
#Formats a rubric dictionary into a readable multi-line string, including all criteria and their performance descriptors. 
# This is useful for inserting rubric details into prompts or reports.
def format_rubric(rubric):
    formatted_rubric = f"""
    Rubric ID: {rubric['rubric_id']}
    Criteria:
    """
    for rubric_item in rubric['criteria']:
      formatted_rubric += f"""
      Criterion: {rubric_item['criterion_id']}
      Name: {rubric_item['name']}
      Description: {rubric_item['description']}
      Performance Descriptors:  """
      for key, val in rubric_item['performance_descriptors'].items():
        formatted_rubric += f"""
        - {key}: {val}
      """
    return formatted_rubric

#Contributor: Qasim
#Selects a small number of representative student submissions and formats them into a text block for few-shot prompting. 
# This helps the AI see examples before making predictions.
def create_few_shot_block(subs: List[Dict[str, Any]], max_examples: int = 3) -> str:
    """
    Select a few representative examples and return a formatted text block for few-shot prompting.
    """
    labels = ["Human", "AI", "Hybrid"]
    shots = []

    # Pick one example per label first
    for label in labels:
        for s in subs:
            if s.get("label_type", "").strip() == label:
                shots.append(s)
                break

    # Fill remaining slots if needed
    for s in subs:
        if len(shots) >= max_examples:
            break
        if s not in shots:
            shots.append(s)

    # Create the formatted few-shot block
    if shots:
        return "\n\n".join(
            f'Submission: """{s.get("final_submission", "")}"""\nLabel: {s.get("label_type", "Unknown")}'
            for s in shots
        )

    return "/* no examples available */"



def build_detection_prompt(example: str,submission: str):
    """
    Build a structured prompt for classifying submissions as Human, AI, or Hybrid.
    """
    role = f'You are an impartial AI text detector evaluating whether a given text is AI- or human-generated or Hybrid.'
    task = 'Classify the text and provide reasoning for your decision.”'   
    step =  """
    Step 1: Analyze the text’s linguistic patterns and style. 
    Step 2: Compare patterns to typical AI-generated and human-written texts. 
    Step 3: Determine the label (AI-generated or human-written). 
    Step 4: Provide reasoning"""

    system_prompt = f"""
    {role}
    Your task is to {task}
    Following the {step}

    Take the input:
        - 'Submission' which is submission.
    
    {example}
    
    Then output in this exact format (JSON):
        {{
            "label": "AI" or "Human" or "Hybrid",
            "reasoning": ["first reason", "second reason"]
        }}
    
    """

    user_prompt = f'This the submission {submission}. Base on that provided me result'
    return {
        "system": system_prompt,
        "user": user_prompt}

#Constribution: Qsaim in prompting
def build_feedback_prompt(rubric: str, submission: str) -> List[Dict[str, str]]:
    """
    Build a structured prompt for rubric-aligned feedback generation.
    """
    role = f"You are a helpful and respectful educational assessment assistant that provides feedback on submitted work. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Provide assessment feedback and a rating for the assessment based on performce descriptors."
    task = "analyze the student’s response and generate detailed, actionable feedback"
    #Extract the CoT
    step = """
    0. Summarize overall performance in 2-4 sentences of the input submission.
    1. Understand assignment context (domain, goals)  
    2. Map submission to rubric descriptors  
    3. Identify strengths (align with "excellent" or "good")  
    4. Identify weaknesses (gaps, misalignments)  
    5. Select concrete evidence from text  
    6. Suggest actionable, domain-relevant improvements  
    7. Ensure tone is constructive, professional, encouraging  
    """
    system = f"""
    {role} and your task is to {task}.
    
    Following the below step: {step}

    {rubric}
    
    Take the input as a text submission of the task and provide the output as these following:
      1) Overall Summary: 2–4 sentences on strengths and priorities.
      2) Criteria Feedback: For each rubric criterion, include:
          - Criterion
          - Rating (excellent, good, average, needs_improvement, poor)
          - Evidence (1–3 bullet points citing excerpts or behaviors)
    """
    user = f"This is the submission of the student {submission} and provide the output"
    return {
        "system": system,
        "user": user}

