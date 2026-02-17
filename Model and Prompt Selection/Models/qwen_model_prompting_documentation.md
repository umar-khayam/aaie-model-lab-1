# Qwen/Qwen3-0.6B Model Prompting Documentation

## 1. Model Summary and Description

**Model:** Qwen/Qwen3-0.6B

Qwen3 is the latest generation of the Qwen series of large language models from Alibaba Cloud. Qwen3-0.6B is a 0.6 billion parameter causal language model.

**Architecture Details:**
*   **Type:** Causal Language Model
*   **Training Stage:** Pretraining & Post-training
*   **Parameters:** 0.6B (0.44B non-embedding)
*   **Layers:** 28
*   **Attention:** Group Query Attention (GQA) with 16 heads for query (Q) and 8 for key/value (KV).
*   **Context Length:** 32,768 tokens

**Key Features:**
*   **Dual Modes:** Uniquely supports seamless switching between a "thinking mode" for complex tasks (reasoning, math, coding) and a "non-thinking mode" for efficient, general-purpose dialogue.
*   **Enhanced Reasoning:** Significantly improved capabilities in mathematics, code generation, and commonsense logical reasoning.
*   **Agent Capabilities:** Expertise in integrating with external tools for complex agent-based tasks.
*   **Multilingual Support:** Supports over 100 languages and dialects.

## 2. Model Suitability on Feedback AI and Detection AI

Please refer to `prompt_pipeline_output.md` file, on which this model's suitability for Feedback AI and Detection AI tasks is based. This used a baseline prompt and small dataset provided by the Data team. Refer to the `Training Data` folder.

### Detection AI

The model's performance on the AI detection task is low. The task is to classify a given text as "Human", "AI", or "Hybrid". Out of 30 submissions across five different domains, the model only correctly classified 9 of them, resulting in an accuracy of 30%.

The model misclassifies AI-generated and Hybrid content as Human-written. This suggests that the model, in its current state, is not well-suited for reliably detecting AI-generated content. It may lack the nuanced understanding of the subtle differences between human and AI writing styles provided in the dataset, may require further prompting techniques or specific fine-tuning for this purpose.

### Feedback AI

For the Feedback AI task, the model is asked to provide a summary and feedback on a student's submission based on a rubric. A review of the `prompt_pipeline_output.md` file shows that the model can generate structured and relevant feedback.

The model's "Thinking" process shows that it can break down the task, analyse the submission against the rubric criteria, and formulate constructive feedback which is impressive for a model of this size. However, the quality and accuracy of the feedback would need to be evaluated by a university assessor to determine its true effectiveness.

**Hypothesis:** The Qwen3-0.6B model shows more promise for the Feedback AI task, where it can leverage its language generation capabilities to produce structured text. For the Detection AI task, significant fine-tuning on a specialised dataset would be required to improve its performance. 

## 3. Evaluation Result

### AI Detection Task Evaluation

| Domain | Total Submissions | Correct | Incorrect | Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| Accounting | 6 | 1 | 5 | 16.7% |
| Engineering | 6 | 2 | 4 | 33.3% |
| IT | 6 | 1 | 5 | 16.7% |
| Psychology | 6 | 2 | 4 | 33.3% |
| Teaching | 6 | 3 | 3 | 50.0% |
| **Total** | **30** | **9** | **21** | **30.0%** |



## 4. Analysis of Results

### Strengths and Weaknesses of the Model

#### Detection AI

*   **Weakness:** The model's primary weakness is its low accuracy (30%) and its strong bias toward classifying text as "Human". It fails to identify the nuances of AI-generated or hybrid content given in the dataset, often mislabeling them as purely human-written. This suggests a significant limitation in its ability to perform fine-grained text classification for AI detection, but is not uncommon for a model of its size.
*   **Strength:** The model shows some capability in correctly identifying text that is genuinely human-written. However, this appears to be more of a side effect of its bias towards the "Human" label rather than a reliable strength.

#### Feedback AI

*   **Strength:** The model excels at following structured prompts. As seen in the "Feedback Thinking" sections, it can systematically break down a student's submission, compare it against a given rubric, and generate well-organised, coherent feedback. Its ability to produce structured text in a specified format is a significant strength.
*   **Weakness:** The feedback, while structured, is often generic and lacks depth. The improvement tips are typically high-level (e.g., "add more examples") and not highly actionable. The model's analysis can be superficial, summarising the student's work without providing deeper critical insights.

### Explanation for Model Performance (Prompt vs. Capability)

The observed results can be attributed to a combination of the model's inherent capabilities, the models comparative small size and the nature of the prompts.

*   **Detection AI Performance:** Qwen3-0.6B, being a smaller model, may lack the sophisticated pattern recognition required to distinguish between human and AI writing styles. This is a complex task that even larger models struggle with. The model's internal bias towards "Human" classification is a significant capability flaw that a simple prompt cannot easily overcome. Given few shot prompting examples, its performance may improve.

*   **Feedback AI Performance:** The success in this area is due to both the prompt and the model's capability. The model's inherent strength in language generation and instruction-following allows it to create structured output. This is amplified by a well-defined prompt, that provides the context, which likely guides the model through the "thinking" process (analysing against a rubric). The model is capable of generating relevant text, and the prompt provides the necessary context for it to do so effectively for this task.

## 5. Summary

Based on this evaluation, the Qwen3-0.6B model is not suited for the Detection AI task in its current state. The accuracy is low for practical application, but scaling to larger Qwen3 models in the series is a viable option which would require little effort in code changes, along with access to GPU resources.

The model, however, shows significant promise for the Feedback AI task. With its ability to follow complex instructions and generate structured, relevant feedback, it could be a valuable tool. Further work would be needed to refine the prompts to elicit more specific and actionable feedback, and human oversight would be essential to ensure the quality and accuracy of its evaluations.




