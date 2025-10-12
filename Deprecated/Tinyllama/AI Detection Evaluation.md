# AI Detection Evaluation – PR Summary  
**Author:** QASIM NASIR  
**Student ID:** 223282352  

---

## Overview  
This PR summarizes the AI detector’s performance on six submissions across AI, Human, and Hybrid labels. The evaluation was conducted **using only psychology data and base prompts** as part of the Phase 1 model selection, later the **scope was expanded to include five datasets** which is completed and can be access with  PR (https://github.com/InnovAIte-Deakin/aaie-model-lab/pull/70). Performance evaluation uses a 0–5 rating scale, based on the alignment between true and predicted labels.

---

## Submission Ratings  

| Submission | True Label | Predicted Label | Correct? | Rating (0–5) |
|------------|------------|-----------------|----------|--------------|
| 1          | AI         | Human           | No       | 1            |
| 2          | AI         | Human           | No       | 1            |
| 3          | Human      | Human           | Yes      | 5            |
| 4          | Human      | Hybrid          | No       | 4            |
| 5          | Hybrid     | Human           | No       | 4            |
| 6          | Hybrid     | Hybrid          | Yes      | 5            |

---

## Prediction Summary  
- Total submissions: 6  
- Correct predictions: 2  
- Incorrect predictions: 4  
- Overall accuracy: 33.3%  

---

## Prediction Count Table  

| Label Type | True Count | Predicted Count | Correct Count |
|------------|------------|-----------------|---------------|
| AI         | 2          | 0               | 0             |
| Human      | 2          | 3               | 1             |
| Hybrid     | 2          | 2               | 1             |

---

## Key Insights  
- AI submissions were never correctly identified (0/2).  
- Human submissions had the highest correct rate (1/2 fully correct, 1 partially misclassified).  
- Hybrid submissions were mixed: 1 correct, 1 misclassified as Human.  
- Detector performance was strongest on Human labels and weakest on AI labels.  
- Overall, there is a bias toward over-predicting Human labels.  

---

## Human Evaluation of TinyLLaMA Outputs  

| Sub | True → Predicted | Correctness | Clarity | Tone | Actionability | Final Rating |
|-----|------------------|-------------|---------|------|---------------|--------------|
| 1   | AI → Human       | 2 – Misclassified; partially useful but wrong label | 3 – Understandable, verbose | 3 – Neutral/supportive, mechanical | 2 – Vague advice | 2.5 / 5 |
| 2   | AI → Human       | 2 – Misclassified again; weak reasoning | 3 – Clear but awkward phrasing | 3 – Supportive but robotic | 2 – Mentions bias mitigation, not specific | 2.5 / 5 |
| 3   | Human → Human    | 5 – Correct classification, rubric aligned | 5 – Strong academic structure | 5 – Supportive and professional | 5 – Clear, concrete advice | 5 / 5 |
| 4   | Human → Hybrid   | 3 – Misclassified; explanation partial | 3 – Mixed, confusing “text-to-speech” | 2 – Neutral, not supportive | 1 – No meaningful next steps | 2.25 / 5 |
| 5   | Hybrid → Human   | 3 – Misclassified, but some recognition | 4 – Structured but verbose | 4 – Supportive | 3 – Shallow strategies | 3.5 / 5 |
| 6   | Hybrid → Hybrid  | 5 – Correct classification | 4 – Clear, references messy | 4 – Supportive | 4 – Concrete, reflective suggestions | 4.25 / 5 |

---

## Interpretation  
The human evaluation highlights that the detector struggles with AI-labeled submissions (both misclassified as Human), while being more reliable on Human and Hybrid texts. Clarity and tone are generally acceptable (scores around 3–4), but correctness and actionability are weaker (averages of 3.3 and 2.8, respectively).  

- **Strengths:** The model is best at recognizing Human writing style and produces supportive, professional tone when correct.  
- **Weaknesses:** Frequent misclassification of AI as Human indicates a detection blind spot. Actionability remains shallow, often lacking specific, practical advice.  

---

## AI Detection Rating (Accuracy & Correctness)  
- Correct predictions: 2/6 → 33.3% accuracy  
- Average correctness score: ~3.3 / 5  
- Human view: Weak overall — the system missed both AI submissions completely and only got 1 Human + 1 Hybrid correct. Performance shows bias toward predicting Human.  

**AI Detection Rating: 2.5 / 5 (Poor–Fair)**  

---

## Feedback Quality Rating (Clarity, Tone, Actionability)  
- Clarity: Avg 3.7 → Generally understandable, though sometimes verbose/confusing.  
- Tone: Avg 3.5 → Neutral/supportive but mechanical.  
- Actionability: Avg 2.8 → Weakest area; feedback often vague and not practically useful.  
- Overall impression: Feedback is supportive but shallow; it sounds like it’s trying to be academic, but lacks depth and specificity.  

**Feedback Rating: 3.5 / 5 (Fair–Good)**  

---

## Summary  
- The AI detection side is underperforming (2.5/5), showing major blind spots.  
- The feedback generation side is moderately useful (3.5/5), but needs stronger actionability and less robotic tone.  
