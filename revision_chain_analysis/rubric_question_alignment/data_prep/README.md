# Data Preparation for Rubric-Question Alignment

## Purpose

This folder contains data processing utilities for preparing student prompts and rubric keywords for downstream rubric-question alignment analysis.

## Functions

### `chat_parser(chat_log: dict) -> list[dict]`

Extracts only student prompts from a raw revision chain log.

**Returns:**
- List of dictionaries with `prompt` (str) and `turn_index` (int) keys

### `extract_keywords(text: str) -> list[str]`

Normalizes text into a list of keywords.

**Processing steps:**
1. Convert text to lowercase
2. Remove punctuation
3. Split into individual words
4. Remove common stop words

### `load_rubric(rubric_json: dict) -> dict`

Loads rubric metadata and extracts keywords from rubric text.

**Returns:**
- Dictionary with:
  - `rubric_id` (str)
  - `domain` (str)
  - `criteria` (list of criterion dicts with keywords extracted)

## Output Samples

The `output_samples/` directory contains JSON files demonstrating the output format of this pipeline. Each sample includes:

- `parsed_chat`: List of extracted student prompts
- `rubric_keywords`: Processed rubric with extracted keywords

These samples use real revision chain logs and IT rubrics and serve as demonstration outputs.