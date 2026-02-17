import torch
import torch.nn as nn


class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, dropout: float):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, idx):
        return self.drop(self.emb(idx))

# No positional embeddings here — RoPE handles position implicitly