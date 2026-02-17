import json
import yaml
import torch
import tiktoken

from model.transformer import MiniGPT

enc = tiktoken.get_encoding("gpt2")


def is_valid_json(text):
    try:
        json.loads(text)
        return True
    except Exception:
        return False


@torch.no_grad()
def generate_json(model, prompt, max_new_tokens=150):
    device = next(model.parameters()).device
    idx = torch.tensor([enc.encode(prompt)], device=device)

    generated_text = ""

    for _ in range(max_new_tokens):
        logits, _ = model(idx)
        next_id = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
        idx = torch.cat([idx, next_id], dim=1)

        generated_text = enc.decode(idx[0].tolist())

        # ✅ stop once JSON likely finished
        if "}" in generated_text or "]" in generated_text:
            break

    return generated_text


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

    prompts = [
        "Return a JSON object with keys: name, age, occupation.",
        "Output a JSON list of three animals with name and habitat."
    ]

    valid = 0
    for p in prompts:
        out = generate_json(model, p)
        if is_valid_json(out):
            valid += 1

    print(f"JSON validity: {valid}/{len(prompts)}")


if __name__ == "__main__":
    main()
