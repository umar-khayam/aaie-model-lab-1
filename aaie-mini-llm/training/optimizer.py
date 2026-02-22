import torch

def build_optimizer(model, lr, weight_decay, betas, eps):
    # Standard GPT-style weight decay: decay only on weight matrices
    decay, no_decay = [], []
    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if p.dim() >= 2 and "ln" not in name.lower() and "norm" not in name.lower():
            decay.append(p)
        else:
            no_decay.append(p)

    optim_groups = [
        {"params": decay, "weight_decay": weight_decay},
        {"params": no_decay, "weight_decay": 0.0},
    ]

    return torch.optim.AdamW(optim_groups, lr=lr, betas=tuple(betas), eps=eps)
