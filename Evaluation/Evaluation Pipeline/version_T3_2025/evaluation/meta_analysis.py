"""
Meta-analysis module using a large parameter LLM.

This module loads the final metrics and the preliminary explainer report,
constructs a high-level prompt, and asks the large model to act as a 
Lead Data Scientist to provide a final executive summary and recommendations.
"""

import logging
import os
import re
from typing import Dict, Any
from .model_manager import ModelManager
from .results_explainer import generate_explanation_text

logger = logging.getLogger(__name__)

# Prompt template for the Meta-Analysis
ANALYSIS_PROMPT = """You are a Lead Data Scientist and EdTech Evaluator.
You have been given the performance metrics for an Automated Essay Feedback System.

### DATA SUMMARY
{explanation_report}

### TASK
Please write a full "Final Executive Analysis" based on the data above.
Since you cannot see the generated charts, rely on the metrics provided.

Your report must strictly follow this structure:

# Executive Analysis of LLM-Based Essay Feedback System

## 1. Executive Summary
[Explain the findings and state if you think the model is ready for deployment?]

## 2. Key Strengths
[What does the model do well? Explain why and back it up with data. Explain why this is important.]

## 3. Critical Weaknesses
[Where does it fail? Explain why and back it up with data. Explain the implications of these weaknesses.]

## 4. Recommendation
[Final verdict: Proceed, Assistance Only, or Retrain?]

**CRITICAL INSTRUCTION:** Do NOT output your internal thought process, planning, or reasoning. 
Start your response DIRECTLY with the line: "# Executive Analysis of LLM-Based Essay Feedback System".
"""

def clean_response(text: str) -> str:
    """
    Cleans the model output to remove 'thinking' traces, Chain-of-Thought,
    and special tokens. It looks for the specific headers requested in the prompt.
    """
    if not text:
        return ""

    # Regex to find the start of the report (Case insensitive)
    # Pattern A: The Title
    match_title = re.search(r'(#+\s*Executive Analysis)', text, re.IGNORECASE)
    if match_title:
        return text[match_title.start():].strip()

    # Pattern B: The First Section (Backup)
    match_section = re.search(r'(#+\s*1\.\s*Executive Summary)', text, re.IGNORECASE)
    if match_section:
        return text[match_section.start():].strip()
        
    # Pattern C: Special Token splitting (Fallback)
    if "<|message|>" in text:
        return text.split("<|message|>")[-1].strip()
    if "<|assistant|>" in text:
        return text.split("<|assistant|>")[-1].strip()

    return text.strip()

def perform_meta_analysis(
    manager: ModelManager, 
    config: Dict[str, Any],
    metrics_csv_path: str, 
    output_dir: str
):
    """
    Runs the meta-analysis using the loaded model in `manager`.
    """
    logger.info("Starting Meta-Analysis stage...")
    
    # Get the data context
    explanation_text = generate_explanation_text(metrics_csv_path)
    
    # Construct Prompt
    prompt = ANALYSIS_PROMPT.format(explanation_report=explanation_text)
    
    # Retrieve model settings
    model_conf = config.get("meta_analysis_model", {})
    repo_id = model_conf.get("repo", "unsloth/gpt-oss-20b-GGUF")
    filename = model_conf.get("file", "gpt-oss-20b-Q4_K_M.gguf")

    # Generate Analysis
    logger.info(f"Querying {repo_id} for executive summary...")
    try:
        # We use max_tokens=-1 to allow the model to use the full 8192 context window
        # This prevents the report from cutting off after the "thinking" process.
        response = manager.generate_response(
            prompt=prompt,
            repo_id=repo_id,
            filename=filename, 
            max_tokens=-1, 
            temp=0.3
        )
        
        if not response:
            print("Warning: Model returned empty response.")
            return

        # CLEANING STEP - Remove CoT and unwanted text
        cleaned_response = clean_response(response)
        
        # Ensure header exists
        if "# Executive Analysis" not in cleaned_response:
            final_output = "# Executive Analysis of LLM-Based Essay Feedback System\n\n" + cleaned_response
        else:
            final_output = cleaned_response

        # Save and Print
        output_path = os.path.join(output_dir, "final_executive_analysis.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_output)
            
        print("\n" + "#"*60)
        print("          META-ANALYSIS (By Lead Data Scientist)")
        print("#"*60 + "\n")
        print(final_output)
        print(f"\nSaved full analysis to: {output_path}")

    except Exception as e:
        logger.error(f"Meta-analysis failed: {e}")
        print(f"Meta-analysis failed: {e}")