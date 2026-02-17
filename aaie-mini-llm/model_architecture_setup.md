# Mini LLM: Model Architecture setup

*Trimester 3, 2025*

Planner task: [Link to MS Planner](https://planner.cloud.microsoft/webui/v1/plan/uYcXdi9j10q2XjnDautR7MgAFL1s/view/board/task/f6Y-HqVXYkKmr0l4RYQU6sgAMQ11?tid=d02378ec-1688-46d5-8540-1c28b5f470f6).  

**Project Leads:** Thai Ha NGUYEN, David Tenni, Matthew O’Donnell.  
**Document contribution:** Thai Ha NGUYEN.

---

# Epic 2 — Model Architecture

## Overview

**Epic 2** focuses on designing and implementing a **from-scratch Transformer language model** optimised for fast experimentation while remaining expressive enough to model long-range dependencies.

The architecture follows a **decoder-only Transformer (GPT-style)** with modern best practices such as **Rotary Positional Embeddings (RoPE)** and **weight tying**.

---

## Design Goals

* Decoder-only architecture for causal language modelling
* Scalable depth and width under a controlled parameter budget
* Support long context lengths (up to 384 tokens)
* Efficient training and inference
* Compatibility with GPT-style tokenizers

---

## Model Configuration

Defined in `configs/model.yaml`:

```yaml
model:
  name: "mini-gpt"
  vocab_size: 50257
  max_seq_len: 384
  d_model: 1024
  n_head: 16
  n_layer: 24
  d_ff: 4096
  dropout: 0.1
  tie_weights: true
```

---

## Architecture Components

### 1. Token Embeddings

* Vocabulary size: **50,257** (GPT-style tokenizer)
* Embedding dimension: **1024**
* Shared across input and output layers (weight tying)

**Justification:**
Weight tying reduces parameter count and improves generalisation in language models.

---

### 2. Positional Encoding (RoPE)

The model uses **Rotary Positional Embeddings (RoPE)** applied directly to query and key vectors inside the attention mechanism.

**Advantages of RoPE:**

* Better extrapolation to longer sequences
* Preserves relative positional information
* Lower memory overhead than learned embeddings

---

### 3. Transformer Blocks

Each block consists of:

1. Pre-LayerNorm
2. Multi-Head Self-Attention (16 heads)
3. Residual connection
4. Feed-Forward Network (MLP)
5. Residual connection

**Block parameters:**

* Hidden size (`d_model`): 1024
* Feed-forward size (`d_ff`): 4096
* Number of layers: 24
* Dropout: 0.1

---

### 4. Output Head

* Linear projection from hidden states to vocabulary size
* Output weights tied to token embedding matrix

**Training objective:**
Causal language modelling with next-token prediction.

---

## Parameter Budget Validation

The chosen configuration results in a **mid-scale model** that:

* Is large enough to learn meaningful structure
* Fits on consumer GPUs with gradient accumulation
* Trains within practical time limits for a capstone project

This balance enables rapid iteration while preserving architectural realism.

---

## Summary of Epic 2 Deliverables

| Component                   | Status |
| --------------------------- | ------ |
| Decoder-only Transformer    | ✅      |
| RoPE positional encoding    | ✅      |
| Multi-head self-attention   | ✅      |
| Deep MLP blocks             | ✅      |
| Weight tying                | ✅      |
| Parameter budget validation | ✅      |
