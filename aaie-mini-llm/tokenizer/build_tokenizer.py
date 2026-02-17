import json
import tiktoken
from pathlib import Path

def build_tokenizer():
    enc = tiktoken.get_encoding("gpt2")  # base BPE

    Path("data/tokenized").mkdir(parents=True, exist_ok=True)

    tokenizer_data = {
        "name": "mini-llm-bpe",
        "vocab_size": enc.n_vocab
    }

    with open("data/tokenized/tokenizer.json", "w") as f:
        json.dump(tokenizer_data, f, indent=2)

    print(f"BPE tokenizer ready | vocab size = {enc.n_vocab}")

if __name__ == "__main__":
    build_tokenizer()
