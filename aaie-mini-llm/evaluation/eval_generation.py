import json
import yaml
import torch
import tiktoken

from model.transformer import MiniGPT

enc = tiktoken.get_encoding("gpt2")


@torch.no_grad()
def generate(model, prompt, max_new_tokens=100, temperature=0.8, top_k=50):
    model.eval()
    idx = torch.tensor([enc.encode(prompt)], device=next(model.parameters()).device)

    for _ in range(max_new_tokens):
        logits, _ = model(idx)
        logits = logits[:, -1, :] / temperature

        if top_k is not None:
            v, _ = torch.topk(logits, top_k)
            logits[logits < v[:, [-1]]] = -float("inf")

        probs = torch.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, num_samples=1)
        idx = torch.cat([idx, next_id], dim=1)

    return enc.decode(idx[0].tolist())


def main():
    with open("configs/model.yaml") as f:
        mcfg = yaml.safe_load(f)["model"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MiniGPT(
        vocab_size=mcfg["vocab_size"],
        max_seq_len=mcfg["max_seq_len"],
        d_model=mcfg["d_model"],
        n_head=mcfg["n_head"],
        n_layer=mcfg["n_layer"],
        d_ff=mcfg["d_ff"],
        dropout=float(mcfg["dropout"]),
        tie_weights=bool(mcfg["tie_weights"]),
    ).to(device)

    ckpt = torch.load("checkpoints/best/ckpt.pt", map_location=device)
    model.load_state_dict(ckpt["model"])

    # ---- Check tokenizer vocab size ----
    enc = tiktoken.get_encoding("gpt2")
    assert enc.n_vocab == model.vocab_size, (
        f"❌ Tokenizer vocab ({enc.n_vocab}) != model vocab ({model.vocab_size})"
    )
    print(f"✅ Tokenizer vocab size matches model vocab size ({enc.n_vocab})")

    prompts = json.load(open("evaluation/qualitative_prompts.json"))

    for p in prompts:
        print("=" * 80)
        print("PROMPT:", p)
        print("OUTPUT:")
        print(generate(model, p))


if __name__ == "__main__":
    main()
