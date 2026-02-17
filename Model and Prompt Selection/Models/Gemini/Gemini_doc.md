# Evaluation of Google Gemini-1.5 Pro

## Model Description
Gemini-1.5 Pro is Google’s mid-tier LLM with strong reasoning and long-context capabilities, accessible via the official `google-generativeai` SDK. It supports academic use with a free API key, which made it practical and sustainable for the AAIE evaluation.  

In our setup, we used our base prompts and our base dataset (teaching, psychology, IT, engineering, accounting) and executed the pipeline that prints a per-submission Detection block and a rubric-aligned Feedback block for each domain.

---

## How the Model Was Used in AAIE
We ran two tasks across all domains (6 submissions each; total 30 submissions) using the base prompt framings:

1. **Academic Integrity Detection (Classification)**  
   - **Goal:** Label each submission as Human / AI / Hybrid with a brief rationale.  
   - **Prompts:** Detection prompt spec with a few-shot prefix taken from the same dataset structure.  
   - **Intended Scoring:** Compare prediction to ground truth using the AI-detection evaluation framework (binary Correct/Wrong) and the Human AI-detection rubric.  

2. **Rubric-Aligned Feedback Generation (Text Generation)**  
   - **Goal:** Produce structured feedback with Overall Summary, Criteria ratings + evidence, Improvement tip, and an Overall rating.  
   - **Prompts:** Feedback prompt that expands the rubric JSON to readable text, per submission.  
   - **Intended Scoring:** Evaluate outputs with the GenAI feedback evaluator and the Human feedback rubric.  

---

## Detection Task – Outputs and What We Can (and Cannot) Measure

### What We Can Read Directly from the Run Output
Across the 5 domains (6 submissions each), the model’s predicted labels are:

| Domain                  | #Human | #AI | #Hybrid | Total |
|--------------------------|--------|-----|---------|-------|
| Teaching                | 4      | 2   | 0       | 6     |
| Psychology              | 0      | 6   | 0       | 6     |
| Information Technology  | 3      | 2   | 1       | 6     |
| Manufacturing Engineering | 2    | 4   | 0       | 6     |
| Accounting              | 2      | 4   | 0       | 6     |
| **Overall**             | 11     | 18  | 1       | 30    |

**Accuracy:** 63.33%  

### Why a True Accuracy % Cannot Be Computed
A correct accuracy requires **ground-truth labels** per submission. The printed output shows only the model’s predicted label and rationale (e.g., “Label: AI … Flags: …”), but it does not include the ground truth for each submission. Neither the AI-detection framework description nor the human detection rubric provides those labels; they only define how to judge correctness once ground truth is known.

---

## Feedback Generation – Quality Ratings (Two Lenses)

### A) GenAI Feedback Evaluator Rating (Overall)
**Overall: 4.4 / 5 (Good → Excellent)**  

**Why (by criterion):**
- **Correctness (4.3/5):** Aligns with rubric, identifies strengths and gaps (e.g., “expand… diversity and inclusion with more specific examples and research-based strategies”). Minor generic phrasing limits depth.  
- **Clarity (4.7/5):** Clear structure with headings/bullets mapped to rubric (e.g., “provides a concise overview…” in Psychology).  
- **Tone (4.8/5):** Supportive and constructive (e.g., “Prioritizing a deeper exploration… will significantly strengthen the work.”).  
- **Actionability (4.2/5):** Provides next steps (e.g., “Provide more specific examples… discuss strategies for incorporating home languages or visual supports.”). Could prioritize better.  
- **Coherence (4.5/5):** Logical flow from Overall Summary → Criteria → Overall rating.  
- **Emotion (4.5/5):** Encouraging and respectful; balances recognition with improvement targets.  

**Representative Strengths:**
- Clear, structured summaries (e.g., “provides a concise overview… effectively links [biases] to real-world scenarios” in Psychology).  
- Actionable advice tied to rubric gaps (e.g., “Provide more specific examples of inclusive practices and connect them to relevant research.”).  

**Observed Limitations:**
- Sometimes high-level phrasing instead of mechanism detail.  
- Diversity/inclusion suggestions recur, accurate but can appear template-like without domain-specific examples.  

---

### B) Human Feedback Rubric Rating (Overall)
**Overall: 4.2 / 5 (Good)**  

**Why (by criterion):**
- **Correctness (4/5):** Sound judgments tied to prompt requirements (e.g., “Integrate more peer-reviewed research… provide a complete reference list”).  
- **Clarity (4.5/5):** Readable, logically structured (intro summary → targeted advice → overall).  
- **Tone (4.7/5):** Constructive/respectful balance of strengths and gaps (e.g., “The writing is clear… consider adding a more formal introduction and conclusion”).  
- **Actionability (4/5):** Provides clear next steps (e.g., “Introduce and critically evaluate at least two evidence-based approaches…”). Could improve specificity.  
- **Coherence (4.3/5):** Feedback reads cohesively with aligned suggestions.  
- **Emotion (4.2/5):** Supportive, encouraging progress without discouragement.  

**Representative Strengths:**
- Targeted criterion-level “what to fix + how” (e.g., “Discuss how individual learner differences… and how instructional approaches can be adapted.”).  
- Balanced tone: acknowledges strengths, then pivots to clear steps (e.g., “The writing is well-structured… expand on the explanation… provide more specific examples.”).  

**Observed Limitations:**
- Some advice is repetitive (e.g., “add more research,” “expand D&I”), occasionally generic.  
- Prioritization of steps could be sharper.  

---

## Recommendation
- **Select Gemini-1.5 Pro for AAIE.**  

**Why:**  
- Accessible (free API key) and sustainable.  
- Produced consistently rubric-aligned feedback of good–excellent quality across both GenAI and Human evaluation lenses.  
- Handled detection rationales sensibly using formality, specificity, and voice markers.  

**Caveats:**  
- Detection accuracy still requires **ground truth labels** to finalize selection.  
- Feedback prompts should nudge for **more concrete mechanisms, examples, and diversity/inclusion exemplars** to avoid generic phrasing.  
