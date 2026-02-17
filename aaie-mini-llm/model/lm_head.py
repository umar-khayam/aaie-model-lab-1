import torch
import torch.nn as nn


class LMHead(nn.Module):
    def __init__(self, d_model: int, vocab_size: int, tie_weights: bool, token_embedding: nn.Embedding):
        super().__init__()
        self.tie_weights = tie_weights

        if tie_weights:
            # Use token embedding weights for output projection
            self.proj = nn.Linear(d_model, vocab_size, bias=False)
            self.proj.weight = token_embedding.weight
        else:
            self.proj = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, x: torch.Tensor):
        # x: (B, T, d_model)
        return self.proj(x)  # (B, T, vocab)
