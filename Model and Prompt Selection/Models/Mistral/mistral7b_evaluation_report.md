# 📄 Model Evaluation Report – Mistral-7B-Instruct-v0.3

## 1. Model Description  
**Mistral-7B-Instruct-v0.3** is an open-weight, instruction-tuned large language model developed by Mistral AI.  
- **Architecture**: 7 billion parameter dense transformer  
- **Training Objective**: Instruction fine-tuned on a mix of synthetic and curated human datasets for task following  
- **Strengths**: Strong at structured prompt following, summarization, and feedback generation  
- **Limitations**: Susceptible to hallucination in domain-specific content, struggles with strict JSON formatting, and occasionally over-polished outputs that resemble AI writing  

---

## 2. Use in AAIE Project  
In the AAIE project (Artificial Assessment Intelligence for Education), this model was used for **two key tasks**:  

1. **AI Detection Task**  
   - Classified student submissions as *AI-generated* or *Human-written*  
   - Evaluated on prediction correctness against ground truth  

2. **Feedback Generation Task**  
   - Produced structured formative feedback for student writing  
   - Evaluated using **human rubrics (Khushi’s framework)** and **GenAI scoring (Wang & Van’s framework)**  

---

## 3. Number of Correct Predictions – Detection Task  
- **Total submissions evaluated**: 30 
- **Correct Predictions**: 14
- **Accuracy**: ⚠️ **14/30**  

> The model often confused **AI-generated text with variation** as *Human*, and **technical Human text** as *AI*.  

---

## 4. Human Rating for Feedback Generation  
Using **Khushi’s Human Rating Rubric** (Correctness, Clarity, Tone, Actionability):  

- **Average Human Rating**:  **2.6  (Below Average)**  
- Some responses scored **3–4 (Average to Good)** where structure and tone were clear  
- Others dropped to **~2 (Poor)** due to parse errors, generic advice, or vague actionability  

---

## 5. GenAI Rating for Feedback Generation  
Using **Wang & Van’s ChatGPT-based evaluation prompts**:  

- **Average GenAI Rating**:  **3.0 / 5 (Average)**  
- More forgiving than human raters (especially for clarity and tone)  
- Both agreed that **Actionability was the weakest dimension**  

---

## 6. Opinion – Should We Select This Model?  

✔️ **Reasons to Select**  
- Open-weight model (no vendor lock-in)  
- Good at structured instruction-following and formal academic responses  
- Performs well in **feedback generation clarity and tone**  

**Reasons Not to Select**  
- Poor AI Detection accuracy ( ~50%)  
- Inconsistent feedback generation (humans rated below average)  
- Weak in **Actionability & Specificity**  
- Formatting issues with JSON outputs  

 **Conclusion**  
Mistral-7B-Instruct-v0.3 is **not ideal for AI Detection**, but is a **potential candidate for Feedback Generation** if combined with strict prompting, post-processing, and quality controls.  

---
