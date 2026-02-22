import json
import os
import pandas as pd
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# Meta-rubric for evaluating LLM-generated feedback
META_RUBRIC = """
You must evaluate the **quality** of the feedback produced by an LLM.

Evaluate the feedback only using the following meta-rubric:

### META-RUBRIC

1. **Accuracy**
   Does the feedback correctly reflect the student's submission?

2. **Specificity**
   Is the feedback concrete, detailed, and supported with examples rather than vague advice?

3. **Constructiveness**
   Does the feedback guide the student on how to improve?

4. **Alignment with assignment rubric**
   Does the feedback clearly reference (and stay aligned with) the criteria used to judge the work?

5. **Tone and clarity**
   Is the feedback easy to understand, supportive, and professionally written?

### SCORING INSTRUCTIONS
For each dimension, give a score from **0 to 10** and provide a justification.
Then provide an overall score and a summary.
"""


class EvaluateFeedbackQuality:
    """
    Evaluation class for assessing LLM-generated feedback quality using LLM-as-judge approach.
    
    This class uses the G-Eval metric to evaluate feedback based on a meta-rubric that
    assesses accuracy, specificity, constructiveness, alignment, and tone/clarity.
    """
    
    def __init__(self, rubric_file=None, feedback_file=None, api_key=None, 
                 model="gpt-4o", meta_rubric=None):
        """
        Initialize the feedback quality evaluator.
        
        Args:
            rubric_file (str): Path to JSON file containing rubric and submission data
            feedback_file (str): Path to JSON file containing LLM-generated feedback
            api_key (str): OpenAI API key for the judge model
            model (str): Model to use for evaluation (default: gpt-4o)
            meta_rubric (str): Custom meta-rubric for evaluation (optional)
        """
        self.rubric_file = rubric_file
        self.feedback_file = feedback_file
        self.model = model
        self.meta_rubric = meta_rubric if meta_rubric else META_RUBRIC
        self.results = []
        
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        elif "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key must be provided or set in environment")
        
        # Initialize G-Eval metric
        self.meta_evaluator = GEval(
            name="Feedback Quality",
            criteria=self.meta_rubric,
            evaluation_params=[
                LLMTestCaseParams.INPUT,          # Student submission
                LLMTestCaseParams.ACTUAL_OUTPUT,  # LLM-generated feedback
                LLMTestCaseParams.CONTEXT         # Original rubric
            ],
            model=self.model
        )
    
    def load_data(self):
        """
        Load rubric and feedback data from JSON files.
        
        Returns:
            tuple: (rubric_data, feedback_data)
        """
        if not self.rubric_file or not self.feedback_file:
            raise ValueError("Both rubric_file and feedback_file must be provided")
        
        with open(self.rubric_file, "r", encoding="utf-8") as f:
            rubric_data = json.load(f)
        
        with open(self.feedback_file, "r", encoding="utf-8") as f:
            feedback_data = json.load(f)
        
        return rubric_data, feedback_data
    
    def llm_based_evaluation(self):
        """
        Evaluate LLM-generated feedback quality using LLM-as-judge approach.
        
        This function:
        1. Loads rubric and feedback data from JSON files
        2. Extracts student submissions, rubric criteria, and LLM feedback
        3. Uses G-Eval to assess feedback quality based on the meta-rubric
        4. Optionally prints and saves detailed evaluation results
        
        
        Returns:
            list: List of evaluation result dictionaries containing:
                - submission_id: Identifier for the submission
                - feedback_quality_score: Overall score (0-1)
                - reasoning: Explanation of the score
                - evaluation_steps: Steps used in evaluation
                - student_submission: Original submission text
                - llm_feedback: Feedback being evaluated
                - rubric_criteria: Criteria used for grading
        
        Workflow:
            - Loads data from provided JSON files
            - Iterates through each submission-feedback pair
            - Creates LLMTestCase with submission, feedback, and rubric
            - Runs G-Eval to score feedback quality
            - Collects and stores evaluation results
            - Optionally prints results and saves to file
        """
        # Load data
        rubric_data, feedback_data = self.load_data()
        
        # Extract rubric criteria
        rubric_criteria = rubric_data.get("rubric", {}).get("criteria", [])
        submissions = rubric_data.get("submissions", [])
        
        # Ensure feedback_data is a list
        if isinstance(feedback_data, dict):
            feedback_data = [feedback_data]
        
        # Iterate through submissions and their feedback
        for idx, (submission_entry, feedback_entry) in enumerate(zip(submissions, feedback_data)):
            submission_text = submission_entry.get("final_submission", "")
            llm_feedback = feedback_entry.get("feedback", "")
            
            if not submission_text or not llm_feedback:
                print(f"Warning: Missing data for submission {idx}. Skipping...")
                continue
            
            # Create test case
            test_case = LLMTestCase(
                input=submission_text,
                actual_output=llm_feedback,
                context=[str(rubric_criteria)]
            )
            
            # Run evaluation
            self.meta_evaluator.measure(test_case)
            
            # Store results
            result = {
                "submission_id": idx,
                "feedback_quality_score": self.meta_evaluator.score,
                "reasoning": self.meta_evaluator.reason,
                "evaluation_steps": self.meta_evaluator.evaluation_steps,
                "student_submission": submission_text[:200] + "...",  # Truncate for readability
                "llm_feedback": llm_feedback,
                "rubric_criteria": rubric_criteria
            }
            
            self.results.append(result)
            
            # Print results
            print(f"G-Eval Score: {self.meta_evaluator.score:.2f}")
            print("Reason")
            print(self.meta_evaluator.reason)
        
        
        return self.results
    
    def get_summary_statistics(self):
        """
        Calculate summary statistics across all evaluations.
        
        Returns:
            dict: Summary statistics including mean, min, max scores
        """
        if not self.results:
            print("No results available. Run llm_based_evaluation first.")
            return None
        
        scores = [r["feedback_quality_score"] for r in self.results]
        
        summary = {
            "total_evaluations": len(scores),
            "mean_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "scores": scores
        }
        
        return summary
    
    def export_to_dataframe(self):
        """
        Export results to a pandas DataFrame for further analysis.
        
        Returns:
            pd.DataFrame: Results as a DataFrame
        """
        if not self.results:
            print("No results available. Run llm_based_evaluation first.")
            return None
        
        df_data = []
        for result in self.results:
            df_data.append({
                "submission_id": result["submission_id"],
                "feedback_quality_score": result["feedback_quality_score"],
                "reasoning": result["reasoning"]
            })
        
        return pd.DataFrame(df_data)


# Example usage
if __name__ == "__main__":
    # Load Environment Variables from root .env_variables
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to find .env_variables (Feedback Evaluation -> Evaluation -> Root)
        env_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), ".env_variables")
        
        if os.path.exists(env_path):
            print(f"Loading environment variables from {env_path}")
            with open(env_path, "r", encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        try:
                            key, value = line.strip().split("=", 1)
                            os.environ[key] = value
                        except ValueError:
                            continue
    except Exception as e:
        print(f"Warning: Could not load .env_variables: {e}")

    # Initialize evaluator
    # Use paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    evaluator = EvaluateFeedbackQuality(
        rubric_file=os.path.join(script_dir, "rub_it_0002.json"),
        feedback_file=os.path.join(script_dir, "FG_Feedback_Results_with_Scores.json"),
        api_key=os.getenv("OPENAI_API_KEY"),  # or provide directly
        model="gpt-4o"
    )
    
    # Run evaluation
    results = evaluator.llm_based_evaluation()
    
    # Get summary statistics
    summary = evaluator.get_summary_statistics()
    if summary:
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        print(f"Total Evaluations: {summary['total_evaluations']}")
        print(f"Mean Score: {summary['mean_score']:.4f}")
        print(f"Min Score: {summary['min_score']:.4f}")
        print(f"Max Score: {summary['max_score']:.4f}")
    
    # Export to DataFrame
    df = evaluator.export_to_dataframe()
    if df is not None:
        print("\nResults DataFrame:")
        print(df)