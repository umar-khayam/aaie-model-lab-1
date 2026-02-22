# evaluate.py
# Evaluation script for Mini-LLaMA (causal LM)

import math
import torch
from torch.utils.data import Dataset, DataLoader

from model.mini_llama import MiniLlamaConfig, MiniLlamaForCausalLM


# -----------------------------
# Config
# -----------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BATCH_SIZE = 24
BLOCK_SIZE = 384
VOCAB_SIZE = 50257

CHECKPOINT_PATH = "checkpoints/step_1000.pt"   # 👈 change to your best checkpoint
TEST_DATA_PATH = "data/processed/test.pt"


# -----------------------------
# Dataset
# -----------------------------
class LMDataset(Dataset):
    def __init__(self, pt_path):
        data = torch.load(pt_path)
        self.input_ids = data["input_ids"]
        self.labels = data["labels"]

    def __len__(self):
        return self.input_ids.size(0)

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "labels": self.labels[idx],
        }


# -----------------------------
# Evaluation
# -----------------------------
@torch.no_grad()
def evaluate(model, dataloader):
    model.eval()
    total_loss = 0.0
    total_tokens = 0

    for batch in dataloader:
        input_ids = batch["input_ids"].to(DEVICE)
        labels = batch["labels"].to(DEVICE)

        outputs = model(input_ids, labels=labels)
        loss = outputs["loss"]

        tokens = labels.numel()
        total_loss += loss.item() * tokens
        total_tokens += tokens

    avg_loss = total_loss / total_tokens
    perplexity = math.exp(avg_loss)

    return avg_loss, perplexity


# -----------------------------
# Text generation sanity check
# -----------------------------
@torch.no_grad()
def generate_sample(model, tokenizer, prompt, max_new_tokens=80):
    model.eval()
    input_ids = torch.tensor(
        tokenizer.encode(prompt),
        dtype=torch.long,
        device=DEVICE
    ).unsqueeze(0)

    output_ids = model.generate(
        input_ids,
        max_new_tokens=max_new_tokens,
        temperature=0.8,
        top_k=40,
    )

    return tokenizer.decode(output_ids[0].tolist())


# -----------------------------
# Main
# -----------------------------
def main():
    print(f"🔍 Evaluating on device: {DEVICE}")

    # Load model config
    cfg = MiniLlamaConfig(
        vocab_size=VOCAB_SIZE,
        max_seq_len=BLOCK_SIZE,
        d_model=1024,
        n_layer=24,
        n_head=16,
        n_kv_head=16,
        d_ff=4096,
        dropout=0.0,
        tie_weights=True,
    )

    model = MiniLlamaForCausalLM(cfg).to(DEVICE)

    # Load checkpoint
    ckpt = torch.load(
        CHECKPOINT_PATH,
        map_location=DEVICE,
        weights_only=False
    )
    model.load_state_dict(ckpt["model"])
    print(f"✅ Loaded checkpoint: {CHECKPOINT_PATH}")

    # Load test data
    test_dataset = LMDataset(TEST_DATA_PATH)
    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        pin_memory=True,
    )

    # Run evaluation
    test_loss, test_ppl = evaluate(model, test_loader)

    print("\n📊 Test Results")
    print(f"  Test Loss       : {test_loss:.4f}")
    print(f"  Test Perplexity : {test_ppl:.2f}")

    print("\n🎉 Evaluation complete")


if __name__ == "__main__":
    main()
