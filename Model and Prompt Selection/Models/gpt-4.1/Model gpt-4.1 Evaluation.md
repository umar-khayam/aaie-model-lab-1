# Evaluation of OpenAI’s GPT-4.1  
**Author:** Arnav Ahuja  
**Student ID:** 223271095  

## Model Description  
GPT-4.1 is part of the GPT-4 family of large language models developed by OpenAI, the same family that underpins the widely known ChatGPT product. These models have been trained on diverse datasets and optimized not only for reasoning but also for multi-task performance, from academic analysis and structured assessment to conversational tutoring and code generation. Unlike reasoning-specialized models, GPT-4.1 is designed as a generalist which implies that it balances instruction-following, creativity, general knowledge, and rubric-aligned structured outputs. It inherits advances from GPT-4 and ChatGPT, which are widely validated in education, professional writing, and domain-specific tasks.  

GPT-4.1’s strength lies in its consistency and fluency, particularly in scenarios requiring clear structure and rubric alignment. This makes it an especially good fit for AAIE’s use case: detection of AI vs human writing with rationale and generation of structured, actionable feedback aligned to academic rubrics. For AI detection, GPT-4.1 combines strong text classification capability with reliable style/rationale explanations. For feedback generation, our model produces highly structured, rubric-aligned responses, with nuanced tone and examples, aligning directly to the student-facing feedback task. Its deployment track record means it benefits from robust safety layers, monitoring, and enterprise governance, which is critical when building tools for academic integrity and student feedback.  

## Azure AI API Key Access  
Instead of using OpenAI’s direct API, we deployed GPT-4.1 through the Azure OpenAI Service which offers free student credits. This was done using the official AzureOpenAI Python SDK client. Running via Azure ensured enterprise-grade reliability, scale, observability, and compliance, all requirements for our AAIE project. It also avoids reliance on free credits from the consumer-facing API and instead anchors the system within Deakin’s cloud infrastructure and cost controls.  

## Use in AAIE  
We used the same pipeline and same dataset structure as with all the other models we tested:  

- **Datasets:** `engineering.json`, `accounting.json`, `it.json`, `psychology.json`, `teaching.json`.  
- **Prompting:** base prompts for detection (Human vs AI vs Hybrid, with rationale & flags) and feedback (Overall Summary → Criteria Feedback → Overall Rating).  
- **Few-shots:** one per label type (Human, AI, Hybrid) where available, capped at 3.  
- **Output captured:** per submission [DETECTION] and [FEEDBACK] blocks in plain text.  

This ensured a like-for-like comparison with other models.  

## AI Detection Task Evaluation  

| Domain                   | Total Submissions | Correct Predictions | Wrong Predictions | Accuracy (%) |
|---------------------------|------------------:|--------------------:|------------------:|-------------:|
| Manufacturing Engineering | 6                 | 5                   | 1                 | 83%          |
| Accounting                | 6                 | 4                   | 2                 | 67%          |
| Information Technology    | 6                 | 6                   | 0                 | 100%         |
| Psychology                | 6                 | 5                   | 1                 | 83%          |
| Teaching                  | 6                 | 6                   | 0                 | 100%         |
| **Overall**               | **30**            | **26**              | **4**             | **87%**      |

### Interpretation  
- The overall accuracy of **87%** is substantially high. This suggests GPT-4.1 performs very well on the detection task under our dataset and prompt setup.  
- By domain: No domain collapsed. Information Technology and Teaching had perfect classification (100%), while Psychology and Engineering were strong at 83%. Accounting was the weakest at 67%, but still above random chance and usable.  
- By label type: The majority of errors were in **Hybrid** label, likely reflecting edge cases or Hybrid-style submissions that leaned ambiguous.  
- Caution on accuracy as a single metric: While 87% is excellent, accuracy can fluctuate with dataset sampling. It is also important to consider distribution of errors. Here, no domain shows critical failure, and the performance is balanced enough that the system remains reliable for AAIE’s use case.  

**Conclusion:** Even accounting for potential variance, GPT-4.1 demonstrates consistently strong detection performance across domains. With minor calibration, it is robust enough to proceed as the primary model.  

## Feedback Generation Task – Human Evaluation  

### Ratings Summary  

| Domain                   | Correctness | Clarity | Tone | Actionability | Overall Avg |
|---------------------------|------------:|--------:|-----:|--------------:|------------:|
| Manufacturing Engineering | 4.0         | 4.5     | 4.5  | 3.8           | 4.2 (Good)  |
| Accounting                | 4.2         | 4.3     | 4.3  | 3.8           | 4.2 (Good)  |
| Information Technology    | 4.0         | 4.5     | 4.7  | 3.9           | 4.3 (Good)  |
| Psychology                | 3.5         | 3.7     | 4.0  | 4.0           | 3.8 (Good)  |
| Teaching                  | 3.8         | 3.9     | 4.1  | 3.5           | 3.8 (Good)  |
| **Overall Average**       | **3.9**     | **4.2** | **4.3** | **3.8**     | **4.1 (Good)** |

### Interpretation  
- **Correctness / Helpfulness: 3.9 / 5**  
  Judgments were sound and aligned to rubric expectations, but occasionally shallow in depth (e.g., “add more evidence” without specifying type/priority).  
- **Clarity & Structure: 4.2 / 5**  
  Very strong. Every output followed the required 3-part structure (Summary → Criteria → Overall Rating). Easy to follow and consistently formatted.  
- **Tone: 4.3 / 5**  
  Supportive and professional across all domains. Balanced recognition of strengths with constructive guidance.  
- **Actionability: 3.8 / 5**  
  Improvement tips were present for nearly all criteria, but some were generic or repetitive (“add detail,” “include case studies”) rather than fully prioritized, example-driven steps.  

**Overall Human Rubric Score:** **4.1 / 5 (Good)**  
GPT-4.1 is reliable for structured, student-friendly feedback. Its main area for growth is Actionability, where prompts can be tuned to elicit concrete, prioritized steps with domain-specific mini-examples.  

## Feedback Generation Task – GenAI Evaluation  

- **Correctness (Accuracy & Helpfulness): 4.0 / 5**  
  Feedback was mostly accurate, aligned with rubric criteria, and domain-aware (e.g., blockchain in Accounting, pedagogy in Teaching). Some suggestions were high-level rather than deeply specific, so not consistently at “Excellent.”  
- **Clarity (Understandability & Communication): 4.3 / 5**  
  Very clear structure and plain language. Headings and bullet points were consistent. Occasionally, examples were generic, but ambiguity was minimal.  
- **Tone (Supportiveness & Constructiveness): 4.4 / 5**  
  Strongly supportive and respectful across all domains. Balanced praise with constructive criticism. Rarely felt generic, though occasionally a bit templated in phrasing.  
- **Actionability (Clear Next Steps): 3.7 / 5**  
  Most criteria included improvement tips, but many were broad (“add examples,” “link to research”) rather than prioritized, step-by-step actions with resources. This was the weakest dimension.  
- **Coherence (Consistency & Flow): 4.2 / 5**  
  Logical progression from Summary → Criteria Feedback → Overall Rating. Flow was smooth and rarely disjointed.  
- **Emotion (Sensitivity & Encouragement): 4.3 / 5**  
  Feedback was emotionally intelligent — respectful, encouraging, and sensitive to student effort. Criticism was constructive, not discouraging.  

**Overall GenAI Rubric Rating:** **4.0 / 5 (Good)**  
GPT-4.1 produced clear, supportive, and rubric-aligned feedback with strong tone and clarity. Its main area for improvement is Actionability, where tips need to be more concrete, prioritized, and domain specific.  

## Time Latency Summary  

| Domain                   | Avg Latency (Detection) | Avg Latency (Feedback) |
|---------------------------|------------------------:|-----------------------:|
| Manufacturing Engineering | 1.86s                  | 4.60s                  |
| Accounting                | 1.99s                  | 6.87s                  |
| Information Technology    | 1.45s                  | 3.77s                  |
| Psychology                | 2.05s                  | 3.92s                  |
| Teaching                  | 2.09s                  | 5.16s                  |
| **Overall Average**       | **1.89s**              | **4.87s**              |

### Interpretation  
The system demonstrates fast detection times (**1.9s** on average) and moderate feedback generation times (**4.9s**). This performance indicates GPT-4.1 is responsive enough for both batch evaluations and interactive classroom or academic support use cases, with latency well within practical limits.  

## Recommendation  

**Short answer:** Yes, select GPT-4.1 as the leading candidate for AAIE’s Phase 1 detection & feedback.  

### Advantages  
- High detection accuracy so far (about **87%**), considerably high for outputs obtained using prompt engineering.  
- Strong rubric alignment and clarity in feedback.  
- Supportive tone across domains, student appropriate.  
- Stable and enterprise-ready via Azure OpenAI (scalable deployment, governance support).  

### Limitations  
- Hybrid detection remains a little weak, model often defaults to AI. Needs calibration with stronger few-shots or a two-stage classifier.  
- Improvement tips sometimes generic. Could be strengthened by prompting for domain-specific examples and prioritized next steps. Actionability could be improved.  
