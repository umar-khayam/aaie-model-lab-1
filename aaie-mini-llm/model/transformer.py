import torch
import torch.nn as nn
import torch.nn.functional as F
from model.attention import CausalSelfAttention
from model.embeddings import TokenEmbedding
from model.lm_head import LMHead


class MLP(nn.Module):
    def __init__(self, d_model: int, d_ff: int, dropout: float):
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_ff, bias=False)
        self.fc2 = nn.Linear(d_ff, d_model, bias=False)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.fc2(x)
        return self.drop(x)


class Block(nn.Module):
    def __init__(self, d_model: int, n_head: int, d_ff: int, dropout: float):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_head, dropout)
        self.ln2 = nn.LayerNorm(d_model)
        self.mlp = MLP(d_model, d_ff, dropout)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x

class MiniGPT(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        max_seq_len: int,
        d_model: int,
        n_head: int,
        n_layer: int,
        d_ff: int,
        dropout: float,
        tie_weights: bool = True,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len

        self.embed = TokenEmbedding(vocab_size, d_model, dropout)
        self.blocks = nn.ModuleList([
            Block(d_model, n_head, d_ff, dropout) for _ in range(n_layer)
        ])
        self.ln_f = nn.LayerNorm(d_model)

        # tie output head to token embeddings if requested
        self.lm_head = LMHead(d_model, vocab_size, tie_weights, self.embed.emb)

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        x = self.embed(idx)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            # causal LM shift
            logits_shifted = logits[:, :-1, :].contiguous()
            targets_shifted = targets[:, 1:].contiguous()

            loss = torch.nn.functional.cross_entropy(
                logits_shifted.view(-1, logits_shifted.size(-1)),
                targets_shifted.view(-1),
                ignore_index=-100
            )

        return logits, loss
