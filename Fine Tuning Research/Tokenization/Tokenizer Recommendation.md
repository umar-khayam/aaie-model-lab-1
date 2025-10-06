# Comparative Analysis of Tokenization Methods

**Author:** Arnav Ahuja (223271095)  
**Date:** 27 July 2025  

---

## Introduction

Tokenization lies at the core of modern language modelling and impacts both accuracy and generalization in tasks such as feedback generation and AI-written content detection. For the Artificial Assessment Intelligence for Educators (AAIE) project, tokenization must account for:

- Complex academic vocabulary
- Mathematical expressions (e.g., $\int_a^b f(x)dx$)
- Programming/code snippets
- Multilingual and citation-heavy content
- Rubric-structured feedback

This analysis compares six tokenization strategies:

1. Character-level BPE  
2. Byte-level BPE  
3. SentencePiece (BPE)  
4. SentencePiece (Unigram LM)  
5. Unigram (Standalone)  
6. WordPiece  

---

## Tokenizer Overviews

### Character-level BPE
- Operates on visible characters.  
- Common in early NLP systems.  
- Struggles with symbols and multilingual data.  

### Byte-level BPE
- Operates on raw UTF-8 bytes.  
- Introduced in GPT-2.  
- Supports any script or symbol, enabling complete reversibility.  
- Tokens may be unreadable to humans.  

### SentencePiece (BPE)
- Implements classic BPE within the SentencePiece framework.  
- Learns merges on raw data without assuming whitespace or language structure.  

### SentencePiece (Unigram LM)
- Uses Expectation-Maximization to select optimal subword vocabularies.  
- Allows stochastic subword splits and dropout regularization.  

### Unigram LM (Standalone)
- Similar to SPM Unigram but trained directly using other libraries or from scratch.  
- Offers flexibility and probabilistic robustness.  

### WordPiece
- Greedy, frequency-based merging.  
- Used in BERT and related models.  
- Encodes unknown words as subword sequences.  

---

## Comparative Table

| Feature                  | Char BPE  | Byte BPE | SPM BPE | SPM Unigram | Standalone Unigram | WordPiece |
|--------------------------|-----------|----------|---------|-------------|--------------------|-----------|
| Input Granularity        | Characters| Bytes    | Characters | Characters | Characters        | Characters|
| Logic                    | Greedy    | Greedy   | Greedy  | Probabilistic | Probabilistic    | Greedy    |
| Multilingual Support     | Low       | High     | High    | High         | High              | Medium    |
| Math/Code Support        | Poor      | High     | High    | High         | High              | Medium    |
| Citation/Brackets        | Poor      | Medium   | High    | High         | High              | Medium    |
| Reversible               | No        | Yes      | Yes     | Yes          | Yes               | No        |
| Subword Flexibility      | Low       | Low      | Medium  | High         | High              | Low       |
| Dropout/Regularization   | No        | No       | No      | Yes          | Yes               | No        |
| Readability              | High      | Low      | Medium  | Medium       | Medium            | Medium    |
| Integration Ease         | Low       | High     | High    | High         | Medium            | High      |
| Used In                  | Char-RNNs | GPT-2    | mT5, T5 | mT5, T5      | Custom LLMs       | BERT      |

---

| Feature                                | Char BPE   | Byte BPE | SPM BPE | SPM Unigram | Standalone Unigram | WordPiece |
|----------------------------------------|------------|----------|---------|-------------|--------------------|-----------|
| Handles academic terms                 | Inadequate | Adequate | Adequate| Ideal       | Ideal              | Adequate  |
| Mathematical fidelity                  | Inadequate | Ideal    | Ideal   | Ideal       | Ideal              | Adequate  |
| Code/Pseudocode support                 | Inadequate | Ideal    | Ideal   | Ideal       | Ideal              | Adequate  |
| Rubric retention (brackets, bullets)   | Inadequate | Adequate | Ideal   | Ideal       | Ideal              | Adequate  |
| Citation structure                      | Inadequate | Adequate | Ideal   | Ideal       | Ideal              | Adequate  |
| Works on multilingual inputs           | Inadequate | Ideal    | Ideal   | Ideal       | Ideal              | Adequate  |

---

## Suitability for AAIE

### Implementation Notes

**Preprocessing:**
- Unicode NFKC normalization  
- Lowercasing with exceptions for code/math  
- Preserving tokens like `[1]`, `\frac`, `\int`  

**Evaluation Metrics:**
- Subword count per sentence  
- Unknown token rate < 0.5%  
- Code/maths formatting breakage  
- Rubric bullet preservation  

---

## Final Recommendations

**Short-Term:**

- **Primary Tokenizer:** SentencePiece (Unigram LM)  
  - Easy to integrate, highly effective across all AAIE content types.  
  - Flexible subword splits improve generation quality.  

- **Secondary Tokenizer:** Byte-level BPE (GPT2Tokenizer)  
  - Compatible with NanoGPT; high robustness for code/math.  

- **Baseline for Comparison:** WordPiece  

---

**Long-Term (Custom LLM Stack):**
- **Preferred Tokenizer:** Standalone BPE or Unigram (Custom-Trained)  
  - Enables full control over vocabulary, merging, and domain adaptation.  
  - Allows AAIE to fine-tune for rubric patterns, formulas, multilingual feedback.  
