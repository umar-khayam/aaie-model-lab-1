from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# -----------------------------
# Config
# -----------------------------
@dataclass
class MiniLlamaConfig:
    vocab_size: int = 50257
    max_seq_len: int = 384

    d_model: int = 1024
    n_layer: int = 24
    n_head: int = 16

    # If you want classic MHA, set n_kv_head = n_head.
    # If you want GQA/MQA-like behavior, set n_kv_head < n_head (must divide n_head).
    n_kv_head: Optional[int] = None

    d_ff: int = 4096
    dropout: float = 0.0

    rope_theta: float = 10000.0
    rmsnorm_eps: float = 1e-6

    tie_weights: bool = True
    use_bias: bool = False  # LLaMA-style uses no bias in linear layers


# -----------------------------
# Utilities
# -----------------------------
class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, C]
        # normalize over last dim
        norm = x.pow(2).mean(dim=-1, keepdim=True)
        x = x * torch.rsqrt(norm + self.eps)
        return x * self.weight


def _rotate_half(x: torch.Tensor) -> torch.Tensor:
    # x: [..., d]
    d = x.size(-1)
    x1 = x[..., : d // 2]
    x2 = x[..., d // 2 :]
    return torch.cat((-x2, x1), dim=-1)


def apply_rope(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    # q,k: [B, n_head, T, head_dim]
    # cos,sin: [T, head_dim] broadcast to [1,1,T,head_dim]
    cos = cos.unsqueeze(0).unsqueeze(0)
    sin = sin.unsqueeze(0).unsqueeze(0)
    q = (q * cos) + (_rotate_half(q) * sin)
    k = (k * cos) + (_rotate_half(k) * sin)
    return q, k


def repeat_kv(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    # x: [B, n_kv, T, hd] -> [B, n_kv*n_rep, T, hd]
    if n_rep == 1:
        return x
    b, nkv, t, hd = x.shape
    x = x[:, :, None, :, :].expand(b, nkv, n_rep, t, hd)
    return x.reshape(b, nkv * n_rep, t, hd)


# -----------------------------
# RoPE cache
# -----------------------------
class RoPECache(nn.Module):
    def __init__(self, head_dim: int, max_seq_len: int, theta: float = 10000.0):
        super().__init__()
        if head_dim % 2 != 0:
            raise ValueError(f"RoPE head_dim must be even, got {head_dim}")
        self.head_dim = head_dim
        self.max_seq_len = max_seq_len
        self.theta = theta

        # register buffers (will be moved with model.to(device))
        self.register_buffer("cos_cache", torch.empty(max_seq_len, head_dim), persistent=False)
        self.register_buffer("sin_cache", torch.empty(max_seq_len, head_dim), persistent=False)
        self._built = False

    def _build(self, device: torch.device, dtype: torch.dtype):
        # Build cos/sin tables for RoPE
        # inv_freq for half dims, then expand to full head_dim via interleaving in rotate_half method.
        half = self.head_dim // 2
        inv_freq = 1.0 / (self.theta ** (torch.arange(0, half, device=device, dtype=dtype) / half))
        positions = torch.arange(self.max_seq_len, device=device, dtype=dtype)
        freqs = torch.einsum("t,f->tf", positions, inv_freq)  # [T, half]
        # Duplicate to full dim (cos/sin apply elementwise on full head_dim)
        emb = torch.cat([freqs, freqs], dim=-1)  # [T, head_dim]
        self.cos_cache = emb.cos()
        self.sin_cache = emb.sin()
        self._built = True

    def forward(self, seq_len: int, device: torch.device, dtype: torch.dtype) -> Tuple[torch.Tensor, torch.Tensor]:
        if seq_len > self.max_seq_len:
            raise ValueError(f"seq_len {seq_len} > max_seq_len {self.max_seq_len}")
        if (not self._built) or (self.cos_cache.device != device) or (self.cos_cache.dtype != dtype):
            self._build(device, dtype)
        return self.cos_cache[:seq_len], self.sin_cache[:seq_len]


# -----------------------------
# Attention + MLP
# -----------------------------
class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: MiniLlamaConfig):
        super().__init__()
        assert cfg.d_model % cfg.n_head == 0
        self.cfg = cfg
        self.n_head = cfg.n_head
        self.n_kv = cfg.n_kv_head if cfg.n_kv_head is not None else cfg.n_head
        if self.n_head % self.n_kv != 0:
            raise ValueError(f"n_head ({self.n_head}) must be divisible by n_kv_head ({self.n_kv}).")
        self.head_dim = cfg.d_model // cfg.n_head
        if self.head_dim % 2 != 0:
            raise ValueError(f"head_dim must be even for RoPE. Got {self.head_dim}")

        # Projections: LLaMA uses separate q, k, v and an output proj
        self.q_proj = nn.Linear(cfg.d_model, cfg.d_model, bias=cfg.use_bias)
        self.k_proj = nn.Linear(cfg.d_model, self.n_kv * self.head_dim, bias=cfg.use_bias)
        self.v_proj = nn.Linear(cfg.d_model, self.n_kv * self.head_dim, bias=cfg.use_bias)
        self.o_proj = nn.Linear(cfg.d_model, cfg.d_model, bias=cfg.use_bias)

        self.attn_dropout = cfg.dropout
        self.resid_dropout = nn.Dropout(cfg.dropout)

        self.rope = RoPECache(self.head_dim, cfg.max_seq_len, theta=cfg.rope_theta)

        # Detect SDPA availability (PyTorch 2.0+)
        self._has_sdpa = hasattr(F, "scaled_dot_product_attention")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, C]
        b, t, c = x.shape

        q = self.q_proj(x)  # [B, T, C]
        k = self.k_proj(x)  # [B, T, n_kv*hd]
        v = self.v_proj(x)  # [B, T, n_kv*hd]

        # reshape to heads
        q = q.view(b, t, self.n_head, self.head_dim).transpose(1, 2)  # [B, n_head, T, hd]
        k = k.view(b, t, self.n_kv, self.head_dim).transpose(1, 2)    # [B, n_kv,   T, hd]
        v = v.view(b, t, self.n_kv, self.head_dim).transpose(1, 2)    # [B, n_kv,   T, hd]

        # RoPE
        cos, sin = self.rope(seq_len=t, device=x.device, dtype=x.dtype)  # [T, hd]
        q, k = apply_rope(q, k, cos, sin)

        # If GQA: repeat k/v to match q heads
        n_rep = self.n_head // self.n_kv
        k = repeat_kv(k, n_rep)  # [B, n_head, T, hd]
        v = repeat_kv(v, n_rep)  # [B, n_head, T, hd]

        if self._has_sdpa:
            # PyTorch SDPA handles causal masking efficiently with is_causal=True
            attn = F.scaled_dot_product_attention(
                q, k, v,
                attn_mask=None,
                dropout_p=self.attn_dropout if self.training else 0.0,
                is_causal=True,
            )  # [B, n_head, T, hd]
        else:
            # Manual attention (slower)
            scale = 1.0 / math.sqrt(self.head_dim)
            scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, n_head, T, T]
            causal = torch.tril(torch.ones(t, t, device=x.device, dtype=torch.bool))
            scores = scores.masked_fill(~causal, float("-inf"))
            probs = torch.softmax(scores, dim=-1)
            if self.training and self.attn_dropout > 0:
                probs = F.dropout(probs, p=self.attn_dropout)
            attn = torch.matmul(probs, v)  # [B, n_head, T, hd]

        attn = attn.transpose(1, 2).contiguous().view(b, t, c)  # [B, T, C]
        out = self.o_proj(attn)
        out = self.resid_dropout(out)
        return out


class SwiGLU(nn.Module):
    def __init__(self, cfg: MiniLlamaConfig):
        super().__init__()
        # LLaMA MLP: up_proj + gate_proj with SiLU, then down_proj
        self.gate = nn.Linear(cfg.d_model, cfg.d_ff, bias=cfg.use_bias)
        self.up = nn.Linear(cfg.d_model, cfg.d_ff, bias=cfg.use_bias)
        self.down = nn.Linear(cfg.d_ff, cfg.d_model, bias=cfg.use_bias)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.down(F.silu(self.gate(x)) * self.up(x)))


class TransformerBlock(nn.Module):
    def __init__(self, cfg: MiniLlamaConfig):
        super().__init__()
        self.attn_norm = RMSNorm(cfg.d_model, eps=cfg.rmsnorm_eps)
        self.attn = CausalSelfAttention(cfg)
        self.mlp_norm = RMSNorm(cfg.d_model, eps=cfg.rmsnorm_eps)
        self.mlp = SwiGLU(cfg)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.attn_norm(x))
        x = x + self.mlp(self.mlp_norm(x))
        return x


# -----------------------------
# Mini-LLaMA Model
# -----------------------------
class MiniLlamaForCausalLM(nn.Module):
    def __init__(self, cfg: MiniLlamaConfig):
        super().__init__()
        self.cfg = cfg

        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.drop = nn.Dropout(cfg.dropout)

        self.blocks = nn.ModuleList([TransformerBlock(cfg) for _ in range(cfg.n_layer)])
        self.norm_f = RMSNorm(cfg.d_model, eps=cfg.rmsnorm_eps)

        self.lm_head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)

        if cfg.tie_weights:
            self.lm_head.weight = self.tok_emb.weight

        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module):
        # Reasonable init for scratch training (GPT/LLaMA-ish)
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self,
        input_ids: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        input_ids: [B, T]
        labels:    [B, T] (optional)
        returns: dict(logits, loss(optional))
        """
        if input_ids.dim() != 2:
            raise ValueError(f"input_ids must be [B, T], got {tuple(input_ids.shape)}")
        b, t = input_ids.shape
        if t > self.cfg.max_seq_len:
            raise ValueError(f"Sequence length {t} > max_seq_len {self.cfg.max_seq_len}")

        x = self.tok_emb(input_ids)  # [B, T, C]
        x = self.drop(x)

        for blk in self.blocks:
            x = blk(x)

        x = self.norm_f(x)
        logits = self.lm_head(x)  # [B, T, V]

        out = {"logits": logits}

        if labels is not None:
            # Causal LM loss: predict token t+1 from position t (shift inside loss)
            # But your dataset uses labels = input_ids; easiest is shift here.
            # logits at [:, :-1] predict labels at [:, 1:].
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = labels[:, 1:].contiguous()
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
            )
            out["loss"] = loss

        return out

    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 50,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        eos_token_id: Optional[int] = None,
    ) -> torch.Tensor:
        """
        Simple greedy/sampling generation (no KV cache; fine for small seq_len).
        input_ids: [B, T]
        """
        self.eval()
        for _ in range(max_new_tokens):
            if input_ids.size(1) > self.cfg.max_seq_len:
                input_ids = input_ids[:, -self.cfg.max_seq_len :]

            logits = self(input_ids)["logits"]  # [B, T, V]
            next_logits = logits[:, -1, :] / max(temperature, 1e-8)

            if top_k is not None and top_k > 0:
                v, _ = torch.topk(next_logits, k=min(top_k, next_logits.size(-1)))
                cutoff = v[:, -1].unsqueeze(-1)
                next_logits = torch.where(next_logits < cutoff, torch.full_like(next_logits, float("-inf")), next_logits)

            probs = F.softmax(next_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)  # [B, 1]

            input_ids = torch.cat([input_ids, next_token], dim=1)

            if eos_token_id is not None:
                if (next_token == eos_token_id).all():
                    break

        return input_ids


# -----------------------------
# Quick sanity test
# -----------------------------
if __name__ == "__main__":
    cfg = MiniLlamaConfig(
        vocab_size=50257,
        max_seq_len=384,
        d_model=1024,
        n_layer=24,
        n_head=16,
        n_kv_head=16,   # set <16 for GQA
        d_ff=4096,
        dropout=0.1,
        tie_weights=True,
    )

    model = MiniLlamaForCausalLM(cfg)
    x = torch.randint(0, cfg.vocab_size, (2, 64))
    out = model(x, labels=x)
    print("logits:", out["logits"].shape, "loss:", float(out["loss"]))