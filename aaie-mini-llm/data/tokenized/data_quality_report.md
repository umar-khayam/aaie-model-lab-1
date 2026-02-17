
# Data Quality Report - Mini-LLM

## Token Length Distribution
- Mean tokens/doc: 141.78
- Median tokens/doc: 148.00
- 95th percentile: 308.00
- Max tokens/doc: 947
- Truncated documents (> 256 tokens): 8.95%

## Sequence Packing Efficiency
- Packing efficiency: 0.1752

## Duplicate Analysis
- Exact duplicate documents: 0

## Data Leakage Checks
- Train-Val overlap: 0
- Train-Test overlap: 0
- Val-Test overlap: 0

## Vocabulary Coverage
- Total tokens: 679389
- Unique tokens: 22820
- Tokenizer vocab size: 200019
- OOV rate: 0.00%

## Source Balance (% of tokens)
- wikitext: 41.79%
- tinystories: 58.21%

## Notes
- Document-level splitting prevents evaluation leakage.
- BPE tokenisation ensures full vocabulary coverage.
- Truncation is mitigated via contiguous token packing.

