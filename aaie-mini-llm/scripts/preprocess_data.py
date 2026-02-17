"""
Preprocess and unify datasets for Mini-LLM.

Datasets:
- WikiText-2
- TinyStories

Output:
- data/processed/all_text.jsonl
- data/processed/train.jsonl
- data/processed/val.jsonl
- data/processed/test.jsonl
"""

import json
import random
from pathlib import Path
from datasets import load_dataset

RANDOM_SEED = 42
TRAIN_RATIO = 0.90
VAL_RATIO = 0.05
TEST_RATIO = 0.05

# Dataset mixing ratios (must sum to 1.0)
WIKITEXT_RATIO = 0.2
TINYSTORIES_RATIO = 0.2
TECHNEWS_RATIO = 0.6

random.seed(RANDOM_SEED)


# -----------------------------
# Dataset loaders
# -----------------------------
def load_wikitext(limit=None):
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1")
    # dataset.save_to_disk("data/raw/wikitext")

    print(f"Wikitext data: {len(dataset)}")

    samples = []

    for split in dataset:
        for item in dataset[split]:
            text = item["text"].strip()
            if len(text) > 0:
                samples.append({
                    "text": text,
                    "source": "wikitext"
                })
            if limit and len(samples) >= limit:
                break

    return samples


def load_tinystories(limit=None):
    dataset = load_dataset("roneneldan/TinyStories")
    # dataset.save_to_disk("data/raw/tinystories")

    print(f"TinyStories data: {len(dataset)}")

    samples = []

    for item in dataset["train"]:
        text = item["text"].strip()
        if len(text) > 0:
            samples.append({
                "text": text,
                "source": "tinystories"
            })
        if limit and len(samples) >= limit:
            break

    return samples

def load_technews(limit=None):
    dataset = load_dataset("vencortex/TechNews", split="train")
    # dataset.save_to_disk("data/raw/technews")

    print(f"TechNews data: {len(dataset)}")

    samples = []

    for item in dataset:
        text = item.get("text")
        if not isinstance(text, str):
            continue

        text = text.strip()
        if not text:
            continue

        samples.append({
            "text": text,
            "source": "technews"
        })

        if limit is not None and len(samples) >= limit:
            break

    return samples

# -----------------------------
# Train / Val / Test split
# -----------------------------
def split_data(data):
    random.shuffle(data)
    n = len(data)

    train_end = int(n * TRAIN_RATIO)
    val_end = train_end + int(n * VAL_RATIO)

    train = data[:train_end]
    val = data[train_end:val_end]
    test = data[val_end:]

    return train, val, test

def deduplicate_data(data):
    """Remove duplicate documents based on text content."""
    seen = set()
    unique_data = []
    duplicates_removed = 0
    
    for item in data:
        text_hash = hash(item["text"])
        if text_hash not in seen:
            seen.add(text_hash)
            unique_data.append(item)
        else:
            duplicates_removed += 1
    
    print(f"Removed {duplicates_removed} duplicate documents")
    return unique_data

# -----------------------------
# Save helpers
# -----------------------------
def save_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# -----------------------------
# Main
# -----------------------------
def main():
    print("Downloading datasets...")

    wikitext = load_wikitext() # adjustable
    tinystories = load_tinystories()  # adjustable
    technews = load_technews()  # adjustable

    # Controlled mixing (prevents domain collapse)
    total_target = min(
        int(len(wikitext) / WIKITEXT_RATIO),
        int(len(tinystories) / TINYSTORIES_RATIO),
        int(len(technews) / TECHNEWS_RATIO),
    )

    mixed_data = (
        random.sample(wikitext, int(total_target * WIKITEXT_RATIO)) +
        random.sample(tinystories, int(total_target * TINYSTORIES_RATIO)) +
        random.sample(technews, int(total_target * TECHNEWS_RATIO))
    )

    print("Dataset composition:")
    print(f"  WikiText:     {int(total_target * WIKITEXT_RATIO)}")
    print(f"  TinyStories:  {int(total_target * TINYSTORIES_RATIO)}")
    print(f"  TechNews:     {int(total_target * TECHNEWS_RATIO)}")
    print(f"  Total docs:   {len(mixed_data)}")

    # Deduplicate before split
    mixed_data = deduplicate_data(mixed_data)

    train, val, test = split_data(mixed_data)

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    save_jsonl(mixed_data, output_dir / "all_text.jsonl")
    save_jsonl(train, output_dir / "train.jsonl")
    save_jsonl(val, output_dir / "val.jsonl")
    save_jsonl(test, output_dir / "test.jsonl")

    print("Preprocessing complete:")
    print(f"  Train: {len(train)}")
    print(f"  Val:   {len(val)}")
    print(f"  Test:  {len(test)}")


if __name__ == "__main__":
    main()
