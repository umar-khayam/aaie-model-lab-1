# generate_examples.py
# Generate qualitative text samples for thesis appendix

import torch
from model.mini_llama import MiniLlamaConfig, MiniLlamaForCausalLM

# -----------------------------
# Config
# -----------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

CHECKPOINT_PATH = "checkpoints/step_1000.pt"   # 👈 update
OUTPUT_FILE = "appendix_generation.txt"

BLOCK_SIZE = 384
VOCAB_SIZE = 50257

MAX_NEW_TOKENS = 120
TEMPERATURE = 0.8
TOP_K = 40

SEED = 42
torch.manual_seed(SEED)


# -----------------------------
# Tokenizer (reuse yours)
# -----------------------------
from tokenizer.tokenizer_utils import tokenize_text, detokenize_text


def encode(text):
    return tokenize_text(text)


def decode(tokens):
    return detokenize_text(tokens)


# -----------------------------
# Prompts for Appendix
# -----------------------------
PROMPTS = [
    "Artificial intelligence is transforming the way",
    "In recent years, large language models have",
    "The future of technology depends on",
    "Once upon a time, there was a small robot that",
    "Machine learning models often struggle when",
]


# -----------------------------
# Generation
# -----------------------------
@torch.no_grad()
def generate(model, prompt):
    input_ids = torch.tensor(
        encode(prompt),
        dtype=torch.long,
        device=DEVICE
    ).unsqueeze(0)

    output_ids = model.generate(
        input_ids,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_k=TOP_K,
    )

    return decode(output_ids[0].tolist())


def main():
    print(f"✍️ Generating samples on {DEVICE}")

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
    ckpt = torch.load(CHECKPOINT_PATH, map_location=DEVICE)
    model.load_state_dict(ckpt["model"])
    model.eval()

    outputs = []

    for i, prompt in enumerate(PROMPTS, start=1):
        print(f"→ Prompt {i}")
        text = generate(model, prompt)
        outputs.append((prompt, text))

    # Save to file (appendix-ready)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("Appendix: Qualitative Text Generation Examples\n")
        f.write("=" * 55 + "\n\n")

        for i, (prompt, text) in enumerate(outputs, start=1):
            f.write(f"Example {i}\n")
            f.write("-" * 30 + "\n")
            f.write(f"Prompt:\n{prompt}\n\n")
            f.write("Generated Text:\n")
            f.write(text.strip() + "\n\n")

    print(f"✅ Saved generation examples to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
