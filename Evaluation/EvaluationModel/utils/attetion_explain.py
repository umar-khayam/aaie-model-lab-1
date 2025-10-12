import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModelForCausalLM

# ----------------------------
# Attention Rollout Class
# ----------------------------

class AttentionRollout(nn.Module):
    def __init__(self, tokenizer, model, device='cuda'):
        super().__init__()
        self.tokenizer = tokenizer
        self.model = model.to(device)
        self.device = device
        self.model.eval()

    def _attention_rollout(self, attentions):
        """
        Compute cumulative attention rollout across all layers.
        attentions: tuple of (num_layers, batch, heads, seq_len, seq_len)
        """
        rollout = torch.eye(attentions[0].shape[-1], device=attentions[0].device)
        for attention in attentions:
            attn_heads_fused = attention[0].mean(dim=0)  # average heads
            attn_heads_fused += torch.eye(attn_heads_fused.shape[-1], device=attn_heads_fused.device)  # residual
            attn_heads_fused /= attn_heads_fused.sum(dim=-1, keepdim=True)  # normalize
            rollout = torch.matmul(rollout, attn_heads_fused)
        return rollout

    def forward(self, text, prompt, token_index=None):
        """
        Compute attention rollout for text segment within prompt.
        Returns:
            token_attention: attention vector for token_index
            tokens_segment: list of tokens in the text segment
        """
        # Tokenize prompt
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        outputs = self.model(**inputs, output_attentions=True)
        attentions = outputs.attentions

        # Tokenize text segment
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        text_tokens = self.tokenizer.tokenize(text)

        def normalize_token(t):
            return t[1:] if t.startswith('Ġ') else t

        text_norm = [normalize_token(t) for t in text_tokens]

        # Find segment in full tokens
        for i in range(len(tokens)):
            slice_norm = [normalize_token(t) for t in tokens[i:i+len(text_tokens)]]
            if slice_norm == text_norm:
                start_idx = i
                end_idx = i + len(text_norm)
                break
        else:
            raise ValueError("Could not find text tokens in prompt")

        # Compute rollout
        rollout = self._attention_rollout(attentions)

        # Slice to segment
        rollout_segment = rollout[start_idx:end_idx, start_idx:end_idx]

        if token_index is None:
            token_index = rollout_segment.shape[0] - 1  # last token
        token_attention = rollout_segment[token_index]

        tokens_segment = tokens[start_idx:end_idx]
        return token_attention, tokens_segment

# ----------------------------
# Attention Weight Class
# ----------------------------
class AttentionWeight(nn.Module):
    def __init__(self, tokenizer, model, device='cuda'):
        super().__init__()
        self.tokenizer = tokenizer
        self.model = model.to(device)
        self.device = device
        self.model.eval()

    def get_attention_weights(self, text, prompt, layer=0, head=0):
        """
        Compute attention weights for the text segment within the prompt.
        Args:
            text (str): The target text segment.
            prompt (str): The full input prompt.
            layer (int or list): Which layer(s) to use. Default 0 (first layer).
            head (int or list): Which head(s) to use. Default 0 (first head).
        Returns:
            attn_segment: tensor of shape (seq_len, seq_len)
            tokens_segment: list of tokens corresponding to the segment
        """
        # Tokenize the full prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Forward pass to get attentions
        outputs = self.model(**inputs, output_attentions=True, return_dict=True)
        attentions = outputs.attentions  # tuple: (num_layers, batch, heads, seq_len, seq_len)

        # Tokenize
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        text_tokens = self.tokenizer.tokenize(text)
        
        # Normalize tokens (remove leading Ġ if present)
        def normalize_token(t):
            return t[1:] if t.startswith('Ġ') else t
        text_norm = [normalize_token(t) for t in text_tokens]

        # Locate segment in full tokens
        for i in range(len(tokens)):
            slice_norm = [normalize_token(t) for t in tokens[i:i+len(text_tokens)]]
            if slice_norm == text_norm:
                start_idx = i
                end_idx = i + len(text_norm)
                break
        else:
            raise ValueError("Could not find text tokens in full prompt tokens")

        # Slice attention for the segment
        if isinstance(layer, int):
            layers = [layer]
        else:
            layers = layer

        attn_segment = 0
        for l in layers:
            layer_attn = attentions[l][0]  # shape: (heads, seq_len, seq_len)
            if isinstance(head, int):
                head_attn = layer_attn[head]  # single head
            else:
                head_attn = layer_attn[head].mean(dim=0)  # average multiple heads
            attn_segment += head_attn[start_idx:end_idx, start_idx:end_idx]

        # Average if multiple layers
        attn_segment /= len(layers)

        tokens_segment = tokens[start_idx:end_idx]

        return attn_segment, tokens_segment

