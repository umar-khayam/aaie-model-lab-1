# Mini LLM: Dataset preparation and Tokenization 

*Trimester 3, 2025*

Planner task: [Link to MS Planner](https://planner.cloud.microsoft/webui/v1/plan/uYcXdi9j10q2XjnDautR7MgAFL1s/view/board/task/ggSmSvjIn02Th3LXps1Ru8gABQ7W?tid=d02378ec-1688-46d5-8540-1c28b5f470f6).  

**Project Leads:** Thai Ha NGUYEN, David Tenni, Matthew O’Donnell.  
**Document contribution:** Thai Ha NGUYEN.

---

# Epic 1 — Data Pipeline

## Overview

**Epic 1** establishes a **robust, reproducible data pipeline** for training the Mini-LLM from scratch.
The pipeline unifies multiple datasets, enforces data quality constraints, prevents data leakage, and prepares clean train/validation/test splits for downstream model training.

### Goals

* Aggregate **general-domain** and **technology-domain** text data
* Enforce **data quality checks** (mandatory for HD)
* Ensure **reproducibility and traceability**
* Produce clean, leakage-free splits for training and evaluation

---

## Datasets Used

| Dataset     | Domain                      | Purpose                                  |
| ----------- | --------------------------- | ---------------------------------------- |
| WikiText-2  | General / encyclopedic      | General language modelling               |
| TinyStories | Narrative / simple language | Fluency and coherence                    |
| TechNews    | Technology domain           | Domain adaptation (tech-focused fluency) |

Each document is tagged with a `source` field to preserve dataset provenance.

---

## Directory Structure (Epic 1)

```
data/
├── raw/
│   ├── wikitext/
│   ├── tinystories/
│   └── technews/
├── processed/
│   ├── all_text.jsonl
│   ├── train.jsonl
│   ├── val.jsonl
│   └── test.jsonl
scripts/
├── preprocess_data.py
├── data_loader.py
├── data_quality_checks.py
```

---

## Pipeline Stages

### Stage 1 — Data Acquisition & Unification

**Script:** `preprocess_data.py`

This script:

* Downloads and caches all datasets locally
* Cleans empty or malformed entries
* Tags each sample with its source dataset
* Deduplicates documents **before splitting**
* Applies a controlled dataset mixing ratio
* Produces train / validation / test splits

#### How to run

```bash
python -m scripts.preprocess_data
```

#### Outputs

* `data/processed/all_text.jsonl`
* `data/processed/train.jsonl`
* `data/processed/val.jsonl`
* `data/processed/test.jsonl`

Each line is a JSON object of the form:

```json
{
  "text": "Sample document text...",
  "source": "technews"
}
```

---

### Stage 2 — Dataset Loading for Training

**Script:** `data_loader.py`

This module provides a **PyTorch-compatible dataset loader** that:

* Reads `.jsonl` files
* Tokenizes text using the project’s tokenizer
* Produces `(input_ids, labels)` pairs for causal language modelling
* Ensures consistent sequence length handling

This script is **imported by the training pipeline** and is not run standalone.

#### How to run

```bash
python -m data.data_loader
```

#### Example usage

```python
from scripts.data_loader import JsonlDataset

train_dataset = JsonlDataset(
    path="data/processed/train.jsonl",
    tokenizer=tokenizer,
    max_seq_len=256
)
```

---

### Stage 3 — Data Quality Checks (MANDATORY for HD)

**Script:** `data_quality_checks.py`

This script verifies that the dataset meets **minimum quality standards** before training.

Checks include:

* Empty or near-empty documents
* Excessively short samples
* Excessively long samples
* Duplicate documents
* Train/validation/test leakage
* Dataset source distribution

These checks prevent:

* Inflated evaluation scores
* Memorisation
* Invalid experimental conclusions

#### How to run

```bash
python -m scripts.data_quality_checks
```

#### Expected output (example)

```
Total documents checked: 145595
Empty documents: 0
Duplicates detected: 0
Train/Val/Test leakage: None
Source distribution:
  wikitext: 20%
  tinystories: 20%
  technews: 60%
Data quality checks passed
```

If a violation is detected, the script **fails fast** and reports the issue.

---

## Reproducibility Measures

* Fixed random seed (`RANDOM_SEED = 42`)
* Deterministic dataset splits
* Cached raw datasets (`data/raw/`)
* Explicit dataset source tracking
* Deduplication performed **before** splitting

These measures ensure that:

* Experiments can be repeated
* Results are auditable
* Training and evaluation remain comparable

---

## Summary of Epic 1 Deliverables

| Component                  | Status |
| -------------------------- | ------ |
| Dataset acquisition        | ✅      |
| Multi-source unification   | ✅      |
| Controlled domain mixing   | ✅      |
| Deduplication              | ✅      |
| Train/Val/Test split       | ✅      |
| Data quality validation    | ✅      |
| Reproducibility safeguards | ✅      |
