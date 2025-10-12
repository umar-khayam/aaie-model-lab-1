# Human and GenAI Evaluation
## Key Findings
* **High-Quality, Structured Feedback:** The model produces detailed, rubric-style feedback. Each evaluation includes specific criteria, ratings, textual evidence, and actionable improvement tips, making it highly valuable for formative assessment.
* **Repetitive Summary Language:** A clear weakness is the repetitive phrasing in the "Overall Summary" sections. Many evaluations begin with nearly identical sentences, such as "The submission demonstrates a solid understanding of...," which reduces the personalization of the feedback.
* **Unreliable AI Detection:** The model's performance in distinguishing between Human, AI, and Hybrid writing is poor. With an overall accuracy of approximately 37%, it performs only slightly better than random chance.
* **Strong Classification Bias:** The model shows a clear bias against classifying submissions as purely Human. It overwhelmingly favors the Hybrid and AI labels, misclassifying 9 out of 10 human-written pieces. This makes it unusable for reliably identifying authentic student work.
## Performance Data
| Metric                | Gemini Result |
|-----------------------|---------------|
| Feedback Quality      | 4/5           |
| AI Detection Accuracy | 37% (11/30)   |

## Human Evaluation

### Overall Assessment

1.  **Feedback Generation**
    * **Clarity & Structure:** The model's responses are consistently well-structured in a rubric style, aligning directly with the provided evaluation criteria. The feedback is clear, professional, and easy to follow.
    * **Weakness:** There is significant repetition in high-level summary statements (e.g., "The submission demonstrates a solid understanding..."). The feedback, while structured, lacks a unique voice or deep personalization, making it feel generic across multiple, distinct submissions.
    * **Score:** 4/5
    * **Reasoning:** The feedback is exceptionally clear and structured, making it highly useful. However, it lacks the originality and personalized insight needed for a perfect score.

2.  **AI Detection**
    * **Classification Performance:** The model performs poorly in distinguishing between AI, Human, and Hybrid submissions. The overall accuracy is very low (36.7%), which is not much better than random chance. There is a strong bias toward misclassifying Human and Hybrid submissions.\
    * **Score:** 1/5
    * **Reasoning:** The detection capability is unreliable and inconsistent across different domains, making it unusable for genuine academic integrity checks.

### Submission-Based Feedback by Category

#### **Accounting**

* **Submission 1**
    * **True Classification:** AI
    * **Model Prediction:** AI
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** Correctly identified the polished, formalized writing, neutral tone, and lack of subjective depth as hallmarks of AI generation.
* **Submission 2**
    * **True Classification:** AI
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** Misclassified the submission, likely because the high specificity and integration of real-world examples were misinterpreted as human revision or input.
* **Submission 3**
    * **True Classification:** Human
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** Incorrectly flagged, mistaking the student's personal voice ("As a business student...") combined with some polished phrasing as a sign of AI assistance rather than natural writing.
* **Submission 4**
    * **True Classification:** Human
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** Similar to Submission 3, the model was confused by the mix of personal context and structured arguments, leading to a misclassification.
* **Submission 5**
    * **True Classification:** Hybrid
    * **Model Prediction:** AI
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** The model failed to detect any human-like "fingerprints," over-indexing on the formal tone and coherent structure while missing subtle signs of human guidance.
* **Submission 6**
    * **True Classification:** Hybrid
    * **Model Prediction:** AI
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** Misclassified due to the absence of a strong personal voice and the presence of polished, technical phrasing, which the model incorrectly attributed solely to AI.

#### **Teaching**

* **Submission 1**
    * **True Classification:** AI
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** The model was thrown off by the inclusion of specific academic citations, assuming this level of detail required human intervention or validation.
* **Submission 2**
    * **True Classification:** AI
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** The model again misinterpreted the use of research citations and a critique about implementation details as signs of human engagement.
* **Submission 3**
    * **True Classification:** Human
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** Misclassified. The model identified the mix of conversational tone and structured academic points as a hybrid, failing to recognize it as a common human writing style.
* **Submission 4**
    * **True Classification:** Human
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** The submission's use of standard academic terminology combined with a somewhat generic structure was incorrectly flagged as AI-assisted.
* **Submission 5**
    * **True Classification:** Hybrid
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** Correctly identified the blend of formal, AI-like phrasing and structure with the slightly more conversational tone indicative of human editing.
* **Submission 6**
    * **True Classification:** Hybrid
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Correct
    * **Confidence Level:** Medium
    * **Key Observations:** Correctly noted the generic, repetitive phrasing as a sign of AI assistance, while acknowledging the overall coherence likely guided by a human.

#### **Psychology**

* **Submission 1**
    * **True Classification:** AI
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** The polished structure was correctly identified as AI-like, but the model incorrectly assumed the specific examples required human contextualization.
* **Submission 2**
    * **True Classification:** AI
    * **Model Prediction:** AI
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** Correctly identified the formulaic structure, high coherence, and lack of any personal or subjective input as clear indicators of pure AI generation.
* **Submission 3**
    * **True Classification:** Human
    * **Model Prediction:** AI
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** A significant error. The model misinterpreted the student's general and somewhat simplistic writing style as a feature of a generic AI, missing the human conversational tone.
* **Submission 4**
    * **True Classification:** Human
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** The model was again confused by a mix of conversational tone and structured examples, incorrectly labeling it as a hybrid.
* **Submission 5**
    * **True Classification:** Hybrid
    * **Model Prediction:** AI
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** The model over-indexed on the generic phrasing and formulaic structure, failing to perceive any signs of human input and thus misclassifying.
* **Submission 6**
    * **True Classification:** Hybrid
    * **Model Prediction:** AI
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** Another miss due to the model perceiving the concise and formulaic style as purely AI, rather than AI-assisted human writing.

#### **Information Technology**

* **Submission 1**
    * **True Classification:** AI
    * **Model Prediction:** AI
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** Correctly identified the polished but generalized discourse, lack of personal anecdotes, and use of industry jargon as clear signs of AI generation.
* **Submission 2**
    * **True Classification:** AI
    * **Model Prediction:** AI
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** The impersonal, broadly informative content without a unique voice was correctly flagged as AI-generated.
* **Submission 3**
    * **True Classification:** Human
    * **Model Prediction:** N/A (No label provided)
    * **Evaluation Result:** N/A
    * **Confidence Level:** N/A
    * **Key Observations:** A label was not generated for this submission.
* **Submission 4**
    * **True Classification:** Human
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** The model incorrectly interpreted the blend of a personal narrative ("As a junior security analyst...") with polished technical explanations as a sign of AI assistance.
* **Submission 5**
    * **True Classification:** Hybrid
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Correct
    * **Confidence Level:** Medium
    * **Key Observations:** Correctly identified the mix of a clear human narrative with formulaic, AI-like phrasing ("AI brought the speed, but human expertise brought the accuracy").
* **Submission 6**
    * **True Classification:** Hybrid
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Correct
    * **Confidence Level:** Medium
    * **Key Observations:** Correctly identified the blend of a specific personal experience (red team-blue team exercise) with a polished, slightly clich\'e9d conclusion.

#### **Manufacturing Engineering**

* **Submission 1**
    * **True Classification:** AI
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** The high level of technical detail and systematic structure were misinterpreted as AI-assisted human work rather than pure AI generation.
* **Submission 2**
    * **True Classification:** AI
    * **Model Prediction:** AI
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** The methodical, impersonal, and technically dense presentation was correctly identified as AI-generated.
* **Submission 3**
    * **True Classification:** Human
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Wrong
    * **Confidence Level:** Medium
    * **Key Observations:** The model misread the simple language and generic phrasing as a sign of AI assistance, failing to recognize it as unrefined human writing.
* **Submission 4**
    * **True Classification:** Human
    * **Model Prediction:** Human
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** Correctly identified the simple sentence structures, anecdotal tone, and limited technical jargon as authentic human writing.
* **Submission 5**
    * **True Classification:** Hybrid
    * **Model Prediction:** AI
    * **Evaluation Result:** Wrong
    * **Confidence Level:** High
    * **Key Observations:** The model was fooled by the highly formal and polished technical text, missing any subtle markers of human guidance.
* **Submission 6**
    * **True Classification:** Hybrid
    * **Model Prediction:** Hybrid
    * **Evaluation Result:** Correct
    * **Confidence Level:** High
    * **Key Observations:** Correctly identified that the practical, real-world insights were likely from a human, while the structured, textbook-like phrasing pointed to AI assistance.

## GenAI Evaluation

### GenAI Rating
* **Feedback Generation Quality: 4/5** Gemini is highly effective at creating structured, rubric-aligned feedback that is clear, professional, and actionable. It consistently identifies relevant evidence from the text to support its ratings. The primary drawback is the generic and repetitive nature of its summary statements, which can make the feedback feel formulaic.
* **AI Detection Accuracy: 1/5** The model's detection capability is fundamentally unreliable. The low accuracy (37%) combined with a severe bias against classifying text as "Human" makes it unsuitable for any real-world classification or academic integrity tasks. Its predictions are not trustworthy.

### Detailed Analysis

#### Feedback Generation Issues and Strengths

While the top-level summary is often generic, the model's strength lies in its detailed, criteria-based breakdown. This granular feedback is far more useful than a single block of text.

**Sample Output Analysis (Strengths):**
* **Criterion:** Technical Acumen
* **Rating:** Excellent
* **Evidence:** "Correctly applies concepts such as lean manufacturing, takt time, and line balancing."
* **Improvement Tip:** "Maintain the strong use of terminology while adding depth by incorporating advanced technical concepts such as downtime minimization metrics or automation integration strategies."

This structured output is a clear advantage, providing specific, actionable insights for student improvement.

#### AI Detection Failures

The model's poor performance is evident from the confusion matrices. It correctly identified only 5/10 AI submissions, 1/10 Human submissions, and 5/10 Hybrid submissions. The most significant failure is its inability to reliably recognize authentic human writing, which it frequently mislabels as Hybrid.
