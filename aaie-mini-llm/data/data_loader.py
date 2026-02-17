import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import torch
from tokenizer.tokenizer_utils import tokenize_text, pack_sequences

BLOCK_SIZE = 384

def build_dataset(jsonl_path, output_path):
    all_tokens = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            tokens = tokenize_text(item["text"])
            all_tokens.extend(tokens)

    sequences = pack_sequences(all_tokens, BLOCK_SIZE)

    input_ids = torch.tensor(sequences, dtype=torch.long)
    labels = input_ids.clone()

    torch.save({
        "input_ids": input_ids,
        "labels": labels
    }, output_path)

if __name__ == "__main__":
    print("Building training dataset...")
    build_dataset("data/processed/train.jsonl", "data/processed/train.pt")
    print("✅ train.pt created")
    
    print("Building validation dataset...")
    build_dataset("data/processed/val.jsonl", "data/processed/val.pt")
    print("✅ val.pt created")
    
    print("Building test dataset...")
    build_dataset("data/processed/test.jsonl", "data/processed/test.pt")
    print("✅ test.pt created")
    
    print("\n🎉 All datasets built successfully!")
