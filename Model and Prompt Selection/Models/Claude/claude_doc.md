# Evaluation of Claude-3.5 Haiku (via OpenRouter)

## Model Description
Claude-3.5 Haiku is part of Anthropic’s Claude 3.5 family of large language models, designed to balance efficiency with quality. Haiku is the fastest and most cost-effective variant compared to Claude-3.5 Sonnet or Claude-3.5 Opus, and is particularly suited to high-volume workloads such as classification, summarization, and structured text generation.  
Technically, Claude models are trained using Anthropic’s constitutional AI approach, emphasizing alignment, safety, and transparent reasoning. Claude-3.5 Haiku supports token lengths up to ~200K, with improved handling of structured prompts, making it theoretically well-suited for rubric-based evaluation and feedback generation.  
Anthropic itself requires a $5 paid credit minimum to access the API, which was not suitable under our project constraints. OpenRouter was selected as the only available free option to trial Claude models, as no other direct or academic access pathways were free at the time. This made OpenRouter appear to be the best possible choice for testing Claude-3.5 Haiku within AAIE.

## Application to the AAIE Project
The model was evaluated for two tasks using our base prompts and base dataset:

1. **Academic Integrity Detection (Classification Task)**  
   - **Aim:** Classify student submissions as Human, AI, or Hybrid.  
   - **Basis:** Discourse features such as subjectivity, coherence, repetitiveness, and style consistency.  
   - **Method:** Applied the base detection prompt with few-shot examples from the dataset.  

2. **Rubric-Aligned Feedback Generation (Text Generation Task)**  
   - **Aim:** Generate criterion-by-criterion feedback aligned to the rubric.  
   - **Input:** Assignment prompt, rubric (converted to plain text), and student submission.  
   - **Expected Output:** Overall summary, criterion ratings with evidence, improvement suggestions, and overall rating.  

## Experimental Setup
- **Base Prompt:** Carefully designed system and user prompts were applied consistently across models to ensure fair comparison.  
- **Base Data:** Standardized datasets (teaching, psychology, IT, engineering, accounting) containing assignment prompts, rubrics, and student submissions were used.  
- **Pipeline:**  
  - Detection prompts → Claude classification output.  
  - Feedback prompts → Claude text generation output.  
  - Human rating (Khushi’s rubric) and Generative AI rating (Wang & Van’s prompt) were intended for evaluation of outputs.  

## Results
- **Execution Failure:** The evaluation could not be completed due to credit limitations on OpenRouter. The API returned a 402 Payment Required error, blocking inference runs for both detection and feedback tasks.  
- **Detection Task:** No predictions generated, therefore no correct classification count could be recorded.  
- **Feedback Task:** No rubric-aligned feedback produced.  
- **Human Rating:** Not applicable.  
- **Generative AI Rating:** Not applicable.  

## Analysis & Limitations
- **Technical Limitation:** The model requires sufficient credits to process the large token context (our prompts requested up to 1,600 tokens). The free allocation was insufficient, preventing results.  
- **Classification Potential:** Based on prior Claude benchmarks, Haiku is expected to handle nuanced classification (Human vs AI vs Hybrid) effectively because of its training on discourse features and stylistic detection.  
- **Text Generation Potential:** Claude models are generally strong at producing structured outputs aligned to rubrics. Haiku, while smaller, could have generated useful criterion-by-criterion feedback efficiently.  
- **Mismatch with Project Criteria:** Since our project requires models that are free or reproducible within academic constraints, Claude-3.5 Haiku cannot be adopted.  

## Recommendation
While Claude-3.5 Haiku is theoretically capable of both classification and structured feedback generation, its reliance on paid credits and inability to run on free tiers disqualify it for AAIE use. With no usable outputs obtained under our base prompts and base dataset, the evaluation criteria fail.  
Even if implementation had been possible, OpenRouter would not have been ideal for AAIE. In real-world deployment our data would be smaller and simpler than the large prompts we tested, but the dependency on credit-based access and the lack of a reliable free pathway mean Claude-3.5 Haiku is not a sustainable or suitable choice for the project.  

**Decision: Not Selected for AAIE.**
