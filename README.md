# AAIE Model Lab – LLM Prototyping & Training

This repository hosts the **LLM Prototyping & Training pillar** of the Artificial Assessment Intelligence for Educators (AAIE) project.  
It contains experiments, evaluation pipelines, prompt-engineering workflows, and research notes to support **AI Detection** and **Feedback Generation** tasks.


## Overview

The **LLM Prototyping & Training team** is responsible for developing and evaluating Large Language Models (LLMs) to enhance educator-focused tools for assessment and feedback.  
Our work this trimester prioritises **prompt engineering** and **evaluation** to deliver reliable, reproducible results under resource constraints.  

The long-term vision is to build specialized, fine-tuned models integrated with Deakin’s LMS platforms (CloudDeakin, OnTrack), providing scalable and explainable AI assistance in academic contexts.


## Objectives (as of T2 2025)

- Experiment with **prompt engineering techniques**: Zero-Shot, Few-Shot, Chain-of-Thought (CoT), Role-based, and Structured prompting.  
- Benchmark **multiple models** (open-source HuggingFace + commercial APIs) with human and GenAI ratings.  
- Develop **evaluation pipelines** for both classification (AI/Human/Hybrid detection) and generation (feedback alignment).  
- Deliver a **functional API package** to the Product Engineering team for integration.  
- Document findings to prepare a pathway for future **fine-tuning**, **revision-chain support**, and **scratch-built models**.


## Repository Structure
``` bash
aaie-model-lab/
├── API Integration/                # API-related documentation and implementation
│
├── Deprecated/                     # Archived or replaced code, experiments, and notes
│
├── Evaluation/                     # Evaluation pipelines, metrics, and analysis
│   ├── AI Detection/                # Experiments and scripts for AI/Human/Hybrid classification
│   └── Feedback Generation/         # Experiments and scripts for rubric-based feedback evaluation
│
├── Experimental Plan/              # Prompt engineering plans, hypotheses, and experiment design
│
├── Fine Tuning Research/           # Research and notes for model development and tuning
│   ├── Evaluation/                  # Evaluation methods and metrics for fine-tuned models
│   ├── Models/                      # Model-specific research (TinyLlama, Qwen, NanoGPT, etc.)
│   ├── Solution Architecture/       # System and workflow architecture diagrams/docs
│   └── Tokenization/                # Research on tokenization methods (BPE, SentencePiece, etc.)
│
├── Infrastructure and Development/ # Infrastructure notes, environment setup, and dev workflows
│
├── Model and Prompt Selection/     # Model and prompt experimentation workflows
│   ├── Models/                      # Open-source and commercial LLM comparisons
│   ├── PromptVariants/              # Variants of prompts tested during optimization
│   └── PromptTechniques/            # Zero-shot, Few-shot, CoT, role-based, structured prompts
│
├── Upskilling Docs/                # Learning resources, guides, and onboarding docs
│
├── .gitignore
└── README.md                       # You are here
```

## Purpose of Key Folders

- **Evaluation** → Scripts and notebooks for testing both AI Detection and Feedback Generation.  
- **Experimental Plan** → High-level design docs, hypotheses, and sprint planning for experiments.  
- **Fine Tuning Research** → Research groundwork for future fine-tuned and custom model training.  
- **Model and Prompt Selection** → Current trimester’s focus: model benchmarking, prompting techniques, and optimization.  
- **API Integration** → Bridges the evaluated models with product engineering for deployment.  
- **Infrastructure and Development** → Documentation on environments, GPU/Cloud usage (Kaggle, Azure, GCP), and CI/CD pipelines.  
- **Upskilling Docs** → Tutorials, learning resources, and onboarding material for team members.  
- **Deprecated** → Archived experiments, old approaches, or superseded scripts kept for reference.  


## Workflow

### Phase 1 – Model Selection  
- Compare HuggingFace and commercial LLMs on AAIE tasks.  
- Evaluate with human + GenAI ratings.  

### Phase 2 – Prompting Technique Selection  
- Experiment with Zero-shot, Few-shot, Chain-of-Thought, Role-based prompts.  
- Select based on formal metrics (Accuracy, F1, AUC, BLEU, ROUGE).  

### Phase 3 – Prompt Optimization  
- Refine best prompts with multiple variants.  
- Finalize configurations for integration.  


## Contributions

### Markdown Documentation (`.md`)  
- Setup or instruction guides  
- Experiment or evaluation notes  
- Research write-ups (fine-tuning methods, new approaches)  
- Upskilling or learning resources  
- Contributor or reviewer guidelines  

### Python Scripts (`.py`)  
- Model training or fine-tuning scripts  
- Evaluation utilities (metrics, logging, reproducibility checks)  
- Experiment automation tools  

### Jupyter Notebooks (`.ipynb`)  
- Experimental runs and results  
- Model evaluation (metrics, comparisons, error analysis)  
- Visualizations of performance or datasets  
- Prototyping new approaches  

### Research Plans / Reports  
- Experimental plans with hypotheses and metrics  
- Fine-tuning research notes  
- Post-experiment analysis 

**Contribution workflow**: fork → branch → PR → peer + senior review (2 peers, 1 senior).  



## Ethics & Safety

- Evaluation includes **bias checks, reproducibility measures, and transparency features**.  
- Outputs are **educator-first**, ensuring explainability, tutor-in-the-loop workflows, and integration-readiness.  



## Tools & Platforms

- **Models**: HuggingFace (TinyLlama, Qwen, NanoGPT, Mistral, Gemma, Phi-2), Commercial APIs (OpenAI GPT, Claude, Gemini).  
- **Evaluation**: Accuracy, F1, AUC, BLEU, ROUGE, recall, confusion matrices.  
- **Infrastructure**: Kaggle GPUs, Azure AI, future GCP support.  
- **Stack**: Python, PyTorch, Jupyter, GitHub Actions for CI/CD.  


## Maintainers

This repository is maintained by the **LLM Prototyping & Training team** under the School of IT, Deakin University.  
The project mentor owns the admin access to this project. 

##### Credits: Qasim Nasir, Arnav Ahuja

