"""
Explainer module for LLM evaluation results.

This module loads the aggregated metrics CSV and generates a detailed,
qualitative report explaining what the numbers actually mean in the context
of educational feedback quality, including statistical validity checks.
"""

import pandas as pd
import logging
import os
import math

logger = logging.getLogger(__name__)

def analyze_sample_size(n: int) -> str:
    """
    Analyzes the statistical validity of the sample size using Cochran's formula
    approximation for large populations with p=0.5 and Margin of Error=0.05.
    """
    # Thresholds for standard infinite population approximation (5% margin of error)
    # 95% CI: Z=1.96 -> (1.96^2 * 0.5 * 0.5) / 0.05^2 ≈ 385
    # 99% CI: Z=2.576 -> (2.576^2 * 0.5 * 0.5) / 0.05^2 ≈ 664
    needed_95 = 385
    needed_99 = 664
    
    msg = f"  • Current Sample Size: {n}\n"
    
    if n < 30:
        msg += "  • Status: CRITICALLY LOW. Results are anecdotal and statistically insignificant."
    elif n < 100:
        msg += "  • Status: LOW. Results may be indicative but lack statistical power."
    elif n < needed_95:
        msg += "  • Status: MODERATE. Acceptable for development, but implies a margin of error >5%."
    else:
        msg += "  • Status: ROBUST. Sample size is sufficient for reliable conclusions."
        
    msg += "\n\n  REQUIREMENTS for 5% Margin of Error (Conservative p=0.5):"
    msg += f"\n  - For 95% Confidence: Need ~{needed_95} samples "
    msg += f"({'+' if n < needed_95 else ''}{needed_95 - n} more needed)."
    msg += f"\n  - For 99% Confidence: Need ~{needed_99} samples "
    msg += f"({'+' if n < needed_99 else ''}{needed_99 - n} more needed)."
    
    return msg

def interpret_correlation(value: float) -> str:
    """Interprets Pearson/Spearman correlation coefficients."""
    if pd.isna(value): return "Insufficient data."
    val = abs(value)
    if val >= 0.9: return "Very Strong relationship. The model's scoring trends almost perfectly mirror human graders."
    if val >= 0.7: return "Strong relationship. The model captures the general ranking logic of human graders well."
    if val >= 0.5: return "Moderate relationship. The model generally agrees with humans but misses some nuances."
    if val >= 0.3: return "Weak relationship. The model's scoring is only loosely related to human judgment."
    return "Negligible relationship. The model's scoring appears random compared to human grades."

def interpret_kappa(value: float) -> str:
    """Interprets Quadratic Weighted Kappa (agreement)."""
    if pd.isna(value): return "Insufficient data."
    if value >= 0.8: return "Almost Perfect agreement. Highly reliable for automated grading."
    if value >= 0.6: return "Substantial agreement. Reliable enough for low-stakes or assistive grading."
    if value >= 0.4: return "Moderate agreement. The model understands the criteria but disagrees on borderline cases."
    if value >= 0.2: return "Fair agreement. Significant noise in grading consistency."
    return "Poor agreement. No consistent alignment with human standards."

def interpret_mse(value: float) -> str:
    """Interprets Mean Squared Error."""
    if pd.isna(value): return "N/A"
    if value < 0.25: return "Excellent precision. Scores are typically within 0.5 points of the human grade."
    if value < 0.5: return "Good precision. Deviations are usually minor (under 0.7 points)."
    if value < 1.0: return "Acceptable precision. Expect errors of around 1 full rubric point."
    return "Low precision. The model frequently deviates by more than 1 point from the ground truth."

def interpret_judge_score(score: float, metric_name: str) -> str:
    """Interprets LLM-as-a-judge scores (assuming 0-1 scale)."""
    if pd.isna(score): return "Not calculated."
    
    # Context-aware explanations...
    explanations = {
        "relevance": "how well the feedback addresses the specific student essay",
        "coherence": "the logical flow and structure of the feedback",
        "actionability": "whether the student can take specific steps to improve",
        "tone": "if the feedback is supportive and professional",
        "safety": "absence of harmful or biased content",
        "faithfulness": "absence of hallucinations relative to the source text",
        "rubric_alignment": "adherence to the grading criteria"
    }
    
    context = explanations.get(metric_name.lower().replace("judge_", ""), "quality")
    
    if score >= 0.9: return f"Excellent ({score:.2f}). The model consistently excels at {context}."
    if score >= 0.75: return f"Good ({score:.2f}). The feedback is generally strong in {context}, with minor lapses."
    if score >= 0.6: return f"Fair ({score:.2f}). The feedback regarding {context} is acceptable but often generic."
    if score >= 0.4: return f"Weak ({score:.2f}). There are frequent issues with {context}."
    return f"Critical Failure ({score:.2f}). The model fails to maintain {context}."

def generate_explanation_text(metrics_csv_path: str) -> str:
    """
    Generates the explanation report as a string (helper for Meta-Analysis).
    """
    if not os.path.exists(metrics_csv_path):
        return "Error: Metrics summary file not found."

    try:
        df = pd.read_csv(metrics_csv_path)
        if df.empty:
            return "Error: Metrics file is empty."
        
        data = df.iloc[0].to_dict()
        lines = []
        
        lines.append("\n" + "="*70)
        lines.append("             AUTOMATED PIPELINE EVALUATION REPORT")
        lines.append("="*70 + "\n")
        
        # Statistical validity check
        lines.append("--- 0. STATISTICAL VALIDITY CHECK ---")
        sample_count = int(data.get("sample_count", 0))
        lines.append(analyze_sample_size(sample_count))
        lines.append("\n")

        # Scoring Reliability
        lines.append("--- 1. SCORING RELIABILITY (Quantitative) ---")
        lines.append("How well the model's numerical grades align with human experts.\n")
        
        for category in ['Content', 'Organization', 'Language', 'Total']:
            p_key = f"{category.lower()}_pearson"
            k_key = f"{category.lower()}_kappa"
            m_key = f"{category.lower()}_mse"
            
            if p_key in data:
                lines.append(f"[{category.upper()}]")
                lines.append(f"  • Correlation (r={data.get(p_key, 0):.2f}): {interpret_correlation(data.get(p_key))}")
                lines.append(f"  • Agreement   (k={data.get(k_key, 0):.2f}): {interpret_kappa(data.get(k_key))}")
                lines.append(f"  • Error Rate  (MSE={data.get(m_key, 0):.2f}): {interpret_mse(data.get(m_key))}")
                lines.append("")

        # Feedback text quality
        lines.append("--- 2. FEEDBACK TEXT QUALITY (Reference-Based) ---")
        if 'avg_bert_score' in data:
            bs = data['avg_bert_score']
            bs_interp = "High similarity." if bs > 0.85 else "Moderate similarity."
            lines.append(f"  • BERTScore (F1={bs:.3f}): {bs_interp}")
            lines.append("    (Measures semantic overlap with expert 'Gold' feedback.)\n")
            
        if 'citation_recall' in data:
            cr = data['citation_recall']
            lines.append(f"  • Citation Recall ({cr:.3f}): {'High' if cr > 0.3 else 'Low'} grounding.")
            lines.append("    (Measures how often the feedback explicitly quotes the essay.)\n")

        # LLM as a judge insights
        lines.append("--- 3. LLM-AS-A-JUDGE INSIGHTS (Qualitative) ---")
        judge_keys = [k for k in data.keys() if k.startswith("judge_") and not k.endswith("_reason")]
        
        if not judge_keys:
            lines.append("  No LLM-Judge metrics found.")
        else:
            for key in sorted(judge_keys):
                name = key.replace("judge_", "").replace("_", " ").title()
                lines.append(f"  • {name}: {interpret_judge_score(data[key], key)}")

        lines.append("\n" + "="*70 + "\n")
        
        return "\n".join(lines)

    except Exception as e:
        return f"Error creating explanation text: {e}"

def explain_results(metrics_csv_path: str):
    """Prints the explanation report to stdout."""
    print(generate_explanation_text(metrics_csv_path))

__all__ = ["explain_results"]