import tiktoken
import torch

enc = tiktoken.get_encoding("gpt2")

def tokenize_text(text: str):
    return enc.encode(text)

def pack_sequences(tokens, block_size):
    sequences = []
    for i in range(0, len(tokens) - block_size, block_size):
        chunk = tokens[i:i+block_size]
        sequences.append(chunk)
    return sequences
