import torch

def rotate_half(x):
    x1 = x[..., :x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2:]
    return torch.cat([-x2, x1], dim=-1)


def apply_rope(q, k, seq_len, base=10000):
    """
    q, k: (B, nh, T, hd)
    """
    device = q.device
    head_dim = q.shape[-1]
    assert head_dim % 2 == 0, "RoPE head_dim must be even"

    half_dim = head_dim // 2

    freq_seq = torch.arange(half_dim, device=device, dtype=torch.float32)
    inv_freq = 1.0 / (base ** (freq_seq / half_dim))

    positions = torch.arange(seq_len, device=device, dtype=torch.float32)
    sinusoid = torch.einsum("i,j->ij", positions, inv_freq)

    sin = sinusoid.sin()[None, None, :, :]
    cos = sinusoid.cos()[None, None, :, :]

    q1, q2 = q[..., :half_dim], q[..., half_dim:]
    k1, k2 = k[..., :half_dim], k[..., half_dim:]

    q = torch.cat([q1 * cos - q2 * sin, q1 * sin + q2 * cos], dim=-1)
    k = torch.cat([k1 * cos - k2 * sin, k1 * sin + k2 * cos], dim=-1)

    return q, k
