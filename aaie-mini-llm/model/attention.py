import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from model.rope import apply_rope


class CausalSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_head: int, dropout: float):
        super().__init__()
        assert d_model % n_head == 0

        self.n_head = n_head
        self.head_dim = d_model // n_head

        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.proj = nn.Linear(d_model, d_model, bias=False)

        self.attn_drop = nn.Dropout(dropout)
        self.resid_drop = nn.Dropout(dropout)

        self.register_buffer("mask", None, persistent=False)

    def _get_mask(self, T, device):
        if self.mask is None or self.mask.size(-1) < T:
            m = torch.tril(torch.ones(T, T, device=device, dtype=torch.bool))
            self.mask = m.view(1, 1, T, T)
        return self.mask[:, :, :T, :T]

    def forward(self, x):
        B, T, C = x.shape

        qkv = self.qkv(x)
        q, k, v = qkv.split(C, dim=2)

        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)

        # Apply Rotary Positional Embeddings
        q, k = apply_rope(q, k, seq_len=T)

        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        mask = self._get_mask(T, x.device)
        att = att.masked_fill(~mask, float("-inf"))

        att = F.softmax(att, dim=-1)
        att = self.attn_drop(att)

        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.resid_drop(self.proj(y))
