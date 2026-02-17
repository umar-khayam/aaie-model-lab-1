# Mini LLM Architecture Design (<100M parameters)

*Trimester 3, 2025*

Planner task: [Link to MS Planner](https://planner.cloud.microsoft/webui/v1/plan/uYcXdi9j10q2XjnDautR7MgAFL1s/view/board/task/WiVQlvp1C0WhkgEqxZ0i_sgAFAmc?tid=d02378ec-1688-46d5-8540-1c28b5f470f6).  

**Project Leads:** Thai Ha NGUYEN, David Tenni, Matthew O’Donnell.  
**Document contribution:** Thai Ha NGUYEN.

*This is a part of **Phase 1: Architecture & Setup***

# 1. Design objectives & constraints

**Goal:**
Design a compact, research-friendly language model that:

* Has **fewer than 100M parameters** (target range: ~60–80M, depending on vocabulary size)
* **Fits comfortably on a single GPU with ≤24GB VRAM** (ideally 16GB) for both **training and inference**
* Is **simple and transparent** enough for:

  * experimentation with fine-tuning,
  * ablation studies (e.g., optimistic initialization, new actions, safety, etc.),
  * reproducible research within an academic environment

**Core design choice:** a **small, decoder-only Transformer** (GPT-style), optimized for:

* **Next-token prediction** and general language modelling
* Compatibility with common research codebases (Hugging Face, nanoGPT, LLaMA-style implementations)
* Future extension to **instruction tuning**, **RL fine-tuning**, and **action-augmented policies**

# 2. High-level architecture: decoder-only Transformer

We adopt a **unidirectional (causal) decoder-only Transformer**, similar in spirit to GPT-2–style models:

* **No encoder**: the model is a single stack of Transformer decoder blocks.
* **Causal self-attention**: each token attends only to previous tokens.
* **Autoregressive training objective**: predict the next token given all previous tokens in the sequence.

This design is:

* **Standard in modern LLM research**, making the model architecture compatible with existing methods, tools, and papers.
* **Simpler than encoder–decoder** architectures (e.g., T5, BART), lowering implementation complexity and making it easier to reason about the behaviour of the model and its modifications.
* **Well-suited to RL-style extensions** (e.g., using the model as a policy over actions expressed as tokens, or coupling it with value heads).

# 3. Detailed architecture specification

## 3.1 Core hyperparameters (baseline proposal)

* **Number of layers (Transformer blocks):** `L = 6`
* **Model (hidden) dimension:** `d_model = 512`
* **Number of attention heads:** `n_heads = 8`

  * Head dimension: `d_head = d_model / n_heads = 512 / 8 = 64`
* **Feed-forward dimension (FFN inner size):** `d_ff = 2048`
* **Maximum context length:** e.g. `T = 1024` tokens (can be tuned)
* **Parameter budget:** ~60–80M (depending mainly on vocabulary size)

These values are chosen to balance:

* **Expressive capacity** sufficient for meaningful experiments and downstream tasks.
* **Low memory footprint**, suitable for 16GB–24GB VRAM even with optimizer states and activations.
* **Fast iteration**: small enough that training runs and ablation studies complete in reasonable time.

## 3.2 Tokenization & vocabulary

* **Tokenizer:** Subword-based (e.g., SentencePiece / BPE).
* **Vocabulary size (example):**

  * Let $ V \in [50,000, 80,000] $  (e.g., 50k or 80k tokens).
* The vocabulary size will directly influence the total parameter count via the embedding and output projection matrices.

## 3.3 Embeddings & positional encoding

* **Token embeddings:**

  * Matrix $ E \in \mathbb{R}^{V \times d_{\text{model}}} $
  * Each token id $ t $ is mapped to an embedding vector $ E_t \in \mathbb{R}^{d_{\text{model}}} $.

* **Positional encodings:**

  * Either **learned positional embeddings**
    $ P \in \mathbb{R}^{T_{\max} \times d_{\text{model}}} $,
    added to the token embeddings;
  * Or **rotary position embeddings (RoPE)**, applied within attention.
  * For simplicity and compatibility, learned positions or RoPE are both acceptable; the choice can be documented in implementation.

* **Input representation:**

  For token index $i$ with id $t_i$, the input to the first layer is:
  $x_i^{(0)} = E_{t_i} + P_i$

## 3.4 Transformer block structure

Each of the `L = 6` layers is a standard decoder block with:

1. **Pre-normalisation** (RMSNorm / LayerNorm)
2. **Multi-Head Causal Self-Attention (MHSA)**
3. **Residual connection**
4. **Pre-normalisation**
5. **Feed-Forward Network (FFN)**
6. **Residual connection**

Formally, for layer $\ell \in {1, \dots, L}$:

1. **Attention sub-layer:**
   $h' = \text{MHSA}(\text{Norm}_1(h)) + h$

2. **FFN sub-layer:**
   $h^{\text{out}} = \text{FFN}(\text{Norm}_2(h')) + h'$


Where:

* **MHSA (Multi-Head Self-Attention)** splits $h \in \mathbb{R}^{T \times d_{\text{model}}}$ into `n_heads` heads of dimension `d_head`, and uses causal masks so each position only attends to positions $\leq i$ .

* **Feed-Forward Network (FFN):**

  $\text{FFN}(x) = W_2 ,\sigma(W_1 x + b_1) + b_2$
  with

  * $W_1 \in \mathbb{R}^{d_{\text{ff}} \times d_{\text{model}}}$
  * $W_2 \in \mathbb{R}^{d_{\text{model}} \times d_{\text{ff}}}$
  * Activation $\sigma$: e.g., GELU or SwiGLU.

## 3.5 Output head & tying

* Apply a final **normalisation layer** to the last hidden state $h^{(L)}$.

* Project to vocabulary logits:

  $z_i = h_i^{(L)} W_{\text{out}}^\top + b_{\text{out}},
  \quad W_{\text{out}} \in \mathbb{R}^{V \times d_{\text{model}}}$

* To reduce parameter count and improve training stability, we **tie the output projection weights with the input embedding**:

  $W_{\text{out}} = E$

  (bias $b_{\text{out}} \in \mathbb{R}^{V}$ is optional.)

* **Training objective:** standard **cross-entropy loss** for next-token prediction:
  
  $\mathcal{L} = -\frac{1}{N} \sum_{i=1}^N \log p(t_i \mid t_{<i})$

  where $N$ is the number of tokens in the batch.

## 4. Parameter count estimation

Let:

* $V$ = vocabulary size (e.g. 50k–80k)
* $d = d_{\text{model}} = 512$
* $d_{\text{ff}} = 2048$
* $L = 6$

**Per-layer parameters (approximate):**

1. **Multi-Head Attention:**

* Q, K, V projections: $3 \times d \times d$
* Output projection: $d \times d$

Total attention weights per layer:
$\text{Attn params} \approx 4 d^2$

2. **Feed-Forward Network:**

* $W_1: d \times d_{\text{ff}}$
* $W_2: d_{\text{ff}} \times d$ 

Total FFN weights per layer:

$\text{FFN params} \approx 2 d \times d_{\text{ff}}$

3. **Norm parameters:**
   Small compared to the above (on the order of $O(d)$), can be ignored in rough counts.

**Total per layer:**

$\text{Layer params} \approx 4d^2 + 2d d_{\text{ff}}$


Plugging in $d = 512, d_{\text{ff}} = 2048$:

* $4d^2 = 4 \times 512^2 = 4 \times 262,144 \approx 1.05M$
* $2 d d_{\text{ff}} = 2 \times 512 \times 2048 \approx 2.10M$

So per layer: $\approx 3.15M \text{ parameters}$


For $L = 6$ layers: $6 \times 3.15M \approx 18.9M$

**Embeddings & output head:**

* **Token embedding matrix**: $V \times d$
* With **weight tying**, we do not add a separate large output matrix; we re-use the embeddings.

Example:

* If $V = 80,000$:
  $V \times d = 80,000 \times 512 \approx 40.96M$
  

* Positional embeddings (if learned):
  $T_{\max} \times d = 1024 \times 512 \approx 0.52M$

**Total model parameters (approximate):**

$\text{Total} \approx \underbrace{V d}_{\text{embeddings \& LM head}} + \underbrace{L(4d^2 + 2d d*{\text{ff}})}_{\text{Transformer blocks}} + \text{(norms, biases)}$

Using $V = 80k$:

* Embeddings: ~41M
* Transformer blocks: ~19M
* Misc: ~1–2M

**Total: ~60–62M parameters**

This satisfies the **<100M** requirement and matches the target **60–80M** range. With a smaller vocabulary (e.g., 50k), total parameters will be closer to **45–50M**, providing even more memory headroom.

## 5. VRAM & compute considerations (16–24GB GPUs)

With ~60M parameters:

* **Parameter memory (FP16 / bfloat16):**

  $60M \times 2 \text{ bytes} \approx 120 \text{MB}$

* **Optimizer states (e.g., Adam, FP32 + moments):**

  Typically ~4–6× parameter size → on the order of a few hundred MB.

The **dominant VRAM usage** comes from:

* Activations for **batch size × sequence length × hidden size**
* Gradients for backpropagation
* Adam states

For a 16GB GPU, this model should support (rough estimates):

* **Sequence length:** 512–1024 tokens
* **Global batch size:** on the order of 64–256 tokens per step (depending on implementation, gradient accumulation, and precision)

For a 24GB GPU, larger batches and/or longer context lengths are feasible.

This architecture therefore:

* **Comfortably fits on 16GB VRAM** with mixed-precision training
* Leaves headroom for:

  * RL heads or auxiliary value heads
  * LoRA adapters or additional small modules
  * Logging / monitoring overhead

## 6. Justification: small decoder-only Transformer for research compatibility

Using a **small decoder-only Transformer** has several advantages in the context of your research goals:

1. **Alignment with mainstream LLM research**

   * The majority of open-source and academic work on LLMs (GPT-2, GPT-Neo, LLaMA, Mistral, etc.) is based on **decoder-only, autoregressive** models.
   * This architecture makes it easy to:

     * Reuse **pre-existing tooling** (Hugging Face, nanoGPT, transformer libraries).
     * Implement techniques from recent papers without major architectural changes.

2. **Simplicity & interpretability**

   * Decoder-only models have a **single stack** of blocks and a clear autoregressive training objective.
   * Easier to:

     * Understand the effect of architectural tweaks (e.g., changing initialisation, adding new actions).
     * Implement **ablation studies** and interpret results.
     * Teach and document for an academic audience.

3. **Compatibility with RL and action-extended settings**

   * Many RL + LLM approaches treat the model as a **policy over token sequences**.
   * Your research on **expanding action spaces**, **optimistic initialisation**, and **model-based transitions** can be naturally integrated by:

     * Mapping discrete actions to tokens or token-like embeddings.
     * Using the same architecture backbone for both language and action prediction.
   * A small decoder-only model is computationally light enough to:

     * Run multiple training runs,
     * Compare different initialization schemes,
     * Explore safety-aware modifications without prohibitive cost.

4. **Resource efficiency**

   * Sub-100M parameter models are **realistic to train and fine-tune** in a university setting:

     * Can be trained from scratch or heavily fine-tuned on a **single 16–24GB GPU**.
     * Shorter iteration cycles → more rapid experimentation and learning.
   * Reduces dependence on large proprietary models or cloud budgets.

5. **Extensibility**

   * Once the core mini-LLM is stable, it is straightforward to:

     * Scale up depth or width (e.g., 12 layers, 768 hidden size) while keeping the same design.
     * Add **LoRA adapters**, **prefix-tuning**, or **task-specific heads**.
     * Integrate **RAG**, **safety filters**, or **hallucination detection** as separate modules around the same backbone.

## 7. Possible extensions / modifications

Within the same architecture family, we may consider:

* **Depth vs. width trade-offs:**

  * If you need more capacity but still want <100M parameters, you can:

    * Increase layers (e.g., 8–10) but slightly reduce $d_{\text{model}}$, or
    * Keep 6 layers and increase $d_{\text{ff}}$ for stronger FFN.
* **Alternative normalisation:**

  * Prefer **RMSNorm** for stability and compatibility with modern LLMs.
* **Activation functions:**

  * Use **GELU** or **SwiGLU** in FFN layers for better performance.
* **Context length:**

  * Start with 512 or 1024 tokens; later experiments can explore longer contexts if VRAM allows.

These are all **incremental changes** around the same core decoder-only Transformer, keeping the design aligned with your initial constraints and research goals.


