import os
import time
import math
import yaml
import torch
import tiktoken
from torch.utils.data import Dataset, DataLoader

from model.transformer import MiniGPT
from training.optimizer import build_optimizer
from training.scheduler import LRScheduler
from training.checkpoint import save_checkpoint, load_checkpoint


# -----------------------------
# Utils
# -----------------------------
def set_seed(seed: int):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def pick_device(mode="auto"):
    if mode == "cpu":
        return torch.device("cpu")
    if mode == "mps":
        return torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    if mode == "cuda":
        return torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    # auto
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# -----------------------------
# Dataset
# -----------------------------
class PackedTokenDataset(Dataset):
    def __init__(self, pt_path: str):
        obj = torch.load(pt_path, map_location="cpu")
        self.input_ids = obj["input_ids"]
        self.labels = obj["labels"]

    def __len__(self):
        return self.input_ids.size(0)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.labels[idx]


@torch.no_grad()
def evaluate(model, loader, device, amp_enabled: bool):
    model.eval()
    losses = []
    for input_ids, labels in loader:
        input_ids = input_ids.to(device)
        labels = labels.to(device)
        with torch.autocast(device_type=device.type, enabled=(amp_enabled and device.type == "cuda")):
            _, loss = model(input_ids, labels)
        losses.append(loss.item())
    model.train()
    return float(sum(losses) / max(1, len(losses)))


def main():
    # ---- Load configs ----
    with open("configs/model.yaml", "r") as f:
        model_cfg = yaml.safe_load(f)["model"]

    with open("configs/training.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    tcfg = cfg["training"]
    ocfg = cfg["optimizer"]
    scfg = cfg["scheduler"]
    dcfg = cfg["data"]
    ccfg = cfg["checkpoint"]
    amp_cfg = cfg.get("amp", {"enabled": True})

    set_seed(tcfg["seed"])
    device = pick_device(tcfg["device"])
    print(f"Device: {device}")

    # ---- Data ----
    train_ds = PackedTokenDataset(dcfg["train_pt"])
    val_ds = PackedTokenDataset(dcfg["val_pt"])

    train_loader = DataLoader(
        train_ds,
        batch_size=tcfg["batch_size"],
        shuffle=True,
        num_workers=tcfg["num_workers"],
        pin_memory=(device.type == "cuda"),
        drop_last=True,
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=tcfg["batch_size"],
        shuffle=False,
        num_workers=tcfg["num_workers"],
        pin_memory=(device.type == "cuda"),
        drop_last=False,
    )

    # ---- Model ----
    model = MiniGPT(
        vocab_size=model_cfg["vocab_size"],
        max_seq_len=model_cfg["max_seq_len"],
        d_model=model_cfg["d_model"],
        n_head=model_cfg["n_head"],
        n_layer=model_cfg["n_layer"],
        d_ff=model_cfg["d_ff"],
        dropout=float(model_cfg["dropout"]),
        tie_weights=bool(model_cfg["tie_weights"]),
    ).to(device)
    
    # ---- Check tokenizer vocab size ----
    enc = tiktoken.get_encoding("gpt2")
    assert enc.n_vocab == model.vocab_size, (
        f"❌ Tokenizer vocab ({enc.n_vocab}) != model vocab ({model.vocab_size})"
    )
    print(f"✅ Tokenizer vocab size matches model vocab size ({enc.n_vocab})")

    # ---- Optim + sched ----
    optimizer = build_optimizer(
        model,
        lr=float(ocfg["lr"]),
        weight_decay=float(ocfg["weight_decay"]),
        betas=ocfg["betas"],
        eps=float(ocfg["eps"]),
    )

    # total training steps
    steps_per_epoch = len(train_loader) // max(1, int(tcfg["grad_accum_steps"]))
    max_steps = tcfg["max_steps"] or int(tcfg["epochs"] * steps_per_epoch)
    scheduler = LRScheduler(
        optimizer=optimizer,
        max_steps=max_steps,
        base_lr=float(ocfg["lr"]),
        min_lr=float(scfg["min_lr"]),
        warmup_steps=int(scfg["warmup_steps"]),
    )

    # AMP only on CUDA
    amp_enabled = bool(amp_cfg.get("enabled", True)) and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)

    # ---- Resume if exists ----
    best_val_loss = float("inf")
    start_step = 0
    start_epoch = 0

    ckpt = load_checkpoint(ccfg["out_dir"], "latest", model, optimizer, scaler, map_location=device)
    if ckpt is not None:
        start_step = int(ckpt.get("step", 0))
        start_epoch = int(ckpt.get("epoch", 0))
        best_val_loss = float(ckpt.get("best_val_loss", best_val_loss))
        print(f"Resumed from step={start_step}, epoch={start_epoch}, best_val_loss={best_val_loss:.4f}")

    # ---- Train ----
    model.train()
    global_step = start_step
    t0 = time.time()

    grad_accum_steps = int(tcfg["grad_accum_steps"])
    grad_clip = float(ocfg.get("grad_clip_norm", 0.0))

    for epoch in range(start_epoch, int(tcfg["epochs"])):
        for it, (input_ids, labels) in enumerate(train_loader):
            input_ids = input_ids.to(device)
            labels = labels.to(device)

            # scale loss by grad_accum
            with torch.autocast(device_type=device.type, enabled=amp_enabled):
                _, loss = model(input_ids, labels)
                loss = loss / grad_accum_steps

            scaler.scale(loss).backward()

            if (it + 1) % grad_accum_steps == 0:
                # gradient clipping (unscale first)
                if grad_clip and grad_clip > 0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)

                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)

                lr = scheduler.step(global_step)

                # ---- Logging ----
                if global_step % int(tcfg["log_every"]) == 0:
                    elapsed = time.time() - t0
                    print(f"step {global_step}/{max_steps} | lr {lr:.6f} | loss {loss.item()*grad_accum_steps:.4f} | {elapsed:.1f}s")

                # ---- Eval ----
                if global_step % int(tcfg["eval_every"]) == 0 and global_step > 0:
                    val_loss = evaluate(model, val_loader, device, amp_enabled)
                    ppl = math.exp(min(20, val_loss))
                    print(f"[val] step {global_step} | val_loss {val_loss:.4f} | ppl {ppl:.2f}")

                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        save_checkpoint(ccfg["out_dir"], "best", model, optimizer, scaler if amp_enabled else None,
                                       global_step, epoch, best_val_loss)
                        print(f"✅ Saved best checkpoint (val_loss={best_val_loss:.4f})")

                # ---- Save latest ----
                if global_step % int(tcfg["save_every"]) == 0 and global_step > 0:
                    save_checkpoint(ccfg["out_dir"], "latest", model, optimizer, scaler if amp_enabled else None,
                                   global_step, epoch, best_val_loss)
                    print("💾 Saved latest checkpoint")

                global_step += 1
                if global_step >= max_steps:
                    break

        if global_step >= max_steps:
            break

    # Final save
    save_checkpoint(ccfg["out_dir"], "latest", model, optimizer, scaler if amp_enabled else None,
                   global_step, epoch, best_val_loss)
    print("✅ Training complete.")


if __name__ == "__main__":
    main()
