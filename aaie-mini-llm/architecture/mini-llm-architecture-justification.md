# Mini LLM Architecture for Student Feedback Generation

## Architecture Specification and Rationale

The proposed model is a decoder-only Transformer with extremely small scale, designed for efficient training and inference on modest hardware (single GPUs with 16–24GB VRAM). Table 1 summarizes the architecture:
| **Component**             | **Specification**                     |
| ------------------------- | ------------------------------------- |
| **Transformer Layers**    | 6 decoder blocks                      |
| **Hidden Size (d_model)** | 512                                   |
| **Attention Heads**       | 8 (head dimension 64 each)            |
| **Feedforward (FFN) Dim** | 2048 (approximately 4× hidden)        |
| **Context Window**        | 1024–2048 tokens (configurable)       |
| **Total Parameters**      | ~60–80 million (including embeddings) |

This design (6 layers, 512 hidden) is much smaller than typical large language models, but it closely mirrors configurations used in research for small-scale LLMs. For example, EleutherAI’s Pythia-70M model also uses 6 layers with 512-dimensional embeddings and 8 heads. Such a lightweight architecture is feasible to train on a single modern GPU and to deploy with low latency. We choose a decoder-only format (like GPT-2/GPT-3 style) because feedback generation is essentially a single-turn text generation task: the model will read a student’s work (included in the prompt) and then produce feedback as a continuation. An encoder-decoder (like T5) is not strictly necessary and would nearly double the parameter count for the same model dimension. By using a decoder-only Transformer, we keep the model compact and training procedure straightforward.

Why these specific hyperparameters? A hidden size of 512 with 8 attention heads balances capability and memory footprint. The feed-forward dimension of 2048 follows the 1:4 ratio typical in Transformers, providing sufficient intermediate capacity without excessive parameters. With ~60–80M total parameters, the model is small enough to fit <1 GB of memory in half-precision, which is trivial on a 16GB GPU. This means we can use reasonably large batch sizes or longer sequences even on limited hardware. The context length is set to 1024 or 2048 tokens to comfortably handle a student’s answer plus lengthy feedback, aligning with standard LLM context lengths (Pythia-70M and GPT-2 used 1024–2048 tokens context). We also adopt modern design improvements such as pre-normalization (LayerNorm or RMSNorm before attention/FFN) and Rotary Positional Embeddings (RoPE) for encoding sequence position, as used in LLaMA2 and TinyLlama. These choices improve training stability and allow better generalization to longer sequences without increasing parameter count.

Overall, using a small decoder-only Transformer is justified by the targeted use case: generating written feedback for students. This task domain is narrower than open-ended chat or code generation, so a smaller model can be sufficient after fine-tuning, provided it has seen relevant language during training. The simplicity and low cost of this architecture make it ideal for research and educational settings where resources are limited.

## Justification for a Small Model in Education

Focusing on a smaller language model (<100M parameters) has several key advantages for educational use:

*  **Research Accessibility**: Small models are much easier to train and experiment with. Educators and researchers can train or fine-tune this 60M model on a single GPU or even a high-end laptop, without needing enormous GPU clusters. This greatly lowers the barrier to entry. As Microsoft’s Phi-2 project noted, a compact model becomes “an ideal playground for researchers” to explore and refine techniques. Likewise, IBM emphasizes that small language models (SLMs) enable experimentation “without having to invest in multiple GPUs or specialized hardware”. This accessibility is crucial in academic settings.

* **Efficiency and Speed**: With fewer parameters, training is faster and inference has lower latency. This model can be trained on fewer tokens or fewer epochs and still converge quickly. Deployment is also efficient – the model can generate feedback for many students in parallel with minimal delay. Small models are less resource-intensive, allowing swift deployment even on local servers. In practice, a ~60M model will have response times and GPU memory usage far below that of multi-billion-parameter models, enabling real-time interactive feedback generation in classrooms.

* **Sufficient Performance on Focused Tasks**: Importantly, a well-trained small model can achieve strong performance on specific tasks even if it cannot match large models generally. For example, DistilGPT-2 (a 82M parameter GPT-2 compression) retains over 95% of the larger model’s language generation capability despite being 40% smaller. Similarly, carefully optimized “small” models like Microsoft’s Phi-2 (2.7B) have outperformed much larger 7B–13B models on certain benchmarks by virtue of high-quality training data. This demonstrates that bigger isn’t always better – with strategic data curation and tuning, smaller models can rival larger ones in their domain. In our case, the model will be specialized for educational feedback, which is a narrower domain than general chat; this specialization can help the small model excel at the task.

* **Cost and Sustainability**: Training and serving a 60M model is far cheaper than a multi-billion parameter one. This is beneficial for educational institutions with limited budgets. It also means less energy consumption, aligning with sustainability goals (smaller models have a lower carbon footprint). Moreover, the model’s size allows deploying it on local machines or campus servers, avoiding ongoing API costs.

* **Privacy and Data Control**: In education, student data privacy is paramount. A small model can be deployed on-premises (e.g. on a school’s own server or teacher’s device) rather than relying on cloud API calls. Its small size makes on-prem deployment feasible and secure. IBM notes that because of their compactness, SLMs can be run in private environments, giving improved data protection. This means student submissions and feedback stay local, addressing privacy concerns in classroom use.

* **Reduced Risk and Interpretability**: A smaller model is easier to audit and align. Its limited capacity means it will have seen less raw data and will likely generate simpler, more straightforward text, which is desirable for clear student feedback. It’s also easier to analyze what a small model has learned or where it fails, facilitating research into interpretability and bias in the educational context. (Of course, one must still guard against issues like knowledge gaps or hallucinations – small models have less factual knowledge capacity, so ensuring the model doesn’t give incorrect feedback is a consideration.)

In summary, a mini-LLM is well-suited for educational applications where the goal is not to have a model that knows everything, but one that can be trained to reliably perform a specific supportive role (providing feedback). The combination of accessibility, low cost, and adequate performance makes the proposed 60–80M model a practical choice for research and deployment in learning environments.

## Comparison with Existing Small-Scale Models

To put this 60–80M parameter model in context, Table below compares it with several existing small language models and variants:

| **Model**                   | **Params** | **Architecture**                           | **Notable Characteristics**                                                                                                           |
| --------------------------- | ---------: | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Proposed Mini (Edu)**     |       ~65M | 6 layers, 512 hidden, 8 heads, 2048 FFN    | Domain-specific (educational feedback); fits in <1GB VRAM for inference.                                                              |
| **DistilGPT-2**             |        82M | 6 layers, 768 hidden, 12 heads, ~3072 FFN  | Distilled from GPT-2 124M, ~2× faster, retains ~97% of GPT-2’s generation quality.                                                    |
| **GPT-2 Small**             |       124M | 12 layers, 768 hidden, 12 heads, 3072 FFN  | OpenAI GPT-2 baseline model (2019); good general text generation, but requires ~0.5GB VRAM.                                           |
| **EleutherAI Pythia-70M**   |        70M | 6 layers, 512 hidden, 8 heads, 2048 FFN    | Small GPT-NeoX model trained on ~300B tokens (The Pile); used as a research baseline.                                                 |
| **EleutherAI GPT-Neo 125M** |       125M | 12 layers, 768 hidden, 12 heads, 3072 FFN  | GPT-Neo (similar to GPT-2 architecture) released in 2021; requires ~0.5GB VRAM, moderate performance.                                 |
| **Meta OPT-125M**           |       125M | 12 layers, 768 hidden, 12 heads, 3072 FFN  | Meta’s open model (2022) with 125M parameters, meant as a small baseline for OPT family.                                              |
| **TinyLlama 1.1B**          |       1.1B | 22 layers, 2048 hidden, 32 heads, 5632 FFN | A compact LLaMA2-style model; pretrained on 1T tokens. Strong performance among 1B models, outperforming older 1.3B baselines.        |
| **Microsoft Phi-2**         |       2.7B | ~32 layers, ~2560 hidden (est.)            | A “small” model that *outperforms some 7B–13B models* on reasoning benchmarks via high-quality training; requires ~11GB VRAM to load. |

Despite being much smaller than mainstream LLMs, our proposed model falls in the range of published research models. Notably, it is architecturally identical to Pythia-70M, which has 6 layers and ~70M params. Pythia-70M was trained on a large general corpus (The Pile) and serves as evidence that such a small Transformer can learn coherent language patterns. Of course, its performance on broad tasks is modest compared to multi-billion models, but it provides a solid starting point for fine-tuning on a specific domain. For instance, Pythia-70M achieves much lower perplexity than a 12M or 30M model on the Pile, showing the jump to ~70M greatly improves basic language fluency.

Looking at DistilGPT-2, we see a closely related example: it has 6 layers (like our model) but a larger hidden size (768). It was created by distilling the knowledge of GPT-2 and manages to maintain high generation quality. This suggests that with the right training approach (e.g. distillation or fine-tuning on good data), a 60–80M model can produce qualitatively useful text. DistilGPT-2 is used in practice for tasks requiring faster or lighter-weight generation, which is analogous to our goals in the educational context.

Comparing to slightly larger baselines, GPT-Neo 125M and OPT-125M (125 million parameters each) are roughly 2× our model’s size. They have 12 layers and higher d_model (768). These 125M models were often the “smallest” foundation models in open releases from EleutherAI and Meta, and they typically require around 2× the VRAM and compute of our 65M model to train or infer. Their performance on language tasks is a bit better, but not dramatically so; for example, OPT-125M’s average accuracy on some language understanding tasks was significantly below OPT-1.3B in Meta’s report, indicating diminishing returns below a few hundred million parameters for broad knowledge. By focusing on a narrower task and leveraging domain data, we expect our ~65M model to close the gap in the specific area of feedback generation.

The table also lists TinyLlama-1.1B and Phi-2 (2.7B) as examples of the emerging trend to maximize performance of “small” models (relative to GPT-3 scale) through data and training innovations. TinyLlama is built on a scaled-down LLaMA2 architecture and trained on an immense dataset (~1 trillion tokens). It achieves state-of-the-art results among ~1B parameter models, even exceeding older 1.3B models on reasoning benchmarks. This reinforces the idea that training data quality and quantity can compensate for size. Similarly, Phi-2 uses a curated “textbook quality” training set and knowledge transfer techniques to outperform models nearly 5× larger on certain tasks. While our 65M model cannot rely on scale, it can draw inspiration from these projects by heavily focusing on high-quality educational data (discussed later) to punch above its weight. These comparisons underscore that a well-designed 60–80M model, optimized for a specific niche, is a viable approach.

In terms of compute requirements, the proposed model is extremely light. It will occupy roughly 0.25 GB of memory (fp16 weights) when loaded, compared to ~2.2 GB for TinyLlama-1.1B or ~10.8 GB for Phi-2. Training the model from scratch is practical on a single 16 GB GPU – for example, Pythia-70M was trained with batch size 2M tokens on 8x A100 GPUs, but one could train with smaller batches or use gradient accumulation on a single GPU if needed. Fine-tuning the model on an educational dataset would be even less demanding, possibly doable on a lower-end GPU (or even CPU in a pinch, albeit slowly). This low resource footprint is a major advantage over any multi-billion parameter model for an academic team or school IT department.

## Training and Inference Stack Recommendations

To implement and train this mini-LM efficiently, we suggest using a modern PyTorch-based stack with libraries that offer optimized Transformer operations. Key recommendations include:

* Framework & Model Implementation: Use PyTorch along with the Hugging Face Transformers library. Hugging Face provides ready implementations for decoder-only Transformer architectures, and a configuration can be created for a 6-layer, 512-hidden model. This saves development time and ensures compatibility with pretrained components or tokenizer pipelines. The AutoModelForCausalLM and Trainer APIs can handle most of the training loop boilerplate (or one can use PyTorch Lightning/Accelerate for more customization).

* Attention Optimization: Integrate FlashAttention for faster training on GPUs. FlashAttention is a technique that reimplements the attention calculation to minimize memory reads/writes, achieving significantly better speed and memory efficiency. By using a FlashAttention-enabled kernel (such as through the HuggingFace torch.scaled_dot_product_attention in PyTorch 2.x or via the xFormers memory_efficient_attention flag), the model can handle longer context (1-2k tokens) with much less GPU memory. In benchmarks, FlashAttention yields up to 2.4× training speedup on sequence lengths around 1k, which will be beneficial if we use, say, 1024 token sequences during training. It also avoids storing the large attention matrix, drastically cutting the memory footprint for backpropagation. Given our model aims at 1024+ token context, this optimization ensures we maximize throughput on 16GB VRAM.

* Mixed Precision Training: Utilize FP16 or bfloat16 precision during training (supported via PyTorch’s autocast or the Trainer’s fp16=True flag). Mixed precision will cut memory usage roughly in half and often increase training speed due to tensor core utilization, with negligible impact on model quality. Since our model is already small, mixed precision makes it even easier to fit larger batches or longer sequences in memory.

* Batching and Data Loading: Use the Hugging Face Datasets library or PyTorch’s DataLoader for efficient data pipeline. We can tokenize inputs in advance (to avoid bottlenecks at runtime) and use dynamic padding or bucketing to group sequences of similar lengths together, minimizing padding waste. For a small model, we can often use fairly large batch sizes (depending on sequence length, e.g. batch of 128 or 256 short sequences) to speed up training.

* Distributed Training (if needed): Although single-GPU training is feasible, if a multi-GPU setup is available, frameworks like PyTorch Distributed Data Parallel (DDP) or DeepSpeed can be used. DeepSpeed’s stage 1 or 2 optimizations would easily handle a 65M model, but frankly for this scale the overhead may not be worth it unless doing extremely large batches. Still, if one wanted to train on say 4 GPUs to finish epochs faster, enabling DDP is straightforward with Hugging Face Trainer (just launch with multiple processes). The model’s gradient memory is small, so even multi-GPU with data parallelism will scale efficiently.

* Inference: For deployment, the model can be loaded with the Transformers library and run in half-precision. Inference for a single instance will be very fast (due to shallow depth), and can be made even faster with techniques like quantization. For example, using 8-bit or 4-bit quantization (via tools like Hugging Face bitsandbytes integration or [GPTQ]) would reduce memory to a few hundred MB or less, allowing the model to potentially run on CPU or edge devices. However, even without quantization, a 65M model can serve dozens of requests per second on a single GPU. Low latency means a student can get feedback almost instantly after submission.

    * Libraries & Tools: In summary, a possible stack could be:

    * Model & Training: PyTorch + HuggingFace Transformers (for model definition, training loop).

    * Acceleration: FlashAttention (fast attention kernels), PyTorch 2.x (for compiler optimizations, if any), DeepSpeed or Accelerate (if doing multi-GPU or to use ZeRO-offloading for larger batches).

    * Memory Optimization: Gradient Checkpointing (if we push context length very high, checkpointing can save memory by recomputing activations), though for 6 layers this likely isn’t needed.

    * Inference Serving: Transformers pipelines or a lightweight Flask/FastAPI service using the model; optionally ONNX export or TorchScript if seeking slightly more speed on CPU.

    * By leveraging these modern tools, we ensure that training our mini model is as smooth as training a larger model – just much faster. For instance, we could fine-tune this 60M model on a new dataset in a matter of a couple of hours on a single GPU, whereas a 6B model would take days on a multi-GPU cluster. The small scale lets us iterate quickly, which is ideal for research and for tuning the model’s behavior (e.g. adjusting how it words feedback).

## Tokenizer Choice and Design

A crucial part of the model design is the tokenizer, which converts text to the token IDs that the Transformer will use. We recommend using a subword tokenizer (either Byte-Pair Encoding or Unigram) tailored to the language of educational content (presumably English, unless a multilingual setting is needed). Key considerations for the tokenizer are:

* Vocabulary Size: Use a moderate vocabulary (on the order of 30k to 50k tokens). This ensures most common words and phrases in the educational domain are represented as single tokens, while keeping the embedding matrix size reasonable. A large vocab (100k+) would inflate the parameter count (each additional 1k tokens adds 512k parameters to embeddings), whereas a very small vocab (e.g. 10k) would break words too much and lengthen sequences. Around 30k is a sweet spot for English for a model of this size. Notably, LLaMA and TinyLlama employed a 32k vocab, and GPT-2 uses ~50k; we can choose in this range based on corpus analysis.

* Existing vs. Custom Tokenizer: We have two approaches:

    1. Reuse an existing tokenizer: For example, adopt the GPT-2 tokenizer (which is BPE-based, 50k vocab trained on WebText) or the LLaMA-2 tokenizer (which is SentencePiece BPE with 32k vocab). Using a well-established tokenizer is convenient and ensures compatibility with any available pretrained embeddings or data. LLaMA’s tokenizer is trained on a mix of internet text and might handle code and multi-lingual bits; GPT-2’s is English-centric with bytes fallback. Both will work reasonably for our task (since student feedback is formal-ish English).

    2. Train a custom tokenizer on our dataset: This could yield slight efficiency gains. We would gather a representative text corpus of educational data (see next section) and train a new SentencePiece model. This can capture domain-specific terms (e.g. “thesis statement”, “quadratic formula”) as single tokens if they appear often, or split rare proper nouns in a sensible way based on our data distribution. A custom tokenizer might also handle things like formatting (bullet points, math symbols, etc.) better if those are prevalent in educational text.

In practice, a custom tokenizer is recommended if the domain has a lot of unique jargon or formatting. For general educational feedback (which is mostly normal English sentences with maybe some academic terms), an existing tokenizer like GPT-2’s might already be sufficient. For example, if a lot of data comes from Wikipedia and scholarly texts, using a tokenizer trained on similar data (like GPT-2’s WebText or LLaMA’s mix) is fine.

* Handling Domain-Specific Tokens: If the feedback generation format needs special tokens, we should include them. For instance, if we adopt an instruction-following style where prompts are like: "\[STUDENT\] ... \[TEACHER\] ...", we might introduce special tokens for \[STUDENT\] and \[TEACHER\] or newline markers. These can be added to the tokenizer’s vocabulary so the model can learn to handle them explicitly. Another example: if feedback often cites grades or uses alphanumeric identifiers (like “Q1” for Question 1), the tokenizer should ideally treat "Q1" as one token or "Q" and "1" separately rather than breaking into random bytes. We can ensure such patterns are handled by including some in the training corpus for the tokenizer.

* Casing and Text Normalization: We will likely keep the tokenizer case-sensitive (so “German” vs “german” remain distinct tokens, preserving proper noun capitalization which can be important in writing feedback). We also keep punctuation and basic formatting symbols, as feedback often involves complete sentences and sometimes lists. Standard pre-processing (lowercasing, removing punctuation) is not done since modern subword tokenizers handle full text. We only need to maybe normalize Unicode (the SentencePiece library can do this) so that accent characters or special quotes are standardized.

* Byte-Fallback (UTF-8) Handling: Most contemporary tokenizers (GPT-2, SentencePiece) have a way to fall back on byte encoding for unseen characters. This ensures any uncommon symbol or foreign text can still be represented. For an education model, this is seldom needed except maybe for mathematical symbols or phonetic characters. If math appears in our data, we should ensure common math symbols (≥, ±, etc.) are either in the vocab or can be constructed. SentencePiece Unigram might break them into pieces or use byte mode. We could explicitly add tokens for frequently used domain symbols if needed.

In summary, the tokenizer should be English-optimized with domain awareness. A practical choice is to start with an existing well-tested tokenizer (for example, use the same tokenizer as Pythia or GPT-Neo for compatibility). This would give us an initial vocabulary of ~50k. If we find that too many tokens are wasted on rarely used words, or that domain terms are split, we can refine the vocab by merging or adding tokens. The goal is to maximize efficiency – e.g. the word “feedback” itself should ideally be one token, not “feed” + “back” (which it is in GPT-2’s tokenizer, actually). If training a new tokenizer, we’d verify that common educational phrases and scoring terms are not fragmented.

One final design note: by limiting vocab size, we also control parameters. For instance, a 50k vocab with 512 embedding dim is 25M parameters just in the embedding matrix. If we used only 30k vocab, that’s ~15M, freeing 10M capacity that could go to the Transformer layers or be omitted to keep model size low. Thus, a slightly smaller vocabulary (without impacting coverage too much) can help keep the total model in the ~60–70M range.

## Training Dataset Design for Educational Feedback

Training the model entails two phases: pre-training on general text to build core language ability, and fine-tuning on the educational feedback domain to specialize it. We outline a strategy for each, along with data sources and preprocessing suited for generating student feedback.

1. Pre-Training Corpus (General Language): Even a small model benefits from a broad pre-training to capture grammar, general knowledge, and fluency. We can use an existing large-scale text corpus but scaled down in size. Candidate corpora:

    * Wikipedia: High-quality, encyclopedic text covering diverse topics. Useful for factual knowledge and formal writing style.

    * Books and Literature: If available (e.g. OpenBooks corpus or Project Gutenberg texts), these provide varied narrative and expository styles. Books corpus can help the model learn long-range coherence and an instructive tone if we include textbooks or non-fiction.

    * Web Text / OpenWeb: A filtered web crawl (like Pile’s Common Crawl subset or OpenWebText which emulates GPT-2’s data) can supply informal and formal discussions. However, we should be careful to filter out toxic content or highly conversational internet slang not relevant to educational settings.

    * The Pile (EleutherAI): The Pile is a 825GB mix of texts. We might not use all of it, but parts of it are very relevant: for example, the Stack Exchange section (contains Q&A from sites like Math, StackOverflow, etc.), the PubMed Central section (academic papers), and Project Gutenberg. We could curate a smaller pile (~10–20GB) focusing on higher-quality components. Since Pythia models were trained on the Pile for ~300B tokens, using a subset of it could allow us to replicate a decent pretraining in fewer tokens for our smaller model (we likely cannot train on 300B tokens on a single GPU, but perhaps on the order of 10–50B tokens is feasible with some time).

The preprocessing for general data involves cleaning and deduplication. We should remove or downsample content that is not useful for our task (e.g. dialogue from fiction, or code snippets if we truly won't do code). Emphasize texts that are explanatory or informative, as that aligns closer to how feedback is written. We also ensure to strip any personally identifiable info if present (especially if scraping education forums).

2. Domain-Specific Data (Educational Feedback): This is critical for model specialization. We want the model to see many examples of student work and corresponding teacher feedback or explanations. Since large curated datasets in this exact format are scarce, we can combine multiple approaches:

    * Open Educational Resources: Look for datasets of student-teacher dialogues or feedback. For example, the Education Dialogue Dataset (ED) contains ~40k teacher-student conversations. These might include a teacher guiding a student, which can be repurposed as feedback-like interactions. Similarly, any datasets from educational research (such as the ACL 2020 dataset focusing on teacher feedback on writing) can provide authentic examples of feedback. The ACL dataset by Pilán et al. has teacher comments on student sentences (especially for writing errors) – this can teach the model the style of giving corrective comments.

    * Peer review and Essay feedback: If accessible, datasets where student essays are annotated with feedback or scores. For instance, some Kaggle competitions (like the Feedback Prize) provided student essays with annotated feedback segments. Those annotations could be turned into full feedback text by concatenation or using them as content pointers. Also, if there are corpora of writing center tutoring transcripts or teacher review comments, those are gold for our purpose.

    * Synthetic Data via Large Models: An effective modern strategy is to generate additional training data using a powerful LLM (like GPT-4 or Claude). We can take real student answers (perhaps from public exam samples, e.g. short answers or essays from standardized test prep materials) and prompt a large model to act as a teacher and write feedback for each. By doing this systematically, we could create a sizable training set of (student answer, teacher feedback) pairs. This approach was used by Stanford’s Alpaca (using GPT-3.5 to create instruction-following data) and could be applied here to bootstrap a domain-specific dataset. We must still vet the generated feedback for correctness (spot-check or filter out hallucinations), but large models are quite good at producing reasonable feedback if instructed properly.

    * Relevant QA and Explanations: We can broaden the scope to include any text where one party explains or gives feedback on another’s content. For example, Q&A from StackExchange (mathematics, homework help) where an expert explains the solution to a student’s question can serve as feedback examples. Also, code review comments (if programming assignments are considered educational feedback) could be included, though our focus is no code generation, so maybe we avoid heavy coding content. However, a small portion of diverse explanatory data (like StackExchange answers, which often correct misconceptions) can be very useful.

**Formatting the Training Data**: We have to decide how to present the input and output to the model during fine-tuning:

* A straightforward format is a concatenation like:
<student_answer>\n\nTeacher's Feedback: <feedback_text>
as a single text sequence. The model then learns to predict the feedback_text given the student_answer and the prompt cue. We might include a special token or delimiter to clearly separate the student answer from the feedback. For example:
\[QUESTION\] ... student text ... \[/QUESTION] \[FEEDBACK\] ... teacher feedback ...
This way the model can learn to condition on the text between \[QUESTION\] tags and then produce content for [FEEDBACK]. In deployment, we would insert a student’s answer and prompt the model to continue after the \[FEEDBACK\] tag.

* We should ensure the model sees a variety of lengths (some feedback are one sentence, some are a paragraph) and styles (direct corrections vs high-level comments) so it can adapt its output.

**Preprocessing for domain data**: Likely involves:

* Cleaning student text (remove any sensitive info or normalize any stray encoding issues),

* Possibly simplifying language in student answers if using them from complex sources so that they resemble the level the model should expect,

* Ensuring alignment: the feedback truly addresses the preceding student answer. For synthetic data, this is by construction. For found data (like forum Q&A), we might have to concatenate question + answer and label the answer as "feedback".

* Balancing the dataset: If we gather from multiple sources, we might weight them. For instance, if synthetic data is huge but somewhat homogeneous, we still want real examples in there. We could up-sample rare but important types (like feedback on math vs feedback on writing) depending on our target use cases in education.

* Quality over Quantity: Given the small model size, feeding it extremely noisy or off-topic data will waste its limited capacity. It’s better to have, say, 50k well-crafted teacher feedback examples than millions of unrelated sentences. This echoes the approach from Phi-2: focus on “textbook-quality” data to maximize the model’s effective knowledge. We should curate the fine-tuning corpus to be high-quality feedback. This might involve manual filtering or using a larger model to score candidate data for how “helpful” the feedback is. If using human-written feedback, we assume it’s generally good; if using AI-synthetic, we can prompt the AI to follow known best practices (e.g. “give at least one praise, and one specific suggestion for improvement”).

* Data Volume: How much data is needed? Pre-training could be done on, say, 20–50 billion tokens of general text if aiming for strong base (though on a single GPU, one might do fewer epochs due to time). The fine-tuning on feedback might only be a few million tokens (for instance, 100k examples of feedback averaging 50 tokens each is 5M tokens). That is plenty to teach the model the task. If we generate synthetic data, we could easily create tens of thousands of examples. It’s important not to overfit the small model on a tiny set of answers, so having diverse student queries in the fine-tuning data is key (cover different subjects: math, literature, programming, etc., if the model is expected to handle all, or focus on the relevant subject domain for your use case).

Finally, we will also prepare a validation set of educational Q&A/feedback examples to monitor training. This could include a mix of a few real teacher feedback instances and some held-out synthetic ones, to ensure the model is learning to produce correct and relevant feedback and not just memorizing responses.

## Evaluation Metrics and Benchmarks

Evaluating the quality of generated student feedback requires a combination of automated metrics and human judgment. We propose using several metrics to cover different aspects:

* BLEU (Bilingual Evaluation Understudy): Originally for machine translation, BLEU measures n-gram overlap between the model’s output and a reference feedback. It is precision-focused, checking how many of the generated words appear in the reference. In our context, if we have one or more reference feedbacks for a given student answer, BLEU can quantify how closely the model’s feedback matches the reference phrasing. A higher BLEU might indicate the model covered similar points as the reference. However, since feedback can be phrased very flexibly, BLEU is only a rough indicator (it penalizes differences in wording even if the meaning is the same). It’s still useful for consistency with NLP evaluations and if we want to compare to prior systems (e.g., if an earlier system had BLEU X on a set of reference feedback).

* ROUGE (Recall-Oriented Understudy for Gisting Evaluation): ROUGE is commonly used for summarization tasks and focuses on recall (how much of the reference’s content is recovered in the output). ROUGE-N (e.g. ROUGE-1,2) looks at overlapping n-grams, and ROUGE-L looks at longest common subsequence between output and reference. For feedback generation, ROUGE can tell us if the model is covering the key points that a reference feedback included. For example, if the reference comment mentions three specific errors and the model only mentions one, ROUGE would be low. A strong model should have high ROUGE recall, meaning it addresses many of the same issues a teacher did. Like BLEU, ROUGE requires reference outputs for comparison.

* METEOR / BERTScore / Semantic Similarity: To complement BLEU/ROUGE, which are surface-level, we can use a metric that accounts for semantic similarity. METEOR uses synonymy and paraphrase matching (and tends to correlate better with human judgment than BLEU alone for some tasks). BERTScore goes further by computing similarity in embedding space between model output and reference, effectively measuring if they are saying the same thing even with different words. These metrics would be appropriate if we have reference feedback and want to allow for wording differences. For instance, BERTScore can catch that “The essay lacks a clear thesis” vs “Your main argument isn’t clear” convey a similar critique. A high BERTScore indicates the model feedback is semantically close to the reference feedback.

* Relevance and Correctness Metrics: Beyond comparing to references, we need to ensure the feedback is relevant to the student’s work and factually correct. One approach is to use an information retrieval style metric: e.g., measure overlap of important content words between the student answer and the feedback to ensure the feedback is on-topic. If the feedback references concepts or elements not present in the student’s answer, that’s a red flag. We could define a simple relevance score by computing how many nouns/keywords from the answer appear in the feedback (this ensures the feedback talks about the student’s content). Another method is to have a classifier (or an LLM) judge whether the feedback is appropriate for the given answer. For example, we can prompt a GPT-4 to evaluate “Does this feedback correctly address the student’s solution above?” and use that as a metric (though that becomes more of a human/LLM eval than an automated metric).

* Tone and Readability Metrics: In educational feedback, how the message is conveyed is as important as the content. While harder to quantify, we can use proxy measures:

    * Politeness or Sentiment analysis to ensure feedback isn’t harsh. A sentiment score (the feedback should be generally positive or neutral, not negative) can be computed with off-the-shelf sentiment analyzers.

    * Formality measure – feedback should be professionally written. One could use a language model to classify if the tone is appropriate (or use a rule-based count of slang/informal words expecting near zero).

    * Length and Specificity – we might set desired ranges (e.g., feedback ideally 1-3 sentences for a short answer). We can track average length and perhaps measure specificity by counting how many specific points or error-types are mentioned (this might require NLP parsing or comparing to an answer key if available).

* Human Evaluation: Ultimately, human judgment is the gold standard, especially for a task as nuanced as student feedback. We should conduct evaluations where instructors or domain experts rate the model’s feedback on criteria like:

    * Correctness: Does the feedback correctly identify errors or strengths in the student’s answer? (A model could hallucinate an issue that isn’t there – that’s bad.)

    * Usefulness: Would the feedback help the student improve? Does it give actionable suggestions or just vague praise?

    * Clarity: Is the feedback clear and well-written?

    * Tone: Is it encouraging and respectful?

These can be rated on Likert scales and aggregated. Human eval can be done on a sample of outputs to provide an overall quality check that automated metrics cannot fully capture.

* Benchmark tasks: If any standard benchmark exists for educational feedback generation, that would be ideal to include. For example, if there was a shared task or competition on generating feedback (similar to a summarization or QA challenge), we would use their test set and metrics. Absent that, we can adapt related benchmarks:

    * Using a summarization metric like ROUGE on a dataset of student answers + ideal feedback (treating feedback like a “summary” of what needs improvement).

    * Using question-answering evaluation style if the feedback can be seen as answering an implied question “How did the student do and how to improve?”.

    * We could also evaluate on general language tasks to ensure the model’s language ability is decent: e.g., perplexity on a held-out set of educational text, or BLEU on a small translation of educational content if multilingual, etc., but those are secondary.

For concreteness, suppose we have a test set of 100 student answers with reference teacher comments. We would calculate BLEU, ROUGE-L, and BERTScore of the model’s feedback against the references. We might find, for instance, BLEU = 25, ROUGE-L = 0.5, BERTScore = 0.85. These numbers by themselves only mean something when compared to either another model or human performance. We could also include a baseline like “always output a generic feedback” to see how much better our model is. Ultimately, we expect our fine-tuned model to significantly outperform a generic small model (like GPT-2 out-of-the-box) on these metrics, and approach human-written feedback’s scores. However, even a model that scores lower on overlap metrics might still be effective if it provides correct advice in different words – hence the need for careful human or qualitative evaluation.

In addition, we should monitor improvement-oriented metrics: does the feedback, when applied, actually help improve student outcomes? This is the true end-goal benchmark. If possible, one could conduct an experiment where students or surrogate models revise their answers based on the feedback, and then measure the improvement (perhaps via a grader model or human grading). This kind of evaluation is complex but very insightful: it closes the loop by showing the feedback’s utility. In research, one might use something like the ACL revision outcomes dataset (which labels if a student revised successfully after feedback) to test if our model’s feedback would likely lead to successful revision.

**Summary of Metrics**: We will report traditional metrics like BLEU and ROUGE for surface-level comparison, use semantic similarity metrics to capture meaning alignment, and heavily incorporate human evaluations for qualities like correctness, relevance, and tone. For an educational feedback generator, high performance means not just parroting a reference (which BLEU/ROUGE check) but truly giving helpful, targeted advice – so our evaluation plan reflects both the NLP overlap measures and educational usefulness measures.

By combining these, we can thoroughly assess the mini LLM’s ability to generate feedback that is content-accurate, pedagogically sound, and phrased in a constructive manner. Each training iteration or model variant can be checked against these benchmarks to guide improvements, ensuring that this small model is ultimately effective in a real classroom scenario.