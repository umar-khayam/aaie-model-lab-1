# Phase 1 Model Report 
**Authors:** Arnav Ahuja, Namit Jain  
**Contributors:** Arnav Ahuja, Mohtashim Misbah, Ed Rasguido, Qasim Nasir, Namit Jain, Prem Sai Reddy, Umar Khayam 

## Project Overview
Artificial Assessment Intelligence for Education (AAIE) aims to assist educators in two tasks:  
•	**AI Detection:** Classify a student submission as Human, AI, or Hybrid, with a short, auditable rationale and a confidence score.  
•	**Feedback Generation:** Produce structured, rubric aligned, student friendly feedback (Criteria feedback with evidence, Improvement tips, Overall rating).  

Both tasks must be reliable, fast enough for classroom use, and easy to audit by staff. Our evaluation emphasises accuracy, clarity, tone, actionability, latency, and maintainability.

## Phase 1 – Model Selection
We evaluated 10 models using the same datasets (Teaching, Psychology, IT, Engineering, Accounting; 6 submissions each) and base prompts for both tasks.  

**Cohorts:**  
•	Commercial: GPT 4.1 (Azure), Gemini 1.5 Pro, Claude 3.5 Haiku (OpenRouter)  
•	Open source: DeepSeek R1, Mistral 7B Instruct v0.3, Gemma, TinyLLaMA, Qwen3 0.6B, Phi 2, NanoGPT (paid)  

**Protocol:** Three few shot exemplars where available; detection labels and rationale; feedback in 3 part structure. Human raters and a GenAI rubric cross checked feedback quality.

## Phase 2 – Prompting Technique, API and Deployment 
### API & System Architecture
•	Primary API: API endpoints for /classification, /rubric-scores and /feedback with strict JSON schemas; retry and timeout policies; request logging; auditor view for rationales.  
•	Orchestration: Router selects a primary model per task; optional secondary model for tie breaks and ambiguous cases; confidence scoring and thresholds.  
•	Observability: Metrics (accuracy, latency, error rate), tracing, dataset drift alerts, reviewer dashboards; red flag queue for human moderation.

### Deployment options
•	Managed (recommended for primary): Exploring Azure AI, OpenRouter, Ollama, LMStudio, Docker and Local deployment options. Currently, Gemini 1.5 Pro for both detection and feedback (free tier).
•	Self hosted (optional second tier): Containerised open models (DeepSeek R1, Mistral, Gemma, Qwen, TinyLLaMA, Phi 2) behind a GPU autoscaling pool; batch mode only where slow.  
•	Cost controls: Per domain routing, caching of stable feedback, batch overnight jobs for heavy/slow models, usage quotas.

### Prompting techniques to standardise
•	Zero shot (ZSL): baselines for both tasks to keep prompts short and fast.  
•	Few shot (FSL): per domain exemplars covering Human, AI, Hybrid (esp. edge case hybrids) for detection; exemplar feedback snippets for actionability.  
•	Chain of Thought (CoT): internal only to improve model reasoning; hide raw chains from students. Summarise rationale succinctly in outputs.  
•	Role based: e.g., “Academic Integrity Analyst” for detection; “University Marker” for feedback to tune tone & criteria alignment.  
•	Structured outputs: enforced JSON renderer transforms to student friendly text. Include fields for priority, examples, first steps this week, longer term steps to lift actionability.

### Evaluation harness & acceptance gates
•	Define acceptance bars per task (e.g., Detection ≥85% overall with ≤5% domain collapse; Feedback ≥4.2/5 human rating, Actionability ≥4.0).  
•	Shadow mode rollout in one unit, then phased release.

## Model by Model Ratings & Recommendations 
Scales used:  
•	Detection = accuracy on 30 submissions (or status)  
•	Feedback = human/GenAI rubric summary  
•	Latency = indicative  
•	Verdict = recommended role  

### GPT 4.1
•	Detection: 87% overall; no domain collapse; Hybrid is main error source.  
•	Feedback: Good (4.1/5); clear structure & tone; actionability sometimes generic.  
•	Latency: Fast (1.9s detect / 4.9s feedback avg).  
•	Verdict: Primary for both tasks with minor prompt tuning (esp. Hybrid calibration and more concrete tips).  

### DeepSeek R1 
•	Detection: 70% overall; several “no outcome” leanings; Hybrid hardest.  
•	Feedback: Average (3.5/5); structure OK, actionability shallow.  
•	Latency: High (34s detect / 58s feedback avg); not ideal for interactive use.  
•	Verdict: Fallback / second opinion model (ensemble, batch, or moderator tool).  

### Gemini 1.5 Pro 
•	Detection: Run outputs suggest 63% but ground truth mapping in the log is incomplete; treat cautiously.  
•	Feedback: Strong (GenAI 4.4/5); clear structure, supportive tone.  
•	Latency: Not captured in this run.  
•	Verdict: Secondary for feedback (vendor redundancy); detection uncertain until re run with labels connected.  

### Claude 3.5 Haiku 
•	Detection/Feedback: Not evaluated as API 402 credit error blocked runs.  
•	Verdict: Not selected (access constraints). Revisit only if reliable credits or direct academic access become available.  

### Mistral 7B Instruct v0.3 
•	Detection: 47% (14/30 correct); misreads technical Human as AI.  
•	Feedback: Below avg (human 2.6/5; GenAI 3.0/5); actionability weak; formatting issues.  
•	Verdict: Not for detection; possible feedback candidate with strict prompting + post processing & QC.  

### Gemma 
•	Detection: 33% with strong Hybrid bias.  
•	Feedback: Good (4/5) but repetitive; very slow (15 min/submission) → unsuitable for real time.  
•	Verdict: Batch only feedback if ever used; otherwise not recommended.  

### NanoGPT
•	Detection: 39%; strong bias; poor Human recall.  
•	Feedback: 4/5 quality but <10% uniqueness; generic across domains.  
•	Verdict: Not recommended (weak detection + generic feedback + paid dependency).  

### Qwen3 0.6B
•	Detection: 30%; bias to “Human”.  
•	Feedback: Structured outputs; quality generic; needs assessor oversight.  
•	Verdict: Not for detection; could prototype as lightweight feedback generator or consider larger Qwen variants.  

### TinyLLaMA 
•	Detection: Poor (2/5); human eval 16/30 correct (53%); bias to Human; overconfident errors.  
•	Feedback: 1/5; format failures and truncation.  
•	Verdict: Unsuitable for AAIE.  

### Phi 2 
•	Detection: 45%.  
•	Feedback: 3.8/5 but 10% uniqueness; generic, low value.  
•	Verdict: Unsuitable (performance + infra cost/latency concerns).  

## Cross Model Comparison Table

| Model              | Type              | Detection (30 subs) | Feedback Quality     | Latency (indicative) | Distinctive Notes                               | Recommended Role                  |
|--------------------|------------------|---------------------|----------------------|----------------------|-----------------------------------------------|-----------------------------------|
| **GPT 4.1**        | Commercial       | 87%                 | Good (4.1/5)         | Fast (1.9s / 4.9s)   | Stable via Azure; Hybrid errors remain         | Primary (Detect + Feedback)       |
| **DeepSeek R1**    | Open             | 70%                 | Avg (3.5/5)          | High (34s / 58s)     | Several "leaning" cases; good structure        | Fallback / Ensemble               |
| **Gemini 1.5 Pro** | Commercial       | 63%*                | Strong (GenAI 4.4/5) | N/A                  | Accuracy caveat (labels not attached in output)| Secondary (Feedback)              |
| **Claude 3.5 Haiku** | Commercial     | N/A (run failed)    | N/A                  | N/A                  | 402 credit error on OpenRouter                 | Not selected                      |
| **Mistral 7B Inst v0.3** | Open       | 47% (14/30)         | Human 2.6 / GenAI 3.0| N/A                  | JSON formatting issues; over polished tone     | Maybe Feedback (strict QC)        |
| **Gemma**          | Open             | 33%                 | 4/5 (repetitive)     | Very slow (15 min)   | Hybrid bias; useful only offline               | Batch feedback (optional)         |
| **NanoGPT**        | Commercial/paid  | 39%                 | 4/5 (generic; <10% unique)| Fast            | Bias toward Hybrid; poor Human recall          | Not recommended                   |
| **Qwen3 0.6B**     | Open             | 30%                 | Structured but generic| N/A                  | Bias to “Human”                                | Not for detection                 |
| **TinyLLaMA**      | Open             | 53% (16/30)         | 1/5 (format fails)   | N/A                  | Overconfidence on wrong preds                  | Not recommended                   |
| **Phi 2**          | Open             | 45%                 | 3.8/5 (10% unique)   | Slow / heavy         | High mem; poor scalability                     | Not recommended                   |


## Final Recommendations for Phase 2  

### AI Detection  
- **Primary:** **Gemini 1.5 Flash** – selected for its fast response time, generous context window, and free availability.  
- **Fallback:** DeepSeek R1 will be added as an ensemble fallback in the next trimester once evaluation pipelines are stable.  

### Feedback Generation  
- **Primary:** **Gemini 1.5 Flash** – chosen because it offers strong rubric alignment, clear structure, and supportive tone **without the token-limit risks of Gemini 1.5 Pro**, which could slow down or truncate outputs during batch evaluation.  
- **Prompt Upgrades:**  
  - Require two mini-examples per weak criterion.  
  - Include **“First steps this week”** and **“Longer term steps”** fields for actionable feedback.  
  - Enforce maximum length per section to keep outputs concise and readable.  
  - Discourage vague verbs (e.g. “add detail”) and encourage specific actions.  
- **Fallback:** Mistral 7B will be explored as a batch fallback for feedback in the next trimester.  

## Rationale for This Approach  
- **Cost-effective:** Gemini 1.5 Flash’s free tier removes Azure’s 30-day GPT-4.1 constraint and allows unlimited development iteration.  
- **Simplified for MVP:** Single-model routing reduces engineering complexity for Phase 2.  
- **Future-ready:** Leaves room to add fallback/ensemble models (DeepSeek for classification, Mistral for feedback) in the next phase.  
- **Auditability:** Structured rationales and logs are maintained for staff review.  
- **Scalable:** Easy to extend with model routing once open-source inference infrastructure is stable.  

## Why GPT-4.1 Was Rejected for Phase 2  

While GPT-4.1 produced the **highest accuracy (87%)** and well-structured feedback, it was rejected as the Phase 2 primary model for the following reasons:  

- **Licensing Constraint:** GPT-4.1 access is only available through a **30-day Azure trial**, which is not sustainable for production.  
- **Cost Considerations:** Paid Azure consumption introduces a recurring cost per request, making budgeting difficult during pilot rollout.  
- **Vendor Lock-in Risk:** Relying on a single paid vendor early would hinder flexibility to pivot to open or hybrid setups later.  
- **Gemini Flash Availability:** Gemini 1.5 Flash is free, offers competitive quality for feedback generation, and avoids the token-limit issues seen with Pro.  
- **Simplicity for MVP:** Using Gemini Flash as the single primary model avoids trial rotation, quota management, and reduces engineering overhead.  

**Conclusion:** GPT-4.1 will remain a **secondary model** and may be reconsidered if free or academic access becomes available in future phases.
