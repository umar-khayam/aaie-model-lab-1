"""
app/services/feedback_generator.py - LLM-based feedback quality evaluation
"""

import os
import logging
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from ..core.config import OPENAI_API_KEY, DEFAULT_MODEL

logger = logging.getLogger(__name__)

META_RUBRIC = """
Evaluate the QUALITY and EFFECTIVENESS of educator-style feedback using these criteria:

1. **Accuracy**: Is the feedback factually correct based on criterion scores and student work?
2. **Specificity**: Does the feedback reference specific examples and behaviors?
3. **Constructiveness**: Does it provide actionable suggestions for improvement?
4. **Alignment with Rubric Criteria**: Does feedback align with the evaluation rubric?
5. **Tone and Clarity**: Is the feedback clear, respectful, and professionally written?

Score each dimension from 0–10 with detailed justification.
Overall Score: Average of the five dimensions.
"""


class FeedbackQualityEvaluator:
    """Evaluates the quality and effectiveness of educator feedback using LLM-based metrics."""

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the evaluator with OpenAI API credentials.
        
        Args:
            model: LLM model to use for evaluation (default: gpt-4o)
        """
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        self.model = model
        self.evaluator = GEval(
            name="Educator Feedback Quality",
            criteria=META_RUBRIC,
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.CONTEXT,
            ],
            model=model,
        )
        logger.info(f"FeedbackQualityEvaluator initialized with model: {model}")

    def evaluate(self, entries: list[dict]) -> list[dict]:
        """
        Evaluate a batch of feedback entries for quality.
        
        Args:
            entries: List of feedback entry dictionaries
            
        Returns:
            List of evaluation results with scores and reasoning
        """
        results = []

        for entry in entries:
            try:
                logger.info(f"Evaluating feedback entry {entry.get('index', 'unknown')}")
                
                # Prepare context from criterion data
                scores_str = "\n".join(
                    [f"  - {k}: {v}/10" for k, v in entry["criterion_scores"].items()]
                )
                
                feedback_str = "\n".join(
                    [f"  - {k}: {v}" for k, v in entry["criterion_feedback"].items()]
                )
                
                input_context = (
                    "CRITERION SCORES:\n"
                    f"{scores_str}\n\n"
                    "CRITERION FEEDBACK:\n"
                    f"{feedback_str}"
                )

                # Create test case with the feedback as the output to evaluate
                test_case = LLMTestCase(
                    input=input_context,
                    actual_output=entry["feedback"],
                    context=["Educator rubric-aligned feedback evaluation"],
                )

                # Measure the feedback quality
                self.evaluator.measure(test_case)

                # Extract results
                result = {
                    "index": entry["index"],
                    "feedback_quality_score": round(self.evaluator.score, 2),
                    "reasoning": self.evaluator.reason,
                    "evaluation_steps": self.evaluator.evaluation_steps,
                }
                
                results.append(result)
                logger.info(f"Entry {entry['index']} evaluated with score: {self.evaluator.score}")

            except Exception as e:
                logger.error(f"Error evaluating entry {entry.get('index', 'unknown')}: {str(e)}")
                results.append({
                    "index": entry.get("index", -1),
                    "feedback_quality_score": 0,
                    "reasoning": f"Evaluation failed: {str(e)}",
                    "evaluation_steps": None,
                })

        return results

    @staticmethod
    def summary(results: list[dict]) -> dict:
        """
        Generate summary statistics from evaluation results.
        
        Args:
            results: List of evaluation result dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        scores = [r["feedback_quality_score"] for r in results if r["feedback_quality_score"] > 0]

        summary = {
            "total_evaluations": len(results),
            "successful_evaluations": len(scores),
            "failed_evaluations": len(results) - len(scores),
            "mean_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "min_score": round(min(scores), 2) if scores else 0,
            "max_score": round(max(scores), 2) if scores else 0,
            "scores": [round(s, 2) for s in scores],
        }

        logger.info(f"Evaluation summary - Mean: {summary['mean_score']}, Total: {len(results)}")
        return summary  