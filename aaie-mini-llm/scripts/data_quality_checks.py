"""
Ticket 1.6 — Data Quality Checks for Mini-LLM

Checks:
1. Token length distribution
2. Sequence packing efficiency
3. Duplicate detection
4. Train/Val/Test leakage
5. Vocabulary coverage (OOV rate)
6. Source balance analysis

Outputs:
- data/tokenized/vocab_stats.json
- data/tokenized/length_distribution.json
- data/tokenized/data_quality_report.md
"""

import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import tiktoken

# -----------------------------
# Config
# -----------------------------
BLOCK_SIZE = 384
DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/tokenized")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

enc = tiktoken.encoding_for_model("gpt-4o")


# -----------------------------
# Helpers
# -----------------------------
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tokenize(text: str):
    return enc.encode(text)


# -----------------------------
# Load datasets
# -----------------------------
train_data = load_jsonl(DATA_DIR / "train.jsonl")
val_data   = load_jsonl(DATA_DIR / "val.jsonl")
test_data  = load_jsonl(DATA_DIR / "test.jsonl")

all_data = train_data + val_data + test_data

print(f"Documents loaded: {len(all_data)}")


# -----------------------------
# 1. Token length distribution
# -----------------------------
token_lengths = []
truncated_count = 0
total_tokens = 0

for item in all_data:
    tokens = tokenize(item["text"])
    length = len(tokens)
    token_lengths.append(length)
    total_tokens += length
    if length > BLOCK_SIZE:
        truncated_count += 1

length_stats = {
    "mean": float(np.mean(token_lengths)),
    "median": float(np.median(token_lengths)),
    "p95": float(np.percentile(token_lengths, 95)),
    "max": int(np.max(token_lengths)),
    "documents": len(token_lengths),
    "truncated_pct": truncated_count / len(token_lengths) * 100
}

with open(OUTPUT_DIR / "length_distribution.json", "w") as f:
    json.dump(length_stats, f, indent=2)


# -----------------------------
# 2. Sequence packing efficiency
# -----------------------------
packed_sequences = sum(l // BLOCK_SIZE for l in token_lengths)
used_tokens = packed_sequences * BLOCK_SIZE

packing_efficiency = used_tokens / total_tokens if total_tokens > 0 else 0.0


# -----------------------------
# 3. Duplicate detection
# -----------------------------
hash_counts = Counter(hash_text(item["text"]) for item in all_data)
exact_duplicates = sum(1 for c in hash_counts.values() if c > 1)


# -----------------------------
# 4. Leakage checks
# -----------------------------
train_hashes = {hash_text(item["text"]) for item in train_data}
val_hashes   = {hash_text(item["text"]) for item in val_data}
test_hashes  = {hash_text(item["text"]) for item in test_data}

leakage = {
    "train_val_overlap": len(train_hashes & val_hashes),
    "train_test_overlap": len(train_hashes & test_hashes),
    "val_test_overlap": len(val_hashes & test_hashes)
}

assert leakage["train_val_overlap"] == 0
assert leakage["train_test_overlap"] == 0
assert leakage["val_test_overlap"] == 0


# -----------------------------
# 5. Vocabulary coverage
# -----------------------------
all_tokens = []
for item in all_data:
    all_tokens.extend(tokenize(item["text"]))

vocab_stats = {
    "total_tokens": len(all_tokens),
    "unique_tokens": len(set(all_tokens)),
    "vocab_size": enc.n_vocab,
    "oov_rate": 0.0  # BPE guarantees zero OOV
}


# -----------------------------
# 6. Source balance
# -----------------------------
source_tokens = defaultdict(int)
for item in all_data:
    source_tokens[item["source"]] += len(tokenize(item["text"]))

source_balance = {
    src: count / total_tokens * 100
    for src, count in source_tokens.items()
}


# -----------------------------
# Save vocab stats
# -----------------------------
with open(OUTPUT_DIR / "vocab_stats.json", "w") as f:
    json.dump({
        "vocab": vocab_stats,
        "packing_efficiency": packing_efficiency,
        "duplicates": exact_duplicates,
        "leakage": leakage,
        "source_balance_pct": source_balance
    }, f, indent=2)


# -----------------------------
# Generate report (HD-ready)
# -----------------------------
report = f"""
# Data Quality Report - Mini-LLM

## Token Length Distribution
- Mean tokens/doc: {length_stats['mean']:.2f}
- Median tokens/doc: {length_stats['median']:.2f}
- 95th percentile: {length_stats['p95']:.2f}
- Max tokens/doc: {length_stats['max']}
- Truncated documents (> {BLOCK_SIZE} tokens): {length_stats['truncated_pct']:.2f}%

## Sequence Packing Efficiency
- Packing efficiency: {packing_efficiency:.4f}

## Duplicate Analysis
- Exact duplicate documents: {exact_duplicates}

## Data Leakage Checks
- Train-Val overlap: {leakage['train_val_overlap']}
- Train-Test overlap: {leakage['train_test_overlap']}
- Val-Test overlap: {leakage['val_test_overlap']}

## Vocabulary Coverage
- Total tokens: {vocab_stats['total_tokens']}
- Unique tokens: {vocab_stats['unique_tokens']}
- Tokenizer vocab size: {vocab_stats['vocab_size']}
- OOV rate: {vocab_stats['oov_rate'] * 100:.2f}%

## Source Balance (% of tokens)
"""

for src, pct in source_balance.items():
    report += f"- {src}: {pct:.2f}%\n"

report += """
## Notes
- Document-level splitting prevents evaluation leakage.
- BPE tokenisation ensures full vocabulary coverage.
- Truncation is mitigated via contiguous token packing.

"""

with open(OUTPUT_DIR / "data_quality_report.md", "w") as f:
    f.write(report)

print("✅ Data quality checks complete.")
print(f"📁 Outputs written to {OUTPUT_DIR.resolve()}")
