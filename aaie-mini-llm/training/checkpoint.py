import os
import torch
from pathlib import Path

def save_checkpoint(out_dir, tag, model, optimizer, scaler, step, epoch, best_val_loss):
    out_dir = Path(out_dir) / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    ckpt = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "step": step,
        "epoch": epoch,
        "best_val_loss": best_val_loss,
    }
    if scaler is not None:
        ckpt["scaler"] = scaler.state_dict()

    torch.save(ckpt, out_dir / "ckpt.pt")


def load_checkpoint(out_dir, tag, model, optimizer=None, scaler=None, map_location="cpu"):
    ckpt_path = Path(out_dir) / tag / "ckpt.pt"
    if not ckpt_path.exists():
        return None

    ckpt = torch.load(ckpt_path, map_location=map_location)
    model.load_state_dict(ckpt["model"])

    if optimizer is not None and "optimizer" in ckpt:
        optimizer.load_state_dict(ckpt["optimizer"])

    if scaler is not None and "scaler" in ckpt:
        scaler.load_state_dict(ckpt["scaler"])

    return ckpt
