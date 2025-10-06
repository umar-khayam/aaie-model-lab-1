# Tokenization Comparison – BPE vs SentencePiece

**Author:** Arnav Ahuja (223271095)  
**Date:** 27 July 2025  

---

## Introduction

The Artificial Assessment Intelligence for Educators (AAIE) project aims to build domain-specific MiniLLMs capable of providing context-aware academic feedback and AI-content detection. As part of this effort, selecting an appropriate tokenization strategy is critical to preserving the semantic and syntactic structure of student submissions, which may include:

- Multilingual phrases
- Mathematical formulas (e.g., $\int_a^b f(x)dx$)
- In-text citations (e.g., [1], (Smith, 2020))
- Pseudocode or programming snippets
- Rubric-styled lists and bullet structures

This document evaluates **Byte Pair Encoding (BPE)** and **SentencePiece (SPM)** tokenizers, alongside additional alternatives, using the criteria and constraints of the AAIE pipeline.

---

## Overview of Tokenization Methods

This section provides a deep comparative breakdown between **Character-level BPE**, **Byte-level BPE**, and **SentencePiece** tokenizers. While all of them are based on the subword principle, their design and behaviour differ significantly in how they handle structure, noise, multilingualism, and formatting — which are key considerations for the AAIE project's diverse input formats.

---

### Character-level vs Byte-level BPE

Character-level BPE starts from visible characters like `a`, `b`, `c`, etc. It was widely used in early models when dealing with mostly English datasets. However, it lacks the flexibility and robustness required for noisy, multilingual, or symbolic data.

Byte-level BPE, introduced in GPT-2, operates on raw UTF-8 bytes rather than Unicode characters. This enables it to represent any input — be it emoji, special symbols, or math equations — without relying on Unicode correctness or normalization.

| Feature                    | Character-level BPE | Byte-level BPE |
|----------------------------|---------------------|----------------|
| **Input unit**              | Visible characters  | UTF-8 bytes    |
| **Supports multilingual**   | Limited (ASCII)     | Full UTF-8     |
| **Handles LaTeX/math/code** | Often splits incorrectly | Preserves structure |
| **Tokenization reversibility** | Depends on corpus | Fully reversible |
| **Token set readability**   | Human-readable      | Mostly unreadable tokens |
| **Robustness to noise**     | Low                 | High           |
| **Used in**                 | Early LSTMs, char-RNNs | GPT-2, GPT-Neo, NanoGPT |

**Recommendation:** For AAIE’s structured academic inputs, Byte-level BPE is a significantly more robust choice compared to its character-level counterpart.

---

## SentencePiece (SPM)

**Core Logic:** SentencePiece is a data-driven tokenization framework developed by Google. Unlike traditional word-based tokenizers, SentencePiece treats the input as a raw stream of characters or bytes and learns how to segment it from scratch.

**Key Idea:** Instead of assuming spaces define word boundaries, it learns them statistically. This is crucial for handling multilingual, noisy, or code-heavy text that lacks clear natural language structure.

---

### SentencePiece Supports Two Backend Algorithms

1. **BPE-based SentencePiece**  
   Implements the standard BPE algorithm within the SentencePiece framework (`model_type=bpe`). This version benefits from SPM's ability to handle raw input but retains BPE's deterministic merging approach.

2. **Unigram Language Model (ULM)**  
   - Starts with a large vocabulary of substrings and uses Expectation-Maximization (EM) to prune it down.
   - Each tokenization is chosen to maximize the overall likelihood of the training data.
   - Unlike BPE, Unigram doesn't always return the same split for a word, introducing stochasticity and flexibility.

**Example:**

Input: `photosynthetically`  
- **SPM-BPE:** `["photo", "synthe", "tically"]`  
- **SPM-Unigram:** `["photosynthetic", "ally"]` or `["photo", "synthetic", "ally"]` (based on likelihood)

---

### Strengths

- Language-independent and whitespace-free
- Supports multilingual, noisy, and structured data
- Probabilistic modelling improves generalization (Unigram)
- Supports subword regularization and dropout

### Weaknesses

- Training can be computationally heavier than greedy BPE
- Needs custom preprocessing and tuning (e.g., character coverage, normalization mode)

**Convenience Factor:** For quick experimentation or integration into pipelines (HuggingFace, TinyLLaMA), SentencePiece is the most convenient choice. It offers fast training, strong baseline performance, and native compatibility with text generation tasks in academic and structured domains.

---

## Tokenizer Suitability for AAIE

**Input Characteristics:**
- Natural academic language: Long sentences, advanced vocabulary
- Citations: e.g., `[2]`, `(Johnson, 2023)`
- LaTeX-style math: e.g., `$\frac{a}{b}$`, `$x^2 + y^2$`
- Code snippets: Python, pseudocode, markdown syntax
- Rubric formats: `[ ]` Checkboxes, numbered steps
- Multilingual: Non-English or mixed language sentences

---

### Evaluation Table

| Feature                        | Byte BPE | Char BPE | SentencePiece (Unigram) |
|--------------------------------|----------|----------|-------------------------|
| Handles math notations         | High     | Low      | High                    |
| Preserves citation boundaries  | Medium   | Poor     | High                    |
| Works with multilingual input  | UTF-8    | ASCII    | High                    |
| Code compatibility (e.g., `\n`) | Good     | Unreliable | High                  |
| Whitespace-aware segmentation  | No       | No       | Yes                     |
| Sentence re-tokenization stability | High  | Low      | Medium                  |

---

## Implementation Pipeline

### Preprocessing
- Unicode normalization (NFKC)
- Removal of HTML tags
- Preserve math symbols and rubric brackets: `[]`, `{}`, `\frac{}`
- Lowercase except in code blocks or formulas

### Training Steps
For SentencePiece: *(replace `model_type='unigram'` with `bpe` for BPE-based tokenization)*

---

## Evaluation Metrics

| Metric                         | Purpose                                           |
|--------------------------------|---------------------------------------------------|
| Average subwords/token         | Measures over-segmentation                        |
| Token length entropy           | Measures diversity in tokenization                |
| Unknown token rate (%)         | Should be <0.5% for academic corpora              |
| Rubric structure accuracy      | Are bullets, brackets retained?                   |
| Math expression fidelity (%)   | % equations retained in logical units             |
| Code formatting breakage (%)   | Lower is better                                   |

---

## Recommendations

**Primary Tokenizer:** SentencePiece (Unigram)  
**Justification:**
- Manages a wide variety of content (math, code, citations)
- Flexible segmentation improves feedback fluency
- Language-independent and robust with domain-specific patterns

**Secondary:** Byte-level BPE (e.g., GPT2Tokenizer)  
**For:**
- NanoGPT-based pipelines where compatibility is a constraint
- Faster tokenization and inference for basic tasks

**Long-term Plan:**
- If AAIE builds a custom tokenizer from scratch, non-SentencePiece BPE offers fine-grained control and excellent performance.
- Until then, SentencePiece offers an ideal trade-off between ease of use, versatility, and accuracy.

---

## Future Considerations

- Implement token-level explainability using token attribution
- Evaluate sentence boundary robustness for longer essays
- Track alignment between tokenizer and generation quality (BLEU, F1)
- Consider vocab sharing across AI detection and feedback models for consistency

---

## References

1. Kudo, T. (2018). Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates. *arXiv preprint arXiv:1804.10959*.  
2. Sennrich, R., Haddow, B., & Birch, A. (2015). Neural Machine Translation of Rare Words with Subword Units.  
3. Radford, A. et al. (2019). Language Models are Unsupervised Multitask Learners. OpenAI.  
4. Devlin, J. et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.  
5. [SentencePiece GitHub](https://github.com/google/sentencepiece)  
6. [HuggingFace Tokenizers](https://huggingface.co/docs/tokenizers)  
7. AAIE Project Proposal (2025). Deakin University.
