# Fallback Approach for Future Work

## Description

During Phase 1 model selection, we identified the need for fallback models to ensure resilience and continuity in the AAIE project. While Gemini 1.5 Flash has been selected as the **primary model** for both detection and feedback tasks in Phase 2, we also planned a fallback approach that can be adopted in later phases once evaluation pipelines and infrastructure are stable.

### Quick Comparison of Primary vs. Fallback Models

| Model                | Role                        | Accuracy / Quality                      | Latency (avg) | Notes                                         |
| -------------------- | --------------------------- | --------------------------------------- | ------------- | --------------------------------------------- |
| **Gemini 1.5 Flash** | Primary (Detect + Feedback) | Detection: \~63% <br> Feedback: 4.4/5 | Fast          | Free tier, reliable, classroom-ready          |
| **DeepSeek R1**      | Fallback (Detection)        | Detection: \~70%  <br> Feedback: 3.5/5                      | \~34s         | Structured rationales, fine-tuning ready      |
| **Mistral 7B**       | Fallback (Feedback)         | Feedback: 2.6–3.0/5                     | N/A (slow)    | Strict prompting/QC needed, fine-tuning ready |



### Fallback Models

* **DeepSeek R1 for Classification (AI Detection):**

  * Detection accuracy of \~70%, with a tendency to lean on ambiguous cases.
  * While slower (34s avg latency), it provides structured rationales and can serve as a reliable *second-opinion* model in an ensemble or moderator workflow.
  * As an open-source model, it is *fine-tuning ready* for domain-specific classification challenges (e.g., handling hybrid submissions in IT or Psychology).
  * [DeepSeek-R1 on OpenRouter (free inference via API)](https://openrouter.ai/deepseek/deepseek-r1:free/api)
  * [DeepSeek-R1 on HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-R1)

* **Mistral 7B Instruct v0.3 for Feedback Generation:**

  * Feedback quality rated lower than commercial models (2.6–3.0/5), but with strict prompting and QC, it can deliver rubric-aligned responses.
  * Useful as a *batch fallback* for feedback generation in scenarios where the primary model is unavailable or where vendor diversification is required.
  * Being open-source, it can be fine-tuned for improved rubric alignment and tone consistency across disciplines.
  * [Mistral 7B on OpenRouter (free inference via API)](https://openrouter.ai/mistralai/mistral-7b-instruct:free)
  * [Mistral 7B on HuggingFace](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)

### Benefits of the Fallback Approach

* **Resilience:** Ensures the system can continue functioning even if the primary vendor (Gemini Flash) becomes unavailable or rate-limited.
* **Cost Flexibility:** Open-source models (DeepSeek, Mistral) avoid vendor lock-in and provide long-term options for self-hosted, GPU-backed deployment.
* **Auditable:** Additional perspectives (especially from DeepSeek reasoning) enhance classification transparency and can support moderation workflows.
* **Future Scalability:** Establishes the groundwork for ensemble routing and hybrid deployments, increasing robustness and domain adaptability.


### Usage of Fallback models:

* **Ensemble Routing:** Router calls both primary and fallback models; disagreement or low-confidence results trigger escalation to human review.
* **Tie-Break Logic:** In detection, DeepSeek could act as a secondary “vote” in hybrid/ambiguous cases.
* **Batch Feedback:** Mistral could generate draft feedback overnight or for low-priority use cases where latency is less critical.

### Why We Couldn’t Implement This in This Trimester

* **Latency Constraints:** Both DeepSeek R1 and Mistral 7B exhibited slower inference times, making them unsuitable for real-time classroom feedback in the current MVP.
* **Infrastructure Readiness:** Self-hosting these models requires GPU infrastructure, orchestration, and autoscaling pools, which were not in scope for this trimester.
* **Engineering Complexity:** Introducing fallback routing early would add orchestration overhead (tie-break logic, model selection pipelines) that would slow down the MVP release.
* **Prioritisation:** The focus this trimester was delivering a simplified MVP using Gemini 1.5 Flash as the single model, enabling faster deployment and testing with educators.

### Milestones for Full Fallback Integration

* **GPU Access:** Secure additional GPUs (or cloud credits) for hosting DeepSeek and Mistral efficiently.
* **Latency Targets:** Reach sub-10s inference for fallback models to ensure project viability.
* **Cloud Platform:** Access to a shared Cloud Platform that would allow team to build and deploy services implementing fallback features. 

### Fallback Models summary

| Model        | Primary Role       | Strengths                              | Trade-offs               |
|--------------|--------------------|----------------------------------------|--------------------------|
| DeepSeek R1  | Detection (AI/Human/Hybrid) | Structured rationales, open-source, fine-tuning ready | Slow (~34s latency)      |
| Mistral 7B   | Feedback generation | Open-source, can be fine-tuned for rubric alignment | Lower feedback quality, QC required |


Reference: [Model and Prompt Selection/Models/Final Model Recommendation/Phase 1 Model Choice.md](https://github.com/InnovAIte-Deakin/aaie-model-lab/blob/24226a16917b8b9c25d826fedba6a16f8b7ecd4a/Model%20and%20Prompt%20Selection/Models/Final%20Model%20Recommendation/Phase%201%20Model%20Choice.md)
