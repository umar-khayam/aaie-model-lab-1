import math

def cosine_lr(step, max_steps, base_lr, min_lr, warmup_steps):
    if step < warmup_steps:
        return base_lr * step / max(1, warmup_steps)

    progress = (step - warmup_steps) / max(1, (max_steps - warmup_steps))
    progress = min(max(progress, 0.0), 1.0)
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return min_lr + cosine * (base_lr - min_lr)


class LRScheduler:
    def __init__(self, optimizer, max_steps, base_lr, min_lr, warmup_steps):
        self.optimizer = optimizer
        self.max_steps = max_steps
        self.base_lr = base_lr
        self.min_lr = min_lr
        self.warmup_steps = warmup_steps

    def step(self, step_idx):
        lr = cosine_lr(step_idx, self.max_steps, self.base_lr, self.min_lr, self.warmup_steps)
        for pg in self.optimizer.param_groups:
            pg["lr"] = lr
        return lr
