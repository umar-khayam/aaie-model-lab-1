# Mini LLM: Training Loop

*Trimester 3, 2025*

Planner task: [Link to MS Planner](https://planner.cloud.microsoft/webui/v1/plan/uYcXdi9j10q2XjnDautR7MgAFL1s/view/board/task/f6Y-HqVXYkKmr0l4RYQU6sgAMQ11?tid=d02378ec-1688-46d5-8540-1c28b5f470f6).  

**Project Leads:** Thai Ha NGUYEN, David Tenni, Matthew O’Donnell.  
**Document contribution:** Thai Ha NGUYEN.

---

# Epic 3 — Training Loop

## Overview

**Epic 3** implements a **robust, scalable training loop** for Mini-LLM, incorporating modern optimisation techniques to ensure stability, efficiency, and reproducibility.

This model was trained on **Nvidia RTX 4000 Ada 20GB VRAM GDDR6**

The training loop supports:

* Mixed-precision training
* Gradient accumulation
* Learning rate warm-up and decay
* Periodic evaluation and checkpointing

#### How to run

```bash
python -m training.train
```

---

## Training Configuration

Defined in `configs/training.yaml`.

### Core Training Settings

```yaml
training:
  seed: 42
  device: "auto"
  epochs: 10
  batch_size: 12
  grad_accum_steps: 8
  log_every: 50
  eval_every: 500
  save_every: 500
```

**Effective batch size:**

```
12 × 8 = 96 sequences per update
```

---

## Optimisation Strategy

### Optimizer — AdamW

```yaml
optimizer:
  name: "adamw"
  lr: 3.0e-4
  weight_decay: 0.1
  betas: [0.9, 0.95]
  eps: 1.0e-8
  grad_clip_norm: 1.0
```

**Rationale:**

* AdamW decouples weight decay from gradient updates
* Commonly used in modern Transformer training
* Gradient clipping prevents exploding gradients

---

### Learning Rate Scheduler — Cosine Decay

```yaml
scheduler:
  name: "cosine"
  warmup_steps: 500
  min_lr: 1.0e-5
```

**Schedule:**

1. Linear warm-up for 500 steps
2. Cosine decay to minimum learning rate

This improves early training stability and final convergence.

---

## Mixed Precision Training (AMP)

```yaml
amp:
  enabled: true
```

* Uses automatic mixed precision (FP16)
* Reduces GPU memory usage
* Improves training throughput
* Maintains numerical stability via gradient scaling

---

## Data Flow

Training data is loaded from preprocessed binary files:

```yaml
data:
  train_pt: "data/processed/train.pt"
  val_pt: "data/processed/val.pt"
  block_size: 384
```

* Inputs and labels are shifted for causal prediction
* Padding and truncation handled consistently
* Validation uses identical preprocessing

---

## Checkpointing Strategy

```yaml
checkpoint:
  out_dir: "checkpoints"
  keep_last_n: 2
```

Saved checkpoints include:

* Model state
* Optimizer state
* Scheduler state
* Training step metadata

The best checkpoint is selected based on **validation loss**.

---

## Logging and Evaluation

* Training loss logged every 50 steps
* Validation loss and perplexity evaluated every 500 steps
* Best model automatically saved
* Supports resuming from checkpoints

---

## Summary of Epic 3 Deliverables

| Component             | Status |
| --------------------- | ------ |
| Stable training loop  | ✅      |
| Gradient accumulation | ✅      |
| Mixed precision       | ✅      |
| AdamW optimisation    | ✅      |
| Cosine LR schedule    | ✅      |
| Periodic evaluation   | ✅      |
| Robust checkpointing  | ✅      |
