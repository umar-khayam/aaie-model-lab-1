# AAIE — Final Report on Evaluation Metrics

## Overview

For AAIE, we are fine-tuning language models to detect AI-generated writing and produce teacher-style feedback for student work. This report explains the metrics we’ll use to assess model performance: what each metric indicates, its limitations, and when we use which metric.

## The Two Things We’re Evaluating

1. **AI-detection** (Is this text likely written by AI?) — we compare the model’s classification vs ground truth (human vs AI).  
2. **Feedback quality** (Does the model’s feedback resemble a teacher’s feedback in content and meaning?) — we compare generated feedback with actual teacher feedback for the same essay.

---

## Evaluation Metrics for Feedback Generation

### Perplexity
Perplexity is a measure of how “surprising” a text is to a language model: lower perplexity means the model finds the sequence more predictable. We use it during training to monitor learning curves and choose checkpoints. However, a low perplexity doesn’t guarantee the feedback is useful, correct, or high quality.

### BLEU
BLEU (Bilingual Evaluation Understudy) is an n-gram overlap metric: it rewards the model when it reuses short phrase segments that appear in reference feedback (teacher feedback) (Papineni et al. 2002). BLEU is popular for measuring surface similarity but can downplay valid paraphrases (Post 2018) and depends heavily on tokenization and parameter choices.

### ROUGE
ROUGE (Recall-oriented Understudy for Gisting Evaluation) focuses more on coverage: did the generated feedback mention the same key points or phrases as the reference? Since it is overlap-based, it still struggles to judge deeper semantic correspondence.

### BERTScore
BERTScore computes similarity in contextual embedding space, not via exact token matches (Zhang et al. 2020). It better captures semantic equivalence, making it more robust to paraphrasing and changes in phrasing while still penalizing divergence.

---

## Evaluation Metrics for AI Detection

### Accuracy
Accuracy is the ratio of correct predictions (both true positives and true negatives) over all samples. However, in imbalanced datasets, accuracy can be misleading: a model that always predicts “human” might score high accuracy but fail to detect AI usage meaningfully (PLOS One 2023).

### Precision
Precision (positive predictive value) is the fraction of items predicted as AI that truly are AI (i.e. true positives / (true positives + false positives)). High precision implies few false flags (“false positives”)—which is especially important in this use case (Google Developers 2025; Wikipedia 2025).

### Recall
Recall (sensitivity) is the fraction of AI-written texts that the model correctly identifies (true positives / (true positives + false negatives)). High recall ensures the model catches many instances of AI usage, though excessive recall can lead to more false positives (Wikipedia 2025).

### F1 Score
The F1 score is the harmonic mean of precision and recall:  
F1 = 2 * (Precision * Recall) / (Precision + Recall)  

F1 balances precision and recall, and is especially useful when both false positives and false negatives matter (GeeksforGeeks 2025).

### Averaging Methods (Macro, Micro, Weighted)
- **Micro-averaging** aggregates all true/false positives/negatives across classes first, then computes precision, recall, F1.  
- **Macro-averaging** computes the metrics per class and then averages them equally—so small classes are weighted equally.  
- **Weighted averaging** also averages per class but weights by class frequency, reflecting dataset imbalance.  

In a binary AI vs human classification, macro and micro may coincide, but in multi-class or subgroup analyses, choosing the right averaging scheme matters.

---

## False Positives in AI Detection

### What False Positives Are & Why They Matter
A false positive is when the detector incorrectly labels a human-written essay as AI-generated. In an educational setting, that is especially unfair: a student who legitimately wrote their assignment could be wrongly flagged and accused of cheating, causing distress and loss of confidence. Given this risk, minimizing false positives is a key design and evaluation goal in AI detection systems.

### Strategies to Mitigate False Positives
- **Threshold tuning:** Set stricter decision thresholds so that the detector only flags text when it is highly confident. This reduces spurious flags at the cost of potentially missing weaker AI signals.  
- **Ensembles or cross-verification:** Use multiple detection models or metrics in concert (e.g. consensus among detectors). Empirical studies show that combining detectors can sharply lower the false positive rate.  
- **Human review for ambiguous cases:** For borderline or uncertain detections, route results to human reviewers (e.g. instructors) rather than acting automatically. This ensures a safety net to catch erroneous flags.

---

## Fairness and Care
We will analyze errors across relevant student subgroups (e.g. ESL vs native writers, essay length, topic domain). If systematic bias emerges, we’ll calibrate thresholds or develop rules to correct it. Remember: the model output is a draft or signal, not the final verdict—teachers remain the final decision-makers.

---

## When to Use Which Metric (Quick Guide)
- **Training stage:** track perplexity for model fluency and selection of checkpoints.  
- **Feedback generation:** use BERTScore for meaning (primary), plus ROUGE and BLEU for coverage and phrasing overlap, combined with teacher qualitative review.  
- **AI detection:** report precision, recall, F1, accuracy, and specify averaging scheme (micro/macro/weighted).  

---

## How We Set Up Trustworthy Testing
We’ll build a stratified gold dataset representing various essay types and student populations. Splits (train/validation/test) remain fixed to ensure comparability across experiments. Where possible, include real teacher feedback so that BLEU/ROUGE/BERTScore comparisons are meaningful.

---

## AI Detection for AAIE
We will calibrate the detector to maintain a balance between precision (limiting false positives) and recall (catching AI usage). The system returns a confidence score and brief explanation, and flagged cases will be reviewed by teachers before any judgment.

---

## Feedback Generation for AAIE
We fine-tune on teacher feedback pairs and evaluate via semantic similarity (BERTScore), plus coverage and wording overlap (ROUGE, BLEU). Teacher review remains the final arbiter of quality. Draft feedback will always be editable and clearly labeled.

---

## What We Will Publish
- **Training curves:** perplexity over time and checkpoint selection.  
- **Feedback quality:** BERTScore, ROUGE, BLEU, plus anonymised side-by-side examples vs teacher feedback.  
- **AI detection performance:** precision, recall, F1, accuracy, plus subgroup fairness analysis and commentary.  

---

## Conclusion
No single metric captures everything. Perplexity is useful for training behavior but not for assessing final quality. For feedback generation, we combine BERTScore, ROUGE, and BLEU to capture semantics, coverage, and phrasing. For AI detection, precision, recall, and F1 (with proper averaging) provide a multi-angle view of reliability, with special emphasis on minimizing false positives to protect students from wrongful flags.

---

## References
- Papineni, K., Roukos, S., Ward, T. & Zhu, W. (2002) *BLEU: a Method for Automatic Evaluation of Machine Translation*. Proceedings of ACL.  
- Zhang, T., Kishore, V., Wu, F., Weinberger, K. & Artzi, Y. (2020) *BERTScore: Evaluating Text Generation with BERT*. arXiv preprint.  
- Google Developers (2025) *Classification: Accuracy, Precision, Recall, and Related Metrics*. [online] Available at: https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall  
- Post, M. (2018) *A Call for Clarity in Reporting BLEU Scores*. arXiv preprint.  
- PLOS One (2023) *Challenges in the real world use of classification accuracy metrics*.  
