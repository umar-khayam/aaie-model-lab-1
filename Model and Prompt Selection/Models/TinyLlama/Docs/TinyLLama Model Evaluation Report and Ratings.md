# GenAI & Human Evaluation Report – TinyLLama Model

## 1. GenAI Evaluation – AI Detection Task

### Overall Accuracy
- Correct Predictions: 16 / 30
- Wrong Predictions: 14 / 30
- Performance is barely above random chance, highlighting significant weaknesses in aligning with human judgments.

### Domain-Level Accuracy

| Domain | Submissions | Correct | Wrong | Notes |
| --- | --- | --- | --- | --- |
| Psychology | 6 | 3 | 3 | Mixed results; struggles distinguishing Hybrid vs Human. Some AI-assisted writing flagged incorrectly. |
| IT | 6 | 3 | 3 | Best-performing domain; Human essays recognized well. Some AI misclassified as Human persists. |
| Engineering | 6 | 5 | 1 | Similar to Psychology; errors mostly in Hybrid detection. |
| Teaching | 6 | 4 | 2 | Weak domain; frequent over-attribution to Human, especially for nuanced AI-assisted submissions. |
| Accounting | 6 | 1 | 5 | Major misclassification of AI as Human; Hybrid detection inconsistent. Only Submission 6 correctly identified as Hybrid. |

**Insight:** IT is the only domain with reasonable reliability. Teaching & Accounting are clear weaknesses, heavily affecting overall performance.

---

### Error Pattern Analysis

#### False Negatives (AI → Human/Hybrid)
- Most frequent error type, especially in Accounting & Teaching.
- Detector tends to trust polished, AI-like academic writing as Human.
- Example: Accounting Submissions 1 & 2 were AI but classified as Human.
- Impact: Undermines the tool’s primary purpose—flagging AI-generated content.

#### Human Misclassified (Human → Hybrid/AI)
- Less frequent but occurs in Teaching & Accounting.
- Detector sometimes overcompensates, labeling nuanced human writing as Hybrid.
- Example: Accounting Submission 4 was Human but labeled Hybrid.

#### Hybrid Misclassifications
- Hybrid texts inconsistently detected.
- Correctly identified in IT Submission 6, but often missed in Engineering, Teaching, and Accounting.
- Example: Accounting Submission 5 (Hybrid) flagged as Human.

#### Confidence Analysis
- High confidence on wrong predictions is concerning, indicating a systematic blind spot.
- Many AI texts misclassified as Human were given high confidence.
- Medium confidence more common for Hybrid misclassifications.

---

### Key Insights
- Bias toward Human labels drives false negatives, particularly in Accounting and Teaching.
- Hybrid detection remains weak and often confused with Human, requiring clearer criteria.
- Overconfidence in incorrect predictions highlights calibration issues in model outputs.
- Domain-specific challenges exist; Accounting’s real-world examples and IT-like precision seem to mislead the detector.

---

### Recommendations
- Recalibrate detection thresholds to reduce bias toward Human in polished, rubric-aligned texts.
- Improve Hybrid recognition using nuanced AI + Human collaboration samples.
- Apply domain-specific fine-tuning for Accounting and Teaching.
- Introduce more real-world academic writing samples in training to improve distinction between Human, AI, and Hybrid texts.

---

## 2. Human  Evaluation (TinyLLama)

### AI Detection Performance: 2/5

#### Critical Performance Issues
- Overall accuracy barely above random chance, showing systematic failures across domains.
- Severe bias toward Human classification; AI-generated content frequently misclassified.
- High false negative rate compromises academic integrity monitoring.
- Overconfident incorrect predictions indicate poor calibration between confidence and accuracy.
- Inconsistent domain performance — ranges from barely functional to unreliable.

#### Domain-Specific Weaknesses
- Teaching and Accounting domains show severe classification failures.
  - Accounting: Only 1/6 submissions correctly classified (Submission 6 as Hybrid).
  - Teaching: Frequent misclassification of nuanced Human and AI-assisted texts.
- IT domain shows marginally acceptable performance.
- Hybrid detection is consistently weak.

---

### Feedback Generation Performance: 1/5

#### Fundamental System Failures
- Cannot execute basic task requirements; fails to provide structured, rubric-aligned feedback.
- Returns rubric content instead of actionable assessment feedback.
- Frequent text cutoffs and truncation issues.
- Generic, non-specific commentary lacks actionable guidance.
- Repetitive patterns and coherence breakdown in generated text.
- Cannot evaluate content against rubric criteria.

---

### Overall Assessment
The TinyLLama model demonstrates critical limitations, rendering it unsuitable for educational assessment applications.

#### Key Concerns
- AI detection reliability insufficient for academic integrity purposes.
- Feedback generation capability fundamentally broken.
- Systematic biases undermine core functionality.
- Performance inconsistency across domains makes it unreliable for diverse educational contexts.

---

**Advantage:** Some potential in IT domain and basic Human vs AI distinction, with high-confidence correct predictions usable for targeted fine-tuning.  
**Limitations:** Overall unreliable AI detection, poor Hybrid recognition, domain inconsistencies, and total failure in feedback generation make TinyLLama unsuitable for academic or high-stakes assessment tasks without major improvements.

---

### Final Ratings

| Task | Rating | Notes |
| --- | --- | --- |
| AI Detection | 2/5 | Poor performance; dangerous false negatives, especially in Accounting & Teaching. |
| Feedback Generation | 1/5 | Complete task failure; cannot provide structured, rubric-aligned feedback. |
