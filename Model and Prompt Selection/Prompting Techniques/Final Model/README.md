# 1. Base prompt (utlis.prompt.py)
This file contains utility functions for building prompts and formatting rubrics in AI detection and feedback generation tasks.

The main components are:

1. format_rubric(rubric):
   - Formats a rubric dictionary into a readable multi-line string with all criteria and their performance descriptors.  
   - Useful for inserting rubric details into prompts or reports.

2. create_few_shot_block(subs, max_examples=3):
   - Selects a small number of representative student submissions and formats them into a text block for few-shot prompting.  
   - Ensures one example per label (Human, AI, Hybrid) if available, and fills remaining slots if needed.  
   - Helps the AI see examples before making predictions.

3. build_detection_prompt(example, submission):
   - Builds a structured prompt for classifying submissions as Human, AI, or Hybrid.  
   - Includes system role, step-by-step reasoning, and JSON output format with label and reasoning.  
   - Takes both few-shot examples and the actual student submission.

4. build_feedback_prompt(rubric, submission):
   - Builds a structured prompt for rubric-aligned feedback generation.  
   - Guides AI to provide feedback that is constructive, professional, and tied to rubric descriptors.  
   - Output includes an overall summary and criterion-level feedback (rating, evidence, suggestions).

# 2. Model Pipeline (model.py)
`generated_response_gemini(message)`
Generates a response from Google’s **Gemini API** using the provided structured prompt.
- Input:  `message`: a dictionary with keys `"system"` (system instructions) and `"user"` (user query).  
- **Process**:  
  - Initializes a Gemini chat model (`gemini-1.5-flash`) with the system instruction.  
  - Sends the user message to the chat.  
- **Output**:  
  - Returns the model’s generated text response.  


` process_single_submission(args)`
Handles the end-to-end AI detection and feedback process for a single student submission.

- **Inputs**:  
  - `args['domain']`: the subject/domain of the task (e.g., `"engineering"`).  
  - `args['submission']`: the student’s text submission.  

- **Steps**:  
  1. Loads the training data file for the domain (rubric + sample submissions).  
  2. Formats the rubric with `format_rubric`.  
  3. Selects a few representative examples with `create_few_shot_block`.  
  4. Builds two prompts:  
     - **AI detection prompt** (`build_detection_prompt`).  
     - **Feedback generation prompt** (`build_feedback_prompt`).  
  5. Runs both prompts through Gemini:  
     - AI detection result (`ai_pred`).  
     - Feedback text (`feedback_result`).  
  6. Returns results as a JSON object containing:  
     - `ai_detection`: predicted label + reasoning.  
     - `feedback_ai`: generated rubric-aligned feedback.  

# 2. EvaluateModel (evaluate_model_genai.py): 

The `EvaluateModel` class provides a flexible pipeline for evaluating both classification models (e.g., AI detection) and generative models.   It supports standard metrics, visualization tools, and integration with Hugging Face models for model-based evaluation.

## 🔧 Features

- **Classification Evaluation**
  - Automatically encodes string labels into integers.
  - Computes accuracy, precision, recall, and F1-score.
  - Generates confusion matrix and classification reports.
  
- **Generative Evaluation**
  - Supports BLEU, ROUGE, and BERTScore metrics.
  - Handles multiple reference texts for evaluation.
  
- **Model-Based Evaluation**
  - Generates structured outputs using predefined prompts.
  - Compatible with Hugging Face transformer models.
  - Allows visualization of model attention weights.
  
- **Visualization**
  - Attention heatmaps for text segments.
  - Confusion matrix with class labels.


## Dataset Structures

### a. Classification Models

```python
dataset = {
    "text": ["Some input text", "Another input text", ...],
    "labels": ["AI", "Human", "Neutral", ...],        # Ground-truth labels
    "predictions": ["AI", "AI", "Human", ...]         # Model predictions
}
### b. Generative Models (e.g., Feedback Generation)
dataset = {
    "text": [
        ["The cat sat on the mat.", "A cat is sitting on a mat."],  # Multiple references
        ["Hello, how are you?"]
    ],
    "generated_texts": [
        "The cat is sitting on the mat.",
        "Hi, how do you do?"
    ]
}

## Usage Examples
a. Classification Evaluation
```python
evaluator = EvaluateModel(dataset=dataset, model_type="ai_detection")
evaluator.evaluate_classification_model(average='macro', print_result=True)
```
✅ Outputs:
Accuracy, Precision, Recall, F1-score
Classification report
Confusion matrix heatmap

b Generative Evaluation
```python
Always show details
evaluator = EvaluateModel(dataset=dataset, model_type="feedback_generation")
evaluator.evaluate_generative_model(metrics=['bleu', 'rouge', 'bertscore'], print_result=True)
```
✅ Outputs:
BLEU Score
ROUGE-1, ROUGE-2, ROUGE-L
BERTScore Precision, Recall, and F1


## c. Model-Based Evaluation with Hugging Face
```
Always show details
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM

# Login with your Hugging Face token
login(token="your_hf_token")

# Load model & tokenizer
model_id = "mistralai/Mistral-7B-Instruct-v0.2"
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Load dataset (CSV with text, labels, predictions, or criteria)
import pandas as pd
testset = pd.read_csv("test_feedback_generation.csv")

# Evaluate
evaluator = EvaluateModel(model=model, tokenizer=tokenizer, dataset=testset, model_type="feedback_generation", device="automap")
evaluator.model_based_evaluation()
```