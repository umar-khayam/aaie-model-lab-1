# Prompt Engineering: Concepts, Techniques, and Application in AAIE Project

**Author:** Arnav Ahuja  
**Date:** August 4, 2025  

---

## Introduction to Prompt Engineering

Prompt engineering is the process of creating effective prompts to guide a large language model (LLM) toward producing the desired output. Unlike training or fine-tuning, prompt engineering does not alter the model’s parameters; instead, it optimizes how we communicate our instructions to the AI. This technique has become essential as generative AI models move from novelties to real production tools.  

A well-designed prompt can bridge the gap between what a user intends and what the model understands, helping avoid vague or misaligned outputs. Prompts also allow control over the tone, structure, and safety of responses (e.g., instructing a model to use bullet points or to avoid certain content). In summary, prompt engineering is a key skill for steering LLMs’ behaviour without additional training, enabling us to tailor an AI’s responses to our specific needs and use cases.  

**AAIE project context:**  
We are developing an AI-assisted system for education that involves:  
1. AI-generated content detection in student submissions.  
2. Automated feedback generation aligned with a grading rubric.  

We plan to apply prompt engineering to both tasks for now, as it offers a lightweight yet powerful way to improve model performance. This document provides a comprehensive overview of prompt engineering techniques, discusses how to implement them in our project, and outlines how they can help us achieve better results. Finally, we propose the evaluation metrics for each task. The goal is to guide fellow team members on effectively using prompt engineering in our system design.

---

## Common Prompt Engineering Techniques

Prompt engineering includes various techniques that can be combined or used separately. Below are the key types of prompt strategies and their characteristics:

---

### Zero-Shot Prompting
**Definition:**  
Zero-shot prompting means giving the model an instruction (or prompt) to perform a task without providing any examples. The prompt is typically a direct query or command describing the task and desired output. The model must rely on its pre-trained knowledge to respond.  

**Example:**  
Prompting *“Explain what a large language model is”* with no additional context or examples is a zero-shot prompt.  

**Use case:**  
- Effective for well-known or simple tasks where the model’s built-in knowledge is sufficient.  
- Commonly used for summarization or simple queries.  

**Limitations:**  
- If the task is complex or requires specific outputs, zero-shot prompting can yield suboptimal or generic results.

---

### Few-Shot Prompting
**Definition:**  
Few-shot prompting involves providing a few examples of the task in the prompt before asking the model to perform it on a new input.  

**Example:**  
Submission: "I completed the assignment using my own understanding and research."
Label: Human

Submission: "This response was generated using ChatGPT based on the prompt."
Label: AI

Submission: "I drafted the answer with AI help and then rewrote parts in my own words."
Label: Hybrid

Submission: "I asked an AI assistant for guidance, then rephrased and added references from my lecture notes."
Label: ?

**Use case:**  
- Useful for complex tasks where examples help the model understand desired format and style.  

**Limitations:**  
- Examples must be clear and representative. Too many examples can bloat the prompt.

---

### Retrieval-Augmented Generation (RAG)
**Definition:**  
RAG is a technique where the model is supplied with external information fetched on-the-fly relevant to the query.  

**How it works:**  
- A retrieval component (search or vector DB) fetches relevant text.  
- Retrieved content is appended to the prompt for the LLM to use.  

**Use case:**  
- Overcomes LLM knowledge cutoff.  
- Useful for domains with frequently updated info.  

**Limitations:**  
- Requires retrieval infrastructure.  
- Irrelevant context can confuse the model.

---

### Chain-of-Thought (CoT) Prompting
**Definition:**  
Encourages the model to generate step-by-step reasoning before the final answer.  

**Example:**  
*"Let’s think this through step-by-step."*  

**Why it helps:**  
- Improves reasoning for complex tasks.  
- Enables error analysis by showing intermediate logic.  

**Use case:**  
- Math problems, logical reasoning, or nuanced classification tasks.  

---

### Role-Based Prompting
**Definition:**  
Assigns the model a persona or role to influence tone, style, and expertise.  

**Example:**  
*"You are an AI text detection expert."*  

**Why it’s useful:**  
- Sets domain context and tone.  
- Useful for consistent style in outputs.  

**Considerations:**  
- Must combine with clear task instructions for best results.

---

### Structured Prompt Templates
**Definition:**  
Prompts built in a consistent, modular format with placeholders for variable content.  

**Components:**  
- System/Context instructions.  
- User Query/Task section.  
- Examples (optional).  
- Output Format instructions.  

**Benefits:**  
- Reusable, maintainable prompts.  
- Easier debugging and improvement.  

---

## Applying Prompt Engineering in the AAIE Project

---

### Prompting for AI-Generated Content Detection
**Task:** Classify submissions as AI, Human, or Hybrid.  

**Recommended Strategy:**  
- Role prompting: *"You are an AI text detection expert."*  
- Chain-of-thought reasoning before classification.  
- Structured output (e.g., JSON label + explanation).  

**Benefits:**  
- Improves transparency and consistency.  
- Supports nuanced classification of hybrid cases.

---

### Prompting for Feedback Generation
**Task:** Generate rubric-aligned feedback for student work.  

**Approach:**  
- Provide assignment prompt + rubric as context.  
- Role prompting: Teacher/Tutor role for constructive tone.  
- Optional few-shot examples for style guidance.  
- Encourage per-criterion feedback (structured).  

**Benefits:**  
- Ensures completeness (all rubric points addressed).  
- Improves clarity, tone, and usefulness of feedback.  

---

## Evaluation Metrics for Each Task

---

### AI Detection Task – Classification Metrics
- Accuracy  
- Precision & Recall (per class)  
- F1-Score  
- Confusion Matrix & Error Analysis  

**Goal:** High precision & recall for AI class, strong performance on Hybrid class.

---

### Feedback Generation Task – Quality Metrics
- BLEU & ROUGE (content overlap with reference feedback).  
- BERTScore or embedding similarity for semantic coverage.  
- Human quality ratings (1–5) on correctness, specificity, tone, rubric alignment.  

**Goal:** Feedback acceptable to instructors with minimal/no edits.

---

## Conclusion

Through prompt engineering techniques (zero-shot, few-shot, RAG, chain-of-thought, role-based prompts, and structured templates), we aim to tailor LLM performance for:  
- **AI-generated content detection** in student work.  
- **High-quality, rubric-aligned feedback generation**.  

Evaluation will combine automated metrics and human ratings to ensure effectiveness, fairness, and scalability.

