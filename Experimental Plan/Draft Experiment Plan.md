# Experimental Plan for Model & Prompting Selection  
**Artificial Assessment Intelligence for Educators (AAIE) Model Development Team**  

---

## Purpose  

This plan specifies how our team will identify the most suitable model(s), select the most effective prompting technique(s), and choose the prompt for generating the best results for two tasks:  

1. **AI Detection** – Classifying a submission as AI, Human, or Hybrid.  
2. **Feedback Generation** – Producing rubric-aligned feedback.  

We will do this in three controlled phases where we change only one variable at a time. By the end, we will lock in a recommended **(Model, Technique, Prompt-Variant)** per task, with human and GenAI ratings, appropriate metrics (e.g., BLEU, ROUGE, Accuracy, F1-Score), cost/latency, and reliability statistics to justify the choice.

---

## Key Decisions to be Made  

1. The best model(s) among **ChatGPT, Gemini, Claude, Mistral, Gemma, Phi, NanoGPT** (as a control), **TinyLLaMA**, and **Qwen**.  
2. The best prompting technique(s) among **Zero-Shot (ZSL), Few-Shot (FSL), Role-based, Structured, Chain-of-Thought (CoT), Retrieval-Augmented Generation (RAG)**, or hybrids.  
3. The single best prompt variant within the chosen technique category for each task.  

---

## Dataset  

- Dataset: **5 subjects × 2 assignments = 10 distinct rubrics**.  
- Each assignment: **6 submissions** (2 AI, 2 Human, 2 Hybrid).  
- **Total:** 60 submissions.  
- Sample data provided in JSON for one Psychology assignment; nine more files will follow after peer review.

---

## Implications for Experimental Control  

To minimize bias (especially for Few-Shot and RAG), we will:  
- Begin with **one subject only** and isolate assignments to avoid cross-assignment contamination.  
- Use **the same assignment** for all techniques so comparisons stay fair.  

**Subject-level design:**  
- One assignment is the **training domain** for FSL and RAG; the second remains unseen for final evaluation.  
- The same separation applies to ZSL, Role-based, Structured, and CoT.  

**Why this design?**  
- Prevents leakage between training and testing.  
- Provides a clean generalization check: moving from Assignment 1 to Assignment 2 within the same subject.

**Scale-out plan:**  
- After the pilot, repeat the same process for the remaining four subjects.

---

## Phased Methodology – Single Variable Control  

### Phase 1: Model Selection  
- **Variable:** Model  
- **Fixed:** Base prompts  
- Run all candidate models using the same dataset items and base prompts.  
- Select top 2 models per task using human ratings and GenAI feedback.  
- Minimal prompt changes allowed (e.g., due to token limits) — all changes documented.  

### Phase 2: Prompting Technique Selection  
- **Variable:** Prompting technique  
- **Fixed:** Best model from Phase 1  
- Compare ZSL, FSL, Role-based, Structured, CoT, and RAG (for Feedback).  
- Same base prompt and settings across techniques.  

### Phase 3: Prompt Variants  
- **Variable:** Prompt variant  
- **Fixed:** Best model and technique from earlier phases  
- Test 3–5 variants within the winning technique family.  
- Choose the single best variant for final evaluation.

---

## Evaluation, Scoring, and Reliability  

**For AI Detection:**  
- Macro-F1, Accuracy, Per-class F1, AUC-ROC, Confusion Matrix.  

**For Feedback Generation:**  
- ROUGE, BLEU, BERTScore.  

**For both tasks:**  
- Human rubric ratings (1–5).  
- GenAI rubric ratings (1–5) via frozen evaluator prompt & seed.  
- Spearman correlation between human and GenAI ratings.  
- Model execution time.

---

## Work Allocation  

- **Model & Prompt Selection Subteam:** 7 members.  
  - 2 leads to design prompt structures and control variables.  
  - 3 focus on AI Detection, 3 on Feedback Generation.  
  - Maintain consistent Few-Shot examples & RAG KBs.  

- **Evaluation Subteam:** 3 members.  
  - Lead to define human rating criteria & GenAI rater prompt.  
  - Research suitable evaluation metrics & prepare code.  

---

## Timeline  

**Mid Trimester Break:**  
- Split teams, assign tasks, set fixed items, and set up GitHub.  
- Start Phase 1 model screening.  
- Down-select top models per task by Monday of Week 6.  

**Week 6:**  
- Run Phase 2 technique comparisons on chosen models.  
- Collect human & GenAI ratings.  
- Choose winning technique(s) by Friday.  

**Week 7:**  
- Tune 3–5 prompt variants within winning technique(s).  
- Run final tests, gather ratings, compute metrics, and finalize recommendations.

---

## Risk Management and Guardrails  

- **Compute limits:** Use GCP from Deep Learning Unit.  
- **Evaluation bias:** Freeze GenAI rater prompt.  
- **API limits:** Use AzureAI or Google AI Studios.  
- **Hybrid definition:**  
  > “Substantial AI assistance is evident alongside human content (e.g., AI-generated paragraphs edited by a human); not merely spell-checking.”  

---

## Deliverables and Reporting  

- **Phase 1 Report:** Model leaderboards, human/GenAI scores, latency, cost, recommendations.  
- **Phase 2 Report:** Technique leaderboards, reliability metrics, recommendations.  
- **Phase 3 Report:** Final results, human ratings, GenAI correlation, evaluation metrics, error analysis, final recommendations.

---

## Success Criteria  

1. Statistically supported improvement over baselines.  
2. Human & GenAI ratings correlate without replacing human judgment.  
3. Final configuration is cost- and latency-feasible for batch or interactive use.
