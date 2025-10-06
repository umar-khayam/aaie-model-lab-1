# Evaluation of DeepSeek-R1  
**Author:** Arnav Ahuja  
**Student ID:** 223271095  

## Model Description  
DeepSeek-R1 is a reasoning-focused large language model developed by DeepSeek AI, a research group known for producing open and high-performance models for math, science, and programming tasks. Unlike broad generalist models, R1 is explicitly trained with a step-by-step regimen that combines reinforcement learning with a supervised “cold start” phase. This design stabilizes training while sharpening its chain-of-thought reasoning particularly valuable for tasks that require logical consistency, structured analysis, and verifiable outputs. In benchmarking reports, R1 has been shown to perform competitively with other reasoning-centric systems such as o1-style models, while remaining open and deployable in enterprise settings.  

DeepSeek-R1 grew out of earlier DeepSeek releases that emphasized efficient architectures and transparent training pipelines. The “R” lineage highlights reasoning, where the model is optimized not for broad fluency but for problem-solving across domains like mathematics, coding, and scientific writing. This makes it particularly well-suited to academic and evaluation contexts where precision and rationale are more important than creative elaboration.  

For AI detection, R1’s reasoning-first training makes it capable of producing not just classification (AI-generated vs human-written) but structured rationale explaining the decision, which is essential for transparency in academic settings. For feedback generation, the model’s chain-of-thought emphasis allows it to output structured, rubric-aligned feedback with explicit stepwise reasoning, improving trust and alignment with educator expectations. Combined with Azure deployment, this ensures reliability, auditability, and scalable delivery to end-users.  

In our project AAIE, DeepSeek-R1 is expected to show some limitations that may affect its suitability. For feedback generation, it might not be able to provide the depth of evidence, and the outputs might often be too generic. For detection, the measured accuracy might not be too high compared to alternative models (especially commercial ones) we tested, indicating that R1 may not be able to provide the reliability required for high-stakes academic integrity tasks.  

## Azure AI API Access  
Instead of using OpenAI’s direct API, we deployed the R1 through the Azure OpenAI Service which offers free student credits. This was done using the official AzureOpenAI Python SDK client. Running via Azure ensured enterprise-grade reliability, scale, observability, and compliance, all requirements for our AAIE project. It also avoids reliance on free credits from the consumer-facing API and instead anchors the system within Deakin’s cloud infrastructure and cost controls.  

## Use in AAIE  
We used the same pipeline and same dataset structure as with all the other models we tested:  

- **Datasets:** `engineering.json`, `accounting.json`, `it.json`, `psychology.json`, `teaching.json`.  
- **Prompting:** base prompts for detection (Human vs AI vs Hybrid, with rationale & flags) and feedback (Overall Summary → Criteria Feedback → Overall Rating).  
- **Few-shots:** one per label type (Human, AI, Hybrid) where available, capped at 3.  
- **Output captured:** per submission [DETECTION] and [FEEDBACK] blocks in plain text.  

This ensured a like-for-like comparison with other models.  

## AI Detection Task Evaluation  

| Domain                   | Total Submissions | Correct Predictions | Wrong Predictions | No Outcome | Accuracy (%) |
|---------------------------|------------------:|--------------------:|------------------:|-----------:|-------------:|
| Manufacturing Engineering | 6                 | 5                   | 0                 | 1          | 83%          |
| Accounting                | 6                 | 3                   | 0                 | 3          | 50%          |
| Information Technology    | 6                 | 4                   | 1                 | 1          | 67%          |
| Psychology                | 6                 | 5                   | 1                 | 0          | 83%          |
| Teaching                  | 6                 | 4                   | 2                 | 0          | 67%          |
| **Overall**               | **30**            | **21**              | **4**             | **5**      | **70%**      |

### Interpretation  
- The overall accuracy of **70%** indicates a moderate but usable performance level. The model demonstrates reasonable capability on the detection task, though less robust than the 80–90% range typically considered “very strong.”  
- **Domain breakdown:** Manufacturing Engineering (83%) and Psychology (83%) performed consistently well. Information Technology (67%) and Teaching (67%) were more error-prone and had no results. Accounting (50%) was the weakest domain, with half the submissions unresolved (classified only with leaning, not explicit outcome).  
- **No-outcome cases:** Five submissions (17%) did not receive explicit outcomes and were only “leaning” predictions. These heavily affected the Accounting domain (3/6) and to a lesser extent IT (1/6) and Manufacturing Engineering (1/6). This highlights that ambiguity, rather than outright misclassification, was a significant factor in reducing accuracy. The presence of “no outcomes” means accuracy figures underestimate the model’s raw detection potential but highlight robustness issues in boundary cases.  
- **Error distribution:** Most errors and ambiguities clustered around Hybrid cases, reflecting the intrinsic challenge of detecting human–AI collaborative writing. Hybrid outputs often blend natural variation with AI-like structure, making them edge cases.  
- **Reliability considerations:** No domain fully collapsed; even the weakest (Accounting, 50%) still produced usable signals above random chance.  

**Conclusion:** At 70% accuracy, the system can provide supportive signals but should not be treated as definitive in high-stakes contexts. Supplementary human oversight and secondary checks are recommended, particularly for Accounting and Teaching submissions where ambiguity was highest. R1 might be used as a **fallback model**.  

## Feedback Generation Task – Human Evaluation  

### Ratings Summary  

| Domain                   | Correctness | Clarity | Tone | Actionability | Overall Avg |
|---------------------------|------------:|--------:|-----:|--------------:|------------:|
| Manufacturing Engineering | 3.7         | 3.9     | 4.0  | 3.2           | 3.7 (Average) |
| Accounting                | 3.6         | 3.8     | 3.8  | 3.1           | 3.6 (Average) |
| Information Technology    | 3.7         | 3.9     | 4.0  | 3.3           | 3.7 (Good)    |
| Psychology                | 3.3         | 3.5     | 3.6  | 3.0           | 3.4 (Average) |
| Teaching                  | 3.4         | 3.6     | 3.7  | 3.1           | 3.5 (Average) |
| **Overall Average**       | **3.5**     | **3.7** | **3.8** | **3.1**     | **3.5 (Average)** |

### Interpretation  
- **Correctness / Helpfulness: 3.5 / 5**  
  Mostly accurate, but evaluations often stopped at surface-level (e.g., identifying missing examples without specifying what kind). Occasional gaps in aligning feedback tightly to rubric criteria.  
- **Clarity & Structure: 3.7 / 5**  
  Generally clear and structured, though explanations could be simplified and more concise in student-facing contexts.  
- **Tone: 3.8 / 5**  
  Professional and supportive, but a little formulaic. Stronger in technical domains, weaker in more empathetic contexts like Psychology.  
- **Actionability: 3.1 / 5**  
  Weakest area. Guidance was generic and not sufficiently prioritized. Students would struggle to turn suggestions into concrete revisions.  

**Overall Human Rubric Score:** **3.5 / 5 (Average)**  
DeepSeek is usable but not yet robust for AAIE’s needs, especially where detailed, actionable, and empathetic feedback is required.  

## Feedback Generation Task – GenAI Evaluation  

- **Correctness (Accuracy & Helpfulness): 3.5 / 5**  
  Feedback was generally aligned with rubric expectations and task requirements, but often shallow in depth. Many comments stopped at high-level guidance (“add more depth,” “include examples”) without identifying specific content gaps or prioritizing the most impactful changes.  
- **Clarity (Understandability & Communication): 3.7 / 5**  
  Structure was consistent, and explanations were mostly understandable. However, some passages were dense or overly formal, making the guidance harder for students to immediately absorb. Concrete examples were limited, which reduced overall clarity.  
- **Tone (Supportiveness & Constructiveness): 3.8 / 5**  
  The tone was respectful and professional, balancing recognition of strengths with constructive criticism. Still, phrasing was sometimes formulaic (“needs more detail,” “expand with examples”) rather than empathetic or encouraging, especially in student-centred domains like Psychology and Teaching.  
- **Actionability (Clear Next Steps): 3.1 / 5**  
  The weakest dimension. Suggestions were present but mostly generic (“add detail,” “use examples,” “link to theory”). They lacked prioritization, step-by-step guidance, or resource references, which limits their usefulness for actual student revision.  
- **Coherence (Consistency & Flow): 3.6 / 5**  
  Most feedback flowed logically and avoided contradictions, but transitions between strengths and weaknesses were sometimes abrupt. Some domain outputs felt disjointed, with criteria feedback reading like separate checklists rather than a cohesive narrative.  
- **Emotion (Sensitivity & Encouragement): 3.7 / 5**  
  Feedback showed awareness of student effort and avoided harsh language, but encouragement was minimal. Comments leaned functional rather than empathetic, giving less motivation for improvement compared to stronger models.  

**Overall GenAI Rubric Rating:** **3.5 / 5 (Average)**  
DeepSeek produced structurally consistent and respectful feedback that aligned broadly with rubric expectations. Strengths were clarity of format and professional tone across domains. However, its feedback often lacked depth and specificity, with improvement tips that were too generic to be highly actionable.  

## Time Latency Summary  

| Domain                   | Avg Latency (Detection) | Avg Latency (Feedback) |
|---------------------------|------------------------:|-----------------------:|
| Manufacturing Engineering | 21.45s                 | 30.23s                 |
| Accounting                | 15.27s                 | 36.47s                 |
| Information Technology    | 48.74s                 | 52.31s                 |
| Psychology                | 36.79s                 | 91.93s                 |
| Teaching                  | 48.94s                 | 77.23s                 |
| **Overall Average**       | **34.24s**             | **57.63s**             |

### Interpretation  
The latency results show clear variation across domains. On average, detection was faster (**34s**) than feedback (**58s**), reflecting the heavier reasoning load in generating rubric-aligned responses. Manufacturing Engineering was the fastest in both detection (21s) and feedback (30s), suggesting simpler content structures. Accounting also remained relatively efficient, though feedback times stretched slightly. In contrast, Psychology (92s) and Teaching (77s) had the slowest feedback, indicating higher cognitive and evaluative overhead. Information Technology stood out for balance, with detection (49s) and feedback (52s) nearly identical, showing stable performance.  

## Recommendation  

**Short answer:** No, do not select DeepSeek-R1 as the primary model for AAIE’s Phase 1 detection & feedback. It may serve better as a fallback/secondary option to complement the primary model(s).  

### Advantages  
- Handles detection reasonably well across most domains (**70% accuracy overall**), indicating potential as a secondary evaluator.  
- Rubric-based outputs are structured and coherent, showing consistent formatting.  
- Maintains supportive and constructive tone, with appropriate sensitivity in feedback.  
- Open-weight availability offers flexibility for customization or on-premises deployment.  

### Limitations  
- Accuracy is notably lower, particularly with Hybrid detection, where it often misclassifies.  
- Feedback actionability is weaker (**3.5/5 average**), with improvement tips often generic or shallow.  
- Latency is significantly higher in certain domains (e.g., Psychology and Teaching), making it less efficient for scaled classroom use. **This is the major reason to reject it as the primary model.**  
- Requires more tuning (few-shot or fine-tuning) to match enterprise reliability expected for Phase 1 deployment.  

### Suggestion to Keep DeepSeek in the Stack  
1. **Use as a fallback/ensemble partner** – Deploy DeepSeek alongside GPT-4.1 in an ensemble or tie-breaker mode, especially for ambiguous submissions, where a second opinion may improve reliability.  
2. **Tighten feedback generation prompts** – Require outputs to include two domain-specific mini-examples per criterion and a clear “First steps this week / Longer-term steps” structure to improve actionability.  
3. **Strengthen detection calibration** – Build few-shot exemplars that cover all three classes (Human, AI, Hybrid) across each domain, with emphasis on ambiguous edge cases (e.g., lightly edited AI text) to reduce misclassification.  
4. **Guardrail output exposure** – Suppress raw reasoning chains; deliver only polished, student-safe feedback. Reserve rationales for moderator dashboards to maintain transparency without overwhelming learners.  
