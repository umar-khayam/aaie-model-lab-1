import math
import yaml
import torch
import tiktoken
from torch.utils.data import DataLoader

from model.transformer import MiniGPT


class PackedTokenDataset(torch.utils.data.Dataset):
    def __init__(self, pt_path):
        obj = torch.load(pt_path, map_location="cpu")
        self.input_ids = obj["input_ids"]
        self.labels = obj["labels"]

    def __len__(self):
        return self.input_ids.size(0)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.labels[idx]


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    losses = []
    for x, y in loader:
        x = x.to(device)
        y = y.to(device)
        _, loss = model(x, y)
        losses.append(loss.item())
    return sum(losses) / len(losses)


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

    val_ds = PackedTokenDataset("data/processed/val.pt")
    val_loader = DataLoader(val_ds, batch_size=8)

    val_loss = evaluate(model, val_loader, device)
    ppl = math.exp(min(20, val_loss))

    print(f"Validation loss: {val_loss:.4f}")
    print(f"Perplexity: {ppl:.2f}")


if __name__ == "__main__":
    main()
