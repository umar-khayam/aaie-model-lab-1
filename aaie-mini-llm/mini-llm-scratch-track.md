# Mini LLM: Scratch-trained Track 

*Trimester 3, 2025*

Planner task: [Link to MS Planner](https://planner.cloud.microsoft/webui/v1/plan/uYcXdi9j10q2XjnDautR7MgAFL1s/view/board/task/FjlICHKHckis44jChL9c7MgAG1sL?tid=d02378ec-1688-46d5-8540-1c28b5f470f6).  

**Project Leads:** Thai Ha NGUYEN, David Tenni, Matthew O’Donnell.  
**Document contribution:** Thai Ha NGUYEN.

## Epic 0 — Project Setup & Alignment (Done)

**Goal:** Ensure everyone builds toward the same technical target.

* **T0.1 Define Mini-LLM scope & success criteria**

  * Finalise parameter budget (e.g. <100M)
  * Define supported tasks (text generation, rubric alignment, JSON output)
  * Decide zero-shot vs fine-tuned expectations

* **T0.2 Repo & workflow setup**

  * Repo structure (`data/`, `model/`, `train/`, `eval/`, `configs/`)
  * Branching strategy + PR template

* **T0.3 Environment reproducibility**

  * `requirements.txt` / `environment.yml`
  * CPU vs GPU vs Apple MPS compatibility

## Epic 1 — Data Pipeline

**Goal:** Reliable, clean, multi-dataset input for training.

* **T1.1 Dataset selection & justification**

  * [WikiText-2](https://huggingface.co/datasets/mindchain/wikitext2) (language modelling)
  * [TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories) (coherence & simplicity)
  * [TechNews](https://huggingface.co/datasets/vencortex/TechNews) (domain-specific Technology)

* **T1.2 Unified dataset schema**

  * Convert all datasets → common `(input_ids, attention_mask, labels)`
  * Train/val/test split strategy

* **T1.3 Tokenisation strategy**

  * Choose tokenizer (BPE / WordPiece / SentencePiece)
  * Vocabulary size trade-off

* **T1.4 Data quality checks**

  * Length distribution
  * OOV rate
  * Duplicate detection


## Epic 2 — Model Architecture

**Goal:** Build a **from-scratch transformer** sized for fast iteration.

* **T2.1 Base transformer design**

  * Decoder-only architecture
  * Layers, heads, hidden size defined
* **T2.2 Embeddings & positional encoding**

  * Token embeddings
  * Learned vs sinusoidal positions
* **T2.3 Output head**

  * LM head tied vs untied embeddings
* **T2.4 Parameter budget validation**

  * Verify total params < target threshold


## Epic 3 — Training Loop

**Goal:** Stable, debuggable training on limited compute.

* **T3.1 Training loop implementation**

  * Teacher forcing
  * Cross-entropy loss

* **T3.2 Optimisation setup**

  * AdamW
  * Learning-rate schedule (cosine / linear warmup)

* **T3.3 Memory & speed optimisations**

  * Gradient accumulation
  * Mixed precision (if GPU)

* **T3.4 Checkpointing**

  * Save best / last
  * Resume training support


## Epic 4 — Evaluation & Metrics

**Goal:** Prove the Mini-LLM is **useful**, not just trainable.

* **T4.1 Perplexity evaluation**

  * Validation perplexity tracking

* **T4.2 Task-level qualitative eval**

  * Prompt → response sanity checks

* **T4.3 Structured output testing**

  * JSON schema adherence
  * Deterministic decoding settings

* **T4.4 Comparison baseline**

  * Compare vs zero-shot small open model (e.g. 1B–3B reference)

## Epic 5 — Inference & Deployment Readiness

**Goal:** Make the model usable by other streams.

* **T5.1 Inference API**

  * Prompt → text
  * Prompt → JSON

* **T5.2 Decoding strategies**

  * Greedy
  * Top-k / top-p

* **T5.3 Latency benchmarking**

  * CPU vs GPU inference time

## Epic 6 — Extensibility (Future-Proofing)

**Goal:** Keep the Mini-LLM relevant beyond this sprint.

* **T6.1 Fine-tuning hooks**

  * LoRA / adapter-ready design

* **T6.2 RAG compatibility**

  * External context injection

* **T6.3 Action-space or tool-use hooks**

  * JSON-first outputs for agents

* **T6.4 Multi-language readiness**

  * Tokeniser & data assumptions documented


---

## 📁 Mini-LLM Repository Structure

```
mini-llm/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── environment.yml
│
├── configs/
│   ├── model.yaml              # model size, layers, heads
│   ├── training.yaml           # lr, batch size, epochs
│   ├── tokenizer.yaml          # vocab size, type
│   └── inference.yaml          # decoding params
│
├── data/
│   ├── raw/
│   │   ├── wikitext/
│   │   ├── tinystories/
│   │   └── domain_edtech/
│   │
│   ├── processed/
│   │   ├── train.pt
│   │   ├── val.pt
│   │   └── test.pt
│   │
│   ├── tokenized/
│   │   └── tokenizer.model
│   │
│   └── data_loader.py
│
├── tokenizer/
│   ├── build_tokenizer.py
│   ├── tokenizer_utils.py
│   └── README.md
│
├── model/
│   ├── __init__.py
│   ├── transformer.py          # decoder-only transformer
│   ├── attention.py
│   ├── embeddings.py
│   ├── lm_head.py
│   └── model_utils.py
│
├── training/
│   ├── train.py
│   ├── optimizer.py
│   ├── scheduler.py
│   ├── loss.py
│   ├── checkpoint.py
│   └── README.md
│
├── evaluation/
│   ├── eval_perplexity.py
│   ├── eval_generation.py
│   ├── eval_json_schema.py
│   ├── qualitative_prompts.json
│   └── README.md
│
├── inference/
│   ├── generate.py
│   ├── decode.py
│   ├── api.py                  # optional (FastAPI/CLI)
│   └── README.md
│
├── experiments/
│   ├── exp_001_baseline/
│   │   ├── config.yaml
│   │   └── results.json
│   └── exp_002_lr_sweep/
│
├── scripts/
│   ├── preprocess_data.py
│   ├── train_small.sh
│   ├── eval_model.sh
│   └── sanity_check.py
│
├── checkpoints/
│   ├── best/
│   └── latest/
│
├── logs/
│   ├── train.log
│   └── eval.log
│
├── tests/
│   ├── test_model_shapes.py
│   ├── test_tokenizer.py
│   └── test_generation.py
│
└── docs/
    ├── architecture.md
    ├── training_strategy.md
    ├── evaluation_protocol.md
    └── limitations.md
```

---

## Why this structure is strong (important)

###  Parallel team work

* Data, model, training, eval → **independent folders**
* Minimal merge conflicts

### Research → engineering bridge

* `experiments/` keeps results reproducible
* `configs/` allows fast ablation studies


### Future-ready

* LoRA / adapters → plug into `model/`
* RAG → extend `inference/`
* Agents / JSON output → `eval_json_schema.py`
