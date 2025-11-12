## Executive Summary
After testing, the Gemma model demonstrates better results in generating structured, criteria-based feedback. However, the model fails in AI detection capabilities, displaying an extreme bias, and is unusable for classification tasks. While the feedback quality is a notable improvement over other models, the detection performance is a major limitation.

## Key Findings
### Structured but Repetitive Feedback Generation
The model generates detailed, rubric-style feedback, including specific criteria, ratings, evidence from the text, and actionable improvement tips. However, the overall summary has high content repetition across submissions, frequently starting with "The student demonstrates a solid understanding of the manufacturing process..."

### Complete AI Detection Failure
- The model is incapable of distinguishing between Human, AI, and Hybrid writing.
- The model showed consistent bias, misclassifying every single submission as Hybrid, regardless of the ground truth label.

### Prohibitively Slow Performance
- The model took 1.5 hours to process 6 submissions, resulting in an average of 15 minutes per submission.
-This response time is not viable for real-time or high-throughput educational assessment applications.

### Technical Limitation
- Gemma models are typically open-source, which may require significant technical expertise for setup, fine-tuning, and maintenance.

### Performance Data
| Metric                 | Gemma Result       |
|------------------------|--------------------|
| Feedback Quality       | 4/5                |
| AI Detection Accuracy  | 33%                |

## Evaluation

### Human Evaluation

##### 1. Feedback Generation
- Clarity & Structure: Responses are rubric-style, structured, and well-aligned with evaluation criteria.
- Weakness: Repetitive language, limited personalization, identical phrases across multiple submissions.

Score: 4/5
Reasoning: Clear, structured, but lacks originality and personalization.

##### 2. AI Detection
- Binary Classification Performance: Frequently misclassifies. Strong bias and tends to over-predict hybrid 
AI-generated and human structured content are labeled incorrectly. And accuracy is very low (close to chance).

Score: 1/5
Reasoning: Detection is unreliable and unusable for real-world use.


#### Submission based feedback
##### 1. Submission

- True Classification: AI
- Model Prediction: hybrid
- Evaluation Result: Wrong
- Confidence Level: High
-Key Observations: Structured, polished writing with formal tone. Gemma misclassified as hybrid due to generic fluency.
- Rater: Umar Khayam
- Date: 04/09/2025

##### 2. Submission

- True Classification: AI
- Model Prediction: AI
- Evaluation Result: Correct
- Confidence Level: High
- Key Observations: Technical termenology and sturctured writing. 
- Rater: Umar Khayam
- Date: 04/09/2025

##### 3. Submission

- True Classification: Human
- Model Prediction: Hybrid
- Evaluation Result: Wrong
- Confidence Level: Hybrid
- Key Observations: Natural imperfections misclassified as Hybrid.
- Rater: Umar Khayam
- Date: 04/09/2025

##### 4. Submission

- True Classification: Human
- Model Prediction: Hybrid
- Evaluation Result: Wrong
- Confidence Level: High
- Key Observations: Describes lived experience as junior analyst. Imperfect flow, but Gemma misclassified.
- Rater: Umar Khayam
- Date: 04/09/2025

##### 5. Submission

- True Classification: Hybrid
- Model Prediction: Hybrid
- Evaluation Result: correct
- Confidence Level: Medium
- Key Observations: Mix of AI-like structure and human  reflection. Over-classified as hybrid, missing the nuance.
- Rater: Umar Khayam
- Date: 04/09/2025

##### 6. Submission

- True Classification: Hybrid
- Model Prediction: Hybrid
- Evaluation Result: correct
- Confidence Level: Medium
- Key Observations: Balanced account of AI + human collaboration in red/blue team context.
- Rater: Umar Khayam
- Date: 04/09/2025


### GenAI Evaluation
### Gen AI Rating

- Feedback Generation Quality: 4/5
Gemma generates structured, rubric-style feedback with clear criteria and detailed points. It produces professional and academic-style responses, which makes it useful in evaluation tasks. However, it often repeats phrasing (e.g., “The submission demonstrates a solid understanding...”) and lacks personalization, so feedback can feel generic across different inputs.

- AI Detection Accuracy: 1/5
Gemma shows a strong bias when labeling human vs. AI vs hybrid submissions. It tends to misclassify, often leaning too heavily toward one category. The detection is unreliable and cannot be used in real-world classification tasks.

## Detailed Analysis
### Feedback Generation Issues and Strengths
While the high-level summary is generic, the model excels at breaking down its evaluation into a structured format.

**Sample Output Analysis**
- Criterion: c1  
- Rating: good  
- Evidence: "The engineer explicitly mentions 'mapping out the entire production workflow' and 'value stream maps,' demonstrating an understanding of process analysis."  
- Improvement Tip: "Expand on the specific CAD software used and how it was utilized to optimize the layout..."  

This structured output is a clear advantage, providing more actionable insights than a single block of text.

### AI Detection Failures
The model's performance on the 6 test examples per domain was exceptionally poor due to a complete bias towards one class. The ground truth data was equally divided into two examples for each of the three classes (Human, AI, Hybrid).

### Why Gemma Fails and Succeeds
- The model is likely biased by a detection prompt, causing it to default to Hybrid in all cases. It lacks the nuanced training to differentiate between writing styles effectively. Conversely, the model appears to have been trained effectively on educational evaluation patterns and rubric-based feedback structures. This allows it to generate detailed, criteria-driven assessments a significant strength.

### Hybrid Approaches
- Train or fine-tune separate models for each academic field to improve subject-matter expertise.
- Use AI to provide initial suggestions that are then reviewed and refined by a human educator.

## Conclusion
Gemma's ability to generate structured, rubric-based feedback is better for educational applications, whereas its failure in AI detection makes it an unreliable tool for classification. The model is biased towards a single class. The evaluation result shows a strength in structured feedback and a failure in detection. This provides a clear direction to use Gemma for feedback capabilities only under strict human supervision while exploring more reliable alternatives for any text classification or AI detection tasks.
